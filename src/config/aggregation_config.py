from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum

class AggregatorType(Enum):
    """
    Types of signal aggregators available.
    
    Example usage:
    ```python
    # Current implementation
    aggregator_type = AggregatorType.WEIGHTED_AVERAGE
    
    # Future implementations (commented out)
    # aggregator_type = AggregatorType.ML_BASED
    # aggregator_type = AggregatorType.VOLATILITY_ADJUSTED
    ```
    """
    WEIGHTED_AVERAGE = "weighted_average"
    # Add more aggregator types as they are implemented
    # ML_BASED = "ml_based"
    # VOLATILITY_ADJUSTED = "volatility_adjusted"

@dataclass
class AggregatorConfig:
    """
    Base configuration for signal aggregators.
    
    Example usage:
    ```python
    config = AggregatorConfig(
        type=AggregatorType.WEIGHTED_AVERAGE
    )
    ```
    """
    type: AggregatorType
    
@dataclass
class WeightedAverageConfig(AggregatorConfig):
    """
    Configuration for weighted average aggregator.
    
    Example usage:
    ```python
    config = WeightedAverageConfig(
        type=AggregatorType.WEIGHTED_AVERAGE,
        weights={
            'strategy1': 0.6,  # 60% weight for strategy1
            'strategy2': 0.4   # 40% weight for strategy2
        }
    )
    """
    weights: Dict[str, float]
    
    def __post_init__(self):
        self.type = AggregatorType.WEIGHTED_AVERAGE
        # Validate weights
        if not self.weights:
            raise ValueError("Weights dictionary cannot be empty")
        if not all(0 <= w <= 1 for w in self.weights.values()):
            raise ValueError("All weights must be between 0 and 1")
        # Normalize weights
        total = sum(self.weights.values())
        self.weights = {k: v/total for k, v in self.weights.items()}

# Add more config classes as new aggregators are implemented
# @dataclass
# class MLBasedConfig(AggregatorConfig):
#     """
#     Configuration for ML-based aggregator.
#     
#     Example usage:
#     ```python
#     config = MLBasedConfig(
#         type=AggregatorType.ML_BASED,
#         weights={
#             'strategy1': 0.6,
#             'strategy2': 0.4
#         },
#         model_path='models/signal_aggregator.pkl',
#         feature_columns=['price', 'volume', 'volatility']
#     )
#     ```
#     """
#     model_path: str
#     feature_columns: List[str]
#     
#     def __post_init__(self):
#         self.type = AggregatorType.ML_BASED
#         
# @dataclass
# class VolatilityAdjustedConfig(AggregatorConfig):
#     """
#     Configuration for volatility-adjusted aggregator.
#     
#     Example usage:
#     ```python
#     config = VolatilityAdjustedConfig(
#         type=AggregatorType.VOLATILITY_ADJUSTED,
#         weights={
#             'strategy1': 0.6,
#             'strategy2': 0.4
#         },
#         lookback_period=20,  # 20 days of historical data
#         volatility_threshold=0.02  # 2% volatility threshold
#     )
#     ```
#     """
#     lookback_period: int
#     volatility_threshold: float
#     
#     def __post_init__(self):
#         self.type = AggregatorType.VOLATILITY_ADJUSTED 