"""
Rithmic implementation of OrderFlowDataProvider.
Provides historical tick bar data from Rithmic systems.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List
import pandas as pd

from src.data.types.base_types import TimeSeriesData
from src.data.types.data_config_types import OrderFlowConfig
from src.data.providers.order_flow_provider import OrderFlowDataProvider
from src.data.types.data_type import DataType
from src.data.types.order_flow_types import Trade, OrderSide
from .protocol.historical_tick_bar import HistoricalTickBarProvider

logger = logging.getLogger(__name__)

# Custom exceptions for Rithmic provider
class RithmicConnectionError(Exception):
    """Exception raised when connection to Rithmic fails."""
    pass

class RithmicAuthenticationError(Exception):
    """Exception raised when authentication with Rithmic fails."""
    pass

class RithmicDataError(Exception):
    """Exception raised when data retrieval from Rithmic fails."""
    pass

class RithmicProvider(OrderFlowDataProvider):
    """
    Rithmic implementation of OrderFlowDataProvider.
    Provides historical tick bar data from Rithmic systems.
    """
    
    def __init__(
        self, 
        uri: Optional[str] = None,
        system_name: Optional[str] = None,
        user_id: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize the Rithmic provider.
        
        Args:
            uri: Rithmic connection URI (e.g., "wss://rituz00100.rithmic.com:443")
            system_name: Rithmic system name
            user_id: User ID for authentication
            password: Password for authentication
        """
        super().__init__()
        
        # Try to get credentials from environment variables first
        self.uri = uri or os.getenv('RITHMIC_URI', "wss://rituz00100.rithmic.com:443")
        self.system_name = system_name or os.getenv('RITHMIC_SYSTEM_NAME')
        self.user_id = user_id or os.getenv('RITHMIC_USER_ID')
        self.password = password or os.getenv('RITHMIC_PASSWORD')
        
        # Initialize the historical tick bar provider
        self._tick_bar_provider = HistoricalTickBarProvider()
        
        # Storage for collected data during the session
        self._collected_data = []
        
    def get_data(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        config: Optional[OrderFlowConfig] = None
    ) -> TimeSeriesData:
        """
        Fetch order flow data from Rithmic.
        
        Args:
            symbol: The trading symbol
            start_time: Start time for data
            end_time: End time for data
            config: Optional configuration for the order flow data request
            
        Returns:
            TimeSeriesData containing order flow data
            
        Raises:
            RithmicConnectionError: If connection to Rithmic fails
            RithmicAuthenticationError: If authentication fails
            RithmicDataError: If data retrieval fails
        """
        if config is None:
            config = OrderFlowConfig()
        
        # Validate required parameters
        if not all([self.system_name, self.user_id, self.password]):
            raise RithmicAuthenticationError(
                "Missing required authentication parameters. Please provide system_name, user_id, and password."
            )
        
        # Parse symbol to get exchange and symbol parts
        exchange, symbol_part = self._parse_symbol(symbol)
        
        try:
            # Clear any previous data
            self._collected_data = []
            
            # Use the historical tick bar provider to get data
            # Note: We need to modify the historical_tick_bar.py to collect data instead of just printing
            logger.info(f"Fetching tick bar data for {symbol} from {start_time} to {end_time}")
            
            # For now, we'll call the existing method and collect the printed data
            # In a production environment, you would modify the historical_tick_bar.py 
            # to return structured data instead of printing
            self._tick_bar_provider.get_historical_data(
                uri=self.uri,
                system_name=self.system_name,
                user_id=self.user_id,
                password=self.password,
                exchange=exchange,
                symbol=symbol_part
            )
            
            # Convert collected data to TimeSeriesData
            # Note: This is a placeholder implementation
            # In a real implementation, you would modify the historical_tick_bar.py
            # to collect and return structured data
            return self._convert_to_time_series_data(config)
            
        except Exception as e:
            logger.error(f"Error fetching data from Rithmic: {e}")
            if "connection" in str(e).lower():
                raise RithmicConnectionError(f"Failed to connect to Rithmic: {e}")
            elif "login" in str(e).lower() or "auth" in str(e).lower():
                raise RithmicAuthenticationError(f"Authentication failed: {e}")
            else:
                raise RithmicDataError(f"Data retrieval failed: {e}")
    
    def _parse_symbol(self, symbol: str) -> tuple[str, str]:
        """
        Parse symbol to extract exchange and symbol parts.
        
        Args:
            symbol: Symbol string (e.g., "CME:ES" or just "ES")
            
        Returns:
            Tuple of (exchange, symbol)
        """
        if ':' in symbol:
            exchange, symbol_part = symbol.split(':', 1)
            return exchange, symbol_part
        else:
            # Default to CME if no exchange specified
            return "CME", symbol
    
    def _convert_to_time_series_data(self, config: OrderFlowConfig) -> TimeSeriesData:
        """
        Convert collected data to TimeSeriesData format.
        
        Args:
            config: Order flow configuration
            
        Returns:
            TimeSeriesData containing order flow data
            
        Note:
            This is a placeholder implementation. In a real implementation,
            you would modify the historical_tick_bar.py to collect structured
            data and convert it here.
        """
        # Placeholder implementation - in reality, you would collect actual tick data
        # from the modified historical_tick_bar.py
        
        # Create sample data structure
        timestamps = []
        trades = []
        
        # For now, return empty data with proper structure
        # In a real implementation, this would contain actual tick bar data
        # converted to Trade objects
        
        logger.warning("Returning placeholder data. Modify historical_tick_bar.py to collect actual data.")
        
        return TimeSeriesData(
            timestamps=timestamps,
            data=trades,
            data_type=DataType.ORDER_FLOW
        )
    
    def list_available_systems(self) -> None:
        """
        List available Rithmic systems.
        
        This method calls the underlying historical tick bar provider
        to list available systems.
        """
        try:
            self._tick_bar_provider.get_historical_data(uri=self.uri)
        except Exception as e:
            logger.error(f"Error listing systems: {e}")
            raise RithmicConnectionError(f"Failed to list systems: {e}")
    
    def test_connection(self) -> bool:
        """
        Test connection to Rithmic systems.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self.list_available_systems()
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False 