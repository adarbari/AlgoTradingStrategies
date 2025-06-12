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
            trades: DataFrame containing trade data
        """
        save_path = os.path.join(self.run_dir, f"{title}_trade_distribution.png")
        plot_trade_distribution(title, trades, save_path)
    
    def plot_backtest_results(
        self,
        title: str,
        results: Dict[str, pd.DataFrame]
    ) -> None:
        """Plot backtest results.
        
        Args:
            title: Plot title
            results: Dictionary of strategy results
        """
        save_path = os.path.join(self.run_dir, f"{title}_backtest_results.png")
        plot_backtest_results(title, results, save_path)
    
    def plot_strategy_comparison(
        self,
        title: str,
        strategies: Dict[str, Dict]
    ) -> None:
        """Plot strategy comparison.
        
        Args:
            title: Plot title
            strategies: Dictionary of strategy metrics
        """
        save_path = os.path.join(self.run_dir, f"{title}_strategy_comparison.png")
        plot_strategy_comparison(title, strategies, save_path)
    
    def get_strategy_summary(self) -> Dict:
        """Get strategy performance summary.
        
        Returns:
            Dictionary containing strategy metrics
        """
        return {
            'total_trades': len(self.metrics['trades']),
            'win_rate': sum(1 for t in self.metrics['trades'] if t.get('profit', 0) > 0) / len(self.metrics['trades']) if self.metrics['trades'] else 0,
            'total_profit': sum(t.get('profit', 0) for t in self.metrics['trades']),
            'total_return': (self.metrics['trades'][-1]['portfolio_value'] / self.metrics['trades'][0]['portfolio_value'] - 1) if self.metrics['trades'] else 0
        }
    
    def compare_strategies(self, strategy1_metrics: Dict, strategy2_metrics: Dict) -> None:
        """Compare two strategies.
        
        Args:
            strategy1_metrics: Metrics for first strategy
            strategy2_metrics: Metrics for second strategy
        """
        self.logger.info("\nStrategy Comparison:")
        self.logger.info("Strategy 1:")
        self.logger.info(f"  Total Trades: {strategy1_metrics['total_trades']}")
        self.logger.info(f"  Win Rate: {strategy1_metrics['win_rate']:.2%}")
        self.logger.info(f"  Total Profit: ${strategy1_metrics['total_profit']:.2f}")
        self.logger.info(f"  Total Return: {strategy1_metrics['total_return']:.2%}")
        
        self.logger.info("\nStrategy 2:")
        self.logger.info(f"  Total Trades: {strategy2_metrics['total_trades']}")
        self.logger.info(f"  Win Rate: {strategy2_metrics['win_rate']:.2%}")
        self.logger.info(f"  Total Profit: ${strategy2_metrics['total_profit']:.2f}")
        self.logger.info(f"  Total Return: {strategy2_metrics['total_return']:.2%}")
    
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