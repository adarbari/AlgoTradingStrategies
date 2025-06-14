from typing import Dict
from datetime import datetime

from src.config.base_enums import StrategyType
from .base_aggregator import BaseAggregator
from src.strategies.base_strategy import StrategySignal
from src.config.aggregation_config import WeightedAverageConfig
from src.config.base_enums import StrategyType

class WeightedAverageAggregator(BaseAggregator):
    """
    Aggregates signals using weighted average based on strategy confidence.
    
    This aggregator combines multiple trading signals by computing their weighted average.
    The weights determine the relative importance of each strategy's signal.
    
    Class Variables:
        config: WeightedAverageConfig
            Configuration for the weighted average aggregator
            Example: WeightedAverageConfig(
                weights={
                    'ma_crossover': 0.5,     # 50% weight for MA strategy
                    'random_forest': 0.5,    # 50% weight for RF strategy
                }
            )
            Constraints:
            - Weights must be non-negative
            - Weights will be normalized to sum to 1.0
    
    Example usage:
    ```python
    # Create aggregator with config
    config = WeightedAverageConfig(
        weights={
            'ma_crossover': 0.5,     # 50% weight for MA strategy
            'random_forest': 0.5,    # 50% weight for RF strategy
        }
    )
    aggregator = WeightedAverageAggregator(config)
    
    # Aggregate signals
    signals = {
        'ma_crossover': StrategySignal(
            symbol='AAPL',
            action='BUY',
            probabilities={'BUY': 0.8, 'SELL': 0.1, 'HOLD': 0.1},
            confidence=0.8,
            timestamp=datetime.now(),
            features={...}
        ),
        'random_forest': StrategySignal(
            symbol='AAPL',
            action='SELL',
            probabilities={'BUY': 0.2, 'SELL': 0.7, 'HOLD': 0.1},
            confidence=0.7,
            timestamp=datetime.now(),
            features={...}
        )
    }
    result = aggregator.aggregate_signals(signals)
    # result will be a StrategySignal with weighted probabilities
    ```
    """
    
    def __init__(self, config: WeightedAverageConfig):
        """
        Initialize the weighted average aggregator.
        
        Args:
            config: Configuration for the weighted average aggregator
                   Type: WeightedAverageConfig
                   Example: WeightedAverageConfig(
                       weights={
                           'ma_crossover': 0.5,     # 50% weight for MA strategy
                           'random_forest': 0.5,    # 50% weight for RF strategy
                       }
                   )
                   Constraints:
                   - Weights must be non-negative
                   - Weights will be normalized to sum to 1.0
        """
        super().__init__(config)
        self.config: WeightedAverageConfig = config
        
    def aggregate_signals(self, signals: Dict[StrategyType, StrategySignal]) -> StrategySignal:
        """
        Aggregate signals using weighted average.
        
        Args:
            signals: Dictionary mapping strategy names to their signals
                    Type: Dict[str, StrategySignal]
                    Example: {
                        'ma_crossover': StrategySignal(
                            symbol='AAPL',
                            action='BUY',
                            probabilities={'BUY': 0.8, 'SELL': 0.1, 'HOLD': 0.1},
                            confidence=0.8,
                            timestamp=datetime.now(),
                            features={...}
                        ),
                        'random_forest': StrategySignal(...)
                    }
                    Constraints:
                    - Must be a non-empty dictionary
                    - Keys must be strategy names (strings)
                    - Values must be valid StrategySignal objects
                    - All signals must be for the same symbol
                    - All strategy names must match the weights in config
            
        Returns:
            StrategySignal: Aggregated signal object
                          Example: StrategySignal(
                              symbol='AAPL',
                              action='BUY',
                              probabilities={'BUY': 0.65, 'SELL': 0.2, 'HOLD': 0.15},
                              confidence=0.65,
                              timestamp=datetime.now(),
                              features={...}
                          )
                  
        Example calculation:
        For two strategies with equal weights (0.5 each):
        - ma_crossover: {'BUY': 0.8, 'SELL': 0.1, 'HOLD': 0.1} * 0.5
        - random_forest: {'BUY': 0.5, 'SELL': 0.3, 'HOLD': 0.2} * 0.5
        - Final probabilities: {'BUY': 0.65, 'SELL': 0.2, 'HOLD': 0.15}
        
        Raises:
            ValueError: If signals have invalid structure or values
                      Examples:
                      - "Signals must be a dictionary, got <class 'list'>"
                      - "Signal for ma_crossover must be a StrategySignal object, got <class 'dict'>"
                      - "Strategy ma_crossover not found in weights"
        """
        self.validate_signals(signals)
        weights = self.config.weights
        for strategy in signals:
            if strategy not in weights.keys():
                raise ValueError(f"Strategy {strategy} not found in weights")
        symbol = next(iter(signals.values())).symbol
        weighted_probs = {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 0.0}
        weighted_confidence = 0.0
        for strategy, signal in signals.items():
            weight = weights[strategy]
            for action, prob in signal.probabilities.items():
                weighted_probs[action] += prob * weight
            weighted_confidence += signal.confidence * weight
        action = max(weighted_probs.items(), key=lambda x: x[1])[0]
        return StrategySignal(
            symbol=symbol,
            action=action,
            probabilities=weighted_probs,
            confidence=weighted_confidence,
            timestamp=datetime.now(),
            features={}
        ) 