"""
Strategy class mappings and configurations.
This module provides centralized access to strategy classes and their configurations.
"""

from typing import Dict, Type
from src.strategies.base_strategy import BaseStrategy
from src.strategies.SingleStock.ma_crossover_strategy import MACrossoverStrategy
from src.strategies.SingleStock.random_forest_strategy import RandomForestStrategy
from src.config.strategy_config import MACrossoverConfig, RandomForestConfig
from enum import Enum, auto

class StrategyType(Enum):
    """Enum for strategy types."""
    MA_CROSSOVER = 'ma_crossover'
    RANDOM_FOREST = 'random_forest'

STRATEGY_CLASSES: Dict[str, Type[BaseStrategy]] = {
    StrategyType.MA_CROSSOVER: MACrossoverStrategy,
    StrategyType.RANDOM_FOREST: RandomForestStrategy
}

# Mapping of strategy types to their configuration classes
CONFIG_CLASSES = {
    StrategyType.MA_CROSSOVER: MACrossoverConfig,
    StrategyType.RANDOM_FOREST: RandomForestConfig
}

# Legacy strategy type mappings
TYPE_MAPPINGS = {
    StrategyType.MA_CROSSOVER: 'ma_crossover',
    StrategyType.RANDOM_FOREST: 'random_forest'
}

# Required features for each strategy type
STRATEGY_DEPENDENCIES = {
    StrategyType.MA_CROSSOVER: {'ma_short', 'ma_long'},
    StrategyType.RANDOM_FOREST: {'open', 'high', 'low', 'close', 'volume'}
} 