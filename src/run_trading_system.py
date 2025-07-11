"""
Main script to run the trading system.
"""

import os
import sys

from src.data.types.base_types import TimeSeriesData
from src.data.types.data_type import DataType
from src.data.types.symbol import Symbol
from src.execution.portfolio_manager import PortfolioManager
# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from src.data.providers.vendors.polygon import PolygonProvider
from src.features.core.feature_store import FeatureStore
from src.execution.portfolio_trade_execution_orchestrator import PortfolioTradeExecutionOrchestrator
from src.helpers.logger import TradingLogger
from src.utils.split_manager import SplitManager
from src.execution.metrics.cumulative_metrics import CumulativeMetrics
from src.data.data_manager import DataManager


# Initialize the trading logger first
trading_logger = TradingLogger()
logger = trading_logger.logger

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
        
        # Initialize components that are phase-independent
        self.logger = trading_logger  # Use the global trading logger
        
        # Initialize data cache and pass it to PolygonProvider
        self.data_manager = DataManager(ohlcv_provider=PolygonProvider())
    
        # Initialize feature store
        self.feature_store = FeatureStore.get_instance()
        
        # Phase-specific components will be initialized in run()
        self.portfolio_manager = None
        self.trade_executor = None
        
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
        
        # Load historical data and calculate features
        self.historical_data = self._load_data()
        self._calculate_and_cache_features()
        
        logger.info("TradingSystem initialized with %d symbols", len(symbols))
        
    def _load_data(self) -> Dict[str, TimeSeriesData]:
        """Load historical data for all symbols."""
        historical_data = {}
        
        for symbol in self.symbols:
            try:
                time_series_data = self.data_manager.get_ohlcv_data(
                    symbol=symbol,
                    start_time=self.start_date,
                    end_time=self.end_date
                )
                if time_series_data is not None:
                    historical_data[symbol] = time_series_data
                else:
                    logger.warning(f"No data found for {symbol}")
            except Exception as e:
                logger.error(f"Error loading data for {symbol}: {e}")
                continue
                
        return historical_data
        
    def _calculate_and_cache_features(self) -> Dict[Symbol, pd.DataFrame]:
        """Calculate and cache features for all symbols."""
        features = {}
        
        for symbol, data in self.historical_data.items():
            try:
                # Convert TimeSeriesData to DataFrame for feature calculation
                df = data.to_dataframe()
                
                # Generate features using the feature store
                symbol_features = self.feature_store.generate_features(
                    symbol=symbol,
                    start_time=self.start_date,
                    end_time=self.end_date
                )
                
                if not symbol_features.empty:
                    features[symbol] = symbol_features
                    logger.info(f"Generated features for {symbol}: {len(symbol_features)} rows")
                else:
                    logger.warning(f"No features generated for {symbol}")
                    
            except Exception as e:
                logger.error(f"Error generating features for {symbol}: {e}")
                continue
                
        logger.info(f"Successfully generated features for {len(features)} symbols")
        return features
        
    def get_data_for_split(self, split_name: str) -> Dict[str, TimeSeriesData]:
        """Get data for a specific split (train, val, or test)."""
        split_data = {}
        
        # Get the appropriate date range for the split
        if split_name == 'train':
            split_start = self.split_dates['train_start']
            split_end = self.split_dates['train_end']
        elif split_name == 'val':
            split_start = self.split_dates['train_end']
            split_end = self.split_dates['val_end']
        elif split_name == 'test':
            split_start = self.split_dates['val_end']
            split_end = self.split_dates['test_end']
        else:
            raise ValueError(f"Invalid split name: {split_name}")
        
        for symbol, features in self.historical_data.items():
            # Use >= for start date and < for end date to prevent overlap
            df = features.to_dataframe()
            mask = (df.index >= split_start) & (df.index < split_end)
            split_data[symbol] = TimeSeriesData(
                timestamps=df[mask].index.tolist(),
                data=df[mask].to_dict('records'),
                data_type=self.historical_data[symbol].data_type)
        return split_data
        
    def _get_current_prices(self, timestamp: datetime) -> Dict[str, float]:
        """Get current prices for all symbols."""
        prices = {}
        for symbol, data in self.historical_data.items():
            if timestamp in data.timestamps:
                idx = data.timestamps.index(timestamp)
                prices[symbol] = data.data[idx].close
        return prices
        
    def _get_current_features(self, timestamp: datetime, split_data: Dict[str, TimeSeriesData]) -> Dict[str, Dict[str, float]]:
        """Get current features for all symbols."""
        features = {}
        for symbol, ts_data in split_data.items():
            # TimeSeriesData stores timestamps in .timestamps (list of datetime) and .data (list of dicts)
            if timestamp in ts_data.timestamps:
                idx = ts_data.timestamps.index(timestamp)
                features[symbol] = ts_data.data[idx]
        return features
        
    def run(self, split_name: str = 'train') -> Dict:
        """Run the trading system for a specific split ('train', 'val', or 'test')."""
        logger.info(f"Starting trading system for split: {split_name}")
        
        # Set the appropriate phase in the logger
        self.logger.set_phase(split_name)
        
        # Initialize phase-specific components
        self.portfolio_manager = PortfolioManager(self.initial_budget)
        self.trade_executor = PortfolioTradeExecutionOrchestrator(
            portfolio_manager=self.portfolio_manager,
            symbols=self.symbols,
            trading_logger=self.logger
        )
        
        # Get split data
        split_data = self.get_data_for_split(split_name)
        
        # Train strategies if in training phase
        if split_name == 'train':
            self.trade_executor.train_strategies(split_data)
        
        # Get all unique timestamps in the split
        all_timestamps = set()
        for data in split_data.values():
            all_timestamps.update(data.timestamps)
        timestamps = sorted(list(all_timestamps))
        
        # Debug: Print timestamps being processed
        logger.debug(f"Processing {len(timestamps)} timestamps in split '{split_name}'")
        logger.debug(f"First 5 timestamps: {timestamps[:5]}")
        logger.debug(f"Last 5 timestamps: {timestamps[-5:]}")
        
        # Run simulation
        for timestamp in timestamps:
            logger.info(f"Processing timestamp: {timestamp}")
            # Get current prices and features
            current_prices = self._get_current_prices(timestamp)
            current_features = self._get_current_features(timestamp, split_data)
            
            # Log period data for each symbol
            for symbol, features in current_features.items():
                if symbol in current_prices:
                    period_data = {
                        'open': features.get('open', current_prices[symbol]),
                        'high': features.get('high', current_prices[symbol]),
                        'low': features.get('low', current_prices[symbol]),
                        'close': current_prices[symbol],
                        'volume': features.get('volume', 0),
                        'signal': features.get('signal', 0),
                        'returns': features.get('returns', 0),
                        'strategy_returns': features.get('strategy_returns', 0)
                    }
                    self.logger.log_period(symbol, timestamp, period_data)
            
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
            
            # Get current metrics and log portfolio value
            current_metrics = self.portfolio_manager.get_current_metrics()
            portfolio_value = current_metrics['portfolio_value']
            logger.info(f"Current portfolio value: ${portfolio_value:.2f}")
            
        # Generate performance reports for each symbol
        for symbol in self.symbols:
            trades_df = pd.read_csv(self.logger.phase_files[split_name]['trades'])
            trades_df = trades_df[trades_df['symbol'] == symbol]
            if not trades_df.empty:
                self.logger.plot_portfolio_performance(symbol, trades_df)
                self.logger.plot_trade_distribution(symbol, trades_df)
                self.logger.generate_performance_report(symbol, trades_df)
                
        return self.get_results()
        
    def get_results(self) -> Dict:
        """Get trading results for the current phase."""
        # Get the last timestamp from historical data
        timestamps = [
            max(data.to_dataframe().index) for data in self.historical_data.values()
            if not data.to_dataframe().empty
        ]
        if not timestamps:
            default_metrics = CumulativeMetrics.create_default(self.portfolio_manager.initial_capital)
            return {
                'daily_metrics': [],
                'cumulative_metrics': default_metrics.to_dict(),
                'trades': [],
                'positions': {}
            }
        # Get daily metrics as list of dicts
        daily_metrics = [m.to_dict() for m in self.portfolio_manager.daily_metrics]
        # Get cumulative metrics as dict
        cumulative_metrics = self.portfolio_manager.get_cumulative_metrics()
        cumulative_metrics_dict = cumulative_metrics.to_dict() if cumulative_metrics else {}
        # Get trades as list of dicts
        trades = self.portfolio_manager.trades if hasattr(self.portfolio_manager, 'trades') else []
        # Get positions as dict
        positions = self.portfolio_manager.positions if hasattr(self.portfolio_manager, 'positions') else {}
        return {
            'daily_metrics': daily_metrics,
            'cumulative_metrics': cumulative_metrics_dict,
            'trades': trades,
            'positions': positions
        }

