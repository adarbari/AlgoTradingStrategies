"""
Moving Average Crossover Strategy implementation for single stock trading.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
import numpy as np
import logging

from src.features.feature_store import FeatureStore
from src.features.technical_indicators import TechnicalIndicators, FeatureNames
from src.strategies.base_strategy import BaseStrategy, StrategySignal
from src.config.strategy_config import MACrossoverConfig

class MACrossoverStrategy(BaseStrategy):
    """
    Moving Average Crossover Strategy for single stock trading.
    
    This strategy generates signals based on the crossover of two moving averages:
    - Short-term moving average (10-day)
    - Long-term moving average (50-day)
    
    A buy signal is generated when the short MA crosses above the long MA,
    and a sell signal is generated when the short MA crosses below the long MA.
    """
    
    def __init__(
        self,
        config: Optional[MACrossoverConfig] = None
    ):
        """
        Initialize the MA Crossover Strategy.
        
        Args:
            config (Optional[MACrossoverConfig]): Strategy configuration. If None, default config will be used.
            feature_store (Optional[FeatureStore]): Feature store instance. If None, a new one will be created.
        """
        super().__init__(name="MA_Crossover")
        self.config = config or MACrossoverConfig()
        self.feature_store = FeatureStore.get_instance()
        self._prev_features = None  # Store previous features for crossover detection
        self.technical_indicators = TechnicalIndicators()

    def train_model(self, data: pd.DataFrame, symbol: str):
        """No training required for MA Crossover strategy."""
        return None
    
    def generate_signals(
        self,
        features: Dict[str, float],
        symbol: str,
        timestamp: datetime
    ) -> StrategySignal:
        """
        Generate trading signals based on MA crossovers.
        
        Args:
            features (Dict[str, float]): Current features including price and moving averages
            symbol (str): Stock symbol
            timestamp (datetime): Current timestamp
            
        Returns:
            StrategySignal: Trading signal with probabilities and confidence
        """
        # Store current features for next comparison
        current_features = features.copy()

        # Get 'ma_short' and 'ma_long' features from technical indicators
        ma_short = FeatureNames.MA_SHORT
        ma_long = FeatureNames.MA_LONG
        
        if ma_short not in current_features or ma_long not in current_features:
            logging.warning(f"Missing '{ma_short}' or '{ma_long}' in features for {symbol} at {timestamp}. Features: {list(current_features.keys())}")
            probabilities = {'BUY': 0.1, 'SELL': 0.1, 'HOLD': 0.8}
            confidence = 0.0
            action = 'HOLD'
            self._prev_features = current_features
            return StrategySignal(
                timestamp=timestamp,
                symbol=symbol,
                action=action,
                features=current_features,
                probabilities=probabilities,
                confidence=confidence
            )

        # Calculate probabilities based on MA crossover
        if self._prev_features is None:
            # First signal, no crossover possible
            probabilities = {'BUY': 0.1, 'SELL': 0.1, 'HOLD': 0.8}
            confidence = 0.6
        else:
            # Check for crossover
            if (current_features[ma_short] > current_features[ma_long] and 
                self._prev_features[ma_short] <= self._prev_features[ma_long]):
                # Bullish crossover
                probabilities = {'BUY': 0.8, 'SELL': 0.1, 'HOLD': 0.1}
                confidence = 0.8
            elif (current_features[ma_short] < current_features[ma_long] and 
                  self._prev_features[ma_short] >= self._prev_features[ma_long]):
                # Bearish crossover
                probabilities = {'BUY': 0.1, 'SELL': 0.8, 'HOLD': 0.1}
                confidence = 0.8
            else:
                # No crossover
                if current_features[ma_short] > current_features[ma_long]:
                    # Uptrend
                    probabilities = {'BUY': 0.3, 'SELL': 0.1, 'HOLD': 0.6}
                    confidence = 0.6
                else:
                    # Downtrend
                    probabilities = {'BUY': 0.1, 'SELL': 0.3, 'HOLD': 0.6}
                    confidence = 0.6
        
        # Store current features for next comparison
        self._prev_features = current_features
        
        # Determine action based on highest probability
        action = max(probabilities.items(), key=lambda x: x[1])[0]
        
        return StrategySignal(
            timestamp=timestamp,
            symbol=symbol,
            action=action,
            features=current_features,
            probabilities=probabilities,
            confidence=confidence
        )
    
    def update(self, data: pd.DataFrame, symbol: str) -> None:
        """
        Update strategy with new data.
        
        Args:
            data (pd.DataFrame): New data to update the strategy with
            symbol (str): Stock symbol
        """
        # No state to update for MA Crossover
        pass
    
    def get_features(self) -> List[str]:
        """
        Get list of features used by the strategy.
        
        Returns:
            List[str]: List of feature names
        """
        return self.config.feature_columns
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get strategy parameters.
        
        Returns:
            Dict[str, Any]: Strategy parameters
        """
        return {
            'short_window': self.config.short_window,
            'long_window': self.config.long_window,
            'feature_columns': self.config.feature_columns
        }
    
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Set strategy parameters.
        
        Args:
            parameters (Dict[str, Any]): New strategy parameters
        """
        self.config = MACrossoverConfig(**parameters) 