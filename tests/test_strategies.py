"""
Tests for the strategy classes.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.strategies.base_strategy import BaseStrategy, StrategySignal
from src.strategies.SingleStock.ma_crossover_strategy import MACrossoverStrategy
from src.strategies.SingleStock.random_forest_strategy import RandomForestStrategy
from src.features.core.feature_store import FeatureStore
from src.features.implementations.technical_indicators import TechnicalIndicators
from src.config.strategy_config import MACrossoverConfig, RandomForestConfig

@pytest.fixture
def sample_data():
    """Create sample price data for testing."""
    dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
    data = pd.DataFrame({
        'open': np.random.normal(150, 5, len(dates)),
        'high': np.random.normal(155, 5, len(dates)),
        'low': np.random.normal(145, 5, len(dates)),
        'close': np.random.normal(150, 5, len(dates)),
        'volume': np.random.randint(1000000, 5000000, len(dates)),
        'target': np.random.choice([-1, 0, 1], len(dates))
    }, index=dates)
    return data

@pytest.fixture
def mock_feature_store():
    """Create a mock FeatureStore for testing."""
    mock_store = Mock(spec=FeatureStore)
    technical_indicators = TechnicalIndicators()
    def mock_get_features(symbol, data, start_date, end_date):
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        rf_strategy = RandomForestStrategy()
        features_dict = {}
        for feature in rf_strategy.feature_columns:
            # Use random values for numeric features
            if feature in ['open', 'high', 'low', 'close', 'volume']:
                features_dict[feature] = np.random.normal(150, 5, len(dates))
            else:
                features_dict[feature] = np.random.normal(0, 1, len(dates))
        features_dict['target'] = np.random.choice([-1, 0, 1], len(dates))
        features = pd.DataFrame(features_dict, index=dates)
        return features
    mock_store.get_features.side_effect = mock_get_features
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

def test_ma_strategy_prepare_data(ma_strategy, sample_data):
    """Test MACrossoverStrategy data preparation."""
    ma_strategy.train_model(sample_data, 'AAPL')
    features = ma_strategy.feature_store.get_features(
        symbol='AAPL',
        data=sample_data,
        start_date=sample_data.index.min().strftime('%Y-%m-%d'),
        end_date=sample_data.index.max().strftime('%Y-%m-%d')
    )
    assert isinstance(features, pd.DataFrame)
    assert len(features) > 0
    technical_indicators = TechnicalIndicators()
    assert technical_indicators.FeatureNames.MA_SHORT in features.columns
    assert technical_indicators.FeatureNames.MA_LONG in features.columns

def test_rf_strategy_prepare_data(rf_strategy, sample_data):
    """Test RandomForestStrategy data preparation."""
    rf_strategy.train_model(sample_data, 'AAPL')
    features = rf_strategy.feature_store.get_features(
        symbol='AAPL',
        data=sample_data,
        start_date=sample_data.index.min().strftime('%Y-%m-%d'),
        end_date=sample_data.index.max().strftime('%Y-%m-%d')
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
        data=sample_data,
        start_date=sample_data.index.min().strftime('%Y-%m-%d'),
        end_date=sample_data.index.max().strftime('%Y-%m-%d')
    )
    signals = ma_strategy.generate_signals(features.iloc[-1].to_dict(), 'AAPL', datetime.now())
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
        data=sample_data,
        start_date=sample_data.index.min().strftime('%Y-%m-%d'),
        end_date=sample_data.index.max().strftime('%Y-%m-%d')
    )
    # Pass only the last row as a dict, excluding 'close' and 'target'
    last_row = features.iloc[-1].drop(['target']).to_dict()
    signals = rf_strategy.generate_signals(last_row, 'AAPL', datetime.now())
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
    new_dates = pd.date_range(start='2023-01-11', end='2023-01-15', freq='D')
    new_data = pd.DataFrame({
        'open': np.random.normal(150, 5, len(new_dates)),
        'high': np.random.normal(155, 5, len(new_dates)),
        'low': np.random.normal(145, 5, len(new_dates)),
        'close': np.random.normal(150, 5, len(new_dates)),
        'volume': np.random.randint(1000000, 5000000, len(new_dates))
    }, index=new_dates)
    ma_strategy.update(new_data, 'AAPL')
    ma_strategy.train_model(new_data, 'AAPL')
    features = ma_strategy.feature_store.get_features(
        symbol='AAPL',
        data=new_data,
        start_date=new_data.index.min().strftime('%Y-%m-%d'),
        end_date=new_data.index.max().strftime('%Y-%m-%d')
    )
    signals = ma_strategy.generate_signals(features.iloc[-1].to_dict(), 'AAPL', datetime.now())
    assert isinstance(signals, StrategySignal)

def test_rf_strategy_update(rf_strategy, sample_data):
    """Test RandomForestStrategy update."""
    # Add a dummy target column for the test
    sample_data_with_target = sample_data.copy()
    sample_data_with_target['target'] = np.random.choice([-1, 0, 1], len(sample_data_with_target))
    rf_strategy.train_model(sample_data_with_target, 'AAPL')
    new_dates = pd.date_range(start='2023-01-11', end='2023-01-15', freq='D')
    new_data = pd.DataFrame({
        'open': np.random.normal(150, 5, len(new_dates)),
        'high': np.random.normal(155, 5, len(new_dates)),
        'low': np.random.normal(145, 5, len(new_dates)),
        'close': np.random.normal(150, 5, len(new_dates)),
        'volume': np.random.randint(1000000, 5000000, len(new_dates)),
        'target': np.random.choice([-1, 0, 1], len(new_dates))
    }, index=new_dates)
    rf_strategy.update(new_data, 'AAPL')
    rf_strategy.train_model(new_data, 'AAPL')
    features = rf_strategy.feature_store.get_features(
        symbol='AAPL',
        data=new_data,
        start_date=new_data.index.min().strftime('%Y-%m-%d'),
        end_date=new_data.index.max().strftime('%Y-%m-%d')
    )
    # Pass only the last row as a dict, excluding 'close' and 'target'
    last_row = features.iloc[-1].drop(['target']).to_dict()
    signals = rf_strategy.generate_signals(last_row, 'AAPL', datetime.now())
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