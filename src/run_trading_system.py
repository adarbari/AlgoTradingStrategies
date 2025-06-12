"""
Main script to run the trading system.
"""

import os
import sys
# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from src.data.vendors.polygon_provider import PolygonProvider
from src.data.base import DataCache
from src.features.feature_store import FeatureStore
from src.strategies.SingleStock.ma_crossover_strategy import MACrossoverStrategy
from src.strategies.SingleStock.random_forest_strategy import RandomForestStrategy
from src.execution.portfolio_manager import PortfolioManager
from src.execution.trade_executor import TradeExecutor
from src.helpers.logger import TradingLogger
from src.utils.split_manager import SplitManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TradingSystem:
    """Main trading system class."""
    
    def __init__(
        self,
        symbols: List[str],
        initial_budget: float = 10000.0,
        start_date: datetime = None,
        end_date: datetime = None,
        split_ratios: Dict[str, float] = None,
        min_train_days: int = 30
    ):
        """Initialize trading system.
        
        Args:
            symbols: List of stock symbols to trade
            initial_budget: Initial portfolio budget
            start_date: Start date for backtesting
            end_date: End date for backtesting
            split_ratios: Dict with keys 'train', 'val', 'test' and float values summing to 1
            min_train_days: Minimum number of days for training split
        """
        self.symbols = symbols
        self.start_date = start_date or (datetime.now() - timedelta(days=365))
        self.end_date = end_date or datetime.now()
        self.initial_budget = initial_budget
        
        # Initialize components
        self.portfolio_manager = PortfolioManager(initial_budget)
        self.strategies = [
            MACrossoverStrategy(),
            RandomForestStrategy()
        ]
        self.trade_executor = TradeExecutor(self.portfolio_manager, self.strategies)
        # Initialize data cache and pass it to PolygonProvider
        self.data_cache = DataCache()
        self.data_fetcher = PolygonProvider(cache=self.data_cache)
        # Initialize feature store
        self.feature_store = FeatureStore()
        self.logger = TradingLogger()
        
        # --- SplitManager integration ---
        if split_ratios is None:
            split_ratios = {'train': 0.6, 'val': 0.2, 'test': 0.2}
        self.split_manager = SplitManager(
            train_ratio=split_ratios['train'],
            val_ratio=split_ratios['val'],
            test_ratio=split_ratios['test'],
            min_train_days=min_train_days
        )
        self.split_dates = self.split_manager.get_split_dates(self.start_date, self.end_date)
        # --- End SplitManager integration ---
        
        # Load historical data and calculate features
        self.historical_data = self._load_data()
        self.features = self._calculate_and_cache_features()
        
    def _load_data(self) -> Dict[str, pd.DataFrame]:
        """Load historical data for all symbols using the data/vendor layer.
        
        Returns:
            Dictionary mapping symbols to their price data
        """
        data = {}
        for symbol in self.symbols:
            try:
                df = self.data_fetcher.get_historical_data(
                    symbol,
                    self.start_date,
                    self.end_date
                )
                if not df.empty:
                    data[symbol] = df
                else:
                    logger.warning(f"No data found for {symbol}")
            except Exception as e:
                logger.error(f"Error loading data for {symbol}: {str(e)}")
        return data
        
    def _calculate_and_cache_features(self) -> Dict[str, pd.DataFrame]:
        """Calculate and cache features for all symbols."""
        features = {}
        for symbol, data in self.historical_data.items():
            try:
                start_date = data.index.min().strftime('%Y-%m-%d')
                end_date = data.index.max().strftime('%Y-%m-%d')
                features_df = self.feature_store.get_features(
                    symbol=symbol,
                    data=data,
                    start_date=start_date,
                    end_date=end_date
                )
                features[symbol] = features_df
            except Exception as e:
                logger.error(f"Error calculating features for {symbol}: {str(e)}")
                continue
        return features
        
    def get_data_for_split(self, split_name: str) -> Dict[str, pd.DataFrame]:
        """Return a dict of symbol: DataFrame for the requested split ('train', 'val', 'test')."""
        assert split_name in ('train', 'val', 'test'), "split_name must be 'train', 'val', or 'test'"
        split_dates = self.split_dates
        if split_name == 'train':
            start, end = split_dates['train_start'], split_dates['train_end']
        elif split_name == 'val':
            start, end = split_dates['train_end'], split_dates['val_end']
        else:  # 'test'
            start, end = split_dates['val_end'], split_dates['test_end']
        split_data = {}
        for symbol, df in self.features.items():
            mask = (df.index >= start) & (df.index < end)
            split_data[symbol] = df.loc[mask].copy()
        return split_data
        
    def run(self, split_name: str = 'train') -> None:
        """Run the trading system for a specific split ('train', 'val', or 'test')."""
        logger.info(f"Starting trading system for split: {split_name}")
        split_data = self.get_data_for_split(split_name)
        # Get all unique timestamps in the split
        all_timestamps = set()
        for data in split_data.values():
            all_timestamps.update(data.index)
        timestamps = sorted(list(all_timestamps))
        # Run simulation
        for timestamp in timestamps:
            logger.info(f"Processing timestamp: {timestamp}")
            # Get current prices and features
            current_prices = self._get_current_prices(timestamp)
            current_features = self._get_current_features(timestamp, split_data)
            # Update trade executor with current state
            self.trade_executor.update_prices(current_prices)
            self.trade_executor.update_features(current_features)
            # Process signals and execute trades
            executed_trades = self.trade_executor.process(timestamp)
            # Log executed trades
            for trade in executed_trades:
                logger.info(
                    f"Executed {trade.action} for {trade.symbol}: "
                    f"{trade.quantity} shares at ${trade.price:.2f}"
                )
            # Log portfolio summary
            portfolio_value = self.portfolio_manager.get_portfolio_value()
            logger.info(
                f"Portfolio value: ${portfolio_value:.2f} "
                f"(Return: {((portfolio_value - self.initial_budget) / self.initial_budget) * 100:.2f}%)"
            )

    def _get_current_features(self, timestamp: datetime, split_data: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, float]]:
        """Get current features for all symbols at the given timestamp from split_data."""
        features = {}
        for symbol, df in split_data.items():
            mask = df.index <= timestamp
            if not mask.any():
                continue
            features[symbol] = df[mask].iloc[-1].to_dict()
        return features
        
    def _get_current_prices(self, timestamp: datetime) -> Dict[str, float]:
        """Get current prices for all symbols at the given timestamp from historical_data."""
        prices = {}
        for symbol, data in self.historical_data.items():
            mask = data.index <= timestamp
            if not mask.any():
                continue
            latest_idx = data.index[mask][-1]
            prices[symbol] = data.loc[latest_idx, 'close']
        return prices
        
    def get_results(self) -> Dict:
        """Get trading results.
        
        Returns:
            Dictionary containing trading results and statistics
        """
        trade_history = self.portfolio_manager.get_trade_history()
        summary = self.portfolio_manager.get_portfolio_summary()
        
        return {
            'trade_history': trade_history,
            'portfolio_summary': summary,
            'final_value': summary['total_value'],
            'return_pct': summary['return_pct'],
            'num_trades': len(trade_history),
            'positions': summary['positions']
        }

def main():
    # Example usage: run all splits
    trading_system = TradingSystem(
        symbols=['AAPL', 'MSFT'],
        initial_budget=10000.0,
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 12, 31)
    )
    for split in ['train', 'val', 'test']:
        trading_system.run(split)
        results = trading_system.get_results()
        logger.info(f"\nResults for split: {split}")
        logger.info(f"Final Portfolio Value: ${results['final_value']:.2f}")
        logger.info(f"Return: {results['return_pct']:.2f}%")
        logger.info(f"Number of Trades: {results['num_trades']}")
        logger.info("\nCurrent Positions:")
        for symbol, position in results['positions'].items():
            logger.info(f"{symbol}: {position['quantity']} shares at ${position['avg_price']:.2f}")

if __name__ == "__main__":
    main() 