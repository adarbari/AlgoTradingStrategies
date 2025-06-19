from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime
from src.data.data_manager import DataManager
from src.data.types.base_types import TimeSeriesData
from src.data.types.ohlcv_types import OHLCVData

def test_get_ohlcv_data():
    """Test getting OHLCV data using DataManager"""
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
        
        # Test data fetching
        data = data_manager.get_ohlcv_data('BTC/USDT', datetime(2021, 7, 1), datetime(2021, 7, 2))
        
        # Verify provider was called correctly
        mock_provider.get_data.assert_called_once()
        
        # Verify returned data
        assert isinstance(data, TimeSeriesData)
        assert len(data.timestamps) == 2
        assert len(data.data) == 2
        assert data.data[0].open == 35000.0
        assert data.data[1].close == 36500.0

def test_get_historical_data():
    """Test getting historical data using DataManager"""
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
        
        # Test data fetching
        data = data_manager.get_ohlcv_data('BTC/USDT', datetime(2021, 7, 1), datetime(2021, 7, 2))
        
        # Verify provider was called correctly
        mock_provider.get_data.assert_called_once()
        
        # Verify returned data
        assert isinstance(data, TimeSeriesData)
        assert len(data.timestamps) == 2
        assert len(data.data) == 2
        assert data.data[0].open == 35000.0
        assert data.data[1].close == 36500.0 