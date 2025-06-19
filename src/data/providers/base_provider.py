from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional
from datetime import datetime
from ..types.base_types import TimeSeriesData
from ..types.data_config_types import DataConfig
from ..cache.smart_cache import SmartCache

T = TypeVar('T')
C = TypeVar('C', bound=DataConfig)

class DataProvider(ABC, Generic[T, C]):
    """
    Base class for all data providers.
    This is the core provider interface without caching.
    
    Type Parameters:
        T: The type of data this provider returns
        C: The type of configuration this provider accepts
    """
    
    @abstractmethod
    def get_data(self, symbol: str, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None, config: Optional[C] = None) -> TimeSeriesData[T]:
        """
        Fetch data directly from the vendor.
        This is the core method that concrete providers must implement.
        
        Args:
            symbol: The trading symbol
            start_time: Optional start time for historical data
            end_time: Optional end time for historical data
            config: Optional configuration for the data request
            
        Returns:
            TimeSeriesData containing the requested data
        """
        pass

class CachedDataProvider(DataProvider[T, C]):
    """
    Decorator that adds caching to any DataProvider.
    This follows the Decorator pattern to add caching functionality
    without modifying the original provider.
    """
    
    def __init__(self, provider: DataProvider[T, C], cache: Optional[SmartCache[T]] = None):
        """
        Initialize with a provider and optional cache.
        
        Args:
            provider: The underlying data provider
            cache: Optional cache instance. If None, creates a new one.
        """
        self.provider = provider
        self.cache = cache or SmartCache[T]()

    def get_data(self, symbol: str, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None, config: Optional[C] = None) -> TimeSeriesData[T]:
        """
        Get data with caching support.
        First checks cache, then fetches missing data from provider.
        
        Args:
            symbol: The trading symbol
            start_time: Optional start time for historical data
            end_time: Optional end time for historical data
            config: Optional configuration for the data request
            
        Returns:
            TimeSeriesData containing the requested data
        """
        return self.cache.get_data(
            symbol=symbol,
            start_time=start_time,
            end_time=end_time,
            provider=self.provider
        ) 