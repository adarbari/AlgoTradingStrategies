import logging
from datetime import datetime
from typing import Optional, Dict, Any
import pandas as pd
import matplotlib.pyplot as plt
import os

class RunManager:
    """Manages the execution and logging of strategy runs."""
    
    def __init__(self, log_dir: str = 'logs'):
        """Initialize the run manager.
        
        Args:
            log_dir: Directory to store logs
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = os.path.join(log_dir, f'strategy_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Initialize metrics
        self.metrics: Dict[str, Any] = {
            'trades': [],
            'portfolio_values': [],
            'start_time': datetime.now()
        }
    
    def log_trade(
        self,
        symbol: str,
        trade_type: str,
        price: float,
        shares: float,
        timestamp: datetime,
        profit: Optional[float] = None
    ) -> None:
        """Log a trade.
        
        Args:
            symbol: Stock symbol
            trade_type: Type of trade (BUY/SELL)
            price: Trade price
            shares: Number of shares
            timestamp: Trade timestamp
            profit: Trade profit (for sells)
        """
        trade_info = {
            'symbol': symbol,
            'type': trade_type,
            'price': price,
            'shares': shares,
            'timestamp': timestamp,
            'profit': profit
        }
        self.metrics['trades'].append(trade_info)
        
        self.logger.info(
            f"Trade: {trade_type} {shares:.2f} shares of {symbol} at ${price:.2f}"
            + (f" (Profit: ${profit:.2f})" if profit is not None else "")
        )
    
    def log_portfolio_value(
        self,
        symbol: str,
        timestamp: datetime,
        portfolio_value: float
    ) -> None:
        """Log portfolio value.
        
        Args:
            symbol: Stock symbol
            timestamp: Timestamp
            portfolio_value: Current portfolio value
        """
        self.metrics['portfolio_values'].append({
            'symbol': symbol,
            'timestamp': timestamp,
            'value': portfolio_value
        })
    
    def plot_portfolio_performance(
        self,
        title: str,
        portfolio_values: pd.Series
    ) -> None:
        """Plot portfolio performance.
        
        Args:
            title: Plot title
            portfolio_values: Series of portfolio values
        """
        plt.figure(figsize=(12, 6))
        portfolio_values.plot()
        plt.title(f'Portfolio Performance - {title}')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value ($)')
        plt.grid(True)
        
        # Save plot
        plot_file = os.path.join(self.log_dir, f'portfolio_performance_{title}.png')
        plt.savefig(plot_file)
        plt.close()
        
        self.logger.info(f"Portfolio performance plot saved to {plot_file}")
    
    def plot_trade_distribution(
        self,
        title: str,
        trades: pd.DataFrame
    ) -> None:
        """Plot trade distribution.
        
        Args:
            title: Plot title
            trades: DataFrame containing trade information
        """
        plt.figure(figsize=(12, 6))
        trades['Signal'].value_counts().plot(kind='bar')
        plt.title(f'Trade Distribution - {title}')
        plt.xlabel('Signal')
        plt.ylabel('Count')
        plt.grid(True)
        
        # Save plot
        plot_file = os.path.join(self.log_dir, f'trade_distribution_{title}.png')
        plt.savefig(plot_file)
        plt.close()
        
        self.logger.info(f"Trade distribution plot saved to {plot_file}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get run summary.
        
        Returns:
            Dictionary containing run summary
        """
        trades = self.metrics['trades']
        portfolio_values = self.metrics['portfolio_values']
        
        if not trades:
            return {
                'total_trades': 0,
                'total_profit': 0.0,
                'win_rate': 0.0,
                'avg_profit_per_trade': 0.0,
                'duration': (datetime.now() - self.metrics['start_time']).total_seconds()
            }
        
        # Calculate metrics
        total_trades = len(trades)
        profitable_trades = sum(1 for t in trades if t.get('profit', 0) > 0)
        total_profit = sum(t.get('profit', 0) for t in trades)
        
        return {
            'total_trades': total_trades,
            'total_profit': total_profit,
            'win_rate': profitable_trades / total_trades if total_trades > 0 else 0.0,
            'avg_profit_per_trade': total_profit / total_trades if total_trades > 0 else 0.0,
            'duration': (datetime.now() - self.metrics['start_time']).total_seconds()
        }
    
    def save_logs(self, symbol: str):
        """Save trades and portfolio values to CSV files."""
        timestamp = self.metrics['start_time'].strftime('%Y%m%d_%H%M%S')
        # Save trades
        trades = self.metrics['trades']
        if trades:
            trades_df = pd.DataFrame(trades)
            trades_file = os.path.join(self.log_dir, f"trades_{symbol}_{timestamp}.csv")
            trades_df.to_csv(trades_file, index=False)
            self.logger.info(f"Trades log saved to {trades_file}")
        # Save portfolio values
        portfolio_values = self.metrics['portfolio_values']
        if portfolio_values:
            portfolio_df = pd.DataFrame(portfolio_values)
            portfolio_file = os.path.join(self.log_dir, f"portfolio_{symbol}_{timestamp}.csv")
            portfolio_df.to_csv(portfolio_file, index=False)
            self.logger.info(f"Portfolio values log saved to {portfolio_file}") 