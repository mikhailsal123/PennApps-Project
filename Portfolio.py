import datetime
from StockData import StockData
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
        
        self.original_value = cash  #keep track of original value fo the portfolio
        self.change_over_time = {}  # {timestamp: portfolio_value}
    
    def get_value(self, timestamp):
        position_val = self.cash
        market_closed = False
        
        for position in self.positions.keys():
            sd = StockData(position, self.var1, self.var2)
            market_price = sd.get_price(timestamp)
            if(market_price is None):
                market_closed = True
                break
            position_val += (market_price * self.positions[position])
        
        # If market is closed, use the last known portfolio value
        if market_closed:
            if self.change_over_time:
                # Get the most recent portfolio value
                last_timestamp = max(self.change_over_time.keys())
                position_val = self.change_over_time[last_timestamp]
                print(f"Market closed at {timestamp}. Using last known value: ${position_val:,.2f}")
            else:
                # If no previous data, just return cash value
                position_val = self.cash
                print(f"Market closed at {timestamp}. No previous data. Using cash value: ${position_val:,.2f}")
        
        # Track value over time
        self.change_over_time[timestamp] = position_val
        return position_val

    def get_PNL(self, timestamp):
        value = self.get_value(timestamp)
        if value is not None:
            return value - self.original_value

    def summary(self, timestamp):
        print("CASH:", self.cash)
        print("POSITIONS:")
        for ticker, shares in self.positions.items():
            sd = StockData(ticker, self.var1, self.var2)
            market_price = sd.get_price(timestamp)
            print(f"  {ticker}: {shares} shares @ ${market_price}")
        print("TOTAL VALUE:", self.get_value(timestamp))
    
    def buy(self, ticker, price, shares, timestamp):

        sd = StockData(ticker, self.var1, self.var2)
        market_price = sd.get_price(timestamp)
        if(market_price is None):
            return

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
        if(market_price is None):
            return

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

    def plot_portfolio_value(self, title="Portfolio Value Over Time", save_path=None, show_percentage=False):
        """
        Plot the portfolio value changes over time.
        Shows constant values during market closures.
        
        Args:
            title (str): Title for the plot
            save_path (str): Optional path to save the plot as an image
            show_percentage (bool): If True, show percentage changes from original value
        """
        if not self.change_over_time:
            print("No portfolio value data available. Call get_value() with timestamps first.")
            return
        
        # Sort timestamps and values
        timestamps = sorted(self.change_over_time.keys())
        values = [self.change_over_time[ts] for ts in timestamps]
        
        # Calculate percentage changes if requested
        if show_percentage:
            values = [((val - self.original_value) / self.original_value) * 100 for val in values]
            ylabel = 'Portfolio Value Change (%)'
            title += " (Percentage Change)"
        else:
            ylabel = 'Portfolio Value ($)'
        
        # Create the plot
        plt.figure(figsize=(12, 6))
        
        # Plot the main line
        plt.plot(timestamps, values, marker='o', linewidth=2, markersize=4, color='blue', label='Portfolio Value')
        
        # Identify and highlight constant value periods (market closures)
        constant_periods = []
        current_period_start = None
        current_value = None
        
        for i, (ts, val) in enumerate(zip(timestamps, values)):
            if i == 0:
                current_value = val
                current_period_start = ts
            elif val == current_value and i < len(values) - 1:
                # Still in a constant period
                continue
            else:
                # Value changed or end of data
                if current_period_start and i > 1:  # Only highlight if period has multiple points
                    constant_periods.append((current_period_start, timestamps[i-1], current_value))
                current_value = val
                current_period_start = ts
        
        # Highlight constant value periods with different styling
        for start_ts, end_ts, const_val in constant_periods:
            period_timestamps = [ts for ts in timestamps if start_ts <= ts <= end_ts]
            period_values = [self.change_over_time[ts] for ts in period_timestamps]
            plt.plot(period_timestamps, period_values, '--', color='gray', alpha=0.7, linewidth=1)
        
        # Add horizontal line for original value
        if show_percentage:
            plt.axhline(y=0, color='r', linestyle='--', alpha=0.7, label='Original Value (0%)')
        else:
            plt.axhline(y=self.original_value, color='r', linestyle='--', alpha=0.7, label=f'Original Value: ${self.original_value:,.2f}')
        
        # Formatting
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Format x-axis dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.xticks(rotation=45)
        
        # Format y-axis based on display type
        if show_percentage:
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1f}%'))
        else:
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Adjust y-axis to show changes more proportionally
        if len(values) > 1:
            min_val = min(values)
            max_val = max(values)
            range_val = max_val - min_val
            
            # Add padding but limit it to reasonable bounds
            if range_val > 0:
                if show_percentage:
                    # More sensitive scaling for percentage view - smaller padding
                    padding = max(range_val * 0.2, 0.1)  # 20% padding, minimum 0.1%
                else:
                    padding = max(range_val * 0.1, 100)  # At least $100 padding
                plt.ylim(min_val - padding, max_val + padding)
            else:
                # If all values are the same, add small padding around the value
                if show_percentage:
                    plt.ylim(min_val - 0.1, min_val + 0.1)  # Small percentage padding
                else:
                    plt.ylim(min_val - 100, min_val + 100)  # Small dollar padding
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
        
        plt.show()

    def plot_pnl(self, title="Portfolio P&L Over Time", save_path=None):
        """
        Plot the portfolio profit and loss over time.
        
        Args:
            title (str): Title for the plot
            save_path (str): Optional path to save the plot as an image
        """
        if not self.change_over_time:
            print("No portfolio value data available. Call get_value() with timestamps first.")
            return
        
        # Sort timestamps and calculate P&L
        timestamps = sorted(self.change_over_time.keys())
        pnl_values = [self.change_over_time[ts] - self.original_value for ts in timestamps]
        
        # Create the plot
        plt.figure(figsize=(12, 6))
        
        # Use different colors for profit/loss
        colors = ['green' if pnl >= 0 else 'red' for pnl in pnl_values]
        plt.bar(range(len(timestamps)), pnl_values, color=colors, alpha=0.7)
        
        # Add horizontal line at zero
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        # Formatting
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel('Time Points', fontsize=12)
        plt.ylabel('Profit/Loss ($)', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Set x-axis labels
        plt.xticks(range(len(timestamps)), [ts.strftime('%m/%d %H:%M') for ts in timestamps], rotation=45)
        
        # Format y-axis as currency
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
        
        plt.show()

def main():
    A = Portfolio(100000, "60d", "2m")
    
    # Make some trades
    A.buy("AAPL", 225, 100, datetime(2025, 8, 8, 9, 30))
    A.sell("AAPL", 200, 50, datetime(2025, 8, 8, 9, 30))
    A.buy("NVDA", 300, 100, datetime(2025, 8, 8, 9, 30))
    
    # Track portfolio value at different times
    print("Tracking portfolio value over time...")
    A.get_value(datetime(2025, 8, 8, 9, 30))   # After trades
    A.get_value(datetime(2025, 8, 9, 9, 30))   # Next day
    A.get_value(datetime(2025, 8, 10, 9, 30))  # Day after
    A.get_value(datetime(2025, 8, 11, 9, 30))  # Another day
    A.get_value(datetime(2025, 8, 12, 9, 30))  # Final day
    A.get_value(datetime(2025, 8, 13, 9, 30))
    A.get_value(datetime(2025, 8, 14, 9, 30))
    A.get_value(datetime(2025, 8, 15, 9, 30))
    A.get_value(datetime(2025, 8, 16, 9, 30))
    A.get_value(datetime(2025, 8, 17, 9, 30))
    A.get_value(datetime(2025, 8, 18, 9, 30))
    A.get_value(datetime(2025, 8, 19, 9, 30))
    A.get_value(datetime(2025, 8, 20, 9, 30))
    
    print("\nPortfolio Summary:")
    print(A.positions)
    print(A.past_trades)
    print(f"P&L: ${A.get_PNL(datetime(2025, 8, 11, 9, 30)):,.2f}")
    print(f"Current Value: ${A.get_value(datetime(2025, 8, 11, 9, 30)):,.2f}")
    
    # Plot the portfolio value over time
    print("\nGenerating plots...")
    A.plot_portfolio_value("My Portfolio Performance")
    A.plot_portfolio_value("My Portfolio Performance (Percentage View)", show_percentage=True)
    A.plot_pnl("Portfolio Profit & Loss")

if __name__ == "__main__":
    main()