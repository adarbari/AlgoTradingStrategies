"""
Portfolio visualization module for trading strategies.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Dict

# --- Helper Functions ---
def _save_and_close(save_path: Optional[str] = None):
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.close()

def _find_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    """Return the first matching column name from candidates, or None."""
    for col in candidates:
        if col in df.columns:
            return col
    return None

# --- Main Visualization Functions ---
def plot_portfolio_performance(
    symbol: str,
    portfolio_values: pd.DataFrame,
    save_path: Optional[str] = None
) -> None:
    """Plot portfolio performance over time."""
    plt.figure(figsize=(12, 6))
    plt.plot(portfolio_values.index, portfolio_values['portfolio_value'])
    plt.title(f"Portfolio Performance - {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")
    plt.grid(True)
    _save_and_close(save_path)

def plot_trade_distribution(
    symbol: str,
    trades: pd.DataFrame,
    save_path: Optional[str] = None
) -> None:
    """Plot trade distribution and statistics."""
    plt.figure(figsize=(12, 8))
    trades = trades.copy()  # Avoid modifying the original DataFrame
    # Plot trade profits distribution
    plt.subplot(2, 2, 1)
    sns.histplot(trades['profit'], bins=30)
    plt.title('Trade Profit Distribution')
    plt.xlabel('Profit ($)')
    # Plot trade size distribution
    plt.subplot(2, 2, 2)
    sns.histplot(trades['shares'], bins=30)
    plt.title('Trade Size Distribution')
    plt.xlabel('Number of Shares')
    # Plot cumulative profit
    plt.subplot(2, 2, 3)
    trades['cumulative_profit'] = trades['profit'].cumsum()
    plt.plot(trades.index, trades['cumulative_profit'])
    plt.title('Cumulative Profit')
    plt.xlabel('Trade Number')
    plt.ylabel('Cumulative Profit ($)')
    # Plot win rate over time
    plt.subplot(2, 2, 4)
    trades['win'] = trades['profit'] > 0
    trades['win_rate'] = trades['win'].rolling(window=20).mean()
    plt.plot(trades.index, trades['win_rate'])
    plt.title('Win Rate (20-trade moving average)')
    plt.xlabel('Trade Number')
    plt.ylabel('Win Rate')
    _save_and_close(save_path)

def plot_backtest_results(
    symbol: str,
    df: pd.DataFrame,
    save_path: Optional[str] = None
) -> None:
    """Plot backtest results including price, signals, and portfolio value."""
    plt.figure(figsize=(15, 10))
    # --- Price and Signals ---
    plt.subplot(2, 1, 1)
    # Find moving average columns
    ma_short_col = _find_column(df, ['MA_short', 'ma_short', 'short_ma', 'ma10', 'ma_10'])
    ma_long_col = _find_column(df, ['MA_long', 'ma_long', 'long_ma', 'ma100', 'ma_100', 'ma50', 'ma_50'])
    price_col = _find_column(df, ['Price', 'close'])
    signal_col = _find_column(df, ['Signal', 'signal'])
    if ma_short_col:
        plt.plot(df.index, df[ma_short_col], label='Short MA', alpha=0.7)
    if ma_long_col:
        plt.plot(df.index, df[ma_long_col], label='Long MA', alpha=0.7)
    if price_col:
        plt.plot(df.index, df[price_col], label='Price', alpha=0.5)
    # Plot buy and sell signals
    if signal_col and price_col:
        buy_signals = df[df[signal_col] == 1]
        sell_signals = df[df[signal_col] == -1]
        plt.scatter(buy_signals.index, buy_signals[price_col], marker='^', color='g', label='Buy Signal', alpha=1)
        plt.scatter(sell_signals.index, sell_signals[price_col], marker='v', color='r', label='Sell Signal', alpha=1)
    plt.title(f'{symbol} Price and Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    # --- Portfolio Value ---
    plt.subplot(2, 1, 2)
    if all(col in df.columns for col in ['cash', 'shares', price_col]):
        portfolio_value = [float(cash) + float(shares) * float(price) 
                          for cash, shares, price in zip(df['cash'], df['shares'], df[price_col])]
        plt.plot(df.index, portfolio_value, label='Portfolio Value')
        plt.title('Portfolio Value Over Time')
        plt.xlabel('Date')
        plt.ylabel('Value ($)')
        plt.legend()
    _save_and_close(save_path)

def plot_strategy_comparison(
    symbol: str,
    results: List[Dict],
    save_path: Optional[str] = None
) -> None:
    """Plot comparison of different strategy results."""
    plt.figure(figsize=(12, 6))
    # Helper for x-tick labels
    def _xticks():
        return [r['Timestamp'].strftime('%Y-%m-%d\n%H:%M:%S') for r in results]
    # Plot total returns
    plt.subplot(2, 2, 1)
    plt.bar(range(len(results)), [r['Total Return'] for r in results])
    plt.title('Total Return (%)')
    plt.xticks(range(len(results)), _xticks(), rotation=45)
    # Plot win rates
    plt.subplot(2, 2, 2)
    plt.bar(range(len(results)), [r['Win Rate'] for r in results])
    plt.title('Win Rate (%)')
    plt.xticks(range(len(results)), _xticks(), rotation=45)
    # Plot number of trades
    plt.subplot(2, 2, 3)
    plt.bar(range(len(results)), [r['Number of Trades'] for r in results])
    plt.title('Number of Trades')
    plt.xticks(range(len(results)), _xticks(), rotation=45)
    # Plot total profit
    plt.subplot(2, 2, 4)
    plt.bar(range(len(results)), [r['Total Profit'] for r in results])
    plt.title('Total Profit ($)')
    plt.xticks(range(len(results)), _xticks(), rotation=45)
    _save_and_close(save_path) 