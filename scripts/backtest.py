import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import time
import logging
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers import RunManager
from decimal import Decimal
from data import get_cached_data, is_market_hours
from strategies.SingleStock.single_stock_strategy import SingleStockStrategy
from strategies.ml_strategy import MLTradingStrategy
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')

def backtest_strategy(symbol, start_date, end_date, run_manager, strategy_type='ma'):
    """Run backtest for a specific strategy"""
    # Get data
    data = get_cached_data(symbol, start_date, end_date)
    if data is None or data.empty:
        return None
        
    # Initialize strategy
    strategy = SingleStockStrategy(use_ml=(strategy_type == 'ml'))
    
    # Generate signals
    signals = strategy.generate_signals(data, run_manager, symbol)
    
    return signals

def plot_results(run_manager, symbol, df):
    """Plot the backtest results"""
    plt.figure(figsize=(15, 10))
    
    # Plot price and moving averages
    plt.subplot(2, 1, 1)
    plt.plot(df.index, df['MA_short'], label='10-period MA', alpha=0.7)
    plt.plot(df.index, df['MA_long'], label='100-period MA', alpha=0.7)
    plt.plot(df.index, df['Price'], label='Price', alpha=0.5)
    
    # Plot buy and sell signals
    signal_col = 'Signal' if 'Signal' in df.columns else 'signal'
    buy_signals = df[df[signal_col] == 1]
    sell_signals = df[df[signal_col] == -1]
    
    plt.scatter(buy_signals.index, buy_signals['Price'], 
                marker='^', color='g', label='Buy Signal', alpha=1)
    plt.scatter(sell_signals.index, sell_signals['Price'], 
                marker='v', color='r', label='Sell Signal', alpha=1)
    
    plt.title(f'{symbol} Price and Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    
    # Plot portfolio value
    plt.subplot(2, 1, 2)
    portfolio_value = [float(cash) + float(shares) * float(price) for cash, shares, price in zip(df['cash'], df['shares'], df['Price'])]
    plt.plot(df.index, portfolio_value, label='Portfolio Value')
    plt.title('Portfolio Value Over Time')
    plt.xlabel('Date')
    plt.ylabel('Value ($)')
    plt.legend()
    
    # Save plot
    plt.tight_layout()
    plt.savefig(os.path.join(run_manager.run_dir, f'{symbol}_results.png'))
    plt.close()

def compare_strategies(symbol, start_date, end_date, run_manager):
    """Compare different trading strategies"""
    # Run backtest for each strategy
    ma_signals = backtest_strategy(symbol, start_date, end_date, run_manager, 'ma')
    ml_signals = backtest_strategy(symbol, start_date, end_date, run_manager, 'ml')
    
    if ma_signals is None or ml_signals is None:
        return
    
    # Calculate final portfolio values
    ma_final_value = float(ma_signals['cash'].iloc[-1]) + float(ma_signals['shares'].iloc[-1]) * float(ma_signals.get('Price', ma_signals.get('price', pd.Series([0] * len(ma_signals)))).iloc[-1])
    ml_final_value = float(ml_signals['cash'].iloc[-1]) + float(ml_signals['shares'].iloc[-1]) * float(ml_signals.get('Price', ml_signals.get('price', pd.Series([0] * len(ml_signals)))).iloc[-1])
    
    # Log comparison results
    run_manager.log_comparison_results(symbol, ma_final_value, ml_final_value)

if __name__ == '__main__':
    # Test both strategies
    symbols = ['AMZN', 'SPY']
    start_date = '2025-04-01'
    end_date = '2025-06-30'
    run_manager = RunManager()
    for symbol in symbols:
        compare_strategies(symbol, start_date, end_date, run_manager) 