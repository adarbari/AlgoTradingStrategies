"""
Source package.
Contains all core functionality for data fetching and feature engineering.
"""

from .features import FeatureEngineer, TechnicalIndicators
from .utils import StrategyManager

__all__ = [
    'FeatureEngineer',
    'TechnicalIndicators',
    'StrategyManager'
] 