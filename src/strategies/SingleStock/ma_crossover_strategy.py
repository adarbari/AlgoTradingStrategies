"""
Moving Average Crossover Strategy implementation for single stock trading.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
import numpy as np
import logging

from src.features.feature_provider import FeatureProvider
from src.features.technical_indicators import TechnicalIndicators
from src.strategies.base_strategy import BaseStrategy, StrategySignal

class MACrossoverStrategy(BaseStrategy):
    """
    Moving Average Crossover Strategy for single stock trading.
    
    This strategy generates signals based on the crossover of two moving averages:
    - Short-term moving average (10-day)
    - Long-term moving average (50-day)
    
    A buy signal is generated when the short MA crosses above the long MA,
    and a sell signal is generated when the short MA crosses below the long MA.
    """
    
    def __init__(self, short_window: int = 10, long_window: int = 50, cache_dir: str = 'feature_cache'):
        """
        Initialize the MA Crossover Strategy.
        
        Args:
            short_window (int): Window size for short-term moving average (default: 10)
            long_window (int): Window size for long-term moving average (default: 50)
            cache_dir (str): Directory for caching features
        """
        super().__init__(name="MA_Crossover")
        self.short_window = short_window
        self.long_window = long_window
        self.cache_dir = cache_dir
        self.feature_provider = FeatureProvider()
        self._prev_features = None  # Store previous features for crossover detection
        self.technical_indicators = TechnicalIndicators()
        
    def prepare_data(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Prepare data for the strategy by using cached moving averages or calculating them.
        
        Args:
            data (pd.DataFrame): Price data
            symbol (str): Stock symbol
            
        Returns:
            pd.DataFrame: Data with moving averages
        """
        # Determine date range
        start_date = data.index.min().strftime('%Y-%m-%d')
        end_date = data.index.max().strftime('%Y-%m-%d')
        
        print(f"Looking for features in cache: {symbol} from {start_date} to {end_date}")
        print(f"Cache directory: {self.cache_dir}")
        
        # Get features using the feature provider
        features = self.feature_provider.get_features(
            symbol=symbol,
            data=data,
            start_date=start_date,
            end_date=end_date
        )
        
        print(f"Found features with columns: {features.columns.tolist()}")
        return features
    
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
        ma_short = self.technical_indicators.FeatureNames.MA_SHORT
        ma_long = self.technical_indicators.FeatureNames.MA_LONG
        
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
        return [
            self.technical_indicators.FeatureNames.MA_SHORT,
            self.technical_indicators.FeatureNames.MA_LONG
        ]
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get strategy parameters.
        
        Returns:
            Dict[str, Any]: Strategy parameters
        """
        return {
            'short_window': self.short_window,
            'long_window': self.long_window
        }
    
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Set strategy parameters.
        
        Args:
            parameters (Dict[str, Any]): New strategy parameters
        """
        if 'short_window' in parameters:
            self.short_window = parameters['short_window']
        if 'long_window' in parameters:
            self.long_window = parameters['long_window'] 