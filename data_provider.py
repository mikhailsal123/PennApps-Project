import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta


class DataProviderError(Exception):
    pass


class BaseDataProvider:
    def validate_ticker(self, symbol: str) -> dict:
        raise NotImplementedError

    def get_history(
        self,
        symbol: str,
        start: datetime | None = None,
        end: datetime | None = None,
        period: str | None = None,
        interval: str = "1d",
    ) -> pd.DataFrame:
        raise NotImplementedError


class AlphaVantageProvider(BaseDataProvider):
    """Alpha Vantage-backed data provider.

    Notes (free tier constraints):
    - Intraday endpoints return up to ~100-500 points depending on function/plan
    - Daily adjusted supports long history
    - Rate limit ~5 req/min on free key; we add basic backoff
    """

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("ALPHAVANTAGE_API_KEY", "demo")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "TradeSphere/1.0 (+https://github.com/mikhailsal123/TradeSphere.ai)",
            "Accept": "application/json",
        })

    def _get(self, params: dict, retries: int = 3, backoff: float = 1.0) -> dict:
        params = {**params, "apikey": self.api_key}
        for attempt in range(retries):
            resp = self.session.get(self.BASE_URL, params=params, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                if "Note" in data or "Information" in data:
                    time.sleep(backoff)
                    backoff *= 1.5
                    continue
                return data
            time.sleep(backoff)
            backoff *= 1.5
        raise DataProviderError(f"AlphaVantage request failed: {resp.status_code}")

    def validate_ticker(self, symbol: str) -> dict:
        symbol = symbol.upper().strip()
        data = self._get({
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
        })
        quote = data.get("Global Quote") or {}
        valid = bool(quote.get("01. symbol"))
        return {
            "valid": valid,
            "ticker": symbol,
            "name": symbol,
            "exchange": "Unknown",
            "source": "alpha_vantage",
        }

    def get_history(
        self,
        symbol: str,
        start: datetime | None = None,
        end: datetime | None = None,
        period: str | None = None,
        interval: str = "1d",
    ) -> pd.DataFrame:
        symbol = symbol.upper().strip()

        # Normalize window
        if end is None:
            end = datetime.utcnow()
        if start is None and period is None:
            # default to 30d
            start = end - timedelta(days=30)

        if interval in {"1m", "5m", "15m", "30m", "60m"}:
            # Alpha Vantage intraday
            av_interval = interval if interval != "60m" else "60min"
            if av_interval.endswith("m") and av_interval != "60min":
                av_interval = av_interval.replace("m", "min")
            data = self._get({
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": av_interval,
                "outputsize": "compact",  # free: ~100 points
                "adjusted": "true",
            })
            key = next((k for k in data.keys() if "Time Series" in k), None)
            ts = data.get(key, {}) if key else {}
            rows = []
            for ts_str, v in ts.items():
                try:
                    ts_dt = datetime.fromisoformat(ts_str)
                except Exception:
                    # Alpha uses "YYYY-MM-DD HH:MM:SS"
                    ts_dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                rows.append({
                    "Datetime": ts_dt,
                    "Open": float(v.get("1. open", 0) or 0),
                    "High": float(v.get("2. high", 0) or 0),
                    "Low": float(v.get("3. low", 0) or 0),
                    "Close": float(v.get("4. close", 0) or 0),
                    "Volume": float(v.get("5. volume", 0) or 0),
                })
            df = pd.DataFrame(rows).sort_values("Datetime").set_index("Datetime")
            if start is not None:
                df = df[df.index >= start]
            if end is not None:
                df = df[df.index <= end]
            return df

        # Daily adjusted
        data = self._get({
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": "full",
        })
        ts = data.get("Time Series (Daily)", {})
        rows = []
        for d_str, v in ts.items():
            d_dt = datetime.strptime(d_str, "%Y-%m-%d")
            rows.append({
                "Date": d_dt,
                "Open": float(v.get("1. open", 0) or 0),
                "High": float(v.get("2. high", 0) or 0),
                "Low": float(v.get("3. low", 0) or 0),
                "Close": float(v.get("4. close", 0) or 0),
                "Adj Close": float(v.get("5. adjusted close", v.get("4. close", 0)) or 0),
                "Volume": float(v.get("6. volume", 0) or 0),
            })
        df = pd.DataFrame(rows).sort_values("Date").set_index("Date")
        if start is not None:
            df = df[df.index >= start]
        if end is not None:
            df = df[df.index <= end]
        # Align columns to expected schema
        if "Adj Close" in df.columns:
            df["Close"] = df["Adj Close"]
            df = df.drop(columns=["Adj Close"])
        return df


def get_provider() -> BaseDataProvider:
    # For now, always Alpha Vantage. Can be extended via ENV switch.
    return AlphaVantageProvider()


