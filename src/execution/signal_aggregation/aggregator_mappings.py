from typing import Dict, Type
from src.execution.signal_aggregation.weighted_average_aggregator import WeightedAverageAggregator
from src.config.base_enums import AggregatorType

# Mapping of aggregator types to their implementation classes
AGGREGATOR_CLASSES = {
    AggregatorType.WEIGHTED_AVERAGE: WeightedAverageAggregator
}

# The mapping of aggregator types to their classes can be created at runtime where needed. 