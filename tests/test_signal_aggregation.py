import pytest
from datetime import datetime
from src.execution.signal_aggregation.base_aggregator import BaseAggregator
from src.execution.signal_aggregation.weighted_average_aggregator import WeightedAverageAggregator
from src.execution.adapters.legacy_adapter import LegacyAdapter
from src.strategies.base_strategy import StrategySignal
from src.config.aggregation_config import AggregatorType, WeightedAverageConfig

def test_weighted_average_aggregator():
    """
    Test the weighted average aggregator with various signal combinations.
    
    Test cases:
    1. Numeric signals with explicit weights
    2. String signals (BUY/SELL/HOLD) with explicit weights
    3. Signals with default equal weights
    4. Empty signal set
    """
    # Create aggregator with weights
    weights = {
        'strategy1': 0.5,    # 50% weight
        'strategy2': 0.3,    # 30% weight
        'strategy3': 0.2     # 20% weight
    }
    aggregator = WeightedAverageAggregator(weights)
    
    # Test case 1: Numeric signals with explicit weights
    signals = {
        'strategy1': 1.0,    # Strong buy signal
        'strategy2': -0.5,   # Moderate sell signal
        'strategy3': 0.0     # Neutral signal
    }
    
    result = aggregator.aggregate_signals(signals)
    assert -1.0 <= result <= 1.0
    assert abs(result - 0.35) < 0.001  # 1.0*0.5 + (-0.5)*0.3 + 0.0*0.2 = 0.35
    
    # Test case 2: String signals with explicit weights
    signals = {
        'strategy1': 'BUY',   # Will be converted to 1.0
        'strategy2': 'SELL',  # Will be converted to -1.0
        'strategy3': 'HOLD'   # Will be converted to 0.0
    }
    result = aggregator.aggregate_signals(signals)
    assert -1.0 <= result <= 1.0
    assert abs(result - 0.2) < 0.001  # 1.0*0.5 + (-1.0)*0.3 + 0.0*0.2 = 0.2
    
    # Test case 3: Signals with default equal weights
    aggregator = WeightedAverageAggregator()  # No weights provided
    signals = {
        'strategy1': 1.0,
        'strategy2': -1.0
    }
    result = aggregator.aggregate_signals(signals)
    assert abs(result) < 0.001  # Should be close to 0 (equal weights)
    
    # Test case 4: Empty signal set
    result = aggregator.aggregate_signals({})
    assert result == 0.0

def test_legacy_adapter():
    """
    Test the legacy adapter with various signal combinations.
    
    Test cases:
    1. Multiple signals for same symbol
    2. Signals for different symbols
    3. Mixed signal types (BUY/SELL/HOLD)
    """
    adapter = LegacyAdapter()
    
    # Test case 1: Multiple signals for same symbol
    signals = [
        StrategySignal(
            symbol='AAPL',
            strategy='strategy1',
            action='BUY',      # Will be converted to 1.0
            confidence=0.8,    # Will be used as weight
            timestamp=datetime.now()
        ),
        StrategySignal(
            symbol='AAPL',
            strategy='strategy2',
            action='SELL',     # Will be converted to -1.0
            confidence=0.6,    # Will be used as weight
            timestamp=datetime.now()
        )
    ]
    
    result = adapter.aggregate_signals(signals)
    assert 'AAPL' in result
    assert -1.0 <= result['AAPL'] <= 1.0
    assert abs(result['AAPL'] - 0.2) < 0.001  # (1.0*0.8 + (-1.0)*0.6) / (0.8 + 0.6)
    
    # Test case 2: Signals for different symbols
    signals.append(
        StrategySignal(
            symbol='MSFT',
            strategy='strategy1',
            action='BUY',
            confidence=0.9,
            timestamp=datetime.now()
        )
    )
    
    result = adapter.aggregate_signals(signals)
    assert 'MSFT' in result
    assert result['MSFT'] == 1.0  # Single signal with confidence 0.9 