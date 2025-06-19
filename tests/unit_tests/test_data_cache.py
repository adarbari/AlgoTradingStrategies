import os
import shutil
import pandas as pd
from datetime import datetime, timedelta
from src.data.cache.smart_cache import SmartCache
from src.data.types.data_config_types import OHLCVConfig
from src.data.types.base_types import TimeSeriesData
from src.data.types.data_type import DataType
import unittest

class TestDataCache(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.test_cache_dir = 'test_data_cache'
        # Clean up before test
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)
        self.cache = SmartCache(cache_dir=self.test_cache_dir)
        self.data_type = DataType.OHLCV
        
    def tearDown(self):
        """Clean up after each test."""
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)
    
    def test_cache_and_retrieve_data(self):
        """Test basic caching and retrieval functionality."""
        symbol = 'AAPL'
        start = datetime(2024, 4, 1)
        end = datetime(2024, 4, 10)
        # Create data for all dates in the range
        dates = pd.date_range(start=start, end=end, freq='D')
        df = pd.DataFrame({'open': range(len(dates)), 'close': range(len(dates))}, index=dates)
        tsdata = TimeSeriesData(
            timestamps=dates.tolist(),
            data=[{'open': i, 'close': i} for i in range(len(dates))],
            data_type=DataType.OHLCV
        )
        self.cache.cache_data(symbol=symbol, data_type=self.data_type, start_time=start, end_time=end, data=tsdata)
        retrieved = self.cache.get_cached_data(symbol=symbol, data_type=self.data_type, start_time=start, end_time=end)
        retrieved_df = pd.DataFrame(retrieved.data, index=retrieved.timestamps)
        pd.testing.assert_frame_equal(retrieved_df, df, check_freq=False)
        # Check file existence
        expected_file = os.path.join(self.test_cache_dir, f"{symbol}_{self.data_type}_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.pkl")
        self.assertTrue(os.path.exists(expected_file))
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty DataFrames."""
        symbol = 'AAPL'
        start = datetime(2024, 4, 1)
        end = datetime(2024, 4, 10)
        empty_tsdata = TimeSeriesData(timestamps=[], data=[],
            data_type=DataType.OHLCV)
        with self.assertRaises(ValueError):
            self.cache.cache_data(symbol=symbol, data_type=self.data_type, start_time=start, end_time=end, data=empty_tsdata)
        # Should not create a file or add to memory
        expected_file = os.path.join(self.test_cache_dir, f"{symbol}_{self.data_type}_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.pkl")
        self.assertFalse(os.path.exists(expected_file))
        self.assertNotIn(symbol, self.cache.memory_cache)
    
    def test_clear_cache(self):
        """Test clearing the cache."""
        symbol = 'AAPL'
        start = datetime(2024, 4, 1)
        end = datetime(2024, 4, 10)
        df = pd.DataFrame({'open': [1, 2], 'close': [2, 3]}, index=[start, end])
        tsdata = TimeSeriesData(timestamps=[start, end], data=[{'open': 1, 'close': 2}, {'open': 2, 'close': 3}],
            data_type=DataType.OHLCV)
        self.cache.cache_data(symbol=symbol, data_type=self.data_type, start_time=start, end_time=end, data=tsdata)
        self.cache.clear_cache()  # Clear all cache
        with self.assertRaises(ValueError):
            self.cache.get_cached_data(symbol=symbol, data_type=self.data_type, start_time=start, end_time=end)
        # File should be deleted
        expected_file = os.path.join(self.test_cache_dir, f"{symbol}_{self.data_type}_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.pkl")
        self.assertFalse(os.path.exists(expected_file))

    def test_cache_metadata_segments(self):
        """Test cache metadata segment tracking."""
        symbol = 'AAPL'
        start1 = datetime(2024, 4, 1)
        end1 = datetime(2024, 4, 5)
        start2 = datetime(2024, 4, 15)
        end2 = datetime(2024, 4, 20)
        
        # Add two non-overlapping segments
        df1 = pd.DataFrame({'open': [1, 2]}, index=[start1, end1])
        tsdata1 = TimeSeriesData(timestamps=[start1, end1], data=[{'open': 1}, {'open': 2}],
            data_type=DataType.OHLCV)
        self.cache.cache_data(symbol=symbol, data_type=self.data_type, start_time=start1, end_time=end1, data=tsdata1)
        df2 = pd.DataFrame({'open': [3, 4]}, index=[start2, end2])
        tsdata2 = TimeSeriesData(timestamps=[start2, end2], data=[{'open': 3}, {'open': 4}],
            data_type=DataType.OHLCV)
        self.cache.cache_data(symbol=symbol, data_type=self.data_type, start_time=start2, end_time=end2, data=tsdata2)
        
        # Get segments for the entire range
        segments = self.cache.metadata.get_segments(symbol=symbol, data_type=self.data_type, start_time=start1, end_time=end2)
        self.assertEqual(len(segments), 2)
        
        # Verify segment properties
        self.assertEqual(segments[0].start_time, start1)
        self.assertEqual(segments[0].end_time, end1)
        self.assertEqual(segments[1].start_time, start2)
        self.assertEqual(segments[1].end_time, end2)

    def test_cache_metadata_missing_ranges(self):
        """Test cache metadata missing ranges detection."""
        symbol = 'AAPL'
        start = datetime(2024, 4, 1)
        end = datetime(2024, 4, 10)
        mid = datetime(2024, 4, 5)
        
        # Add a segment for the first half
        df = pd.DataFrame({'open': [1, 2]}, index=[start, mid])
        tsdata = TimeSeriesData(timestamps=[start, mid], data=[{'open': 1}, {'open': 2}],
            data_type=DataType.OHLCV)
        self.cache.cache_data(symbol=symbol, data_type=self.data_type, start_time=start, end_time=mid, data=tsdata)
        
        # Check missing ranges for the entire period
        missing_ranges = self.cache.metadata.get_missing_ranges(symbol=symbol, data_type=self.data_type, start_time=start, end_time=end)
        self.assertEqual(len(missing_ranges), 1)
        self.assertEqual(missing_ranges[0][0], mid)
        self.assertEqual(missing_ranges[0][1], end)

    def test_cache_metadata_segment_merging(self):
        """Test cache metadata segment merging for non-overlapping ranges."""
        symbol = 'AAPL'
        start = datetime(2024, 4, 1)
        mid = datetime(2024, 4, 5)
        end = datetime(2024, 4, 10)
        
        # Add non-overlapping segments
        df1 = pd.DataFrame({'open': [1, 2]}, index=[start, mid - timedelta(days=1)])
        tsdata1 = TimeSeriesData(timestamps=[start, mid - timedelta(days=1)], data=[{'open': 1}, {'open': 2}],
            data_type=DataType.OHLCV)
        self.cache.cache_data(symbol=symbol, data_type=self.data_type, start_time=start, end_time=mid - timedelta(days=1), data=tsdata1)
        df2 = pd.DataFrame({'open': [3, 4]}, index=[mid, end])
        tsdata2 = TimeSeriesData(timestamps=[mid, end], data=[{'open': 3}, {'open': 4}],
            data_type=DataType.OHLCV)
        self.cache.cache_data(symbol=symbol, data_type=self.data_type, start_time=mid, end_time=end, data=tsdata2)
        
        # Get segments for the entire range
        segments = self.cache.metadata.get_segments(symbol=symbol, data_type=self.data_type, start_time=start, end_time=end)
        self.assertEqual(len(segments), 2)  # Should not be merged
        self.assertEqual(segments[0].start_time, start)
        self.assertEqual(segments[0].end_time, mid - timedelta(days=1))
        self.assertEqual(segments[1].start_time, mid)
        self.assertEqual(segments[1].end_time, end)

    def test_cache_metadata_clear_segments(self):
        """Test clearing cache segments."""
        symbol = 'AAPL'
        start = datetime(2024, 4, 1)
        end = datetime(2024, 4, 10)
        
        # Add a segment
        df = pd.DataFrame({'open': [1, 2]}, index=[start, end])
        tsdata = TimeSeriesData(timestamps=[start, end], data=[{'open': 1}, {'open': 2}],
            data_type=DataType.OHLCV)
        self.cache.cache_data(symbol=symbol, data_type=self.data_type, start_time=start, end_time=end, data=tsdata)
        
        # Clear segments
        self.cache.metadata.clear_segments(symbol)
        
        # Verify segments are cleared
        segments = self.cache.metadata.get_segments(symbol=symbol, data_type=self.data_type, start_time=start, end_time=end)
        self.assertEqual(len(segments), 0)

if __name__ == '__main__':
    unittest.main() 