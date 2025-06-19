"""
Tests for the DataManager class.
"""

import unittest
from unittest.mock import MagicMock
from datetime import datetime, timedelta
import pandas as pd

from src.data.data_manager import DataManager
from src.data.cache.smart_cache import SmartCache
from src.data.providers.ohlcv_provider import OHLCVDataProvider
from src.data.types.base_types import TimeSeriesData
from src.data.types.data_config_types import OHLCVConfig
from src.data.providers.vendors.polygon.polygon_provider import PolygonProvider
from src.data.types.data_type import DataType


class TestDataManager(unittest.TestCase):
    """Test cases for DataManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_provider = MagicMock(spec=OHLCVDataProvider)
        self.mock_cache = MagicMock(spec=SmartCache)
        # Add a mock metadata with get_missing_ranges
        self.mock_cache.metadata = MagicMock()
        self.mock_cache.metadata.get_missing_ranges.return_value = []
        self.mock_cache.get_stats.return_value = {'segments': 1, 'size': 100, 'symbols': 1}
        self.manager = DataManager(
            ohlcv_provider=self.mock_provider,
            cache=self.mock_cache
        )
        self.symbol = 'AAPL'
        self.start_time = datetime(2023, 1, 1)
        self.end_time = datetime(2023, 1, 3)
        self.timeframe = '1d'
        self.config = OHLCVConfig(
            timeframe=self.timeframe,
            adjust_splits=True,
            adjust_dividends=True,
            include_volume=True
        )
        self.timestamps = [self.start_time, self.end_time]
        self.data = [{'open': 1, 'high': 2, 'low': 0.5, 'close': 1.5, 'volume': 1000}, {'open': 1.5, 'high': 2.5, 'low': 1, 'close': 2, 'volume': 1500}]
        self.df = pd.DataFrame(self.data, index=self.timestamps)
        self.mock_cache.get_cached_data.return_value = self.df
        self.mock_provider.get_data.return_value = TimeSeriesData(timestamps=self.timestamps, data=self.data, data_type=DataType.OHLCV)
    
    def test_init_with_providers(self):
        """Test initialization with providers."""
        manager = DataManager(ohlcv_provider=self.mock_provider, cache=self.mock_cache)
        self.assertIs(manager.ohlcv_provider, self.mock_provider)
        self.assertIs(manager.cache, self.mock_cache)
    
    def test_init_without_providers(self):
        """Test initialization without providers."""
        manager = DataManager()
        self.assertIsNotNone(manager.ohlcv_provider)
        self.assertIsNotNone(manager.cache)
    
    def test_get_ohlcv_data_no_cache(self):
        """Test getting OHLCV data with no cache."""
        # Simulate no cache: all data is missing
        self.mock_cache.metadata.get_missing_ranges.return_value = [(self.start_time, self.end_time)]
        self.mock_cache.get_cached_data.return_value = None
        result = self.manager.get_ohlcv_data(self.symbol, self.start_time, self.end_time, self.config)
        self.assertEqual(result.timestamps, self.timestamps)
        self.mock_provider.get_data.assert_called_once_with(
            symbol=self.symbol,
            start_time=self.start_time,
            end_time=self.end_time,
            config=self.config
        )
    
    def test_get_ohlcv_data_full_cache(self):
        """Test getting OHLCV data when fully cached."""
        self.mock_cache.get_cached_data.return_value = self.df
        result = self.manager.get_ohlcv_data(self.symbol, self.start_time, self.end_time, self.config)
        self.assertEqual(result.timestamps, self.timestamps)
        self.assertEqual(result.data, self.df.to_dict('records'))
        self.mock_provider.get_data.assert_not_called()
    
    def test_get_ohlcv_data_partial_cache(self):
        """Test getting OHLCV data with partial cache."""
        # Simulate partial cache: only the second timestamp is missing
        self.mock_cache.metadata.get_missing_ranges.return_value = [(self.timestamps[1], self.timestamps[1])]
        # First timestamp is cached, second is not
        cached_df = pd.DataFrame([self.data[0]], index=[self.timestamps[0]])
        self.mock_cache.get_cached_data.side_effect = [cached_df, pd.DataFrame(self.data, index=self.timestamps)]
        result = self.manager.get_ohlcv_data(self.symbol, self.start_time, self.end_time, self.config)
        result_timestamps = pd.to_datetime(result.timestamps)
        self.assertIn(pd.Timestamp(self.timestamps[0]), result_timestamps)
        self.assertIn(pd.Timestamp(self.timestamps[1]), result_timestamps)
        self.mock_provider.get_data.assert_called_with(
            symbol=self.symbol,
            start_time=self.timestamps[1],
            end_time=self.timestamps[1],
            config=self.config
        )
    
    def test_clear_cache(self):
        """Test clearing cache."""
        self.manager.clear_cache(self.symbol)
        self.mock_cache.clear_cache.assert_called_with(self.symbol)
    
    def test_clear_all_cache(self):
        """Test clearing all cache."""
        self.manager.clear_cache()
        self.mock_cache.clear_cache.assert_called_with(None)
    
    def test_get_cache_stats(self):
        """Test getting cache statistics."""
        self.mock_cache.get_stats.return_value = {'segments': 1, 'size': 100}
        stats = self.manager.get_cache_stats()
        self.assertEqual(stats, {'segments': 1, 'size': 100})


if __name__ == '__main__':
    unittest.main() 