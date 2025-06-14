from typing import Dict, Optional
from datetime import datetime
from .base_aggregator import BaseAggregator
from src.strategies.base_strategy import StrategySignal

class WeightedAverageAggregator(BaseAggregator):
    """
    Aggregates signals using weighted average based on strategy confidence.
    
    This aggregator combines multiple trading signals by computing their weighted average.
    The weights determine the relative importance of each strategy's signal.
    
    Class Variables:
        weights: Dict[str, float]
            Dictionary mapping strategy names to their weights
            Example: {
                'ma_crossover': 0.5,     # 50% weight for MA strategy
                'random_forest': 0.5,    # 50% weight for RF strategy
            }
            Constraints:
            - Keys must be strategy names (strings)
            - Values must be non-negative
            - Sum of weights should be 1.0 (will be normalized)
    
    Example usage:
    ```python
    # Create aggregator with weights
    weights = {
        'ma_crossover': 0.5,     # 50% weight for MA strategy
        'random_forest': 0.5,    # 50% weight for RF strategy
    }
    aggregator = WeightedAverageAggregator(weights)
    
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
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize the weighted average aggregator.
        
        Args:
            weights: Optional dictionary mapping strategy names to their weights
                    Type: Dict[str, float]
                    Example: {
                        'ma_crossover': 0.5,     # 50% weight for MA strategy
                        'random_forest': 0.5,    # 50% weight for RF strategy
                    }
                    Constraints:
                    - Keys must be strategy names (strings)
                    - Values must be non-negative
                    - Sum of weights should be 1.0 (will be normalized)
        """
        self.weights = weights
        
    def _validate_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """
        Validate and normalize weights to sum to 1.
        This is specific to weighted average aggregation.
        
        Args:
            weights: Dictionary mapping strategy names to their weights
                    Type: Dict[str, float]
                    Example: {
                        'ma_crossover': 0.6,    # 60% weight for MA strategy
                        'random_forest': 0.4,    # 40% weight for RF strategy
                    }
                    Constraints:
                    - Must be a non-empty dictionary
                    - Keys must be strategy names (strings)
                    - Values must be non-negative
                    - At least one weight must be positive
            
        Returns:
            Dict[str, float]: Normalized weights that sum to 1
                            Example: {
                                'ma_crossover': 0.6,    # 60% after normalization
                                'random_forest': 0.4,   # 40% after normalization
                            }
                            
        Raises:
            ValueError: If weights have invalid structure or values
                      Examples:
                      - "Weights must be a dictionary, got <class 'list'>"
                      - "Weights dictionary cannot be empty"
                      - "Strategy name must be a string, got <class 'int'>"
                      - "Weight for ma_crossover must be numeric, got <class 'str'>"
                      - "Weight for random_forest must be non-negative, got -0.3"
        """
        if not isinstance(weights, dict):
            raise ValueError(f"Weights must be a dictionary, got {type(weights)}")
            
        if not weights:
            raise ValueError("Weights dictionary cannot be empty")
            
        for strategy, weight in weights.items():
            if not isinstance(strategy, str):
                raise ValueError(f"Strategy name must be a string, got {type(strategy)}")
                
            if not isinstance(weight, (int, float)):
                raise ValueError(f"Weight for {strategy} must be numeric, got {type(weight)}")
                
            if weight < 0:
                raise ValueError(f"Weight for {strategy} must be non-negative, got {weight}")
        
        total = sum(weights.values())
        if total == 0:
            return {k: 1.0/len(weights) for k in weights}
            
        return {k: v/total for k, v in weights.items()}
        
    def aggregate_signals(self, signals: Dict[str, StrategySignal]) -> StrategySignal:
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
                    - All strategy names must match the weights dictionary
            
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
        # Validate input signals
        self.validate_signals(signals)
            
        # If no weights provided, use equal weights
        if not self.weights:
            self.weights = {strategy: 1.0/len(signals) for strategy in signals}
            
        # Validate and normalize weights
        normalized_weights = self._validate_weights(self.weights)
        
        # Check that all strategies in signals have weights
        for strategy in signals:
            if strategy not in normalized_weights:
                raise ValueError(f"Strategy {strategy} not found in weights")
        
        # Get the symbol from the first signal (all signals should be for the same symbol)
        symbol = next(iter(signals.values())).symbol
        
        # Calculate weighted probabilities
        weighted_probs = {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 0.0}
        weighted_confidence = 0.0
        
        for strategy, signal in signals.items():
            weight = normalized_weights[strategy]
            for action, prob in signal.probabilities.items():
                weighted_probs[action] += prob * weight
            weighted_confidence += signal.confidence * weight
        
        # Determine the action with highest probability
        action = max(weighted_probs.items(), key=lambda x: x[1])[0]
        
        # Create aggregated signal
        return StrategySignal(
            symbol=symbol,
            action=action,
            probabilities=weighted_probs,
            confidence=weighted_confidence,
            timestamp=datetime.now(),
            features={}  # Features are not aggregated
        ) 