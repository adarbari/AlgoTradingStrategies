"""
Base strategy class that defines the interface for all trading strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
import numpy as np

from src.execution.trade_decider import StrategySignal

class BaseStrategy(ABC):
    """Base class for all trading strategies."""
    
    def __init__(self, name: str):
        """Initialize base strategy.
        
        Args:
            name: Name of the strategy
        """
        self.name = name
        
    @abstractmethod
    def prepare_data(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Prepare data for the strategy.
        
        Args:
            data: Raw price/indicator data
            symbol: Stock symbol
            
        Returns:
            Processed data ready for strategy
        """
        pass
        
    @abstractmethod
    def generate_signals(
        self,
        data: pd.DataFrame,
        symbol: str,
        timestamp: datetime
    ) -> StrategySignal:
        """Generate trading signals for a symbol at a given timestamp.
        
        Args:
            data: Prepared data for the strategy
            symbol: Stock symbol
            timestamp: Current timestamp
            
        Returns:
            StrategySignal with probabilities and confidence
        """
        pass
        
    @abstractmethod
    def update(self, data: pd.DataFrame, symbol: str) -> None:
        """Update strategy with new data.
        
        Args:
            data: New data to update the strategy with
            symbol: Stock symbol
        """
        pass
        
    def get_features(self) -> List[str]:
        """Get list of features used by the strategy.
        
        Returns:
            List of feature names
        """
        return []
        
    def get_parameters(self) -> Dict[str, Any]:
        """Get strategy parameters.
        
        Returns:
            Dictionary of strategy parameters
        """
        return {}
        
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """Set strategy parameters.
        
        Args:
            parameters: Dictionary of strategy parameters
        """
        pass 