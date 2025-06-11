import os
import logging
from datetime import datetime
import pandas as pd

class RunManager:
    def __init__(self):
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = os.path.join("logs", f"run_{self.run_timestamp}")
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
        
        return detailed_log_file
    
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
    
    def log_comparison_results(self, symbol, ma_final_value, ml_final_value):
        """Log comparison results of different trading strategies"""
        log_file = os.path.join(self.run_dir, f'{symbol}_comparison_results.txt')
        with open(log_file, 'w') as f:
            f.write(f'Comparison Results for {symbol}\n')
            f.write('=' * 80 + '\n\n')
            f.write(f'Moving Average Strategy Final Value: ${float(ma_final_value):.2f}\n')
            f.write(f'ML Strategy Final Value: ${float(ml_final_value):.2f}\n')
            f.write(f'Difference: ${float(ml_final_value - ma_final_value):.2f}\n')

    def log_training_data(self, log_df, symbol):
        """Log training data to a file in the run directory"""
        log_file = os.path.join(self.run_dir, f'training_data_{symbol}.csv')
        log_df.to_csv(log_file)

    def get_training_data_path(self, symbol):
        """Get the path to the training data log file for a specific ticker"""
        return os.path.join(self.run_dir, f'training_data_{symbol}.csv') 