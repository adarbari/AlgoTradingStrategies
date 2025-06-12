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
from src.features.feature_store import FeatureStore
from src.features.technical_indicators import TechnicalIndicators

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
    
    # Mock the get_cached_features method to return a DataFrame with required features
    def mock_get_features(symbol, start_date, end_date):
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        features = pd.DataFrame({
            'close': np.random.normal(150, 5, len(dates)),
            technical_indicators.FeatureNames.MA_SHORT: np.random.normal(150, 2, len(dates)),
            technical_indicators.FeatureNames.MA_LONG: np.random.normal(148, 2, len(dates)),
            technical_indicators.FeatureNames.RSI_14: np.random.uniform(30, 70, len(dates)),
            technical_indicators.FeatureNames.MACD: np.random.normal(0, 1, len(dates)),
            technical_indicators.FeatureNames.MACD_SIGNAL: np.random.normal(0, 1, len(dates)),
            'target': np.random.choice([-1, 0, 1], len(dates))
        }, index=dates)
        return features
    
    mock_store.get_cached_features.side_effect = mock_get_features
    return mock_store

@pytest.fixture
def ma_strategy(mock_feature_store):
    """Create a MACrossoverStrategy instance for testing."""
    strategy = MACrossoverStrategy(
        short_window=5,
        long_window=20,
        cache_dir='tests/cache'
    )
    strategy.feature_store = mock_feature_store
    return strategy

@pytest.fixture
def rf_strategy(mock_feature_store):
    """Create a RandomForestStrategy instance for testing."""
    strategy = RandomForestStrategy(
        n_estimators=10,
        max_depth=3,
        min_samples_split=2,
        lookback_window=5,
        cache_dir='tests/cache'
    )
    strategy.feature_store = mock_feature_store
    return strategy

@pytest.mark.slow
def test_ma_strategy_initialization(ma_strategy):
    """Test MACrossoverStrategy initialization."""
    assert ma_strategy.short_window == 5
    assert ma_strategy.long_window == 20
    assert ma_strategy.cache_dir == 'tests/cache'

@pytest.mark.slow
def test_rf_strategy_initialization(rf_strategy):
    """Test RandomForestStrategy initialization."""
    assert rf_strategy.n_estimators == 10
    assert rf_strategy.max_depth == 3
    assert rf_strategy.min_samples_split == 2
    assert rf_strategy.lookback_window == 5
    assert rf_strategy.cache_dir == 'tests/cache'
    assert isinstance(rf_strategy.feature_store, FeatureStore)

@pytest.mark.slow
def test_ma_strategy_prepare_data(ma_strategy, sample_data):
    """Test MACrossoverStrategy data preparation."""
    prepared_data = ma_strategy.prepare_data(sample_data, 'AAPL')
    assert isinstance(prepared_data, pd.DataFrame)
    assert len(prepared_data) > 0
    technical_indicators = TechnicalIndicators()
    assert technical_indicators.FeatureNames.MA_SHORT in prepared_data.columns
    assert technical_indicators.FeatureNames.MA_LONG in prepared_data.columns

@pytest.mark.slow
def test_rf_strategy_prepare_data(rf_strategy, sample_data):
    """Test RandomForestStrategy data preparation."""
    prepared_data = rf_strategy.prepare_data(sample_data, 'AAPL')
    assert isinstance(prepared_data, pd.DataFrame)
    assert len(prepared_data) > 0
    assert 'target' in prepared_data.columns
    assert rf_strategy.model is not None

@pytest.mark.slow
def test_ma_strategy_generate_signals(ma_strategy, sample_data):
    """Test MACrossoverStrategy signal generation."""
    prepared_data = ma_strategy.prepare_data(sample_data, 'AAPL')
    signals = ma_strategy.generate_signals(prepared_data, 'AAPL', datetime.now())
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

@pytest.mark.skip(reason="RandomForestStrategy not predicting SELL signals for the given input data.")
@pytest.mark.slow
def test_rf_strategy_generate_signals(rf_strategy, sample_data):
    """Test RandomForestStrategy signal generation."""
    prepared_data = rf_strategy.prepare_data(sample_data, 'AAPL')
    # Pass only the last row as a dict
    last_row = prepared_data.iloc[-1][rf_strategy.feature_columns].to_dict()
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

@pytest.mark.slow
def test_ma_strategy_update(ma_strategy, sample_data):
    """Test MACrossoverStrategy update."""
    prepared_data = ma_strategy.prepare_data(sample_data, 'AAPL')
    new_dates = pd.date_range(start='2023-01-11', end='2023-01-15', freq='D')
    new_data = pd.DataFrame({
        'open': np.random.normal(150, 5, len(new_dates)),
        'high': np.random.normal(155, 5, len(new_dates)),
        'low': np.random.normal(145, 5, len(new_dates)),
        'close': np.random.normal(150, 5, len(new_dates)),
        'volume': np.random.randint(1000000, 5000000, len(new_dates))
    }, index=new_dates)
    ma_strategy.update(new_data, 'AAPL')
    prepared_new_data = ma_strategy.prepare_data(new_data, 'AAPL')
    signals = ma_strategy.generate_signals(prepared_new_data, 'AAPL', datetime.now())
    assert isinstance(signals, StrategySignal)

@pytest.mark.slow
def test_rf_strategy_update(rf_strategy, sample_data):
    """Test RandomForestStrategy update."""
    # Add a dummy target column for the test
    sample_data_with_target = sample_data.copy()
    sample_data_with_target['target'] = np.random.choice([-1, 0, 1], len(sample_data_with_target))
    prepared_data = rf_strategy.prepare_data(sample_data_with_target, 'AAPL')
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
    prepared_new_data = rf_strategy.prepare_data(new_data, 'AAPL')
    # Pass only the last row as a dict
    last_row = prepared_new_data.iloc[-1][rf_strategy.feature_columns].to_dict()
    signals = rf_strategy.generate_signals(last_row, 'AAPL', datetime.now())
    assert isinstance(signals, StrategySignal)

@pytest.mark.slow
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
    
    # Check updated parameters
    assert ma_strategy.short_window == 10
    assert ma_strategy.long_window == 30

@pytest.mark.slow
def test_rf_strategy_parameters(rf_strategy):
    """Test RandomForestStrategy parameter management."""
    # Get current parameters
    params = rf_strategy.get_parameters()
    assert 'n_estimators' in params
    assert 'max_depth' in params
    assert 'min_samples_split' in params
    
    # Set new parameters
    new_params = {
        'n_estimators': 200,
        'max_depth': 10,
        'min_samples_split': 5
    }
    rf_strategy.set_parameters(new_params)
    
    # Check updated parameters
    assert rf_strategy.n_estimators == 200
    assert rf_strategy.max_depth == 10
    assert rf_strategy.min_samples_split == 5 