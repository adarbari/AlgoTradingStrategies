"""
Tests for trading strategies.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from unittest.mock import MagicMock, patch

from src.strategies.SingleStock.ma_crossover_strategy import MACrossoverStrategy
from src.strategies.SingleStock.random_forest_strategy import RandomForestStrategy
from src.config.strategy_config import MACrossoverConfig, RandomForestConfig
from src.features.core.feature_store import FeatureStore
from src.features import TechnicalIndicators
from src.data.types.base_types import TimeSeriesData
from src.data.types.ohlcv_types import OHLCVData
from src.data.types.data_type import DataType
from src.strategies.base_strategy import StrategySignal


@pytest.fixture
def sample_data():
    """Create sample OHLCV data for testing."""
    dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
    
    # Create TimeSeriesData with OHLCVData objects
    timestamps = [datetime.combine(date, datetime.min.time()) for date in dates]
    ohlcv_data = [
        OHLCVData(
            timestamp=timestamp,
            open=np.random.normal(150, 5),
            high=np.random.normal(155, 5),
            low=np.random.normal(145, 5),
            close=np.random.normal(150, 5),
            volume=np.random.randint(1000000, 5000000)
        )
        for timestamp in timestamps
    ]
    
    return TimeSeriesData(
        timestamps=timestamps,
        data=ohlcv_data,
        data_type=DataType.OHLCV
    )


@pytest.fixture
def mock_feature_store():
    """Create a mock feature store for testing."""
    mock_store = MagicMock(spec=FeatureStore)
    
    def mock_get_features(symbol, start_timestamp, end_timestamp):
        """Mock get_features method that returns a DataFrame with features."""
        dates = pd.date_range(start=start_timestamp, end=end_timestamp, freq='D')
        features_dict = {}
        
        # Add OHLCV columns
        features_dict['open'] = np.random.normal(150, 5, len(dates))
        features_dict['high'] = np.random.normal(155, 5, len(dates))
        features_dict['low'] = np.random.normal(145, 5, len(dates))
        features_dict['close'] = np.random.normal(150, 5, len(dates))
        features_dict['volume'] = np.random.normal(2000000, 500000, len(dates))
        
        # Add technical indicators that strategies expect (using exact names from config)
        features_dict['ma_short'] = np.random.normal(150, 2, len(dates))
        features_dict['ma_long'] = np.random.normal(148, 2, len(dates))
        features_dict['rsi_14'] = np.random.uniform(30, 70, len(dates))
        features_dict['macd'] = np.random.normal(0, 1, len(dates))
        features_dict['macd_signal'] = np.random.normal(0, 1, len(dates))
        features_dict['macd_hist'] = np.random.normal(0, 1, len(dates))
        
        # Add additional technical indicators that RandomForestStrategy expects
        features_dict['sma_20'] = np.random.normal(150, 2, len(dates))
        features_dict['sma_50'] = np.random.normal(148, 2, len(dates))
        features_dict['sma_200'] = np.random.normal(147, 2, len(dates))
        features_dict['ema_20'] = np.random.normal(150, 2, len(dates))
        features_dict['ema_50'] = np.random.normal(148, 2, len(dates))
        features_dict['ema_200'] = np.random.normal(147, 2, len(dates))
        features_dict['rsi'] = np.random.uniform(30, 70, len(dates))
        features_dict['stoch_k'] = np.random.uniform(0, 100, len(dates))
        features_dict['stoch_d'] = np.random.uniform(0, 100, len(dates))
        features_dict['bb_upper'] = np.random.normal(155, 5, len(dates))
        features_dict['bb_middle'] = np.random.normal(150, 5, len(dates))
        features_dict['bb_lower'] = np.random.normal(145, 5, len(dates))
        features_dict['atr'] = np.random.normal(5, 1, len(dates))
        features_dict['volume_ma_5'] = np.random.normal(2000000, 500000, len(dates))
        features_dict['volume_ma_15'] = np.random.normal(2000000, 500000, len(dates))
        features_dict['volume_change'] = np.random.normal(0, 0.1, len(dates))
        features_dict['price_change'] = np.random.normal(0, 0.02, len(dates))
        features_dict['price_change_5min'] = np.random.normal(0, 0.02, len(dates))
        features_dict['price_change_15min'] = np.random.normal(0, 0.02, len(dates))
        features_dict['price_range'] = np.random.normal(0.02, 0.01, len(dates))
        features_dict['price_range_ma'] = np.random.normal(0.02, 0.01, len(dates))
        features_dict['volatility'] = np.random.normal(0.02, 0.01, len(dates))
        features_dict['volatility_5min'] = np.random.normal(0.02, 0.01, len(dates))
        features_dict['volatility_15min'] = np.random.normal(0.02, 0.01, len(dates))
        
        # Add target column
        features_dict['target'] = np.random.choice([-1, 0, 1], len(dates))
        
        features = pd.DataFrame(features_dict, index=dates)
        return features
    
    def mock_get_features_at_timestamp(symbol, timestamp):
        """Mock get_features_at_timestamp method that returns a single row DataFrame."""
        features_dict = {}
        
        # Add OHLCV columns
        features_dict['open'] = np.random.normal(150, 5)
        features_dict['high'] = np.random.normal(155, 5)
        features_dict['low'] = np.random.normal(145, 5)
        features_dict['close'] = np.random.normal(150, 5)
        features_dict['volume'] = np.random.normal(2000000, 500000)
        
        # Add technical indicators that strategies expect (using exact names from config)
        features_dict['ma_short'] = np.random.normal(150, 2)
        features_dict['ma_long'] = np.random.normal(148, 2)
        features_dict['rsi_14'] = np.random.uniform(30, 70)
        features_dict['macd'] = np.random.normal(0, 1)
        features_dict['macd_signal'] = np.random.normal(0, 1)
        features_dict['macd_hist'] = np.random.normal(0, 1)
        
        # Add additional technical indicators that RandomForestStrategy expects
        features_dict['sma_20'] = np.random.normal(150, 2)
        features_dict['sma_50'] = np.random.normal(148, 2)
        features_dict['sma_200'] = np.random.normal(147, 2)
        features_dict['ema_20'] = np.random.normal(150, 2)
        features_dict['ema_50'] = np.random.normal(148, 2)
        features_dict['ema_200'] = np.random.normal(147, 2)
        features_dict['rsi'] = np.random.uniform(30, 70)
        features_dict['stoch_k'] = np.random.uniform(0, 100)
        features_dict['stoch_d'] = np.random.uniform(0, 100)
        features_dict['bb_upper'] = np.random.normal(155, 5)
        features_dict['bb_middle'] = np.random.normal(150, 5)
        features_dict['bb_lower'] = np.random.normal(145, 5)
        features_dict['atr'] = np.random.normal(5, 1)
        features_dict['volume_ma_5'] = np.random.normal(2000000, 500000)
        features_dict['volume_ma_15'] = np.random.normal(2000000, 500000)
        features_dict['volume_change'] = np.random.normal(0, 0.1)
        features_dict['price_change'] = np.random.normal(0, 0.02)
        features_dict['price_change_5min'] = np.random.normal(0, 0.02)
        features_dict['price_change_15min'] = np.random.normal(0, 0.02)
        features_dict['price_range'] = np.random.normal(0.02, 0.01)
        features_dict['price_range_ma'] = np.random.normal(0.02, 0.01)
        features_dict['volatility'] = np.random.normal(0.02, 0.01)
        features_dict['volatility_5min'] = np.random.normal(0.02, 0.01)
        features_dict['volatility_15min'] = np.random.normal(0.02, 0.01)
        
        # Add target column
        features_dict['target'] = np.random.choice([-1, 0, 1])
        
        features = pd.DataFrame([features_dict], index=[timestamp])
        return features
    
    mock_store.get_features.side_effect = mock_get_features
    mock_store.get_features_at_timestamp.side_effect = mock_get_features_at_timestamp
    return mock_store


@pytest.fixture
def ma_strategy(mock_feature_store):
    """Create a MACrossoverStrategy instance for testing."""
    config = MACrossoverConfig(
        short_window=5,
        long_window=20,
        cache_dir='tests/cache'
    )
    strategy = MACrossoverStrategy(config=config)
    strategy.feature_store = mock_feature_store
    return strategy


@pytest.fixture
def rf_strategy(mock_feature_store):
    """Create a RandomForestStrategy instance for testing."""
    config = RandomForestConfig(cache_dir='tests/cache')
    strategy = RandomForestStrategy(config=config)
    # Set the mock feature store after initialization
    strategy.feature_store = mock_feature_store
    return strategy


def test_ma_strategy_initialization(ma_strategy):
    """Test MACrossoverStrategy initialization."""
    assert ma_strategy.config.short_window == 5
    assert ma_strategy.config.long_window == 20
    assert isinstance(ma_strategy.feature_store, FeatureStore)


def test_rf_strategy_initialization(rf_strategy):
    """Test RandomForestStrategy initialization."""
    assert isinstance(rf_strategy.feature_store, FeatureStore)
    assert rf_strategy.config.n_estimators == 100
    assert rf_strategy.config.max_depth == 5


def test_ma_strategy_prepare_data(sample_data, mock_feature_store):
    """Test MA strategy data preparation."""
    ma_strategy = MACrossoverStrategy()
    ma_strategy.feature_store = mock_feature_store
    
    # Test data preparation by getting features from the feature store
    features = ma_strategy.feature_store.get_features(
        symbol='AAPL',
        start_timestamp=sample_data.timestamps[0],
        end_timestamp=sample_data.timestamps[-1]
    )
    
    # Check that features DataFrame has expected columns
    assert isinstance(features, pd.DataFrame)
    assert not features.empty
    
    # Check for the actual feature names that are in the DataFrame
    expected_features = ['ma_short', 'ma_long', 'rsi_14', 'macd', 'macd_signal', 'macd_hist']
    for feature in expected_features:
        assert feature in features.columns, f"Feature {feature} not found in DataFrame"


def test_rf_strategy_prepare_data(rf_strategy, sample_data):
    """Test RandomForestStrategy data preparation."""
    rf_strategy.train_model(sample_data, 'AAPL')
    features = rf_strategy.feature_store.get_features(
        symbol='AAPL',
        start_timestamp=sample_data.timestamps[0],
        end_timestamp=sample_data.timestamps[-1]
    )
    assert isinstance(features, pd.DataFrame)
    assert len(features) > 0
    assert 'target' in features.columns
    assert rf_strategy.model is not None


def test_ma_strategy_generate_signals(ma_strategy, sample_data):
    """Test MACrossoverStrategy signal generation."""
    ma_strategy.train_model(sample_data, 'AAPL')
    features = ma_strategy.feature_store.get_features(
        symbol='AAPL',
        start_timestamp=sample_data.timestamps[0],
        end_timestamp=sample_data.timestamps[-1]
    )
    
    # Create a proper features dict for signal generation
    current_features = {
        'open': 150.0,
        'high': 155.0,
        'low': 145.0,
        'close': 150.5,
        'volume': 2000000,
        'ma_short': 150.2,
        'ma_long': 148.8,
        'rsi_14': 55.0,
        'macd': 0.5,
        'macd_signal': 0.3
    }
    
    signals = ma_strategy.generate_signals(current_features, 'AAPL', datetime.now())
    assert isinstance(signals, StrategySignal)
    assert hasattr(signals, 'timestamp')
    assert hasattr(signals, 'symbol')
    assert hasattr(signals, 'features')
    assert hasattr(signals, 'probabilities')
    assert hasattr(signals, 'confidence')
    probs = signals.probabilities
    assert 'BUY' in probs
    assert 'SELL' in probs
    assert 'HOLD' in probs
    assert sum(probs.values()) == pytest.approx(1.0)


def test_rf_strategy_generate_signals(rf_strategy, sample_data):
    """Test RandomForestStrategy signal generation."""
    rf_strategy.train_model(sample_data, 'AAPL')
    features = rf_strategy.feature_store.get_features(
        symbol='AAPL',
        start_timestamp=sample_data.timestamps[0],
        end_timestamp=sample_data.timestamps[-1]
    )
    
    # Create a proper features dict for signal generation
    current_features = {
        'open': 150.0,
        'high': 155.0,
        'low': 145.0,
        'close': 150.5,
        'volume': 2000000,
        'ma_short': 150.2,
        'ma_long': 148.8,
        'rsi_14': 55.0,
        'macd': 0.5,
        'macd_signal': 0.3
    }
    
    signals = rf_strategy.generate_signals(current_features, 'AAPL', datetime.now())
    assert isinstance(signals, StrategySignal)
    assert hasattr(signals, 'timestamp')
    assert hasattr(signals, 'symbol')
    assert hasattr(signals, 'features')
    assert hasattr(signals, 'probabilities')
    assert hasattr(signals, 'confidence')
    probs = signals.probabilities
    assert 'BUY' in probs
    assert 'SELL' in probs
    assert 'HOLD' in probs
    assert sum(probs.values()) == pytest.approx(1.0)


def test_ma_strategy_update(ma_strategy, sample_data):
    """Test MACrossoverStrategy update."""
    ma_strategy.train_model(sample_data, 'AAPL')
    
    # Create new data as TimeSeriesData
    new_dates = pd.date_range(start='2023-01-11', end='2023-01-15', freq='D')
    new_timestamps = [datetime.combine(date, datetime.min.time()) for date in new_dates]
    new_ohlcv_data = [
        OHLCVData(
            timestamp=timestamp,
            open=np.random.normal(150, 5),
            high=np.random.normal(155, 5),
            low=np.random.normal(145, 5),
            close=np.random.normal(150, 5),
            volume=np.random.randint(1000000, 5000000)
        )
        for timestamp in new_timestamps
    ]
    
    new_data = TimeSeriesData(
        timestamps=new_timestamps,
        data=new_ohlcv_data,
        data_type=DataType.OHLCV
    )
    
    ma_strategy.update(new_data, 'AAPL')
    ma_strategy.train_model(new_data, 'AAPL')
    
    features = ma_strategy.feature_store.get_features(
        symbol='AAPL',
        start_timestamp=new_data.timestamps[0],
        end_timestamp=new_data.timestamps[-1]
    )
    
    # Create a proper features dict for signal generation
    current_features = {
        'open': 150.0,
        'high': 155.0,
        'low': 145.0,
        'close': 150.5,
        'volume': 2000000,
        'ma_short': 150.2,
        'ma_long': 148.8,
        'rsi_14': 55.0,
        'macd': 0.5,
        'macd_signal': 0.3
    }
    
    signals = ma_strategy.generate_signals(current_features, 'AAPL', datetime.now())
    assert isinstance(signals, StrategySignal)


def test_rf_strategy_update(rf_strategy, sample_data):
    """Test RandomForestStrategy update."""
    # Add a dummy target column for the test
    sample_data_with_target = sample_data
    rf_strategy.train_model(sample_data_with_target, 'AAPL')
    
    # Create new data as TimeSeriesData
    new_dates = pd.date_range(start='2023-01-11', end='2023-01-15', freq='D')
    new_timestamps = [datetime.combine(date, datetime.min.time()) for date in new_dates]
    new_ohlcv_data = [
        OHLCVData(
            timestamp=timestamp,
            open=np.random.normal(150, 5),
            high=np.random.normal(155, 5),
            low=np.random.normal(145, 5),
            close=np.random.normal(150, 5),
            volume=np.random.randint(1000000, 5000000)
        )
        for timestamp in new_timestamps
    ]
    
    new_data = TimeSeriesData(
        timestamps=new_timestamps,
        data=new_ohlcv_data,
        data_type=DataType.OHLCV
    )
    
    rf_strategy.update(new_data, 'AAPL')
    rf_strategy.train_model(new_data, 'AAPL')
    
    features = rf_strategy.feature_store.get_features(
        symbol='AAPL',
        start_timestamp=new_data.timestamps[0],
        end_timestamp=new_data.timestamps[-1]
    )
    
    # Create a proper features dict for signal generation
    current_features = {
        'open': 150.0,
        'high': 155.0,
        'low': 145.0,
        'close': 150.5,
        'volume': 2000000,
        'ma_short': 150.2,
        'ma_long': 148.8,
        'rsi_14': 55.0,
        'macd': 0.5,
        'macd_signal': 0.3
    }
    
    signals = rf_strategy.generate_signals(current_features, 'AAPL', datetime.now())
    assert isinstance(signals, StrategySignal)


def test_ma_strategy_parameters(ma_strategy):
    """Test MACrossoverStrategy parameter management."""
    # Get current parameters
    params = ma_strategy.get_parameters()
    assert 'short_window' in params
    assert 'long_window' in params
    
    # Set new parameters
    new_params = {
        'short_window': 10,
        'long_window': 30
    }
    ma_strategy.set_parameters(new_params)
    assert ma_strategy.config.short_window == 10
    assert ma_strategy.config.long_window == 30


def test_rf_strategy_parameters(rf_strategy):
    """Test RandomForestStrategy parameter management."""
    # Get current parameters
    params = rf_strategy.get_parameters()
    assert 'n_estimators' in params
    assert 'max_depth' in params
    
    # Set new parameters
    new_params = {
        'n_estimators': 200,
        'max_depth': 10
    }
    rf_strategy.set_parameters(new_params)
    assert rf_strategy.config.n_estimators == 200
    assert rf_strategy.config.max_depth == 10 