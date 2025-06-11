from typing import Dict, List, Union, Optional
import os
import pandas as pd
from datetime import datetime
import time
from polygon import RESTClient
from ..base import DataProvider, DataCache

class PolygonProvider(DataProvider):
    """Polygon.io data provider implementation."""
    def __init__(self, api_key: str = None, cache: Optional[DataCache] = None):
        # Always use the working API key
        api_key = "rD9rEIzrzJOcVlPq1ttiAyRLyZyquFiF"
        self.client = RESTClient(api_key)
        super().__init__(cache=cache)
        self._cache_dir = 'data_cache'
        os.makedirs(self._cache_dir, exist_ok=True)
        # Add delay between requests (in seconds)
        self.request_delay = 2.0  # 2 seconds delay between requests
        self.max_retries = 3  # Maximum number of retries
        self.base_delay = 5.0  # Base delay for exponential backoff (in seconds)

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names to lowercase."""
        df.columns = df.columns.str.lower()
        return df

    def _make_api_request(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Make API request with retry mechanism."""
        for attempt in range(self.max_retries):
            try:
                # Add delay before making API request
                time.sleep(self.request_delay)
                
                # Fetch from API
                aggs = self.client.list_aggs(
                    ticker=symbol,
                    multiplier=5,
                    timespan="minute",
                    from_=start_date.strftime('%Y-%m-%d'),
                    to=end_date.strftime('%Y-%m-%d'),
                    limit=50000
                )
                
                if not aggs:
                    return pd.DataFrame()
                    
                df = pd.DataFrame([{
                    'Date': pd.to_datetime(agg.timestamp, unit='ms'),
                    'open': agg.open,
                    'high': agg.high,
                    'low': agg.low,
                    'close': agg.close,
                    'volume': agg.volume
                } for agg in aggs])
                
                df.set_index('Date', inplace=True)
                df = df[(df.index >= start_date) & (df.index <= end_date)]
                return df
                
            except Exception as e:
                if '429' in str(e) and attempt < self.max_retries - 1:
                    # Calculate exponential backoff delay
                    delay = self.base_delay * (2 ** attempt)
                    print(f"Rate limit hit. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise e
        
        return pd.DataFrame()

    def get_historical_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = '5min'
    ) -> pd.DataFrame:
        """Fetch historical data from Polygon.io."""
        # Convert dates
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)
            
        # Try to get from cache first
        if self.cache:
            cached_data = self.cache.get_cached_data(
                symbol=symbol,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            if cached_data is not None:
                return cached_data
        
        # Fetch from API with retry mechanism
        df = self._make_api_request(symbol, start_date, end_date)
        
        # Cache the data if we got any
        if not df.empty and self.cache:
            self.cache.cache_data(
                symbol=symbol,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                data=df
            )
        
        return df

    def get_realtime_data(
        self,
        symbol: str,
        interval: str = '1m'
    ) -> pd.DataFrame:
        # Polygon does not provide free real-time data; return empty
        return pd.DataFrame()

    def get_market_data(
        self,
        symbols: List[str],
        data_types: List[str]
    ) -> Dict[str, pd.DataFrame]:
        result = {}
        for symbol in symbols:
            result[symbol] = {'history': self.get_historical_data(symbol, '2023-01-01', '2023-12-31')}
        return result

    def get_company_info(
        self,
        symbol: str
    ) -> Dict[str, Union[str, float, int]]:
        # Polygon's company info API is not implemented here
        return {'symbol': symbol} 