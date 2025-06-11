"""
Moving Average Crossover Strategy implementation for single stock trading.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np
import logging

from src.features.feature_store import FeatureStore
from src.strategies.base_strategy import BaseStrategy, StrategySignal

class MACrossoverStrategy(BaseStrategy):
    """
    Moving Average Crossover Strategy for single stock trading.
    
    This strategy generates signals based on the crossover of two moving averages:
    - Short-term moving average (e.g., 5-day)
    - Long-term moving average (e.g., 20-day)
    
    A buy signal is generated when the short MA crosses above the long MA,
    and a sell signal is generated when the short MA crosses below the long MA.
    """
    
    def __init__(self, short_window: int = 5, long_window: int = 20, cache_dir: str = 'feature_cache'):
        """
        Initialize the MA Crossover Strategy.
        
        Args:
            short_window (int): Window size for short-term moving average
            long_window (int): Window size for long-term moving average
            cache_dir (str): Directory for caching features
        """
        super().__init__(name="MA_Crossover")
        self.short_window = short_window
        self.long_window = long_window
        self.cache_dir = cache_dir
        self.feature_store = FeatureStore(cache_dir=cache_dir)
        self._prev_features = None  # Store previous features for crossover detection
        
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
        
        # Set MA windows in feature store
        self.feature_store.set_ma_windows(symbol, self.short_window, self.long_window)
        
        # Try to get cached features
        features = self.feature_store.get_cached_features(
            symbol, 
            start_date, 
            end_date
        )

        if features is None:
            print("No cached features found, calculating moving averages...")
            features = self.feature_store.calculate_and_cache_features(
                symbol,
                data,
                start_date,
                end_date
            )
        else:
            print(f"Found cached features with columns: {features.columns.tolist()}")

        # Map SMA columns to 'ma_short' and 'ma_long' for each row
        short_col = f'sma_{self.short_window}'
        long_col = f'sma_{self.long_window}'
        if short_col in features.columns and long_col in features.columns:
            features = features.copy()
            features['ma_short'] = features[short_col]
            features['ma_long'] = features[long_col]
        else:
            print(f"Warning: Expected columns {short_col} and/or {long_col} not found in features.")

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

        # Patch: Handle missing 'ma_short' or 'ma_long' gracefully
        if 'ma_short' not in current_features or 'ma_long' not in current_features:
            logging.warning(f"Missing 'ma_short' or 'ma_long' in features for {symbol} at {timestamp}. Features: {list(current_features.keys())}")
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
            if (current_features['ma_short'] > current_features['ma_long'] and 
                self._prev_features['ma_short'] <= self._prev_features['ma_long']):
                # Bullish crossover
                probabilities = {'BUY': 0.8, 'SELL': 0.1, 'HOLD': 0.1}
                confidence = 0.8
            elif (current_features['ma_short'] < current_features['ma_long'] and 
                  self._prev_features['ma_short'] >= self._prev_features['ma_long']):
                # Bearish crossover
                probabilities = {'BUY': 0.1, 'SELL': 0.8, 'HOLD': 0.1}
                confidence = 0.8
            else:
                # No crossover
                if current_features['ma_short'] > current_features['ma_long']:
                    # Uptrend
                    probabilities = {'BUY': 0.3, 'SELL': 0.1, 'HOLD': 0.6}
                    confidence = 0.6
                else:
                    # Downtrend
                    probabilities = {'BUY': 0.1, 'SELL': 0.3, 'HOLD': 0.6}
                    confidence = 0.6
        
        # Update previous features for next comparison
        self._prev_features = current_features
        
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
        Update the strategy with new data.
        
        Args:
            data (pd.DataFrame): New price data
            symbol (str): Stock symbol
        """
        # Reset previous features when updating with new data
        self._prev_features = None
    
    def get_features(self) -> list:
        """
        Get the list of features used by the strategy.
        
        Returns:
            list: List of feature names
        """
        return ['price', 'ma_short', 'ma_long']
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get the strategy parameters.
        
        Returns:
            Dict[str, Any]: Strategy parameters
        """
        return {
            'short_window': self.short_window,
            'long_window': self.long_window
        }
    
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Set the strategy parameters.
        
        Args:
            parameters (Dict[str, Any]): New strategy parameters
        """
        if 'short_window' in parameters:
            self.short_window = parameters['short_window']
        if 'long_window' in parameters:
            self.long_window = parameters['long_window'] 