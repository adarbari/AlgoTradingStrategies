"""
Scripts for running and testing the trading system.
"""

from .backtest import backtest_strategy, compare_strategies, plot_results
from .compare_results import compare_results

__all__ = [
    'backtest_strategy',
    'compare_strategies',
    'plot_results',
    'compare_results'
] 