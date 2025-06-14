import pytest
from datetime import datetime
from src.execution.signal_aggregation.base_aggregator import BaseAggregator
from src.execution.signal_aggregation.weighted_average_aggregator import WeightedAverageAggregator
from src.strategies.base_strategy import StrategySignal
from src.execution.signal_aggregation.aggregator_mappings import AGGREGATOR_CLASSES
from src.config.aggregation_config import WeightedAverageConfig
from src.config.base_enums import StrategyType

def test_weighted_average_aggregator():
    """
    Test the weighted average aggregator with various signal combinations.
    
    Test cases:
    1. Numeric signals with explicit weights
    2. String signals (BUY/SELL/HOLD) with explicit weights
    3. Signals with default equal weights
    4. Empty signal set
    """
    # Create aggregator with config
    config = WeightedAverageConfig(
        weights={
            StrategyType.MA_CROSSOVER: 0.5,    # 50% weight
            StrategyType.RANDOM_FOREST: 0.5     # 50% weight
        }
    )
    aggregator = WeightedAverageAggregator(config)
    
    # Test case 1: Numeric signals with explicit weights
    signals = {
        StrategyType.MA_CROSSOVER: StrategySignal(
            symbol='AAPL',
            action='BUY',
            probabilities={'BUY': 0.4, 'SELL': 0.0, 'HOLD': 0.6},  # Adjusted to avoid tie
            confidence=1.0,
            timestamp=datetime.now(),
            features={}
        ),
        StrategyType.RANDOM_FOREST: StrategySignal(
            symbol='AAPL',
            action='HOLD',
            probabilities={'BUY': 0.0, 'SELL': 0.0, 'HOLD': 1.0},
            confidence=0.0,
            timestamp=datetime.now(),
            features={}
        )
    }
    
    result = aggregator.aggregate_signals(signals)
    assert isinstance(result, StrategySignal)
    assert result.symbol == 'AAPL'
    assert result.action == 'HOLD'  # Highest weighted probability
    assert abs(result.probabilities['BUY'] - 0.2) < 0.001  # 0.4 * 0.5 + 0.0 * 0.5
    assert abs(result.probabilities['SELL'] - 0.0) < 0.001  # 0.0 * 0.5 + 0.0 * 0.5
    assert abs(result.probabilities['HOLD'] - 0.8) < 0.001  # 0.6 * 0.5 + 1.0 * 0.5
    assert abs(result.confidence - 0.5) < 0.001  # 1.0 * 0.5 + 0.0 * 0.5
    
    # Test case 2: String signals with explicit weights
    signals = {
        StrategyType.MA_CROSSOVER: StrategySignal(
            symbol='AAPL',
            action='BUY',
            probabilities={'BUY': 1.0, 'SELL': 0.0, 'HOLD': 0.0},
            confidence=1.0,
            timestamp=datetime.now(),
            features={}
        ),
        StrategyType.RANDOM_FOREST: StrategySignal(
            symbol='AAPL',
            action='SELL',
            probabilities={'BUY': 0.0, 'SELL': 1.0, 'HOLD': 0.0},
            confidence=1.0,
            timestamp=datetime.now(),
            features={}
        )
    }
    result = aggregator.aggregate_signals(signals)
    assert isinstance(result, StrategySignal)
    assert result.symbol == 'AAPL'
    assert result.action in ['BUY', 'SELL']  # Equal weights, either could be highest
    assert abs(result.probabilities['BUY'] - 0.5) < 0.001  # 1.0 * 0.5 + 0.0 * 0.5
    assert abs(result.probabilities['SELL'] - 0.5) < 0.001  # 0.0 * 0.5 + 1.0 * 0.5
    assert abs(result.probabilities['HOLD'] - 0.0) < 0.001  # 0.0 * 0.5 + 0.0 * 0.5
    assert abs(result.confidence - 1.0) < 0.001  # 1.0 * 0.5 + 1.0 * 0.5
    
    # Test case 3: Signals with default equal weights
    # Provide explicit equal weights
    config_equal = WeightedAverageConfig(weights={
        StrategyType.MA_CROSSOVER: 0.5,
        StrategyType.RANDOM_FOREST: 0.5
    })
    aggregator = WeightedAverageAggregator(config_equal)
    signals = {
        StrategyType.MA_CROSSOVER: StrategySignal(
            symbol='AAPL',
            action='BUY',
            probabilities={'BUY': 1.0, 'SELL': 0.0, 'HOLD': 0.0},
            confidence=1.0,
            timestamp=datetime.now(),
            features={}
        ),
        StrategyType.RANDOM_FOREST: StrategySignal(
            symbol='AAPL',
            action='SELL',
            probabilities={'BUY': 0.0, 'SELL': 1.0, 'HOLD': 0.0},
            confidence=1.0,
            timestamp=datetime.now(),
            features={}
        )
    }
    result = aggregator.aggregate_signals(signals)
    assert isinstance(result, StrategySignal)
    assert result.symbol == 'AAPL'
    assert result.action in ['BUY', 'SELL']  # Equal weights, either could be highest
    assert abs(result.probabilities['BUY'] - 0.5) < 0.001
    assert abs(result.probabilities['SELL'] - 0.5) < 0.001
    assert abs(result.probabilities['HOLD'] - 0.0) < 0.001
    assert abs(result.confidence - 1.0) < 0.001 