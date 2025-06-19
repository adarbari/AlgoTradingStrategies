import ccxt
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
from ..types.base_types import TimeSeriesData
from ..types.data_config_types import OHLCVConfig
from .base_provider import DataProvider

class OHLCVDataProvider(DataProvider[TimeSeriesData, OHLCVConfig]):
    """
    Interface for providers that supply OHLCV (Open, High, Low, Close, Volume) data.
    This is the core interface without caching.
    """
    
    @abstractmethod
    def get_data(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        config: Optional[OHLCVConfig] = None
    ) -> TimeSeriesData:
        """
        Fetch OHLCV data directly from the vendor.
        
        Args:
            symbol: The trading symbol
            start_time: Start time for data
            end_time: End time for data
            config: Optional configuration for the OHLCV data request
            
        Returns:
            TimeSeriesData containing OHLCV data
        """
        pass
