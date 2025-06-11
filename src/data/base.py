from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import pandas as pd
import os
import joblib
from datetime import datetime
import glob

class DataCache(ABC):
    """Base class for data caching."""
    
    def __init__(self, cache_dir: str = 'data_cache'):
        """Initialize the data cache.
        
        Args:
            cache_dir: Directory to store cached data
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, symbol: str, start_date: str, end_date: str) -> str:
        """Get the cache file path for a given symbol and date range."""
        return os.path.join(
            self.cache_dir,
            f"{symbol}_{start_date}_{end_date}.joblib"
        )
    
    def get_cached_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> Optional[pd.DataFrame]:
        """Get cached data if it exists.
        
        Args:
            symbol: Stock symbol
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with cached data or None if not found
        """
        cache_path = self._get_cache_path(symbol, start_date, end_date)
        if os.path.exists(cache_path):
            try:
                return joblib.load(cache_path)
            except Exception as e:
                print(f"Error loading cache file {cache_path}: {e}")
        return None
    
    def cache_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        data: pd.DataFrame
    ) -> None:
        """Cache data.
        
        Args:
            symbol: Stock symbol
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            data: DataFrame containing the data
        """
        if data.empty:
            return
            
        cache_path = self._get_cache_path(symbol, start_date, end_date)
        try:
            joblib.dump(data, cache_path)
        except Exception as e:
            print(f"Error caching data: {e}")
    
    def clear_cache(self, symbol: Optional[str] = None) -> None:
        """Clear the cache.
        
        Args:
            symbol: If provided, only clear cache for this symbol
        """
        if symbol:
            pattern = f"{symbol}_*.joblib"
            for file in glob.glob(os.path.join(self.cache_dir, pattern)):
                os.remove(file)
        else:
            for file in glob.glob(os.path.join(self.cache_dir, "*.joblib")):
                os.remove(file)

class DataProvider(ABC):
    """Base class for all data providers."""
    
    def __init__(self, cache: Optional[DataCache] = None):
        """Initialize the data provider.
        
        Args:
            cache: Optional data cache instance
        """
        self.cache = cache
    
    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = '1d'
    ) -> pd.DataFrame:
        """Fetch historical data for a given symbol and date range."""
        pass
    
    @abstractmethod
    def get_realtime_data(
        self,
        symbol: str,
        interval: str = '1m'
    ) -> pd.DataFrame:
        """Fetch real-time data for a given symbol."""
        pass
    
    @abstractmethod
    def get_market_data(
        self,
        symbols: List[str],
        data_types: List[str]
    ) -> Dict[str, pd.DataFrame]:
        """Fetch market data for multiple symbols and data types."""
        pass
    
    @abstractmethod
    def get_company_info(
        self,
        symbol: str
    ) -> Dict[str, Union[str, float, int]]:
        """Fetch company information for a given symbol."""
        pass 