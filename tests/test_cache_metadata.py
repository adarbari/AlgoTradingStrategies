import unittest
from datetime import datetime, timedelta
from src.data.cache.cache_metadata import CacheMetadata, CacheSegment
from src.data.types.symbol import Symbol
from src.data.types.data_type import DataType

class TestCacheMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = CacheMetadata()
        self.symbol = Symbol("AAPL")
        self.data_type = DataType.OHLCV
        self.start_time = datetime(2023, 1, 1)
        self.end_time = datetime(2023, 1, 10)

    def test_initialization(self):
        self.assertEqual(self.metadata._cache_segments, {})

    def test_add_segment(self):
        self.metadata.add_segment(self.symbol, self.data_type, self.start_time, self.end_time, True)
        self.assertIn(self.symbol, self.metadata._cache_segments)
        self.assertIn(self.data_type, self.metadata._cache_segments[self.symbol])
        self.assertEqual(len(self.metadata._cache_segments[self.symbol][self.data_type]), 1)

    def test_get_segments(self):
        self.metadata.add_segment(self.symbol, self.data_type, self.start_time, self.end_time, True)
        segments = self.metadata.get_segments(self.symbol, self.data_type, self.start_time, self.end_time)
        self.assertEqual(len(segments), 1)

    def test_get_missing_ranges(self):
        self.metadata.add_segment(self.symbol, self.data_type, datetime(2023, 1, 2), datetime(2023, 1, 3), True)
        self.metadata.add_segment(self.symbol, self.data_type, datetime(2023, 1, 5), datetime(2023, 1, 7), True)
        missing_ranges = self.metadata.get_missing_ranges(self.symbol, self.data_type, datetime(2023, 1, 1), datetime(2023, 1, 10))
        self.assertEqual(missing_ranges, [(datetime(2023, 1, 1), datetime(2023, 1, 2)), (datetime(2023, 1, 3), datetime(2023, 1, 5)), (datetime(2023, 1, 7), datetime(2023, 1, 10))])

    def test_clear_segments(self):
        self.metadata.add_segment(self.symbol, self.data_type, self.start_time, self.end_time, True)
        self.metadata.clear_segments(self.symbol)
        self.assertNotIn(self.symbol, self.metadata._cache_segments)

    def test_add_overlapping_segment(self):
        self.metadata.add_segment(self.symbol, self.data_type, self.start_time, self.end_time, True)
        with self.assertRaises(ValueError):
            self.metadata.add_segment(self.symbol, self.data_type, self.start_time, self.end_time, True)

    def test_get_missing_ranges_edge_cases(self):
        """Test missing ranges with edge cases."""
        # Test with no segments
        missing_ranges = self.metadata.get_missing_ranges(self.symbol, self.data_type, self.start_time, self.end_time)
        self.assertEqual(missing_ranges, [(self.start_time, self.end_time)])

        # Test with exact match
        self.metadata.add_segment(self.symbol, self.data_type, self.start_time, self.end_time, True)
        missing_ranges = self.metadata.get_missing_ranges(self.symbol, self.data_type, self.start_time, self.end_time)
        self.assertEqual(missing_ranges, [])

        # Test with single point (should raise ValueError)
        self.metadata.clear_segments(self.symbol)
        point_time = datetime(2023, 1, 5)
        with self.assertRaises(ValueError):
            self.metadata.get_missing_ranges(self.symbol, self.data_type, point_time, point_time)

        # Test with invalid time range
        with self.assertRaises(ValueError):
            self.metadata.get_missing_ranges(self.symbol, self.data_type, self.end_time, self.start_time)

        # Test with adjacent segments
        self.metadata.clear_segments(self.symbol)
        mid_time = datetime(2023, 1, 5)
        self.metadata.add_segment(self.symbol, self.data_type, self.start_time, mid_time, True)
        self.metadata.add_segment(self.symbol, self.data_type, mid_time, self.end_time, True)
        missing_ranges = self.metadata.get_missing_ranges(self.symbol, self.data_type, self.start_time, self.end_time)
        self.assertEqual(missing_ranges, [])

        # Test with overlapping segments
        self.metadata.clear_segments(self.symbol)
        self.metadata.add_segment(self.symbol, self.data_type, self.start_time, mid_time, True)
        with self.assertRaises(ValueError):
            self.metadata.add_segment(self.symbol, self.data_type, self.start_time, self.end_time, True)

        # Test with gap between segments
        self.metadata.clear_segments(self.symbol)
        gap_start = datetime(2023, 1, 2)
        gap_end = datetime(2023, 1, 3)
        self.metadata.add_segment(self.symbol, self.data_type, self.start_time, gap_start, True)
        self.metadata.add_segment(self.symbol, self.data_type, gap_end, self.end_time, True)
        missing_ranges = self.metadata.get_missing_ranges(self.symbol, self.data_type, self.start_time, self.end_time)
        self.assertEqual(missing_ranges, [(gap_start, gap_end)])

        # Test with multiple gaps
        self.metadata.clear_segments(self.symbol)
        gap1_start = datetime(2023, 1, 2)
        gap1_end = datetime(2023, 1, 3)
        gap2_start = datetime(2023, 1, 5)
        gap2_end = datetime(2023, 1, 6)
        self.metadata.add_segment(self.symbol, self.data_type, self.start_time, gap1_start, True)
        self.metadata.add_segment(self.symbol, self.data_type, gap1_end, gap2_start, True)
        self.metadata.add_segment(self.symbol, self.data_type, gap2_end, self.end_time, True)
        missing_ranges = self.metadata.get_missing_ranges(self.symbol, self.data_type, self.start_time, self.end_time)
        self.assertEqual(missing_ranges, [(gap1_start, gap1_end), (gap2_start, gap2_end)])

    def test_get_missing_ranges_multiple_symbols(self):
        """Test missing ranges with multiple symbols."""
        symbol2 = Symbol("MSFT")
        
        # Add segments for both symbols
        self.metadata.add_segment(self.symbol, self.data_type, self.start_time, self.end_time, True)
        self.metadata.add_segment(symbol2, self.data_type, self.start_time, self.end_time, True)
        
        # Test missing ranges for each symbol
        missing_ranges1 = self.metadata.get_missing_ranges(self.symbol, self.data_type, self.start_time, self.end_time)
        missing_ranges2 = self.metadata.get_missing_ranges(symbol2, self.data_type, self.start_time, self.end_time)
        
        self.assertEqual(missing_ranges1, [])
        self.assertEqual(missing_ranges2, [])

    def test_get_missing_ranges_different_data_types(self):
        """Test missing ranges with different data types."""
        data_type2 = DataType.ORDER_FLOW
        
        # Add segments for both data types
        self.metadata.add_segment(self.symbol, self.data_type, self.start_time, self.end_time, True)
        self.metadata.add_segment(self.symbol, data_type2, self.start_time, self.end_time, True)
        
        # Test missing ranges for each data type
        missing_ranges1 = self.metadata.get_missing_ranges(self.symbol, self.data_type, self.start_time, self.end_time)
        missing_ranges2 = self.metadata.get_missing_ranges(self.symbol, data_type2, self.start_time, self.end_time)
        
        self.assertEqual(missing_ranges1, [])
        self.assertEqual(missing_ranges2, [])

if __name__ == '__main__':
    unittest.main()