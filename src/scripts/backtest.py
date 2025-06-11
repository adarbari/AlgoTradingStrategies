import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import time
import logging
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import StrategyManager
# from src.data import get_cached_data, is_market_hours  # Uncomment if these exist in src.data
from src.strategies.SingleStock.single_stock_strategy import SingleStockStrategy
# from src.strategies.ml_strategy import MLTradingStrategy  # Uncomment if this exists in src.strategies
from src.visualization.portfolio_visualizer import plot_backtest_results

warnings.filterwarnings('ignore')

def backtest_strategy(symbol, start_date, end_date, strategy_manager, strategy_type='ma'):
    """Run backtest for a specific strategy"""
    # Get data
    # data = get_cached_data(symbol, start_date, end_date)
    if data is None or data.empty:
        return None
        
    # Initialize strategy
    strategy = SingleStockStrategy(use_ml=(strategy_type == 'ml'))
    
    # Initialize strategy tracking
    strategy_manager.initialize_strategy(symbol, strategy_type)
    
    # Generate signals
    signals = strategy.generate_signals(data, strategy_manager, symbol)
    
    return signals

def plot_results(strategy_manager, symbol, df):
    """Plot the backtest results"""
    save_path = os.path.join(strategy_manager.run_dir, f'{symbol}_results.png')
    plot_backtest_results(symbol, df, save_path)

def compare_strategies(symbol, start_date, end_date, strategy_manager):
    """Compare different trading strategies"""
    # Run backtest for each strategy
    ma_signals = backtest_strategy(symbol, start_date, end_date, strategy_manager, 'ma')
    ml_signals = backtest_strategy(symbol, start_date, end_date, strategy_manager, 'ml')
    
    if ma_signals is None or ml_signals is None:
        return
    
    # Get strategy summaries
    ma_summary = strategy_manager.get_strategy_summary()
    ml_summary = strategy_manager.get_strategy_summary()
    
    # Print comparison
    print("\nStrategy Comparison:")
    print("===================")
    print(f"Moving Average Strategy:")
    print(f"Total Trades: {ma_summary['total_trades']}")
    print(f"Win Rate: {ma_summary['win_rate']:.2f}%")
    print(f"Total Profit: ${ma_summary['total_profit']:.2f}")
    print(f"Sharpe Ratio: {ma_summary['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {ma_summary['max_drawdown']:.2f}%")
    print("\nMachine Learning Strategy:")
    print(f"Total Trades: {ml_summary['total_trades']}")
    print(f"Win Rate: {ml_summary['win_rate']:.2f}%")
    print(f"Total Profit: ${ml_summary['total_profit']:.2f}")
    print(f"Sharpe Ratio: {ml_summary['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {ml_summary['max_drawdown']:.2f}%")

if __name__ == '__main__':
    # Test both strategies
    symbols = ['AMZN', 'SPY']
    start_date = '2025-04-01'
    end_date = '2025-06-30'
    strategy_manager = StrategyManager()
    for symbol in symbols:
        compare_strategies(symbol, start_date, end_date, strategy_manager) 