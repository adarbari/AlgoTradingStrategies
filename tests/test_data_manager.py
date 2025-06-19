"""
Tests for the DataManager class.
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import pandas as pd

from src.data.data_manager import DataManager
from src.data.cache.smart_cache import SmartCache
from src.data.providers.ohlcv_provider import OHLCVDataProvider
from src.data.types.base_types import TimeSeriesData
from src.data.types.data_config_types import OHLCVConfig
from src.data.providers.vendors.polygon.polygon_provider import PolygonProvider
from src.data.types.data_type import DataType
from src.data.types.ohlcv_types import OHLCVData


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
        
        # Mock the cache initialization to avoid file operations
        with patch('src.data.cache.smart_cache.SmartCache.__init__') as mock_cache_init:
            mock_cache_init.return_value = None
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
        
        # Create proper OHLCVData objects
        self.ohlcv_data = [
            OHLCVData(timestamp=self.start_time, open=1, high=2, low=0.5, close=1.5, volume=1000),
            OHLCVData(timestamp=self.end_time, open=1.5, high=2.5, low=1, close=2, volume=1500)
        ]
        
        # Create TimeSeriesData object
        self.time_series_data = TimeSeriesData(
            timestamps=self.timestamps, 
            data=self.ohlcv_data, 
            data_type=DataType.OHLCV
        )
        
        self.df = pd.DataFrame([
            {'open': 1, 'high': 2, 'low': 0.5, 'close': 1.5, 'volume': 1000}, 
            {'open': 1.5, 'high': 2.5, 'low': 1, 'close': 2, 'volume': 1500}
        ], index=self.timestamps)
        
        self.mock_cache.get_cached_data.return_value = self.time_series_data
        self.mock_provider.get_data.return_value = self.time_series_data
    
    def test_init_with_providers(self):
        """Test initialization with providers."""
        with patch('src.data.cache.smart_cache.SmartCache.__init__') as mock_cache_init:
            mock_cache_init.return_value = None
            manager = DataManager(ohlcv_provider=self.mock_provider, cache=self.mock_cache)
            self.assertIs(manager.ohlcv_provider, self.mock_provider)
            self.assertIs(manager.cache, self.mock_cache)
    
    def test_init_without_providers(self):
        """Test initialization without providers."""
        with patch('src.data.cache.smart_cache.SmartCache.__init__') as mock_cache_init:
            mock_cache_init.return_value = None
            manager = DataManager()
            self.assertIsNotNone(manager.ohlcv_provider)
            self.assertIsNotNone(manager.cache)
    
    def test_get_ohlcv_data_no_cache(self):
        """Test getting OHLCV data with no cache."""
        # Simulate no cache: all data is missing
        self.mock_cache.metadata.get_missing_ranges.return_value = [(self.start_time, self.end_time)]
        empty_data = TimeSeriesData(timestamps=[], data=[], data_type=DataType.OHLCV)
        self.mock_cache.get_cached_data.return_value = empty_data
        
        # Mock the provider to return data
        self.mock_provider.get_data.return_value = self.time_series_data
        
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
        self.mock_cache.get_cached_data.return_value = self.time_series_data
        result = self.manager.get_ohlcv_data(self.symbol, self.start_time, self.end_time, self.config)
        self.assertEqual(result.timestamps, self.timestamps)
        self.assertEqual(len(result.data), len(self.ohlcv_data))
        self.mock_provider.get_data.assert_not_called()
    
    def test_get_ohlcv_data_partial_cache(self):
        """Test getting OHLCV data with partial cache."""
        # Simulate partial cache: only the second timestamp is missing
        self.mock_cache.metadata.get_missing_ranges.return_value = [(self.timestamps[1], self.timestamps[1])]
        
        # First timestamp is cached, second is not
        cached_data = TimeSeriesData(
            timestamps=[self.timestamps[0]], 
            data=[self.ohlcv_data[0]], 
            data_type=DataType.OHLCV
        )
        
        # Mock the cache to return cached data first, then combined data
        self.mock_cache.get_cached_data.side_effect = [
            cached_data,  # First call returns partial cache
            self.time_series_data  # Second call returns full data
        ]
        
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
        self.mock_cache.clear_cache.assert_called_once()
    
    def test_clear_all_cache(self):
        """Test clearing all cache."""
        self.manager.clear_cache()
        self.mock_cache.clear_cache.assert_called_once()
    
    def test_get_cache_stats(self):
        """Test getting cache statistics."""
        self.mock_cache.get_stats.return_value = {'segments': 1, 'size': 100}
        stats = self.manager.get_cache_stats()
        self.assertEqual(stats, {'segments': 1, 'size': 100})


if __name__ == '__main__':
    unittest.main() 