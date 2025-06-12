
"""
Scripts package.
Contains executable scripts for running backtests and comparing results.
"""

from .backtest import backtest_strategy, compare_strategies, plot_results
from .compare_results import compare_results

__all__ = [
    'backtest_strategy',
    'compare_strategies',
    'plot_results',
    'compare_results'
] 