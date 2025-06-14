from dataclasses import dataclass
from typing import Dict
from .base_config import BaseConfig

@dataclass
class AggregationConfig(BaseConfig):
    """Base configuration class for signal aggregators."""
    pass

@dataclass
class WeightedAverageConfig(AggregationConfig):
    """Configuration for weighted average signal aggregation."""
    weights: Dict[str, float]
    
    def __post_init__(self):
        """Validate weights and set type."""
        super().__post_init__()
        
        if not self.weights:
            raise ValueError("Weights dictionary cannot be empty")
            
        if not all(isinstance(w, (int, float)) for w in self.weights.values()):
            raise ValueError("All weights must be numeric")
            
        if not all(w >= 0 for w in self.weights.values()):
            raise ValueError("All weights must be non-negative")
            
        # Normalize weights to sum to 1.0
        total = sum(self.weights.values())
        if total == 0:
            raise ValueError("Sum of weights cannot be zero")
        self.weights = {k: v/total for k, v in self.weights.items()}