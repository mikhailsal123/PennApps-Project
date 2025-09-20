import yfinance as yf
from datetime import datetime, timedelta

period_limit = 60 # 60 days
interval_set = set(["1m", "2m", "5m", "15m", "30m", "60m"])
# print error when no data is found
def stock_error_message(stock_symbol, date):
    print(f"${stock_symbol}: No data found for {date}")
    print("This might be because:")
    print("- The date falls on a weekend or holiday")
    print("- The stock symbol is invalid")

# get stock data in a range (per day basis)
def get_stock_data(stock_symbol, start_date, end_date):
    """Get stock data for a given symbol and date range.
    Args:
        stock_symbol: Stock ticker symbol (e.g., 'AAPL')
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
    Returns:
        pandas.DataFrame: Stock data or empty DataFrame if no data found"""

    if start_date == end_date:
        return "Error: End date is the same as start date"
    
    stock = yf.Ticker(stock_symbol)
    stock_data = stock.history(start=start_date, end=end_date)
        
    if stock_data.empty:
        stock_error_message(stock_symbol, start_date)
        
    return stock_data

# get stock data (per day basis)
def get_stock_data_for_date(stock_symbol, date):
    """Get stock data for a specific date.
    Args:
        stock_symbol: ticker symbol (e.g., 'AAPL')
        date: Date in 'YYYY-MM-DD' format
    Returns:
        pandas.DataFrame: Stock data for the specific date"""

    stock = yf.Ticker(stock_symbol)
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    new_date = date_obj + timedelta(days=1)
    stock_data = stock.history(start = date, end = new_date.strftime('%Y-%m-%d'))
        
    if stock_data.empty:
        stock_error_message(stock_symbol, date)
        
    return stock_data

# retrive stock data for minute time intervals 
def get_stock_data_for_time_interval(stock_symbol, period, interval):
    """Get stock data for a specific time interval.
    Args:
        stock_symbol: ticker symbol (e.g., 'AAPL')
        period: period (e.g., '1d', '5d', '1mo')
        interval: interval (e.g., '1m', '5m', '15m', '30m', '60m')
    Returns:
        pandas.DataFrame: Stock data for the specific time interval"""
    
    if int(period[0:-1]) > period_limit and 'm' in interval:
        return "Error: Period cannot be greater than 60 days for minute intervals"
    elif interval not in interval_set:
        return "Error: Invalid interval"
    elif int(period[0:-1]) > 8 and interval == "1m":
        return "Error: Period cannot be greater than 8 days for 1-minute intervals"
    
    stock = yf.Ticker(stock_symbol)
    stock_data = stock.history(period=period, interval=interval)
        
    if stock_data.empty:
        stock_error_message(stock_symbol, period)
        
    return stock_data

def main():
    print(get_stock_data("AAPL", "2024-01-04", "2024-01-06")) # end date is exclusive
    print(get_stock_data_for_date("AAPL", "2024-01-04")) 
    print(get_stock_data_for_time_interval("AAPL", "58d", "1m"))

if __name__ == "__main__":
    main()