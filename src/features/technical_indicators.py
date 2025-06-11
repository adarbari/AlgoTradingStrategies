from typing import List, Optional
import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands
from .base import FeatureEngineer

class TechnicalIndicators(FeatureEngineer):
    """Technical indicators feature engineering implementation."""
    
    def __init__(self):
        """Initialize the technical indicators feature engineer."""
        self._available_features = [
            # Trend Indicators
            'sma_20', 'sma_50', 'sma_200',
            'ema_20', 'ema_50', 'ema_200',
            'macd', 'macd_signal', 'macd_hist',
            
            # Momentum Indicators
            'rsi_14',
            'stoch_k', 'stoch_d',
            
            # Volatility Indicators
            'bb_upper', 'bb_middle', 'bb_lower',
            
            # Volume Indicators
            'volume_ma_5', 'volume_ma_15',
            
            # Price Action
            'price_change', 'volume_change', 'volatility',
            'price_change_5min', 'price_change_15min',
            'price_range', 'price_range_ma',
            'volatility_5min', 'volatility_15min'
        ]
        
        self._feature_dependencies = {
            # Trend Indicators
            'sma_20': ['close'],
            'sma_50': ['close'],
            'sma_200': ['close'],
            'ema_20': ['close'],
            'ema_50': ['close'],
            'ema_200': ['close'],
            'macd': ['close'],
            'macd_signal': ['close'],
            'macd_hist': ['close'],
            
            # Momentum Indicators
            'rsi_14': ['close'],
            'stoch_k': ['high', 'low', 'close'],
            'stoch_d': ['high', 'low', 'close'],
            
            # Volatility Indicators
            'bb_upper': ['close'],
            'bb_middle': ['close'],
            'bb_lower': ['close'],
            
            # Volume Indicators
            'volume_ma_5': ['volume'],
            'volume_ma_15': ['volume'],
            
            # Price Action
            'price_change': ['close'],
            'volume_change': ['volume'],
            'volatility': ['close'],
            'price_change_5min': ['close'],
            'price_change_15min': ['close'],
            'price_range': ['high', 'low', 'close'],
            'price_range_ma': ['high', 'low', 'close'],
            'volatility_5min': ['close'],
            'volatility_15min': ['close']
        }
    
    def calculate_features(
        self,
        data: pd.DataFrame,
        features: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Calculate technical indicators for the given data."""
        if features is None:
            features = self._available_features
            
        df = data.copy()
        
        # Ensure required columns exist
        required_columns = set()
        for feature in features:
            if feature in self._feature_dependencies:
                required_columns.update(self._feature_dependencies[feature])
        
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Calculate trend indicators
        if any(f in features for f in ['sma_20', 'sma_50', 'sma_200']):
            for period in [20, 50, 200]:
                if f'sma_{period}' in features:
                    df[f'sma_{period}'] = SMAIndicator(close=df['close'], window=period).sma_indicator()
        
        if any(f in features for f in ['ema_20', 'ema_50', 'ema_200']):
            for period in [20, 50, 200]:
                if f'ema_{period}' in features:
                    df[f'ema_{period}'] = EMAIndicator(close=df['close'], window=period).ema_indicator()
        
        if any(f in features for f in ['macd', 'macd_signal', 'macd_hist']):
            macd = MACD(close=df['close'])
            if 'macd' in features:
                df['macd'] = macd.macd()
            if 'macd_signal' in features:
                df['macd_signal'] = macd.macd_signal()
            if 'macd_hist' in features:
                df['macd_hist'] = macd.macd_diff()
        
        # Calculate momentum indicators
        if 'rsi_14' in features:
            df['rsi_14'] = RSIIndicator(close=df['close']).rsi()
        
        if any(f in features for f in ['stoch_k', 'stoch_d']):
            stoch = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'])
            if 'stoch_k' in features:
                df['stoch_k'] = stoch.stoch()
            if 'stoch_d' in features:
                df['stoch_d'] = stoch.stoch_signal()
        
        # Calculate volatility indicators
        if any(f in features for f in ['bb_upper', 'bb_middle', 'bb_lower']):
            bb = BollingerBands(close=df['close'])
            if 'bb_upper' in features:
                df['bb_upper'] = bb.bollinger_hband()
            if 'bb_middle' in features:
                df['bb_middle'] = bb.bollinger_mavg()
            if 'bb_lower' in features:
                df['bb_lower'] = bb.bollinger_lband()
        
        # Calculate volume indicators
        if 'volume_ma_5' in features:
            df['volume_ma_5'] = df['volume'].rolling(window=5).mean()
        if 'volume_ma_15' in features:
            df['volume_ma_15'] = df['volume'].rolling(window=15).mean()
        
        # Calculate price action indicators
        if 'price_change' in features:
            df['price_change'] = df['close'].pct_change()
        if 'volume_change' in features:
            df['volume_change'] = df['volume'].pct_change()
        if 'volatility' in features:
            df['volatility'] = df['price_change'].rolling(window=20).std()
        if 'price_change_5min' in features:
            df['price_change_5min'] = df['close'].pct_change(5)
        if 'price_change_15min' in features:
            df['price_change_15min'] = df['close'].pct_change(15)
        if 'price_range' in features:
            df['price_range'] = (df['high'] - df['low']) / df['close']
        if 'price_range_ma' in features:
            df['price_range_ma'] = df['price_range'].rolling(window=10).mean()
        if 'volatility_5min' in features:
            df['volatility_5min'] = df['price_change'].rolling(window=5).std()
        if 'volatility_15min' in features:
            df['volatility_15min'] = df['price_change'].rolling(window=15).std()
        
        return df
    
    def get_available_features(self) -> List[str]:
        """Get list of available features that can be calculated."""
        return self._available_features
    
    def get_feature_dependencies(self, feature: str) -> List[str]:
        """Get list of features that a given feature depends on."""
        return self._feature_dependencies.get(feature, []) 