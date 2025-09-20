import datetime
from StockData import StockData
from datetime import datetime, timedelta

class Portfolio:
    def __init__(self, cash, var1, var2 = None, positions = None, past_trades = None): 
        self.cash = cash     # Starting cash
        self.var1 = var1 
        self.var2 = var2

        if positions is not None:
            self.positions = positions
        else:
            self.positions = {}       # {ticker: shares held}
        
        if past_trades is not None:
            self.past_trades = past_trades
        else:
            self.past_trades = []
    
    def buy(self, ticker, price, shares, timestamp):

        sd = StockData(ticker, self.var1, self.var2)
        market_price = sd.get_price(timestamp)

        if(market_price > price):
            print(f"Order refused. Market Price higher than {price}")
            return 
        price = min(price, market_price)
        cost = price * shares
        if self.cash >= cost:
            self.cash -= cost
            self.positions[ticker] = self.positions.get(ticker, 0) + shares
            self.past_trades.append({'action': 'BUY', 'ticker': ticker, 'price': price, 'shares': shares, 'timestamp': timestamp})
        else:
            print(f"Not enough cash to buy {shares} shares of {ticker}")
    
    def sell(self, ticker, price, shares, timestamp):
        sd = StockData(ticker, self.var1, self.var2)
        market_price = sd.get_price(timestamp)

        if(market_price < price):
            print(f"Order refused. Market Price lower than {price}")
            return 
        price = max(price, market_price)

        if self.positions.get(ticker, 0) >= shares:
            self.positions[ticker] -= shares
            self.cash += price * shares
            self.past_trades.append({'action': 'SELL', 'ticker': ticker, 'price': price, 'shares': shares, 'timestamp': timestamp})
        else:
            print(f"Not enough shares to sell {shares} of {ticker}")

def main():
    A = Portfolio(100000, "60d", "2m")
    A.buy("AAPL", 225, 100, datetime(2025, 8, 8, 9, 30))
    A.sell("AAPL", 200, 50, datetime(2025, 8, 8, 9, 30))
    print(A.positions)
    print(A.past_trades)


if __name__ == "__main__":
    main()