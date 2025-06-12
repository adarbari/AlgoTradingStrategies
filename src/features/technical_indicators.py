from typing import List, Optional, Dict
import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands
from .base import FeatureEngineer

class TechnicalIndicators(FeatureEngineer):
    """Technical indicators feature engineering implementation."""
    
    # Feature name constants
    class FeatureNames:
        # Trend Indicators
        SMA_20 = 'sma_20'
        SMA_50 = 'sma_50'
        SMA_200 = 'sma_200'
        EMA_20 = 'ema_20'
        EMA_50 = 'ema_50'
        EMA_200 = 'ema_200'
        MACD = 'macd'
        MACD_SIGNAL = 'macd_signal'
        MACD_HIST = 'macd_hist'
        
        # Momentum Indicators
        RSI_14 = 'rsi_14'
        STOCH_K = 'stoch_k'
        STOCH_D = 'stoch_d'
        
        # Volatility Indicators
        BB_UPPER = 'bb_upper'
        BB_MIDDLE = 'bb_middle'
        BB_LOWER = 'bb_lower'
        
        # Volume Indicators
        VOLUME_MA_5 = 'volume_ma_5'
        VOLUME_MA_15 = 'volume_ma_15'
        
        # Price Action
        PRICE_CHANGE = 'price_change'
        VOLUME_CHANGE = 'volume_change'
        VOLATILITY = 'volatility'
        PRICE_CHANGE_5MIN = 'price_change_5min'
        PRICE_CHANGE_15MIN = 'price_change_15min'
        PRICE_RANGE = 'price_range'
        PRICE_RANGE_MA = 'price_range_ma'
        VOLATILITY_5MIN = 'volatility_5min'
        VOLATILITY_15MIN = 'volatility_15min'
        
        # Moving Average Crossover specific
        MA_SHORT = 'ma_short'
        MA_LONG = 'ma_long'
    
    def __init__(self):
        """Initialize the technical indicators feature engineer."""
        self._available_features = [
            # Trend Indicators
            self.FeatureNames.SMA_20,
            self.FeatureNames.SMA_50,
            self.FeatureNames.SMA_200,
            self.FeatureNames.EMA_20,
            self.FeatureNames.EMA_50,
            self.FeatureNames.EMA_200,
            self.FeatureNames.MACD,
            self.FeatureNames.MACD_SIGNAL,
            self.FeatureNames.MACD_HIST,
            
            # Momentum Indicators
            self.FeatureNames.RSI_14,
            self.FeatureNames.STOCH_K,
            self.FeatureNames.STOCH_D,
            
            # Volatility Indicators
            self.FeatureNames.BB_UPPER,
            self.FeatureNames.BB_MIDDLE,
            self.FeatureNames.BB_LOWER,
            
            # Volume Indicators
            self.FeatureNames.VOLUME_MA_5,
            self.FeatureNames.VOLUME_MA_15,
            
            # Price Action
            self.FeatureNames.PRICE_CHANGE,
            self.FeatureNames.VOLUME_CHANGE,
            self.FeatureNames.VOLATILITY,
            self.FeatureNames.PRICE_CHANGE_5MIN,
            self.FeatureNames.PRICE_CHANGE_15MIN,
            self.FeatureNames.PRICE_RANGE,
            self.FeatureNames.PRICE_RANGE_MA,
            self.FeatureNames.VOLATILITY_5MIN,
            self.FeatureNames.VOLATILITY_15MIN,
            
            # Moving Average Crossover specific
            self.FeatureNames.MA_SHORT,
            self.FeatureNames.MA_LONG
        ]
        
        self._feature_dependencies = {
            # Trend Indicators
            self.FeatureNames.SMA_20: ['close'],
            self.FeatureNames.SMA_50: ['close'],
            self.FeatureNames.SMA_200: ['close'],
            self.FeatureNames.EMA_20: ['close'],
            self.FeatureNames.EMA_50: ['close'],
            self.FeatureNames.EMA_200: ['close'],
            self.FeatureNames.MACD: ['close'],
            self.FeatureNames.MACD_SIGNAL: ['close'],
            self.FeatureNames.MACD_HIST: ['close'],
            
            # Momentum Indicators
            self.FeatureNames.RSI_14: ['close'],
            self.FeatureNames.STOCH_K: ['high', 'low', 'close'],
            self.FeatureNames.STOCH_D: ['high', 'low', 'close'],
            
            # Volatility Indicators
            self.FeatureNames.BB_UPPER: ['close'],
            self.FeatureNames.BB_MIDDLE: ['close'],
            self.FeatureNames.BB_LOWER: ['close'],
            
            # Volume Indicators
            self.FeatureNames.VOLUME_MA_5: ['volume'],
            self.FeatureNames.VOLUME_MA_15: ['volume'],
            
            # Price Action
            self.FeatureNames.PRICE_CHANGE: ['close'],
            self.FeatureNames.VOLUME_CHANGE: ['volume'],
            self.FeatureNames.VOLATILITY: ['close'],
            self.FeatureNames.PRICE_CHANGE_5MIN: ['close'],
            self.FeatureNames.PRICE_CHANGE_15MIN: ['close'],
            self.FeatureNames.PRICE_RANGE: ['high', 'low', 'close'],
            self.FeatureNames.PRICE_RANGE_MA: ['high', 'low', 'close'],
            self.FeatureNames.VOLATILITY_5MIN: ['close'],
            self.FeatureNames.VOLATILITY_15MIN: ['close'],
            
            # Moving Average Crossover specific
            self.FeatureNames.MA_SHORT: ['close'],
            self.FeatureNames.MA_LONG: ['close']
        }
        
        # Default MA windows
        self._short_window = 10
        self._long_window = 50
    
    def calculate_features(
        self,
        data: pd.DataFrame,
        features: Optional[List[str]] = None,
        symbol: Optional[str] = None
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
        if any(f in features for f in [self.FeatureNames.SMA_20, self.FeatureNames.SMA_50, self.FeatureNames.SMA_200]):
            for period in [20, 50, 200]:
                feature_name = f'sma_{period}'
                if feature_name in features:
                    df[feature_name] = SMAIndicator(close=df['close'], window=period).sma_indicator()
        
        if any(f in features for f in [self.FeatureNames.EMA_20, self.FeatureNames.EMA_50, self.FeatureNames.EMA_200]):
            for period in [20, 50, 200]:
                feature_name = f'ema_{period}'
                if feature_name in features:
                    df[feature_name] = EMAIndicator(close=df['close'], window=period).ema_indicator()
        
        if any(f in features for f in [self.FeatureNames.MACD, self.FeatureNames.MACD_SIGNAL, self.FeatureNames.MACD_HIST]):
            macd = MACD(close=df['close'])
            if self.FeatureNames.MACD in features:
                df[self.FeatureNames.MACD] = macd.macd()
            if self.FeatureNames.MACD_SIGNAL in features:
                df[self.FeatureNames.MACD_SIGNAL] = macd.macd_signal()
            if self.FeatureNames.MACD_HIST in features:
                df[self.FeatureNames.MACD_HIST] = macd.macd_diff()
        
        # Calculate momentum indicators
        if self.FeatureNames.RSI_14 in features:
            df[self.FeatureNames.RSI_14] = RSIIndicator(close=df['close']).rsi()
        
        if any(f in features for f in [self.FeatureNames.STOCH_K, self.FeatureNames.STOCH_D]):
            stoch = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'])
            if self.FeatureNames.STOCH_K in features:
                df[self.FeatureNames.STOCH_K] = stoch.stoch()
            if self.FeatureNames.STOCH_D in features:
                df[self.FeatureNames.STOCH_D] = stoch.stoch_signal()
        
        # Calculate volatility indicators
        if any(f in features for f in [self.FeatureNames.BB_UPPER, self.FeatureNames.BB_MIDDLE, self.FeatureNames.BB_LOWER]):
            bb = BollingerBands(close=df['close'])
            if self.FeatureNames.BB_UPPER in features:
                df[self.FeatureNames.BB_UPPER] = bb.bollinger_hband()
            if self.FeatureNames.BB_MIDDLE in features:
                df[self.FeatureNames.BB_MIDDLE] = bb.bollinger_mavg()
            if self.FeatureNames.BB_LOWER in features:
                df[self.FeatureNames.BB_LOWER] = bb.bollinger_lband()
        
        # Calculate volume indicators
        if self.FeatureNames.VOLUME_MA_5 in features:
            df[self.FeatureNames.VOLUME_MA_5] = df['volume'].rolling(window=5).mean()
        if self.FeatureNames.VOLUME_MA_15 in features:
            df[self.FeatureNames.VOLUME_MA_15] = df['volume'].rolling(window=15).mean()
        
        # Calculate price action indicators
        if self.FeatureNames.PRICE_CHANGE in features:
            df[self.FeatureNames.PRICE_CHANGE] = df['close'].pct_change()
        if self.FeatureNames.VOLUME_CHANGE in features:
            df[self.FeatureNames.VOLUME_CHANGE] = df['volume'].pct_change()
        if self.FeatureNames.VOLATILITY in features:
            df[self.FeatureNames.VOLATILITY] = df[self.FeatureNames.PRICE_CHANGE].rolling(window=20).std()
        if self.FeatureNames.PRICE_CHANGE_5MIN in features:
            df[self.FeatureNames.PRICE_CHANGE_5MIN] = df['close'].pct_change(5)
        if self.FeatureNames.PRICE_CHANGE_15MIN in features:
            df[self.FeatureNames.PRICE_CHANGE_15MIN] = df['close'].pct_change(15)
        if self.FeatureNames.PRICE_RANGE in features:
            df[self.FeatureNames.PRICE_RANGE] = (df['high'] - df['low']) / df['close']
        if self.FeatureNames.PRICE_RANGE_MA in features:
            df[self.FeatureNames.PRICE_RANGE_MA] = df[self.FeatureNames.PRICE_RANGE].rolling(window=10).mean()
        if self.FeatureNames.VOLATILITY_5MIN in features:
            df[self.FeatureNames.VOLATILITY_5MIN] = df[self.FeatureNames.PRICE_CHANGE].rolling(window=5).std()
        if self.FeatureNames.VOLATILITY_15MIN in features:
            df[self.FeatureNames.VOLATILITY_15MIN] = df[self.FeatureNames.PRICE_CHANGE].rolling(window=15).std()
        
        # Calculate MA crossover specific features
        if self.FeatureNames.MA_SHORT in features:
            df[self.FeatureNames.MA_SHORT] = df['close'].rolling(window=self._short_window).mean()
        if self.FeatureNames.MA_LONG in features:
            df[self.FeatureNames.MA_LONG] = df['close'].rolling(window=self._long_window).mean()
        
        return df
    
    def get_available_features(self) -> List[str]:
        """Get list of available features that can be calculated."""
        return self._available_features
    
    def get_feature_dependencies(self, feature: str) -> List[str]:
        """Get list of features that a given feature depends on."""
        return self._feature_dependencies.get(feature, []) 