import os
import pandas as pd
from datetime import datetime, timedelta
from polygon import RESTClient
from decimal import Decimal, ROUND_DOWN

# Initialize Polygon client
polygon_client = RESTClient("rD9rEIzrzJOcVlPq1ttiAyRLyZyquFiF")

# Constants for financial calculations
SHARE_PRECISION = 4  # Number of decimal places for share quantities
CASH_PRECISION = 2  # Number of decimal places for cash amounts

def round_decimal(value, precision):
    """Round a value to the specified precision using Decimal for accuracy"""
    return Decimal(str(value)).quantize(Decimal('0.' + '0' * precision), rounding=ROUND_DOWN)

def get_cached_data(symbol, start_date, end_date):
    """Get data from cache or fetch from Polygon if not cached"""
    cache_dir = 'data_cache'
    os.makedirs(cache_dir, exist_ok=True)
    
    # Create cache filename based on symbol and date range
    cache_file = os.path.join(cache_dir, f"{symbol}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv")
    
    # Check if we have cached data
    if os.path.exists(cache_file):
        print(f"Loading cached data for {symbol}")
        df = pd.read_csv(cache_file, parse_dates=['Date'])
        df.set_index('Date', inplace=True)
        # Ensure we only return data within the requested range
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        return df
    
    # If no cache, fetch from Polygon
    print(f"Fetching fresh data for {symbol}")
    try:
        # Fetch data for the exact date range
        aggs = polygon_client.list_aggs(
            ticker=symbol,
            multiplier=5,
            timespan="minute",
            from_=start_date,
            to=end_date,
            limit=50000
        )
        
        if not aggs:
            print(f"No data available for {symbol}")
            return pd.DataFrame()
            
        # Convert to DataFrame
        df = pd.DataFrame([{
            'Date': pd.to_datetime(agg.timestamp, unit='ms'),
            'Open': agg.open,
            'High': agg.high,
            'Low': agg.low,
            'Close': agg.close,
            'Volume': agg.volume
        } for agg in aggs])
        
        df.set_index('Date', inplace=True)
        
        # Ensure we only return data within the requested range
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        
        # Save to cache
        df.to_csv(cache_file)
        print(f"Cached {len(df)} data points for {symbol}")
        
        return df
        
    except Exception as e:
        print(f"Error downloading {symbol}: {str(e)}")
        return pd.DataFrame()

def is_market_hours(timestamp):
    """Check if the given timestamp is during market hours (9:30 AM - 4:00 PM ET)"""
    # Convert to ET (assuming input is in ET)
    hour = timestamp.hour
    minute = timestamp.minute
    
    # Market hours: 9:30 AM - 4:00 PM ET
    market_start = (9, 30)  # 9:30 AM
    market_end = (16, 0)    # 4:00 PM
    
    current_time = (hour, minute)
    return market_start <= current_time <= market_end

def is_end_of_day(timestamp, next_timestamp):
    """Check if this is the last market data point of the day"""
    if next_timestamp is None:
        return True
    return timestamp.date() != next_timestamp.date() or not is_market_hours(next_timestamp) 