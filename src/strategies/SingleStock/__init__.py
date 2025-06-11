"""
Single stock trading strategies package.
"""

from src.strategies.SingleStock.ma_crossover_strategy import MACrossoverStrategy
from src.strategies.SingleStock.random_forest_strategy import RandomForestStrategy

__all__ = [
    'MACrossoverStrategy',
    'RandomForestStrategy'
] 