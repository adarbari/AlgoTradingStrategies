import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os
import logging
from typing import Optional, List, Dict
import json
import pyarrow as pa
import pyarrow.parquet as pq
from concurrent.futures import ThreadPoolExecutor, as_completed

class DataFetcher:
    def __init__(self, cache_dir: str = "data_cache", max_workers: int = 4):
        self.cache_dir = cache_dir
        self.max_workers = max_workers
        self._setup_cache()
        self.logger = logging.getLogger(__name__)
        
    def _setup_cache(self):
        """Create cache directory if it doesn't exist"""
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(os.path.join(self.cache_dir, "raw"), exist_ok=True)
        
    def _get_cache_path(self, symbol: str) -> str:
        """Generate cache file path for a given symbol"""
        return os.path.join(self.cache_dir, "raw", f"{symbol}.parquet")
        
    def _is_cached(self, symbol: str) -> bool:
        """Check if data is already cached for the symbol"""
        cache_path = self._get_cache_path(symbol)
        return os.path.exists(cache_path)
        
    def _save_to_cache(self, data: pd.DataFrame, symbol: str):
        """Save data to cache using pyarrow for better performance"""
        cache_path = self._get_cache_path(symbol)
        table = pa.Table.from_pandas(data)
        pq.write_table(table, cache_path, compression='snappy')
        self.logger.info(f"Saved data for {symbol} to cache")
        
    def _load_from_cache(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Load data from cache and filter to requested date range"""
        cache_path = self._get_cache_path(symbol)
        table = pq.read_table(cache_path)
        data = table.to_pandas()
        
        # Make index naive (remove timezone)
        if hasattr(data.index, 'tz') and data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        
        # Convert dates to datetime if they're strings
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        elif not isinstance(start_date, pd.Timestamp):
            start_date = pd.to_datetime(start_date)
            
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)
        elif not isinstance(end_date, pd.Timestamp):
            end_date = pd.to_datetime(end_date)
            
        # Filter data to requested range
        data = data[(data.index >= start_date) & (data.index <= end_date)]
        self.logger.info(f"Loaded data for {symbol} from cache, filtered to {start_date} - {end_date}")
        return data
        
    def _fetch_single_symbol(self, symbol: str, start_date: str, end_date: str, 
                           force_refresh: bool = False) -> Optional[pd.DataFrame]:
        """Fetch intraday data for a single symbol by chunking the date range into 8-day segments."""
        try:
            # Convert dates to datetime if they're strings
            if isinstance(start_date, str):
                start_date = pd.to_datetime(start_date)
            elif not isinstance(start_date, pd.Timestamp):
                start_date = pd.to_datetime(start_date)
                
            if isinstance(end_date, str):
                end_date = pd.to_datetime(end_date)
            elif not isinstance(end_date, pd.Timestamp):
                end_date = pd.to_datetime(end_date)
                
            # Check if we have cached data that covers our range
            if not force_refresh and self._is_cached(symbol):
                cached_data = self._load_from_cache(symbol, start_date, end_date)
                if not cached_data.empty:
                    return cached_data
                    
            self.logger.info(f"Downloading intraday data for {symbol}")
            delta = pd.Timedelta(days=8)
            data_list = []
            
            # Use 5-minute interval (change to '15m' if you want 15-minute bars)
            interval = '5m'  # or '15m'
            
            current_start = start_date
            while current_start < end_date:
                current_end = min(current_start + delta, end_date)
                self.logger.debug(f"Fetching data for {symbol} from {current_start} to {current_end}")
                chunk = yf.download(symbol, start=current_start, end=current_end, interval=interval, progress=False)
                if not chunk.empty:
                    data_list.append(chunk)
                current_start = current_end
            
            if not data_list:
                self.logger.warning(f"No data found for {symbol}")
                return None
                
            data = pd.concat(data_list)
            data.index = pd.to_datetime(data.index)
            
            # Save to cache
            self._save_to_cache(data, symbol)
            
            # Return only the requested date range
            return data[(data.index >= start_date) & (data.index <= end_date)]
            
        except Exception as e:
            self.logger.error(f"Error downloading data for {symbol}: {str(e)}")
            return None
            
    def fetch_data(self, symbol: str, start_date: str, end_date: str, 
                  force_refresh: bool = False) -> pd.DataFrame:
        """
        Fetch data for a symbol, using cache if available
        
        Args:
            symbol: Stock symbol
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            force_refresh: If True, ignore cache and download fresh data
            
        Returns:
            DataFrame with OHLCV data
        """
        data = self._fetch_single_symbol(symbol, start_date, end_date, force_refresh)
        if data is None:
            raise ValueError(f"Failed to fetch data for {symbol}")
        return data
            
    def fetch_multiple_symbols(self, symbols: List[str], start_date: str, end_date: str, 
                             force_refresh: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple symbols using parallel processing
        
        Args:
            symbols: List of stock symbols
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            force_refresh: If True, ignore cache and download fresh data
            
        Returns:
            Dictionary mapping symbols to their respective DataFrames
        """
        results = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Create future tasks
            future_to_symbol = {
                executor.submit(
                    self._fetch_single_symbol, 
                    symbol, 
                    start_date, 
                    end_date, 
                    force_refresh
                ): symbol for symbol in symbols
            }
            
            # Process completed tasks
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    data = future.result()
                    if data is not None:
                        results[symbol] = data
                except Exception as e:
                    self.logger.error(f"Failed to fetch {symbol}: {str(e)}")
                    
        return results 