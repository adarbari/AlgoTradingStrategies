"""
Feature definitions for the trading system.
This file contains all available feature names and their metadata.
"""

from typing import List, Dict, Any, Optional
from src.data.types.data_type import DataType


class FeatureNames:
    """Constants for feature names."""
    
    # OHLCV Base Features
    OPEN = 'open'
    HIGH = 'high'
    LOW = 'low'
    CLOSE = 'close'
    VOLUME = 'volume'
    
    # Technical Indicators - Moving Averages
    SMA_20 = 'sma_20'
    SMA_50 = 'sma_50'
    SMA_200 = 'sma_200'
    EMA_20 = 'ema_20'
    EMA_50 = 'ema_50'
    EMA_200 = 'ema_200'
    
    # Technical Indicators - Momentum
    RSI_14 = 'rsi_14'
    RSI_21 = 'rsi_21'
    RSI = 'rsi'
    MACD = 'macd'
    MACD_SIGNAL = 'macd_signal'
    MACD_HIST = 'macd_hist'
    MACD_HISTOGRAM = 'macd_histogram'
    STOCH_K = 'stoch_k'
    STOCH_D = 'stoch_d'
    
    # Technical Indicators - Volatility
    ATR_14 = 'atr_14'
    ATR = 'atr'
    BOLLINGER_UPPER = 'bollinger_upper'
    BOLLINGER_LOWER = 'bollinger_lower'
    BOLLINGER_MIDDLE = 'bollinger_middle'
    BB_UPPER = 'bb_upper'
    BB_MIDDLE = 'bb_middle'
    BB_LOWER = 'bb_lower'
    
    # Technical Indicators - Volume
    VOLUME_SMA = 'volume_sma'
    VOLUME_EMA = 'volume_ema'
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
    
    # Additional Indicators
    TARGET = 'target'
    
    # Future: Order Flow Features
    # BID_VOLUME = 'bid_volume'
    # ASK_VOLUME = 'ask_volume'
    # BID_ASK_SPREAD = 'bid_ask_spread'
    
    # Future: Fundamental Features
    # PE_RATIO = 'pe_ratio'
    # MARKET_CAP = 'market_cap'
    # DIVIDEND_YIELD = 'dividend_yield'

from enum import Enum

class FeatureType(Enum):
    """Enumeration of feature types."""
    BASE = 'base'           # Raw data features (OHLCV)
    DERIVED = 'derived'     # Calculated features (technical indicators)
    
class FeatureCalculationEngineType(Enum):
    OHLCV_DERIVED ='ohlc_derived'
    ORDER_FLOW_DERIVED = 'order_flow_derived'

