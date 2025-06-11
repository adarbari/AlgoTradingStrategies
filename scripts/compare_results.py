import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import sys
from collections import namedtuple
from strategies.SingleStock.single_stock_strategy import SingleStockStrategy

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BacktestResult = namedtuple('BacktestResult', [
    'symbol', 'timestamp', 'initial_capital', 'final_value',
    'total_profit', 'num_trades', 'win_rate', 'best_day', 'worst_day'
])

def parse_trade_file(file_path, run_timestamp):
    """Parse a trade file and extract trading results."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    symbol = os.path.basename(file_path).split('_')[0]
    trades = []
    current_trade = {}
    for line in content.split('\n'):
        if line.startswith('Time:'):
            if current_trade:
                trades.append(current_trade)
            current_trade = {'Time': line.split('Time:')[1].strip()}
        elif ':' in line and current_trade is not None:
            key, value = line.split(':', 1)
            current_trade[key.strip()] = value.strip()
        elif line.startswith('-') and current_trade:
            trades.append(current_trade)
            current_trade = {}
    if current_trade:
        trades.append(current_trade)
    # Only keep SELL trades for profit calculation
    sell_trades = [t for t in trades if t.get('Signal', '').upper() == 'SELL']
    if not sell_trades:
        return None
    initial_capital = float(trades[0].get('Cash', '0').replace('$', '')) + float(trades[0].get('Shares', '0')) * float(trades[0].get('Price', '0').replace('$', ''))
    final_value = float(trades[-1].get('Cash', '0').replace('$', '')) + float(trades[-1].get('Shares', '0')) * float(trades[-1].get('Price', '0').replace('$', ''))
    total_profit = final_value - initial_capital
    num_trades = len(sell_trades)
    win_rate = sum(1 for t in sell_trades if float(t.get('Trade Profit', '0').replace('$', '')) > 0) / num_trades * 100 if num_trades > 0 else 0
    # Daily profits
    daily_profits = {}
    for t in sell_trades:
        date = t.get('Time', '').split()[0]
        profit = float(t.get('Trade Profit', '0').replace('$', ''))
        if date in daily_profits:
            daily_profits[date] += profit
        else:
            daily_profits[date] = profit
    best_day = max(daily_profits.values()) if daily_profits else 0
    worst_day = min(daily_profits.values()) if daily_profits else 0
    # Use run directory timestamp as the run timestamp
    return BacktestResult(
        symbol=symbol,
        timestamp=run_timestamp,
        initial_capital=initial_capital,
        final_value=final_value,
        total_profit=total_profit,
        num_trades=num_trades,
        win_rate=win_rate,
        best_day=best_day,
        worst_day=worst_day
    )

def compare_results():
    run_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and d.startswith('run_')]
    if not run_dirs:
        print("No run directories found!")
        return
    symbol_files = {}
    for run_dir in run_dirs:
        # Extract timestamp from run_dir name
        match = re.search(r'run_(\d{8}_\d{6})', run_dir)
        run_timestamp = datetime.strptime(match.group(1), '%Y%m%d_%H%M%S') if match else None
        for file in os.listdir(run_dir):
            if file.endswith('_trades.txt'):
                symbol = file.split('_')[0]
                if symbol not in symbol_files:
                    symbol_files[symbol] = []
                symbol_files[symbol].append((os.path.join(run_dir, file), run_timestamp))
    if not symbol_files:
        print("No trade files found in run directories!")
        return
    for symbol, files in symbol_files.items():
        print(f"\n=== {symbol} Backtest Results Comparison ===\n")
        results = []
        for file, run_timestamp in files:
            result = parse_trade_file(file, run_timestamp)
            if result:
                results.append(result)
        if not results:
            print(f"No valid results found for {symbol}")
            continue
        df = pd.DataFrame([{
            'Initial Capital': r.initial_capital,
            'Final Portfolio Value': r.final_value,
            'Total Return': ((r.final_value - r.initial_capital) / r.initial_capital) * 100,
            'Total Profit': r.total_profit,
            'Number of Trades': r.num_trades,
            'Win Rate': r.win_rate,
            'Best Day': r.best_day,
            'Worst Day': r.worst_day,
            'Timestamp': r.timestamp
        } for r in results])
        df = df.sort_values('Timestamp')
        print("Summary Statistics:")
        print(df.to_string(index=False))
        plt.figure(figsize=(12, 6))
        plt.subplot(2, 2, 1)
        plt.bar(range(len(df)), df['Total Return'])
        plt.title('Total Return (%)')
        plt.xticks(range(len(df)), [ts.strftime('%Y-%m-%d\n%H:%M:%S') for ts in df['Timestamp']], rotation=45)
        plt.subplot(2, 2, 2)
        plt.bar(range(len(df)), df['Win Rate'])
        plt.title('Win Rate (%)')
        plt.xticks(range(len(df)), [ts.strftime('%Y-%m-%d\n%H:%M:%S') for ts in df['Timestamp']], rotation=45)
        plt.subplot(2, 2, 3)
        plt.bar(range(len(df)), df['Number of Trades'])
        plt.title('Number of Trades')
        plt.xticks(range(len(df)), [ts.strftime('%Y-%m-%d\n%H:%M:%S') for ts in df['Timestamp']], rotation=45)
        plt.subplot(2, 2, 4)
        plt.bar(range(len(df)), df['Total Profit'])
        plt.title('Total Profit ($)')
        plt.xticks(range(len(df)), [ts.strftime('%Y-%m-%d\n%H:%M:%S') for ts in df['Timestamp']], rotation=45)
        plt.tight_layout()
        plt.savefig(f'{symbol}_backtest_comparison.png')
        print(f"\nComparison chart saved as '{symbol}_backtest_comparison.png'")

if __name__ == '__main__':
    compare_results() 