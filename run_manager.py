import os
import logging
from datetime import datetime
import pandas as pd

class RunManager:
    def __init__(self):
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = f"run_{self.run_timestamp}"
        os.makedirs(self.run_dir, exist_ok=True)
    
    def setup_logging(self, symbol):
        """Set up logging for a specific symbol in this run"""
        # Set up detailed logging
        detailed_log_file = os.path.join(self.run_dir, f'trading_log.txt')
        logging.basicConfig(
            filename=detailed_log_file,
            level=logging.INFO,
            format='%(message)s'
        )
        
        # Set up trade-specific logging
        trade_log_file = os.path.join(self.run_dir, f'{symbol}_trades.txt')
        if os.path.exists(trade_log_file):
            os.remove(trade_log_file)
        
        return detailed_log_file, trade_log_file
    
    def log_trade_details(self, symbol, data, signals, trade_size):
        """Log trade details for a symbol."""
        log_file = os.path.join(self.run_dir, f'{symbol}_trade_details.txt')
        with open(log_file, 'w') as f:
            f.write(f'Trade Details for {symbol}\n')
            f.write('=' * 80 + '\n\n')
            # Iterate only up to the minimum length of data and signals
            min_len = min(len(data), len(signals))
            for i in range(min_len):
                try:
                    timestamp = data.index[i]
                    price = data['Close'].iloc[i]
                    ma_short = signals['MA_short'].iloc[i] if 'MA_short' in signals else None
                    ma_long = signals['MA_long'].iloc[i] if 'MA_long' in signals else None
                    ma_diff = signals['ma_diff'].iloc[i] if 'ma_diff' in signals else None
                    prev_ma_diff = signals.get('prev_ma_diff', pd.Series([None] * len(signals))).iloc[i]
                    position = signals.get('Position', pd.Series([None] * len(signals))).iloc[i]
                    signal = signals.get('Signal', pd.Series([None] * len(signals))).iloc[i]
                    cash = signals['Cash'].iloc[i] if 'Cash' in signals else signals.get('cash', pd.Series([None] * len(signals))).iloc[i]
                    portfolio_value = signals['Portfolio_Value'].iloc[i] if 'Portfolio_Value' in signals else signals.get('portfolio_value', pd.Series([None] * len(signals))).iloc[i]
                    shares = signals['Shares'].iloc[i] if 'Shares' in signals else signals.get('shares', pd.Series([None] * len(signals))).iloc[i]
                    trade_profit = signals['Trade_Profit'].iloc[i] if 'Trade_Profit' in signals else None
                    volume = signals['volume'].iloc[i] if 'volume' in signals else None
                    volume_ma_10 = signals['volume_ma_10'].iloc[i] if 'volume_ma_10' in signals else None
                    volume_ma_100 = signals['volume_ma_100'].iloc[i] if 'volume_ma_100' in signals else None
                    price_change = signals.get('price_change', pd.Series([None] * len(signals))).iloc[i]
                    volume_change = signals.get('volume_change', pd.Series([None] * len(signals))).iloc[i]
                    divergence = (price_change is not None and volume_change is not None and ((price_change > 0 and volume_change < 0) or (price_change < 0 and volume_change > 0)))
                    f.write(f'Time: {timestamp}\n')
                    f.write(f'Price: ${price:.2f}\n')
                    if ma_short is not None:
                        f.write(f'10-period MA: ${ma_short:.2f}\n')
                    else:
                        f.write('10-period MA: N/A\n')
                    if ma_long is not None:
                        f.write(f'100-period MA: ${ma_long:.2f}\n')
                    else:
                        f.write('100-period MA: N/A\n')
                    if ma_diff is not None:
                        f.write(f'MA Difference: ${ma_diff:.2f}\n')
                    else:
                        f.write('MA Difference: N/A\n')
                    if prev_ma_diff is not None:
                        f.write(f'Previous MA Difference: ${prev_ma_diff:.2f}\n')
                    else:
                        f.write('Previous MA Difference: N/A\n')
                    f.write(f'Position: {position}\n')
                    if shares is not None:
                        f.write(f'Shares: {shares:.4f}\n')
                    else:
                        f.write('Shares: N/A\n')
                    if cash is not None:
                        f.write(f'Cash: ${cash:.2f}\n')
                    else:
                        f.write('Cash: N/A\n')
                    if portfolio_value is not None:
                        f.write(f'Portfolio Value: ${portfolio_value:.2f}\n')
                    else:
                        f.write('Portfolio Value: N/A\n')
                    f.write(f'Signal: {signal}\n')
                    if volume is not None:
                        f.write(f'Volume: {volume}\n')
                    else:
                        f.write('Volume: N/A\n')
                    if volume_ma_10 is not None:
                        f.write(f'10-period Volume MA: {volume_ma_10:.2f}\n')
                    else:
                        f.write('10-period Volume MA: N/A\n')
                    if volume_ma_100 is not None:
                        f.write(f'100-period Volume MA: {volume_ma_100:.2f}\n')
                    else:
                        f.write('100-period Volume MA: N/A\n')
                    if price_change is not None:
                        f.write(f'Price Change: {price_change:.2%}\n')
                    else:
                        f.write('Price Change: N/A\n')
                    if volume_change is not None:
                        f.write(f'Volume Change: {volume_change:.2%}\n')
                    else:
                        f.write('Volume Change: N/A\n')
                    if divergence:
                        f.write('Divergence Detected: Price and volume are diverging.\n')
                    if signal == -1:  # Only show profit for sells
                        if trade_profit is not None:
                            f.write(f'Trade Profit: ${trade_profit:.2f}\n')
                        else:
                            f.write('Trade Profit: N/A\n')
                    f.write('-' * 40 + '\n')
                except Exception as e:
                    f.write(f'Error logging trade details: {e}\n')
                    f.write('-' * 40 + '\n')
    
    def log_run_statistics(self, results):
        """Log overall run statistics"""
        stats_file = os.path.join(self.run_dir, 'run_stats.txt')
        with open(stats_file, 'w') as f:
            f.write(f"Backtest Run: {self.run_timestamp}\n")
            f.write("=" * 50 + "\n\n")
            for symbol, result in results.items():
                f.write(f"{symbol} Statistics:\n")
                f.write(f"Initial Capital: $10,000\n")
                f.write(f"Final Portfolio Value: ${result['final_portfolio_value']:.2f}\n")
                f.write(f"Total Return: {result['total_return']:.2%}\n")
                f.write(f"Total Profit: ${result['total_profit']:.2f}\n")
                f.write(f"Number of Trades: {result['num_trades']}\n")
                f.write(f"Average Daily Return: {result['avg_daily_return']:.2%}\n")
                f.write(f"Daily Return Std Dev: {result['daily_return_std']:.2%}\n")
                f.write(f"Win Rate: {result['win_rate']:.2%}\n")
                f.write(f"Best Day: {result['best_day']:.2%}\n")
                f.write(f"Worst Day: {result['worst_day']:.2%}\n")
                f.write("-" * 50 + "\n\n")
    
    def log_all_datapoints(self, signals, symbol, run_dir):
        """Log all datapoints for a symbol."""
        log_file = os.path.join(run_dir, f'{symbol}_all_datapoints.txt')
        with open(log_file, 'w') as f:
            f.write(f'All Datapoints for {symbol}\n')
            f.write('=' * 80 + '\n\n')
            for i in range(len(signals)):
                current_time = signals.index[i]
                price = signals['Price'].iloc[i]
                if i < len(signals):
                    ma_short = signals['MA_short'].iloc[i]
                else:
                    ma_short = None
                if i < len(signals):
                    ma_long = signals['MA_long'].iloc[i]
                else:
                    ma_long = None
                if i < len(signals):
                    ma_diff = signals['ma_diff'].iloc[i]
                else:
                    ma_diff = None
                if i < len(signals):
                    position = signals.get('Position', pd.Series([None] * len(signals))).iloc[i]
                else:
                    position = None
                shares = signals['shares'].iloc[i]
                cash = signals['cash'].iloc[i]
                portfolio_value = signals.get('portfolio_value', pd.Series([None] * len(signals))).iloc[i]
                signal = signals['signal'].iloc[i]
                volume = signals['volume'].iloc[i]
                volume_ma_10 = signals.get('volume_ma_10', pd.Series([None] * len(signals))).iloc[i]
                volume_ma_100 = signals.get('volume_ma_100', pd.Series([None] * len(signals))).iloc[i]
                price_change = signals.get('price_change', pd.Series([None] * len(signals))).iloc[i]
                volume_change = signals.get('volume_change', pd.Series([None] * len(signals))).iloc[i]
                divergence = (price_change is not None and volume_change is not None and ((price_change > 0 and volume_change < 0) or (price_change < 0 and volume_change > 0)))
                f.write(f'Time: {current_time}\n')
                f.write(f'Price: ${price:.2f}\n')
                if ma_short is not None:
                    f.write(f'10-period MA: ${ma_short:.2f}\n')
                else:
                    f.write('10-period MA: N/A\n')
                if ma_long is not None:
                    f.write(f'100-period MA: ${ma_long:.2f}\n')
                else:
                    f.write('100-period MA: N/A\n')
                f.write(f'MA Difference: ${ma_diff:.2f}\n')
                f.write(f'Position: {position}\n')
                f.write(f'Shares: {shares}\n')
                f.write(f'Cash: ${cash:.2f}\n')
                if portfolio_value is not None:
                    f.write(f'Portfolio Value: ${portfolio_value:.2f}\n')
                else:
                    f.write('Portfolio Value: N/A\n')
                f.write(f'Signal: {signal}\n')
                f.write(f'Volume: {volume}\n')
                if volume_ma_10 is not None:
                    f.write(f'10-period Volume MA: {volume_ma_10:.2f}\n')
                else:
                    f.write('10-period Volume MA: N/A\n')
                if volume_ma_100 is not None:
                    f.write(f'100-period Volume MA: {volume_ma_100:.2f}\n')
                else:
                    f.write('100-period Volume MA: N/A\n')
                if price_change is not None:
                    f.write(f'Price Change: {price_change:.2%}\n')
                else:
                    f.write('Price Change: N/A\n')
                if volume_change is not None:
                    f.write(f'Volume Change: {volume_change:.2%}\n')
                else:
                    f.write('Volume Change: N/A\n')
                if divergence:
                    f.write('Divergence Detected: Price and volume are diverging.\n')
                f.write('-' * 40 + '\n') 