class FeatureMetadata:
    """Metadata for feature definitions."""
    
    @staticmethod
    def get_feature_mapping() -> Dict[str, Dict[str, Any]]:
        """
        Get the complete feature mapping.
        
        Returns:
            Dictionary mapping feature names to their metadata
        """
        return {
            # OHLCV Base Features
            FeatureNames.OPEN: {
                'feature_type': FeatureType.BASE,
                'data_type': DataType.OHLCV,
                'method': 'get_ohlcv_data',
                'description': 'Opening price',
                'category': 'price'
            },
            FeatureNames.HIGH: {
                'feature_type': FeatureType.BASE,
                'data_type': DataType.OHLCV,
                'method': 'get_ohlcv_data',
                'description': 'Highest price during the period',
                'category': 'price'
            },
            FeatureNames.LOW: {
                'feature_type': FeatureType.BASE,
                'data_type': DataType.OHLCV,
                'method': 'get_ohlcv_data',
                'description': 'Lowest price during the period',
                'category': 'price'
            },
            FeatureNames.CLOSE: {
                'feature_type': FeatureType.BASE,
                'data_type': DataType.OHLCV,
                'method': 'get_ohlcv_data',
                'description': 'Closing price',
                'category': 'price'
            },
            FeatureNames.VOLUME: {
                'feature_type': FeatureType.BASE,
                'data_type': DataType.OHLCV,
                'method': 'get_ohlcv_data',
                'description': 'Trading volume',
                'category': 'volume'
            },
            
            # Technical Indicators - Moving Averages
            FeatureNames.SMA_20: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': '20-period Simple Moving Average',
                'category': 'moving_average'
            },
            FeatureNames.SMA_50: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': '50-period Simple Moving Average',
                'category': 'moving_average'
            },
            FeatureNames.SMA_200: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': '200-period Simple Moving Average',
                'category': 'moving_average'
            },
            FeatureNames.EMA_20: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': '20-period Exponential Moving Average',
                'category': 'moving_average'
            },
            FeatureNames.EMA_50: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': '50-period Exponential Moving Average',
                'category': 'moving_average'
            },
            FeatureNames.EMA_200: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': '200-period Exponential Moving Average',
                'category': 'moving_average'
            },
            
            # Technical Indicators - Momentum
            FeatureNames.RSI_14: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': '14-period Relative Strength Index',
                'category': 'momentum'
            },
            FeatureNames.RSI_21: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': '21-period Relative Strength Index',
                'category': 'momentum'
            },
            FeatureNames.RSI: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': 'Relative Strength Index',
                'category': 'momentum'
            },
            FeatureNames.MACD: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': 'MACD line',
                'category': 'momentum'
            },
            FeatureNames.MACD_SIGNAL: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': 'MACD signal line',
                'category': 'momentum'
            },
            FeatureNames.MACD_HIST: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': 'MACD histogram',
                'category': 'momentum'
            },
            FeatureNames.MACD_HISTOGRAM: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': 'MACD histogram',
                'category': 'momentum'
            },
            FeatureNames.STOCH_K: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': 'Stochastic K',
                'category': 'momentum'
            },
            FeatureNames.STOCH_D: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': 'Stochastic D',
                'category': 'momentum'
            },
            
            # Technical Indicators - Volatility
            FeatureNames.ATR_14: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.HIGH, FeatureNames.LOW, FeatureNames.CLOSE],
                'description': '14-period Average True Range',
                'category': 'volatility'
            },
            FeatureNames.ATR: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.HIGH, FeatureNames.LOW, FeatureNames.CLOSE],
                'description': 'Average True Range',
                'category': 'volatility'
            },
            FeatureNames.BOLLINGER_UPPER: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': 'Bollinger Bands upper band',
                'category': 'volatility'
            },
            FeatureNames.BOLLINGER_LOWER: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': 'Bollinger Bands lower band',
                'category': 'volatility'
            },
            FeatureNames.BOLLINGER_MIDDLE: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': 'Bollinger Bands middle band',
                'category': 'volatility'
            },
            FeatureNames.BB_UPPER: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': 'Bollinger Bands upper band',
                'category': 'volatility'
            },
            FeatureNames.BB_MIDDLE: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': 'Bollinger Bands middle band',
                'category': 'volatility'
            },
            FeatureNames.BB_LOWER: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': 'Bollinger Bands lower band',
                'category': 'volatility'
            },
            
            # Technical Indicators - Volume
            FeatureNames.VOLUME_SMA: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.VOLUME],
                'description': 'Volume Simple Moving Average',
                'category': 'volume'
            },
            FeatureNames.VOLUME_EMA: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.VOLUME],
                'description': 'Volume Exponential Moving Average',
                'category': 'volume'
            },
            FeatureNames.VOLUME_MA_5: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.VOLUME],
                'description': '5-period Volume Moving Average',
                'category': 'volume'
            },
            FeatureNames.VOLUME_MA_15: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.VOLUME],
                'description': '15-period Volume Moving Average',
                'category': 'volume'
            },
            
            # Price Action
            FeatureNames.PRICE_CHANGE: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': 'Price change percentage',
                'category': 'price_action'
            },
            FeatureNames.VOLUME_CHANGE: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.VOLUME],
                'description': 'Volume change percentage',
                'category': 'price_action'
            },
            FeatureNames.VOLATILITY: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': 'Price volatility (rolling standard deviation)',
                'category': 'price_action'
            },
            FeatureNames.PRICE_CHANGE_5MIN: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': '5-minute price change percentage',
                'category': 'price_action'
            },
            FeatureNames.PRICE_CHANGE_15MIN: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': '15-minute price change percentage',
                'category': 'price_action'
            },
            FeatureNames.PRICE_RANGE: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.HIGH, FeatureNames.LOW, FeatureNames.CLOSE],
                'description': 'Price range as percentage of close',
                'category': 'price_action'
            },
            FeatureNames.PRICE_RANGE_MA: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.HIGH, FeatureNames.LOW, FeatureNames.CLOSE],
                'description': 'Moving average of price range',
                'category': 'price_action'
            },
            FeatureNames.VOLATILITY_5MIN: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': '5-minute volatility',
                'category': 'price_action'
            },
            FeatureNames.VOLATILITY_15MIN: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': '15-minute volatility',
                'category': 'price_action'
            },
            
            # Moving Average Crossover specific
            FeatureNames.MA_SHORT: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': 'Short-term moving average for crossover strategy',
                'category': 'moving_average'
            },
            FeatureNames.MA_LONG: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': 'Long-term moving average for crossover strategy',
                'category': 'moving_average'
            },
            
            # Additional Indicators
            FeatureNames.TARGET: {
                'feature_type': FeatureType.DERIVED,
                'feature_generation_engine_type': FeatureCalculationEngineType.OHLCV_DERIVED,
                'method': 'calculate_technical_indicators',
                'depends_on': [FeatureNames.CLOSE],
                'description': 'Target labels for machine learning (local extrema)',
                'category': 'target'
            },
        }
    
    @staticmethod
    def get_features_by_category() -> Dict[str, List[str]]:
        """
        Get features grouped by category.
        
        Returns:
            Dictionary mapping categories to feature lists
        """
        mapping = FeatureMetadata.get_feature_mapping()
        categories = {}
        
        for feature_name, metadata in mapping.items():
            category = metadata.get('category', 'other')
            if category not in categories:
                categories[category] = []
            categories[category].append(feature_name)
        
        return categories
    
    @staticmethod
    def get_base_features() -> List[str]:
        """
        Get list of base features (no dependencies).
        
        Returns:
            List of base feature names
        """
        mapping = FeatureMetadata.get_feature_mapping()
        return [name for name, metadata in mapping.items() 
                if 'depends_on' not in metadata]
    
    @staticmethod
    def get_derived_features() -> List[str]:
        """
        Get list of derived features (with dependencies).
        
        Returns:
            List of derived feature names
        """
        mapping = FeatureMetadata.get_feature_mapping()
        return [name for name, metadata in mapping.items() 
                if 'depends_on' in metadata] 