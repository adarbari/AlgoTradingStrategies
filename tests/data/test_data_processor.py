import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.data.data_manager import DataManager
from src.data.types.base_types import TimeSeriesData
from src.data.types.ohlcv_types import OHLCVData

def test_data_processing():
    """Test data processing with DataManager"""
    # Create a mock provider
    mock_provider = MagicMock()
    mock_provider.get_data.return_value = TimeSeriesData(
        timestamps=[datetime(2021, 7, 1), datetime(2021, 7, 2)],
        data=[
            OHLCVData(timestamp=datetime(2021, 7, 1), open=35000.0, high=36000.0, low=34000.0, close=35500.0, volume=100.0),
            OHLCVData(timestamp=datetime(2021, 7, 2), open=35500.0, high=37000.0, low=35000.0, close=36500.0, volume=150.0)
        ],
        data_type=None
    )
    
    # Create DataManager with mock provider
    with patch('src.data.data_manager.PolygonProvider', return_value=mock_provider):
        data_manager = DataManager()
        
        # Test data fetching and processing
        data = data_manager.get_ohlcv_data('BTC/USDT', datetime(2021, 7, 1), datetime(2021, 7, 2))
        
        # Convert to DataFrame for processing
        df = data.to_dataframe()
        
        # Verify DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == ['open', 'high', 'low', 'close', 'volume']
        assert df.index.name == 'timestamp'

def test_cache_integration():
    """Test cache integration with DataManager"""
    data_manager = DataManager()
    
    # Test cache stats
    stats = data_manager.get_cache_stats()
    assert isinstance(stats, dict)
    
    # Test cache clearing
    data_manager.clear_cache()
    assert True  # Should not raise an error 