from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import pandas as pd

class DataProvider(ABC):
    """Base class for all data providers."""
    
    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = '1d'
    ) -> pd.DataFrame:
        """Fetch historical data for a given symbol and date range."""
        pass
    
    @abstractmethod
    def get_realtime_data(
        self,
        symbol: str,
        interval: str = '1m'
    ) -> pd.DataFrame:
        """Fetch real-time data for a given symbol."""
        pass
    
    @abstractmethod
    def get_market_data(
        self,
        symbols: List[str],
        data_types: List[str]
    ) -> Dict[str, pd.DataFrame]:
        """Fetch market data for multiple symbols and data types."""
        pass
    
    @abstractmethod
    def get_company_info(
        self,
        symbol: str
    ) -> Dict[str, Union[str, float, int]]:
        """Fetch company information for a given symbol."""
        pass 