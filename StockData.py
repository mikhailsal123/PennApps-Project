import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

'''Code for the data struture storing stock time series and analysis functions'''

class StockData:
    period_limit = 60 # 60 days for minute intervals 
    interval_set = set(["1m", "2m", "5m", "15m", "30m", "60m"])

    def __init__(self, stock_symbol, var1, var2 = None):
        self.ticker = stock_symbol
        if var2 is None:
            self.get_stock_data_for_date(stock_symbol, var1)
        #date format length
        elif len(var2) == 10:
            self.get_stock_data(stock_symbol, var1, var2)
        else:
            self.get_stock_data_for_time_interval(stock_symbol, var1, var2)

    # print error when no data is found
    def stock_error_message(self, stock_symbol, date):
        print(f"${stock_symbol}: No data found for {date}")
        print("This might be because:")
        print("- The date falls on a weekend or holiday")
        print("- The stock symbol is invalid")

    # get stock data in a range (per day basis)
    def get_stock_data(self, stock_symbol, start_date, end_date):
        """Get stock data for a given symbol and date range.
        Args:
            stock_symbol: Stock ticker symbol (e.g., 'AAPL')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
        Returns:
            pandas.DataFrame: Stock data or empty DataFrame if no data found"""

        if start_date == end_date:
            print("Error: End date is the same as start date")
    
        stock = yf.Ticker(stock_symbol)
        self.stock_data = stock.history(start=start_date, end=end_date)
        
        if self.stock_data.empty:
            self.stock_error_message(stock_symbol, start_date)
        else:
            self.stock_data.index = self.stock_data.index.tz_localize(None)

    # get stock data (per day basis)
    def get_stock_data_for_date(self, stock_symbol, date):
        """Get stock data for a specific date.
        Args:
            stock_symbol: ticker symbol (e.g., 'AAPL')
            date: Date in 'YYYY-MM-DD' format
        Returns:
            pandas.DataFrame: Stock data for the specific date"""

        stock = yf.Ticker(stock_symbol)
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        new_date = date_obj + timedelta(days=1)
        self.stock_data = stock.history(start = date, end = new_date.strftime('%Y-%m-%d'))
        
        if self.stock_data.empty:
            self.stock_error_message(stock_symbol, date)
        else:
            self.stock_data.index = self.stock_data.index.tz_localize(None)

    # retrive stock data for minute time intervals 
    def get_stock_data_for_time_interval(self, stock_symbol, period, interval):
        """Get stock data for a specific time interval.
        Args:
            stock_symbol: ticker symbol (e.g., 'AAPL')
            period: period (e.g., '1d', '5d', '1mo')
            interval: interval (e.g., '1m', '5m', '15m', '30m', '60m')
        Returns:
            pandas.DataFrame: Stock data for the specific time interval"""
    
        if int(period[0:-1]) > self.period_limit and 'm' in interval:
            return "Error: Period cannot be greater than 60 days for minute intervals"
        elif interval not in self.interval_set:
            return "Error: Invalid interval"
        elif int(period[0:-1]) > 8 and interval == "1m":
            return "Error: Period cannot be greater than 8 days for 1-minute intervals"
    
        stock = yf.Ticker(stock_symbol)
        self.stock_data = stock.history(period=period, interval=interval)
        
        if self.stock_data.empty:
            self.stock_error_message(stock_symbol, period)
        else:
            self.stock_data.index = self.stock_data.index.tz_localize(None)
    
    def get_price(self, time):
        if time in self.stock_data.index:
            mid_price = (float(self.stock_data.loc[time, "High"]) + float(self.stock_data.loc[time, "Low"]))/2
            return mid_price

def main():
    df = StockData("AAPL", "60d", "2m")
    print(df.stock_data)
    print(df.ticker)
    print(df.get_price(datetime(2025, 8, 8, 9, 30)))

if __name__ == "__main__":
    main()