import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import time
import logging
import os
from run_manager import RunManager
from decimal import Decimal
from data_manager import get_cached_data, is_market_hours
from strategy import IntradayMovingAverageCrossoverStrategy
from ml_strategy import MLTradingStrategy
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')

def backtest_strategy(symbol, start_date, end_date, run_manager, strategy_type='ma'):
    """Run backtest for a symbol using the specified strategy type."""
    # Ensure dates are datetime objects
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    print(f"\nBacktesting {symbol}...")
    
    # Load data
    data = get_cached_data(symbol, start_date, end_date)
    print(f"Loaded {len(data)} data points")
    
    # Initialize strategy based on type
    if strategy_type == 'ma':
        strategy = IntradayMovingAverageCrossoverStrategy()
    else:
        strategy = MLTradingStrategy()
        print("Training ML model...")
        strategy.train_model(data)
        print("Generating signals...")
    
    # Generate signals
    signals = strategy.generate_signals(data)
    
    # Log trade details using RunManager
    run_manager.log_trade_details(symbol, data, signals, strategy.trade_size)
    
    # Log all datapoints using RunManager
    run_manager.log_all_datapoints(signals, symbol, run_manager.run_dir)
    
    # Plot results
    plot_results(run_manager, symbol, signals)
    
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
    """Compare MA and ML strategies for a symbol."""
    ma_signals = backtest_strategy(symbol, start_date, end_date, run_manager, 'ma')
    ml_signals = backtest_strategy(symbol, start_date, end_date, run_manager, 'ml')
    
    # Calculate and print comparison metrics
    ma_final_value = float(ma_signals['cash'].iloc[-1]) + float(ma_signals['shares'].iloc[-1]) * float(ma_signals['Price'].iloc[-1])
    ml_final_value = float(ml_signals['cash'].iloc[-1]) + float(ml_signals['shares'].iloc[-1]) * float(ml_signals['Price'].iloc[-1])
    
    print("\nStrategy Comparison:")
    print(f"Moving Average Strategy Final Value: ${ma_final_value:.2f}")
    print(f"ML Strategy Final Value: ${ml_final_value:.2f}")
    print(f"Difference: ${(ml_final_value - ma_final_value):.2f}")

if __name__ == '__main__':
    # Test both strategies
    symbols = ['AMZN', 'SPY']
    start_date = '2025-04-01'
    end_date = '2025-06-30'
    run_manager = RunManager()
    for symbol in symbols:
        compare_strategies(symbol, start_date, end_date, run_manager) 