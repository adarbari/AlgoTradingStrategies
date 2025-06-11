from decimal import Decimal, ROUND_DOWN
from datetime import datetime, time

# Constants for decimal precision
SHARE_PRECISION = Decimal('0.000001')  # 6 decimal places for shares
CASH_PRECISION = Decimal('0.01')       # 2 decimal places for cash

def is_market_hours(current_time, next_time=None):
    """
    Check if the current time is during market hours (9:30 AM - 4:00 PM ET)
    """
    market_open = time(9, 30)
    market_close = time(16, 0)
    
    if isinstance(current_time, datetime):
        current_time = current_time.time()
    
    return market_open <= current_time <= market_close

def is_end_of_day(current_time, next_time=None):
    """
    Check if the current time is at the end of the trading day
    """
    market_close = time(16, 0)
    
    if isinstance(current_time, datetime):
        current_time = current_time.time()
    
    if next_time is not None:
        if isinstance(next_time, datetime):
            next_time = next_time.time()
        return current_time >= market_close or next_time < current_time
    
    return current_time >= market_close

def round_decimal(value, precision):
    """
    Round a Decimal value to the specified precision
    """
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(precision, rounding=ROUND_DOWN) 