from datetime import datetime
from typing import Dict, List, Optional, Tuple, TypeVar, Generic, Any

from src.data.types.data_type import DataType
from src.data.types.symbol import Symbol
from ..types.base_types import SegmentID, TimeSeriesData
from ..types.ohlcv_types import OHLCVData
import bisect
import os
import json
import pickle
from pathlib import Path
import sys
import logging
import pandas as pd

from .cache_metadata import CacheMetadata, CacheSegment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')

class SmartCache(Generic[T]):
    """
    Smart cache implementation that handles both memory and file caching.
    Tracks cache availability using CacheMetadata.
    
    Type Parameters:
        T: The type of data this cache stores
    """
    
    def __init__(self, cache_dir: str = "cache"):
        """
        Initialize the smart cache.
        
        Args:
            cache_dir: Directory for file cache
        """
        self.cache_dir = cache_dir
        self.memory_cache: Dict[SegmentID, TimeSeriesData] = {}
        self.metadata = CacheMetadata(segment_file=os.path.join(cache_dir, "cache_segments.pkl"))
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cached_data(
            self, 
            symbol: Symbol, 
            data_type: DataType, 
            start_time: Optional[datetime] = None, 
            end_time: Optional[datetime] = None) -> TimeSeriesData:
        """
        Get cached data for a symbol and time range.
        
        Args:
            symbol: Trading symbol
            data_type: Type of data to retrieve
            start_time: Start time for data
            end_time: End time for data
            
        Returns:
            TimeSeriesData containing the requested data
            
        Raises:
            ValueError: If there are missing data ranges
        """
        # 1. Check for missing data ranges
        missing_ranges = self.metadata.get_missing_ranges(symbol, data_type, start_time, end_time)
        if missing_ranges:
            raise ValueError(f"Missing data ranges for {symbol} {data_type} between {start_time} and {end_time}: {missing_ranges}")
            
        # 2. Get all overlapping segments
        segments = self.metadata.get_segments(symbol, data_type, start_time, end_time)
        if not segments:
            raise ValueError(f"No overlapping segments found for {symbol} {data_type} between {start_time} and {end_time}")
            
        # 3 & 4. Collect data from all segments
        all_timestamps = []
        all_data = []
        
        for segment in segments:
            # Get data from memory cache
            if segment.segment_id and segment.segment_id in self.memory_cache:
                data = self.memory_cache[segment.segment_id]
                segment_timestamps = data.timestamps
                segment_data = data.data
            # Get data from file cache
            elif segment.file_path and os.path.exists(segment.file_path):
                with open(segment.file_path, 'rb') as f:
                    data = pickle.load(f)
                segment_timestamps = data.timestamps
                segment_data = data.data
            else:
                raise ValueError(f"Couldn't find segment data for {symbol} {data_type} between {start_time} and {end_time} in both memory and file cache")

            # Filter for the requested time range
            filtered_timestamps = []
            filtered_data = []
            for ts, d in zip(segment_timestamps, segment_data):
                if (start_time and ts < start_time) or (end_time and ts > end_time):
                    continue
                filtered_timestamps.append(ts)
                filtered_data.append(d)
                
            all_timestamps.extend(filtered_timestamps)
            all_data.extend(filtered_data)
        
        # 5. Return combined data
        return TimeSeriesData(timestamps=all_timestamps, data=all_data,data_type=data_type)
    
    def cache_data(
        self,
        symbol: Symbol,
        data_type: DataType,
        start_time: datetime,
        end_time: datetime,
        data: TimeSeriesData
    ) -> None:
        """
        Cache data for the specified time range.
        """
        if start_time >= end_time:
            raise ValueError("start_time must be before end_time")
        if not data.timestamps:
            raise ValueError("No data to cache.")
        # Check for overlapping segments
        if self.metadata._check_for_overlapping_segments(symbol, data_type, start_time, end_time):
            raise ValueError(f"Overlapping segments found for symbol {symbol} and data type {data_type}")

        # Create a file path for the pickle file and store Timeseries data 
        cache_path = os.path.join(self.cache_dir, f"{symbol}_{data_type}_{start_time.strftime('%Y%m%d')}_{end_time.strftime('%Y%m%d')}.pkl")
        with open(cache_path, 'wb') as f:
            pickle.dump(data, f)

        #  Create a segment 
        segment_id = self.metadata.add_segment(
            symbol=symbol,
            data_type=data_type,
            start_time=start_time,
            end_time=end_time,
            file_path=cache_path)

        # Store in memory cache as TimeSeriesData
        self.memory_cache[segment_id] = data
    
    
    def clear_cache(self) -> None:
        """
        Clear cached data.
        
        Args:
            symbol: Optional symbol to clear cache for. If None, clears all cache.
        """
        self.memory_cache.clear()
        self.metadata.clear_segments()
        
        # Clear file cache
        for file in os.listdir(self.cache_dir):
            if file.endswith('.pkl'):
                os.remove(os.path.join(self.cache_dir, file))
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        total_memory_segments = 0
        total_memory_size = 0
        total_file_segments = 0
        total_file_size = 0
        symbols = set()

        # Count memory cache stats (flat dict: segment_id -> TimeSeriesData)
        for segment_id, tsdata in self.memory_cache.items():
            total_memory_segments += 1
            # Estimate memory size: sum of __sizeof__ for all OHLCVData objects + timestamps
            total_memory_size += sum(getattr(d, '__sizeof__', lambda: 0)() for d in tsdata.data)
            total_memory_size += sum(getattr(ts, '__sizeof__', lambda: 0)() for ts in tsdata.timestamps)
            # Try to extract symbol from segment_id if possible (or skip)
            # (If you want to track symbols, you may need to store a mapping elsewhere)

        # Count file cache stats
        for file in os.listdir(self.cache_dir):
            if file.endswith('.pkl'):
                total_file_segments += 1
                total_file_size += os.path.getsize(os.path.join(self.cache_dir, file))
                symbol = file.split('_')[0]
                symbols.add(symbol)

        return {
            'memory_segments': total_memory_segments,
            'memory_size': total_memory_size,
            'file_segments': total_file_segments,
            'file_size': total_file_size,
            'symbols': len(symbols)
        } 