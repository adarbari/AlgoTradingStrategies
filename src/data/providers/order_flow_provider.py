from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
from ..types.base_types import TimeSeriesData
from ..types.data_config_types import OrderFlowConfig
from .base_provider import DataProvider

class OrderFlowDataProvider(DataProvider[TimeSeriesData, OrderFlowConfig]):
    """
    Interface for providers that supply Order Flow data.
    This is the core interface without caching.
    """
    
    @abstractmethod
    def get_data(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        config: Optional[OrderFlowConfig] = None
    ) -> TimeSeriesData:
        """
        Fetch Order Flow data directly from the vendor.
        
        Args:
            symbol: The trading symbol
            start_time: Start time for data
            end_time: End time for data
            config: Optional configuration for the Order Flow data request
            
        Returns:
            TimeSeriesData containing Order Flow data
        """
        pass 