import logging
from datetime import datetime
from typing import Optional, Dict, Any
import pandas as pd
import os
from src.helpers.logger import TradingLogger
from src.visualization.portfolio_visualizer import (
    plot_portfolio_performance,
    plot_trade_distribution
)

class StrategyManager:
    """Manages strategy execution, metrics tracking, and performance analysis."""
    
    def __init__(self, trading_logger: Optional[TradingLogger] = None):
        self.trading_logger = trading_logger if trading_logger is not None else TradingLogger()
        self.logger = self.trading_logger.logger
        self.run_dir = self.trading_logger.run_timestamp_dir
        
        # Initialize metrics
        self.metrics: Dict[str, Any] = {
            'trades': [],
            'portfolio_values': [],
            'start_time': datetime.now(),
            'strategy_type': None,
            'symbol': None
        }
    
    def initialize_strategy(self, symbol: str, strategy_type: str) -> None:
        """Initialize strategy tracking.
        
        Args:
            symbol: Stock symbol
            strategy_type: Type of strategy (e.g., 'ml', 'ma')
        """
        self.metrics['symbol'] = symbol
        self.metrics['strategy_type'] = strategy_type
        self.logger.info(f"Initializing {strategy_type.upper()} strategy for {symbol}")
    
    def log_trade(
        self,
        symbol: str,
        trade_type: str,
        price: float,
        shares: float,
        timestamp: datetime,
        profit: Optional[float] = None,
        portfolio_value: Optional[float] = None
    ) -> None:
        """Log a trade.
        
        Args:
            symbol: Stock symbol
            trade_type: Type of trade (buy/sell)
            price: Trade price
            shares: Number of shares
            timestamp: Trade timestamp
            profit: Optional trade profit
            portfolio_value: Optional portfolio value after trade
        """
        # Delegate to TradingLogger for file operations
        self.trading_logger.log_trade(
            symbol=symbol,
            trade_type=trade_type,
            price=price,
            shares=shares,
            timestamp=timestamp,
            profit=profit,
            portfolio_value=portfolio_value
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
            portfolio_value: Portfolio value
        """
        # Delegate to TradingLogger for file operations
        self.trading_logger.log_portfolio_value(
            symbol=symbol,
            timestamp=timestamp,
            portfolio_value=portfolio_value
        )
    
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
        save_path = os.path.join(self.run_dir, f"{title}_portfolio_performance.png")
        plot_portfolio_performance(title, portfolio_values, save_path)
    
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
        save_path = os.path.join(self.run_dir, f"{title}_trade_distribution.png")
        plot_trade_distribution(title, trades, save_path)
    
    def get_strategy_summary(self) -> Dict[str, Any]:
        """Get comprehensive strategy execution summary.
        
        Returns:
            Dictionary containing strategy summary metrics
        """
        trades = self.metrics['trades']
        portfolio_values = self.metrics['portfolio_values']
        
        if not trades:
            return {
                'symbol': self.metrics['symbol'],
                'strategy_type': self.metrics['strategy_type'],
                'total_trades': 0,
                'total_profit': 0.0,
                'win_rate': 0.0,
                'avg_profit_per_trade': 0.0,
                'max_drawdown': 0.0,
                'sharpe_ratio': 0.0,
                'total_return': 0.0,
                'final_portfolio_value': 0.0
            }
        
        # Calculate metrics
        total_trades = len(trades)
        total_profit = sum(t['profit'] for t in trades)
        win_rate = sum(1 for t in trades if t['profit'] > 0) / total_trades * 100
        avg_profit = total_profit / total_trades
        
        # Calculate drawdown
        portfolio_values = [float(pv) for pv in portfolio_values]
        peak = max(portfolio_values)
        drawdown = (peak - min(portfolio_values)) / peak * 100
        
        # Calculate Sharpe ratio (assuming risk-free rate of 0)
        returns = pd.Series(portfolio_values).pct_change().dropna()
        sharpe_ratio = returns.mean() / returns.std() * (252 ** 0.5) if len(returns) > 0 else 0
        
        # Calculate total return and final portfolio value
        initial_value = portfolio_values[0] if portfolio_values else 0.0
        final_value = portfolio_values[-1] if portfolio_values else 0.0
        total_return = ((final_value - initial_value) / initial_value * 100) if initial_value else 0.0
        
        return {
            'symbol': self.metrics['symbol'],
            'strategy_type': self.metrics['strategy_type'],
            'total_trades': total_trades,
            'total_profit': total_profit,
            'win_rate': win_rate,
            'avg_profit_per_trade': avg_profit,
            'max_drawdown': drawdown,
            'sharpe_ratio': sharpe_ratio,
            'total_return': total_return,
            'final_portfolio_value': final_value
        }
    
    def compare_strategies(self, ma_summary: Dict[str, Any], ml_summary: Dict[str, Any]) -> None:
        """Compare performance of different strategies.
        
        Args:
            ma_summary: Moving Average strategy summary
            ml_summary: Machine Learning strategy summary
        """
        comparison_file = os.path.join(self.run_dir, f'{self.metrics["symbol"]}_strategy_comparison.txt')
        
        with open(comparison_file, 'w') as f:
            f.write(f'Strategy Comparison for {self.metrics["symbol"]}\n')
            f.write('=' * 80 + '\n\n')
            
            # MA Strategy Results
            f.write('Moving Average Strategy:\n')
            f.write(f'Total Return: {ma_summary["total_return"]:.2%}\n')
            f.write(f'Final Portfolio Value: ${ma_summary["final_portfolio_value"]:.2f}\n')
            f.write(f'Total Trades: {ma_summary["total_trades"]}\n')
            f.write(f'Win Rate: {ma_summary["win_rate"]:.2%}\n')
            f.write(f'Total Profit: ${ma_summary["total_profit"]:.2f}\n\n')
            
            # ML Strategy Results
            f.write('Machine Learning Strategy:\n')
            f.write(f'Total Return: {ml_summary["total_return"]:.2%}\n')
            f.write(f'Final Portfolio Value: ${ml_summary["final_portfolio_value"]:.2f}\n')
            f.write(f'Total Trades: {ml_summary["total_trades"]}\n')
            f.write(f'Win Rate: {ml_summary["win_rate"]:.2%}\n')
            f.write(f'Total Profit: ${ml_summary["total_profit"]:.2f}\n\n')
            
            # Comparison
            f.write('Comparison:\n')
            f.write(f'Return Difference: {(ml_summary["total_return"] - ma_summary["total_return"]):.2%}\n')
            f.write(f'Portfolio Value Difference: ${(ml_summary["final_portfolio_value"] - ma_summary["final_portfolio_value"]):.2f}\n')
            f.write(f'Profit Difference: ${(ml_summary["total_profit"] - ma_summary["total_profit"]):.2f}\n')
        
        self.logger.info(f"Strategy comparison saved to {comparison_file}")
    
    def log_training_data(self, data: pd.DataFrame, symbol: str) -> None:
        """Log training data for analysis.
        
        Args:
            data: Training data DataFrame
            symbol: Stock symbol
        """
        training_file = os.path.join(self.run_dir, f'training_data_{symbol}.csv')
        data.to_csv(training_file, index=False)
        self.logger.info(f"Training data saved to {training_file}")
    
    def get_training_data_path(self, symbol: str) -> str:
        """Get the path to the training data file.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Path to training data file
        """
        return os.path.join(self.run_dir, f'training_data_{symbol}.csv') 