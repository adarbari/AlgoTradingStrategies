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
from src.execution.portfolio_manager import PortfolioManager
from src.execution.trade_executor import TradeExecutor
from src.strategies.SingleStock.ma_crossover_strategy import MACrossoverStrategy
from src.strategies.SingleStock.random_forest_strategy import RandomForestStrategy
from src.data.vendors.polygon_provider import PolygonProvider
from src.features.feature_store import FeatureStore
from src.features.technical_indicators import TechnicalIndicators
from src.data.data_loader import DataLoader
from src.helpers.logger import TradingLogger
from src.data.base import DataCache

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
        end_date: datetime = None
    ):
        """Initialize trading system.
        
        Args:
            symbols: List of stock symbols to trade
            initial_budget: Initial portfolio budget
            start_date: Start date for backtesting
            end_date: End date for backtesting
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
        self.feature_store = FeatureStore()
        self.technical_indicators = TechnicalIndicators()
        self.logger = TradingLogger()
        
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

    def _calculate_and_cache_features(self) -> None:
        """Calculate and cache features for all symbols."""
        features = {}
        for symbol, data in self.historical_data.items():
            try:
                # Get date range for the data
                start_date = data.index.min().strftime('%Y-%m-%d')
                end_date = data.index.max().strftime('%Y-%m-%d')
                
                # Try to get features from cache first
                features_df = self.feature_store.get_cached_features(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date
                )
                
                # If no cached features found, calculate and cache them
                if features_df is None:
                    features_df = self.technical_indicators.calculate_features(
                        data,
                        None,  # Calculate all available features
                        symbol=symbol
                    )
                    # Cache the calculated features
                    self.feature_store.cache_features(
                        symbol=symbol,
                        start_date=start_date,
                        end_date=end_date,
                        features_df=features_df
                    )
                features[symbol] = features_df
            except Exception as e:
                logger.error(f"Error calculating features for {symbol}: {str(e)}")
                continue
            return features
        
    def _get_current_features(self, timestamp: datetime) -> Dict[str, Dict[str, float]]:
        """Get current features for all symbols at the given timestamp.
        
        Args:
            timestamp: Current timestamp
            
        Returns:
            Dictionary mapping symbols to their current features
        """
        features = {}
        for symbol, data in self.historical_data.items():
            # Get data up to the current timestamp
            mask = data.index <= timestamp
            if not mask.any():
                continue
                
            # Get the latest data point
            latest_data = data[mask].iloc[-1]
            
            # Get features from our cached features
            if symbol in self.features:
                symbol_features_df = self.features[symbol]
                # Get features for the current timestamp
                mask = symbol_features_df.index <= timestamp
                if mask.any():
                    features[symbol] = symbol_features_df[mask].iloc[-1].to_dict()
                else:
                    logger.warning(f"No features found for {symbol} at {timestamp}")
            else:
                logger.warning(f"No cached features found for {symbol}")
                
        return features
        
    def _get_current_prices(self, timestamp: datetime) -> Dict[str, float]:
        """Get current prices for all symbols at the given timestamp.
        
        Args:
            timestamp: Current timestamp
            
        Returns:
            Dictionary mapping symbols to their current prices
        """
        prices = {}
        for symbol, data in self.historical_data.items():
            # Find the latest available price before or at the timestamp
            mask = data.index <= timestamp
            if not mask.any():
                continue
            latest_idx = data.index[mask][-1]
            prices[symbol] = data.loc[latest_idx, 'close']
        return prices
        
    def run(self) -> None:
        """Run the trading system."""
        logger.info("Starting trading system...")
        
        # Get all unique timestamps
        all_timestamps = set()
        for data in self.historical_data.values():
            all_timestamps.update(data.index)
        timestamps = sorted(list(all_timestamps))
        
        # Run simulation
        for timestamp in timestamps:
            logger.info(f"Processing timestamp: {timestamp}")
            
            # Get current prices and features
            current_prices = self._get_current_prices(timestamp)
            current_features = self._get_current_features(timestamp)
            
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
    """Main function to run the trading system."""
    # Initialize trading system with test parameters
    trading_system = TradingSystem(
        symbols=['AAPL'],
        initial_budget=100000,
        start_date=datetime(2023, 6, 12),
        end_date=datetime(2023, 6, 29)
    )
    
    # Run the trading system
    trading_system.run()
    
    # Get and display results
    results = trading_system.get_results()
    logger.info("\nTrading Results:")
    logger.info(f"Final Portfolio Value: ${results['final_value']:.2f}")
    logger.info(f"Return: {results['return_pct']:.2f}%")
    logger.info(f"Number of Trades: {results['num_trades']}")
    logger.info("\nCurrent Positions:")
    for symbol, position in results['positions'].items():
        logger.info(f"{symbol}: {position['quantity']} shares at ${position['avg_price']:.2f}")

if __name__ == "__main__":
    main() 