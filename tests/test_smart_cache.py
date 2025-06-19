import unittest
from datetime import datetime, timedelta
import pandas as pd
import os
import shutil
from pathlib import Path

from src.data.cache.smart_cache import SmartCache
from src.data.types.symbol import Symbol
from src.data.types.data_type import DataType
from src.data.types.base_types import TimeSeriesData
from src.data.types.ohlcv_types import OHLCVData

class TestSmartCache(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.test_cache_dir = "test_cache"
        self.cache = SmartCache(cache_dir=self.test_cache_dir)
        self.symbol = Symbol("AAPL")
        self.data_type = DataType.OHLCV
        
        # Create test data
        self.start_time = datetime(2023, 1, 1)
        self.end_time = datetime(2023, 1, 10)
        self.test_data = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [105, 106, 107],
            'low': [95, 96, 97],
            'close': [103, 104, 105],
            'volume': [1000, 2000, 3000]
        }, index=[
            datetime(2023, 1, 1),
            datetime(2023, 1, 2),
            datetime(2023, 1, 3)
        ])
        
        # Convert DataFrame to TimeSeriesData
        self.test_time_series = TimeSeriesData(
            timestamps=self.test_data.index.tolist(),
            data=[
                OHLCVData(
                    timestamp=idx,
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    volume=row['volume']
                )
                for idx, row in self.test_data.iterrows()
            ],
            data_type=self.data_type
        )

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)

    def test_initialization(self):
        """Test cache initialization."""
        self.assertEqual(self.cache.cache_dir, self.test_cache_dir)
        self.assertTrue(os.path.exists(self.test_cache_dir))
        self.assertEqual(self.cache.memory_cache, {})

    def test_cache_data_basic(self):
        """Test basic data caching functionality."""
        self.cache.cache_data(
            symbol=self.symbol,
            data_type=self.data_type,
            start_time=self.start_time,
            end_time=self.end_time,
            data=self.test_time_series
        )
        
        # Verify memory cache: should have at least one segment
        self.assertTrue(len(self.cache.memory_cache) > 0)
        
        # Verify file cache
        cache_files = list(Path(self.test_cache_dir).glob(f"{self.symbol}_{self.data_type}_*.pkl"))
        self.assertEqual(len(cache_files), 1)

    def test_get_cached_data_basic(self):
        """Test basic data retrieval."""
        self.cache.cache_data(
            symbol=self.symbol,
            data_type=self.data_type,
            start_time=self.start_time,
            end_time=self.end_time,
            data=self.test_time_series
        )
        
        result = self.cache.get_cached_data(
            symbol=self.symbol,
            data_type=self.data_type,
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        self.assertIsInstance(result, TimeSeriesData)
        self.assertEqual(len(result.timestamps), len(self.test_time_series.timestamps))
        self.assertEqual(len(result.data), len(self.test_time_series.data))

    def test_get_cached_data_missing(self):
        """Test behavior when requested data is missing."""
        with self.assertRaises(ValueError):
            self.cache.get_cached_data(
                symbol=self.symbol,
                data_type=self.data_type,
                start_time=self.start_time,
                end_time=self.end_time
            )

    def test_get_cached_data_partial(self):
        """Test retrieving partial data range."""
        self.cache.cache_data(
            symbol=self.symbol,
            data_type=self.data_type,
            start_time=self.start_time,
            end_time=self.end_time,
            data=self.test_time_series
        )
        # Request a valid subset of data (start < end)
        result = self.cache.get_cached_data(
            symbol=self.symbol,
            data_type=self.data_type,
            start_time=datetime(2023, 1, 2),
            end_time=datetime(2023, 1, 3)
        )
        self.assertEqual(len(result.timestamps), 2)
        self.assertEqual(result.timestamps[0], datetime(2023, 1, 2))
        self.assertEqual(result.timestamps[1], datetime(2023, 1, 3))

    def test_cache_data_overlapping(self):
        """Test caching overlapping data ranges."""
        # Cache initial data
        self.cache.cache_data(
            symbol=self.symbol,
            data_type=self.data_type,
            start_time=self.start_time,
            end_time=self.end_time,
            data=self.test_time_series
        )
        
        # Create overlapping data
        overlapping_data = pd.DataFrame({
            'open': [104, 105],
            'high': [108, 109],
            'low': [98, 99],
            'close': [106, 107],
            'volume': [4000, 5000]
        }, index=[
            datetime(2023, 1, 2),
            datetime(2023, 1, 3)
        ])
        
        # Convert to TimeSeriesData
        overlapping_time_series = TimeSeriesData(
            timestamps=overlapping_data.index.tolist(),
            data=[
                OHLCVData(
                    timestamp=idx,
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    volume=row['volume']
                )
                for idx, row in overlapping_data.iterrows()
            ],
            data_type=self.data_type
        )
        
        with self.assertRaises(ValueError):
            self.cache.cache_data(
                symbol=self.symbol,
                data_type=self.data_type,
                start_time=datetime(2023, 1, 2),
                end_time=datetime(2023, 1, 4),
                data=overlapping_time_series
            )

    def test_clear_cache(self):
        """Test clearing cache."""
        self.cache.cache_data(
            symbol=self.symbol,
            data_type=self.data_type,
            start_time=self.start_time,
            end_time=self.end_time,
            data=self.test_time_series
        )
        
        # Clear all cache
        self.cache.clear_cache()
        self.assertEqual(len(self.cache.memory_cache), 0)
        cache_files = list(Path(self.test_cache_dir).glob(f"{self.symbol}_{self.data_type}_*.pkl"))
        self.assertEqual(len(cache_files), 0)
        
        # Test clearing all cache again after recaching
        self.cache.cache_data(
            symbol=self.symbol,
            data_type=self.data_type,
            start_time=self.start_time,
            end_time=self.end_time,
            data=self.test_time_series
        )
        self.cache.clear_cache()
        self.assertEqual(self.cache.memory_cache, {})
        self.assertEqual(len(list(Path(self.test_cache_dir).glob("*.pkl"))), 0)

    def test_get_cache_stats(self):
        """Test getting cache statistics."""
        self.cache.cache_data(
            symbol=self.symbol,
            data_type=self.data_type,
            start_time=self.start_time,
            end_time=self.end_time,
            data=self.test_time_series
        )
        
        stats = self.cache.get_stats()
        self.assertIn('memory_segments', stats)
        self.assertIn('memory_size', stats)
        self.assertIn('file_segments', stats)
        self.assertIn('file_size', stats)
        self.assertIn('symbols', stats)
        self.assertEqual(stats['symbols'], 1)

    def test_empty_data(self):
        """Test handling empty data."""
        empty_time_series = TimeSeriesData(timestamps=[], data=[],data_type=self.data_type)
        with self.assertRaises(ValueError):
            self.cache.cache_data(
                symbol=self.symbol,
                data_type=self.data_type,
                start_time=self.start_time,
                end_time=self.end_time,
                data=empty_time_series
            )

    def test_invalid_time_range(self):
        """Test handling invalid time ranges."""
        with self.assertRaises(ValueError):
            self.cache.cache_data(
                symbol=self.symbol,
                data_type=self.data_type,
                start_time=self.end_time,
                end_time=self.start_time,
                data=self.test_time_series
            )

    def test_cache_data_multiple_symbols(self):
        """Test caching data for multiple symbols."""
        symbol2 = Symbol("MSFT")
        
        # Cache data for both symbols
        self.cache.cache_data(
            symbol=self.symbol,
            data_type=self.data_type,
            start_time=self.start_time,
            end_time=self.end_time,
            data=self.test_time_series
        )
        
        self.cache.cache_data(
            symbol=symbol2,
            data_type=self.data_type,
            start_time=self.start_time,
            end_time=self.end_time,
            data=self.test_time_series
        )
        
        # Verify both symbols are cached
        cache_files = list(Path(self.test_cache_dir).glob("*.pkl"))
        self.assertEqual(len(cache_files), 2)
        
        # Verify data can be retrieved for both symbols
        result1 = self.cache.get_cached_data(
            symbol=self.symbol,
            data_type=self.data_type,
            start_time=self.start_time,
            end_time=self.end_time
        )
        result2 = self.cache.get_cached_data(
            symbol=symbol2,
            data_type=self.data_type,
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        self.assertIsInstance(result1, TimeSeriesData)
        self.assertIsInstance(result2, TimeSeriesData)
        self.assertEqual(len(result1.timestamps), len(self.test_time_series.timestamps))
        self.assertEqual(len(result2.timestamps), len(self.test_time_series.timestamps))

    def test_cache_data_different_data_types(self):
        """Test caching data for different data types."""
        data_type2 = DataType.ORDER_FLOW
        
        # Cache data for both data types
        self.cache.cache_data(
            symbol=self.symbol,
            data_type=self.data_type,
            start_time=self.start_time,
            end_time=self.end_time,
            data=self.test_time_series
        )
        
        self.cache.cache_data(
            symbol=self.symbol,
            data_type=data_type2,
            start_time=self.start_time,
            end_time=self.end_time,
            data=self.test_time_series
        )
        
        # Verify both data types are cached
        cache_files = list(Path(self.test_cache_dir).glob("*.pkl"))
        self.assertEqual(len(cache_files), 2)
        
        # Verify data can be retrieved for both data types
        result1 = self.cache.get_cached_data(
            symbol=self.symbol,
            data_type=self.data_type,
            start_time=self.start_time,
            end_time=self.end_time
        )
        result2 = self.cache.get_cached_data(
            symbol=self.symbol,
            data_type=data_type2,
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        self.assertIsInstance(result1, TimeSeriesData)
        self.assertIsInstance(result2, TimeSeriesData)
        self.assertEqual(len(result1.timestamps), len(self.test_time_series.timestamps))
        self.assertEqual(len(result2.timestamps), len(self.test_time_series.timestamps))

    def test_cache_data_single_point(self):
        """Test caching data for a single point in time (should raise ValueError)."""
        point_time = datetime(2023, 1, 5)
        single_point_series = TimeSeriesData(
            timestamps=[point_time],
            data=[
                OHLCVData(
                    timestamp=point_time,
                    open=100,
                    high=105,
                    low=95,
                    close=103,
                    volume=1000
                )
            ],
            data_type=DataType.OHLCV
        )
        with self.assertRaises(ValueError):
            self.cache.cache_data(
                symbol=self.symbol,
                data_type=self.data_type,
                start_time=point_time,
                end_time=point_time,
                data=single_point_series
            )

if __name__ == '__main__':
    unittest.main() 