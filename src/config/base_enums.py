from enum import Enum

class StockTicker(str): # type: ignore
    """A custom string type that inherits from str."""
    pass

class StrategyType(Enum):
    """Enum for strategy types."""
    MA_CROSSOVER = 'ma_crossover'
    RANDOM_FOREST = 'random_forest'

class AggregatorType(Enum):
    """Enum for aggregator types."""
    WEIGHTED_AVERAGE = 'weighted_average'
    #MAJORITY_VOTE = 'majority_vote'
    #CONFIDENCE_WEIGHTED = 'confidence_weighted' 




