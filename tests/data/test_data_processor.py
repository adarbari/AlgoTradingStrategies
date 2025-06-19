import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime
import tempfile
import shutil
from src.data.data_manager import DataManager
from src.data.types.base_types import TimeSeriesData
from src.data.types.ohlcv_types import OHLCVData
from src.data.types.data_type import DataType

def test_data_processing():
    """Test data processing with DataManager"""
    temp_cache_dir = tempfile.mkdtemp()
    try:
        mock_provider = MagicMock()
        mock_provider.get_data.return_value = TimeSeriesData(
            timestamps=[datetime(2021, 7, 1), datetime(2021, 7, 2)],
            data=[
                OHLCVData(timestamp=datetime(2021, 7, 1), open=35000.0, high=36000.0, low=34000.0, close=35500.0, volume=1000),
                OHLCVData(timestamp=datetime(2021, 7, 2), open=35500.0, high=37000.0, low=35000.0, close=36500.0, volume=1200)
            ],
            data_type=DataType.OHLCV
        )
        mock_cache = MagicMock()
        empty_data = TimeSeriesData(timestamps=[], data=[], data_type=DataType.OHLCV)
        mock_cache.get_cached_data.return_value = empty_data
        
        # Mock the cache metadata to return missing ranges when cache is empty
        mock_metadata = MagicMock()
        mock_metadata.get_missing_ranges.return_value = [(datetime(2021, 7, 1), datetime(2021, 7, 2))]
        mock_cache.metadata = mock_metadata
        
        data_manager = DataManager(ohlcv_provider=mock_provider)
        data_manager.cache = mock_cache
        
        data = data_manager.get_ohlcv_data('BTC/USDT', datetime(2021, 7, 1), datetime(2021, 7, 2))
        
        # Convert to DataFrame for processing
        df = data.to_dataframe()
        
        # Since cache returns empty data, provider should be called and we should get the provider's data
        assert len(df) == 2
        assert 'open' in df.columns
        assert 'high' in df.columns
        assert 'low' in df.columns
        assert 'close' in df.columns
        assert 'volume' in df.columns
        
        # Verify provider was called since cache was empty
        mock_provider.get_data.assert_called_once()
        
    finally:
        shutil.rmtree(temp_cache_dir)

def test_cache_integration():
    """Test cache integration with DataManager"""
    with patch('src.data.cache.smart_cache.SmartCache.__init__') as mock_cache_init:
        mock_cache_init.return_value = None
        data_manager = DataManager()
        
        # Mock the cache methods
        mock_cache = MagicMock()
        mock_cache.get_stats.return_value = {'memory_segments': 0, 'file_segments': 0, 'symbols': 0}
        data_manager.cache = mock_cache
        
        # Test cache stats
        stats = data_manager.get_cache_stats()
        assert isinstance(stats, dict)
        
        # Test cache clearing
        data_manager.clear_cache()
        assert True  # Should not raise an error 