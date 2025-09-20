
class Portfolio:
    def __init__(self, cash): 
        self.cash = cash          # Starting cash
        self.positions = {}       # {ticker: shares held}
        self.past_trades = []
    
    def buy(self, ticker, price, shares, timestamp):
        cost = price * shares
        if self.cash >= cost:
            self.cash -= cost
            self.positions[ticker] = self.positions.get(ticker, 0) + shares
            self.history.append({'action': 'BUY', 'ticker': ticker, 'price': price, 'shares': shares, 'timestamp': timestamp})
        else:
            print(f"Not enough cash to buy {shares} shares of {ticker}")
    
    def sell(self, ticker, price, shares, timestamp):
        if self.positions.get(ticker, 0) >= shares:
            self.positions[ticker] -= shares
            self.cash += price * shares
            self.history.append({'action': 'SELL', 'ticker': ticker, 'price': price, 'shares': shares, 'timestamp': timestamp}})
        else:
            print(f"Not enough shares to sell {shares} of {ticker}")