def main():
    try:
        # Initialize trading system
        trading_system = TradingSystem(
            symbols=['AAPL', 'MSFT', 'GOOGL'],
            initial_budget=10000.0,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )
        
        # Run training phase
        logger.info("Running training phase...")
        training_results = trading_system.run('train')
        
        # Run validation phase
        logger.info("\nRunning validation phase...")
        validation_results = trading_system.run('val')
        
        # Run test phase
        logger.info("\nRunning test phase...")
        test_results = trading_system.run('test')
        
        # Print results for each stage
        for phase_name, results in zip([
            'Training Results', 'Validation Results', 'Test Results'],
            [training_results, validation_results, test_results]
        ):
            logger.info(f"\n{phase_name}:")
            # Print cumulative metrics
            logger.info("Cumulative Metrics:")
            for key, value in results['cumulative_metrics'].items():
                logger.info(f"  {key}: {value}")
            
            # Print number of trades
            logger.info(f"Number of Trades: {len(results['trades'])}")
            
            # Optionally print daily metrics summary
            logger.info(f"Number of Daily Metrics: {len(results['daily_metrics'])}")
            
            # Print current positions
            logger.info("\nCurrent Positions:")
            for symbol, position in results.get('positions', {}).items():
                logger.info(f"{symbol}: {position['quantity']} shares at ${position['avg_price']:.2f}")
                
    except Exception as e:
        logger.error(f"Error running trading system: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 