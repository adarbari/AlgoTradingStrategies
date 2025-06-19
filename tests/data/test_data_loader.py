import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime
import tempfile
import shutil
from src.data.data_manager import DataManager
from src.data.types.base_types import TimeSeriesData
from src.data.types.ohlcv_types import OHLCVData
from src.data.types.data_type import DataType

def test_get_ohlcv_data():
    """Test getting OHLCV data using DataManager"""
    # Create a temporary cache directory
    temp_cache_dir = tempfile.mkdtemp()
    try:
        # Create a mock provider
        mock_provider = MagicMock()
        mock_provider.get_data.return_value = TimeSeriesData(
            timestamps=[datetime(2021, 7, 1), datetime(2021, 7, 2)],
            data=[
                OHLCVData(timestamp=datetime(2021, 7, 1), open=35000.0, high=36000.0, low=34000.0, close=35500.0, volume=1000),
                OHLCVData(timestamp=datetime(2021, 7, 2), open=35500.0, high=37000.0, low=35000.0, close=36500.0, volume=1200)
            ],
            data_type=DataType.OHLCV
        )
        
        # Mock the cache to return empty data (simulate cache miss)
        mock_cache = MagicMock()
        empty_data = TimeSeriesData(timestamps=[], data=[], data_type=DataType.OHLCV)
        mock_cache.get_cached_data.return_value = empty_data
        
        # Mock the cache metadata to return missing ranges when cache is empty
        mock_metadata = MagicMock()
        mock_metadata.get_missing_ranges.return_value = [(datetime(2021, 7, 1), datetime(2021, 7, 2))]
        mock_cache.metadata = mock_metadata
        
        data_manager = DataManager(ohlcv_provider=mock_provider)
        data_manager.cache = mock_cache
        
        # Get data
        data = data_manager.get_ohlcv_data('BTC/USDT', datetime(2021, 7, 1), datetime(2021, 7, 2))
        
        # Since cache returns empty data, provider should be called and we should get the provider's data
        assert len(data.timestamps) == 2
        assert len(data.data) == 2
        assert data.data_type == DataType.OHLCV
        
        # Verify provider was called since cache was empty
        mock_provider.get_data.assert_called_once()
        
    finally:
        shutil.rmtree(temp_cache_dir)

def test_data_manager_initialization():
    """Test DataManager initialization"""
    with patch('src.data.cache.smart_cache.SmartCache.__init__') as mock_cache_init:
        mock_cache_init.return_value = None
        data_manager = DataManager()
        assert data_manager.ohlcv_provider is not None
        assert data_manager.cache is not None

def test_clear_cache():
    """Test clearing cache"""
    with patch('src.data.cache.smart_cache.SmartCache.__init__') as mock_cache_init:
        mock_cache_init.return_value = None
        data_manager = DataManager()
        
        # Mock the cache clear method
        mock_cache = MagicMock()
        data_manager.cache = mock_cache
        
        # This should not raise an error
        data_manager.clear_cache()
        data_manager.clear_cache('AAPL')
        
        # Verify clear_cache was called
        assert mock_cache.clear_cache.call_count == 2 