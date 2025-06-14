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
from src.config.base_enums import StrategyType

# Mapping of strategy types to their implementation classes
STRATEGY_CLASSES = {
    StrategyType.MA_CROSSOVER: MACrossoverStrategy,
    StrategyType.RANDOM_FOREST: RandomForestStrategy
}

# Mapping of strategy types to their config classes
CONFIG_CLASSES = {
    StrategyType.MA_CROSSOVER: MACrossoverConfig,
    StrategyType.RANDOM_FOREST: RandomForestConfig
}

# Required features for each strategy type
STRATEGY_DEPENDENCIES = {
    StrategyType.MA_CROSSOVER: {'ma_short', 'ma_long'},
    StrategyType.RANDOM_FOREST: {'open', 'high', 'low', 'close', 'volume'}
} 