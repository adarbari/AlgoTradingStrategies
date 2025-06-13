"""
Configuration classes for trading strategies.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from src.features.technical_indicators import TechnicalIndicators


@dataclass
class BaseStrategyConfig:
    """Base configuration class for all strategies."""
    lookback_window: int = 20
    cache_dir: str = 'feature_cache'


@dataclass
class RandomForestConfig(BaseStrategyConfig):
    """Configuration class for Random Forest Strategy."""
    n_estimators: int = 100
    max_depth: int = 5
    min_samples_split: int = 2 
    random_state: int = 42  
    feature_columns: List[str] = field(default_factory=lambda: [
            # Price data
            'open',
            'high',
            'low',
            'close',
            'volume',
            
            # Moving Averages
            TechnicalIndicators.FeatureNames.SMA_20,
            TechnicalIndicators.FeatureNames.SMA_50,
            TechnicalIndicators.FeatureNames.SMA_200,
            TechnicalIndicators.FeatureNames.EMA_20,
            TechnicalIndicators.FeatureNames.EMA_50,
            TechnicalIndicators.FeatureNames.EMA_200,
            TechnicalIndicators.FeatureNames.MA_SHORT,
            TechnicalIndicators.FeatureNames.MA_LONG,
            
            # MACD
            TechnicalIndicators.FeatureNames.MACD,
            TechnicalIndicators.FeatureNames.MACD_SIGNAL,
            TechnicalIndicators.FeatureNames.MACD_HIST,
            
            # Momentum
            TechnicalIndicators.FeatureNames.RSI_14,
            TechnicalIndicators.FeatureNames.RSI,
            TechnicalIndicators.FeatureNames.STOCH_K,
            TechnicalIndicators.FeatureNames.STOCH_D,
            
            # Volatility
            TechnicalIndicators.FeatureNames.BB_UPPER,
            TechnicalIndicators.FeatureNames.BB_MIDDLE,
            TechnicalIndicators.FeatureNames.BB_LOWER,
            TechnicalIndicators.FeatureNames.ATR,
            
            # Volume
            TechnicalIndicators.FeatureNames.VOLUME_MA_5,
            TechnicalIndicators.FeatureNames.VOLUME_MA_15,
            TechnicalIndicators.FeatureNames.VOLUME_CHANGE,
            
            # Price Action
            TechnicalIndicators.FeatureNames.PRICE_CHANGE,
            TechnicalIndicators.FeatureNames.PRICE_CHANGE_5MIN,
            TechnicalIndicators.FeatureNames.PRICE_CHANGE_15MIN,
            TechnicalIndicators.FeatureNames.PRICE_RANGE,
            TechnicalIndicators.FeatureNames.PRICE_RANGE_MA,
            
            # Volatility
            TechnicalIndicators.FeatureNames.VOLATILITY,
            TechnicalIndicators.FeatureNames.VOLATILITY_5MIN,
            TechnicalIndicators.FeatureNames.VOLATILITY_15MIN
        ])
    target_columns: List[str] = field(default_factory=lambda: [
        TechnicalIndicators.FeatureNames.TARGET
    ])


@dataclass
class MACrossoverConfig(BaseStrategyConfig):
    """Configuration class for MA Crossover Strategy."""
    short_window: int = 10
    long_window: int = 50
    feature_columns: List[str] = field(default_factory=lambda: [
        TechnicalIndicators.FeatureNames.MA_SHORT,
        TechnicalIndicators.FeatureNames.MA_LONG
    ])