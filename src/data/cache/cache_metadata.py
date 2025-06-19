"""
Cache metadata tracking for both memory and file caches.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
import pandas as pd
import uuid
import pickle
import os

from src.data.types.base_types import SegmentID
from src.data.types.data_type import DataType
from src.data.types.symbol import Symbol


@dataclass
class CacheSegment:
    """
    Represents a segment of cached data.
    """
    segment_id: SegmentID  # Unique identifier for the segment
    start_time: datetime
    end_time: datetime
    file_path: Optional[str] = None


class CacheMetadata:
    """
    Tracks cache availability for both memory and file caches.
    Maintains a mapping of symbol -> data_type -> list of cache segments.
    """
    
    def __init__(self, segment_file: str = "cache/cache_segments.pkl"):
        self.segment_file = segment_file
        self._cache_segments = self._load_segments()
        
    def _load_segments(self):
        if os.path.exists(self.segment_file):
            with open(self.segment_file, "rb") as f:
                return pickle.load(f)
        return {}

    def _save_segments(self):
        with open(self.segment_file, "wb") as f:
            pickle.dump(self._cache_segments, f)

    def add_segment(
        self,
        symbol: Symbol,
        data_type: DataType,
        start_time: datetime,
        end_time: datetime,
        file_path: Optional[str] = None
    ) -> SegmentID:
        """
        Add a new cache segment.
        
        Args:
            symbol: Trading symbol
            data_type: Type of data being cached
            start_time: Start time for the segment
            end_time: End time for the segment
            file_path: Optional path to the file if segment is on disk
        """
        if symbol not in self._cache_segments:
            self._cache_segments[symbol] = {}
            
        if data_type not in self._cache_segments[symbol]:
            self._cache_segments[symbol][data_type] = []
            
        # Check for overlapping segments
        if self._check_for_overlapping_segments(symbol, data_type, start_time, end_time):
            raise ValueError(f"Overlapping segments found for symbol {symbol} and data type {data_type}")
            
        # Create new segment with unique ID
        segment = CacheSegment(
            segment_id=str(uuid.uuid4()),
            start_time=start_time,
            end_time=end_time,
            file_path=file_path
        )
        
        # Insert segment in chronological order
        segments = self._cache_segments[symbol][data_type]
        for i, existing in enumerate(segments):
            if start_time < existing.start_time:
                segments.insert(i, segment)
                break
        else:
            segments.append(segment)
            
        self._save_segments()
        return segment.segment_id
    
    def get_segments(
        self,
        symbol: Symbol,
        data_type: DataType,
        start_time: datetime,
        end_time: datetime
    ) -> List[CacheSegment]:
        """
        Get overlapping cache segments.
        
        Args:
            symbol: Trading symbol
            data_type: Type of data being cached
            start_time: Start time for the range
            end_time: End time for the range
            
        Returns:
            List of overlapping cache segments
        """
        if symbol not in self._cache_segments or data_type not in self._cache_segments[symbol]:
            return []
            
        segments = self._cache_segments[symbol][data_type]
        segments = [
            segment for segment in segments
            if (segment.start_time <= end_time and segment.end_time >= start_time) or  # Partial overlap
               (segment.start_time >= start_time and segment.end_time <= end_time) or  # Complete containment
               (segment.start_time <= start_time and segment.end_time >= end_time) or  # Complete coverage
               (segment.start_time == start_time and segment.end_time == end_time) or  # Exact match
               (segment.start_time <= start_time and segment.end_time <= end_time)     # Early segment
        ]
            
        return segments
        
    def get_missing_ranges(
        self,
        symbol: Symbol,
        data_type: DataType,
        start_time: datetime,
        end_time: datetime
    ) -> List[Tuple[datetime, datetime]]:
        """
        Get missing data ranges between start_time and end_time.
        
        Args:
            symbol: The symbol to check
            data_type: The data type to check
            start_time: Start time for the range
            end_time: End time for the range
            
        Returns:
            List of (start_time, end_time) tuples representing missing ranges
        """
        if start_time >= end_time:
            raise ValueError("start_time must be before end_time")
            
        segments = self.get_segments(symbol, data_type, start_time, end_time)
        if not segments:
            return [(start_time, end_time)]
            
        missing_ranges = []
        current_start = start_time
        
        # Sort segments by start time to ensure proper order
        segments.sort(key=lambda x: x.start_time)
        
        for segment in segments:
            # If segment starts after current_start, there's a gap
            if segment.start_time > current_start:
                missing_ranges.append((current_start, segment.start_time))
            # Update current_start to the end of this segment
            current_start = max(current_start, segment.end_time)
        
        # Check if there's a gap after the last segment
        if current_start < end_time:
            missing_ranges.append((current_start, end_time))
            
        return missing_ranges
    
    def clear_segments(self, symbol: Optional[str] = None) -> None:
        """
        Clear cache segments.
        
        Args:
            symbol: Optional symbol to clear segments for. If None, clears all segments.
        """
        if symbol is None:
            self._cache_segments.clear()
        else:
            self._cache_segments.pop(symbol, None)
        self._save_segments()

    def _check_for_overlapping_segments(self, symbol: str, data_type: str, start_time: datetime, end_time: datetime) -> bool:
        """
        Check if there are any overlapping segments for a symbol and data type.
        
        Args:
            symbol: Trading symbol
            data_type: Data type of the segments
            start_time: Start time for the segment
            end_time: End time for the segment
            
        Returns:
            True if there are overlapping segments, False otherwise
        """
        if symbol not in self._cache_segments or data_type not in self._cache_segments[symbol]:
            return False
            
        segments = self._cache_segments[symbol][data_type]
        for segment in segments:
            if ((start_time <= segment.start_time <= end_time) or  # incoming start time is in middle of segment
                (start_time <= segment.end_time <= end_time) or    # incoming end time is in middle of segment
                (segment.start_time <= start_time and segment.end_time >= end_time)):  # segment completely contains incoming range
                return True
                
        return False 