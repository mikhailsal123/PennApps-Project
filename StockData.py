import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

'''Code for the data struture storing stock time series and analysis functions'''

class StockData:
    period_limit = 60 # 60 days for minute intervals 
    interval_set = set(["1m", "2m", "5m", "15m", "30m", "60m"])

    def __init__(self, stock_symbol, var1, var2 = None): # var1 and var2 define which 
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
            self.curtime = self.stock_data.index[0]
        

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
    
    def get_price(self):
        time = self.curtime
        if time in self.stock_data.index:
            mid_price = (float(self.stock_data.loc[time, "High"]) + float(self.stock_data.loc[time, "Low"]))/2
            return mid_price
        else:
            print("Market is not open at this time")
    
    def moving_average(self, window='1h'):
        self.stock_data["SMA"] = self.stock_data['Close'].rolling(window=window).mean()
        return self.stock_data.loc[self.curtime, "SMA"]

    def price_increase(self):
        current_time = self.curtime
        start_time = self.stock_data.index[0]
        # Get the start price
        if start_time in self.stock_data.index:
            start_price = self.stock_data.loc[start_time, 'Close']
        else:
            # Find the closest available time to start_time
            available_times = self.stock_data.index
            if len(available_times) == 0:
                print("No data available for start time")
                return None
            
            # Find the closest time after or equal to start_time
            valid_times = available_times[available_times >= start_time]
            if len(valid_times) == 0:
                print(f"No data available after start time {start_time}")
                return None
            
            closest_start_time = valid_times[0]
            start_price = self.stock_data.loc[closest_start_time, 'Close']
        
        # Get the current price
        if current_time is None:
            # Use the latest available time
            current_price = self.stock_data['Close'].iloc[-1]
            current_time = self.stock_data.index[-1]
        else:
            if current_time in self.stock_data.index:
                current_price = self.stock_data.loc[current_time, 'Close']
            else:
                # Find the closest available time to current_time
                available_times = self.stock_data.index
                valid_times = available_times[available_times <= current_time]
                if len(valid_times) == 0:
                    print(f"No data available before current time {current_time}")
                    return None
                
                closest_current_time = valid_times[-1]
                current_price = self.stock_data.loc[closest_current_time, 'Close']
                current_time = closest_current_time
        
        # Calculate percentage change
        if start_price == 0:
            print("Start price is zero, cannot calculate percentage change")
            return None
        
        change_pct = (current_price - start_price) / start_price * 100
        
        return change_pct


def main():
    # Test with date range data
    df = StockData("AAPL", "2025-08-08", "2025-09-08")
    print(f"Stock: {df.ticker}")
    print(f"Data range: {df.stock_data.index[0]} to {df.stock_data.index[-1]}")
    # Test price increase with specific times
    df.curtime = datetime(2025, 8, 20)
    change = df.price_increase()
    print(change)
    print(df.moving_average())

if __name__ == "__main__":
    main()