"""
Data manager for handling data access and caching.
"""

from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any, List, Tuple
import pandas as pd
import dataclasses

from src.data.cache.smart_cache import SmartCache
from src.data.providers.ohlcv_provider import OHLCVDataProvider
from src.data.providers.vendors.polygon.polygon_provider import PolygonProvider
from src.data.types.base_types import TimeSeriesData, MissingDataRange
from src.data.types.ohlcv_types import OHLCVData
from src.data.types.data_config_types import OHLCVConfig, OrderFlowConfig
from src.data.types.data_type import DataType


class DataManager:
    """
    Central manager for data access and caching.
    
    This class provides a unified interface for accessing market data,
    handling caching, and managing different data providers. It implements
    smart caching that can handle partial data availability.
    """
    
    def __init__(
        self,
        ohlcv_provider: Optional[OHLCVDataProvider] = None,
        cache: Optional[SmartCache] = None
    ):
        """
        Initialize the data manager.
        
        Args:
            ohlcv_provider: Optional OHLCV data provider
            cache: Optional cache instance
        """
        self.ohlcv_provider = ohlcv_provider or PolygonProvider()
        self.cache = cache or SmartCache()
    
    def _get_data(
        self,
        provider,
        symbol: str,
        data_type: DataType, 
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        config,
        config_default,
    ) -> TimeSeriesData:
        """
        Get data from cache and provider, handling missing ranges.
        
        Args:
            provider: Data provider
            symbol: Trading symbol
            start_time: Start time for data
            end_time: End time for data
            config: Data configuration
            config_default: Default configuration class
            
        Returns:
            TimeSeriesData containing the requested data
        """
        if not provider:
            raise ValueError("No provider configured")
        if config is None:
            config = config_default()
            
        # Get missing ranges from cache metadata
        missing_ranges = self.cache.metadata.get_missing_ranges(
            symbol=symbol,
            data_type=data_type,
            start_time=start_time,
            end_time=end_time
        )
        
        # If we have all the data cached, return it
        if not missing_ranges:
            cached_df = self.cache.get_cached_data(symbol, data_type,start_time, end_time)
            if cached_df is not None:
                return cached_df
            
        # Fetch missing data ranges
        new_data = TimeSeriesData(timestamps=[], data=[], data_type=data_type)
        for missing_start, missing_end in missing_ranges:
            range_data = provider.get_data(
                symbol=symbol,
                start_time=missing_start,
                end_time=missing_end,
                config=config
            )
            if range_data is not None:
                new_data = self._merge_data(new_data, range_data)
                
                # Cache the new data
                if range_data.timestamps:
                    df = pd.DataFrame(range_data.data, index=range_data.timestamps)
                    self.cache.cache_data(
                        symbol=symbol,
                        data_type=data_type,
                        start_time=missing_start,
                        end_time=missing_end,
                        data=range_data
                    )
        
        # Get cached data for the entire range
        cached_data = self.cache.get_cached_data(symbol, data_type, start_time, end_time)
        new_data = self._merge_data(cached_data, new_data)
        
        return new_data
    
    def _merge_data(
        self,
        cached_data: TimeSeriesData,
        new_data: TimeSeriesData
    ) -> TimeSeriesData:
        """
        Merge cached and new data, handling overlaps.
        
        Args:
            cached_data: TimeSeriesData with cached data
            new_data: TimeSeriesData with newly fetched data
            
        Returns:
            Merged TimeSeriesData
        """
        if not cached_data.timestamps:
            return new_data
        if not new_data.timestamps:
            return cached_data
            
        # Convert data to dictionaries if they're dataclass instances
        cached_dicts = [
            dataclasses.asdict(d) if hasattr(d, '__dataclass_fields__') else d
            for d in cached_data.data
        ]
        new_dicts = [
            dataclasses.asdict(d) if hasattr(d, '__dataclass_fields__') else d
            for d in new_data.data
        ]
        
        # Combine data and remove duplicates
        all_timestamps = cached_data.timestamps + new_data.timestamps
        all_data = cached_dicts + new_dicts
        
        # Create DataFrame for easier manipulation
        df = pd.DataFrame(all_data, index=all_timestamps)
        df = df.sort_index().loc[~df.index.duplicated(keep='last')]
        
        # Convert back to the original data format
        merged_data = df.to_dict('records')
        
        return TimeSeriesData(
            timestamps=df.index.tolist(),
            data=merged_data,
            data_type=cached_data.data_type
        )
    
    def get_ohlcv_data(
        self,
        symbol: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        config: Optional[OHLCVConfig] = None
    ) -> TimeSeriesData:
        """
        Get OHLCV data for a symbol.
        
        Args:
            symbol: Trading symbol
            start_time: Start time for data
            end_time: End time for data
            config: Optional configuration
            
        Returns:
            TimeSeriesData containing OHLCV data
        """
        return self._get_data(
            provider=self.ohlcv_provider,
            symbol=symbol,
            data_type=DataType.OHLCV,
            start_time=start_time,
            end_time=end_time,
            config=config,
            config_default=OHLCVConfig
        )
    
    def clear_cache(self, symbol: Optional[str] = None):
        """
        Clear cached data.
        
        Args:
            symbol: Optional symbol to clear cache for. If None, clears all cache.
        """
        self.cache.clear_cache()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        return self.cache.get_stats() 