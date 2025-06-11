"""
Moving Average Crossover Strategy implementation for single stock trading.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np

from src.features.feature_store import FeatureStore
from src.strategies.base_strategy import BaseStrategy
from src.execution.trade_decider import StrategySignal

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
        
    def prepare_data(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Prepare data for the strategy by calculating moving averages.
        
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
        
        # Fetch features from feature store
        features = self.feature_store.get_cached_features(symbol, start_date, end_date)
        if features is None:
            raise ValueError(f"No features found in cache for {symbol} from {start_date} to {end_date}")
            
        print(f"Found features with columns: {features.columns.tolist()}")
        
        # Calculate moving averages
        features['ma_short'] = features['price'].rolling(window=self.short_window).mean()
        features['ma_long'] = features['price'].rolling(window=self.long_window).mean()
        return features
    
    def generate_signals(
        self,
        data: pd.DataFrame,
        symbol: str,
        timestamp: datetime
    ) -> StrategySignal:
        """
        Generate trading signals based on MA crossovers.
        
        Args:
            data (pd.DataFrame): Price data
            symbol (str): Stock symbol
            timestamp (datetime): Current timestamp
            
        Returns:
            StrategySignal: Trading signal with probabilities and confidence
        """
        # Get latest values
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        # Calculate probabilities based on MA crossover
        if latest['ma_short'] > latest['ma_long'] and prev['ma_short'] <= prev['ma_long']:
            # Bullish crossover
            probabilities = {'BUY': 0.8, 'SELL': 0.1, 'HOLD': 0.1}
            confidence = 0.8
        elif latest['ma_short'] < latest['ma_long'] and prev['ma_short'] >= prev['ma_long']:
            # Bearish crossover
            probabilities = {'BUY': 0.1, 'SELL': 0.8, 'HOLD': 0.1}
            confidence = 0.8
        else:
            # No crossover
            if latest['ma_short'] > latest['ma_long']:
                # Uptrend
                probabilities = {'BUY': 0.3, 'SELL': 0.1, 'HOLD': 0.6}
                confidence = 0.6
            else:
                # Downtrend
                probabilities = {'BUY': 0.1, 'SELL': 0.3, 'HOLD': 0.6}
                confidence = 0.6
        
        return StrategySignal(
            timestamp=timestamp,
            symbol=symbol,
            features={
                'price': latest['price'],
                'ma_short': latest['ma_short'],
                'ma_long': latest['ma_long']
            },
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
        # No state to update for MA Crossover
        pass
    
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