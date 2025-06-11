"""
Main script to run the trading system.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from src.execution.portfolio_manager import PortfolioManager
from src.execution.trade_decider import TradeDecider, StrategySignal
from src.execution.trade_executor import TradeExecutor, Trade
from src.risk.risk_manager import RiskManager
from src.strategies.SingleStock import MACrossoverStrategy
from src.strategies.SingleStock import RandomForestStrategy
from src.data.vendors.polygon_provider import PolygonProvider
from src.features.feature_store import FeatureStore
from src.features.technical_indicators import TechnicalIndicators
from src.data.data_loader import DataLoader

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
        
        # Initialize components
        self.portfolio_manager = PortfolioManager(initial_budget=initial_budget)
        self.trade_decider = TradeDecider(self.portfolio_manager)
        self.data_fetcher = PolygonProvider()
        self.feature_store = FeatureStore()
        self.technical_indicators = TechnicalIndicators()
        
        # Clear feature cache
        self.feature_store.clear_cache()
        
        # Initialize strategies
        self.strategies = {
            'ma_crossover': MACrossoverStrategy(),
            'random_forest': RandomForestStrategy()
        }
        
        # Load historical data and calculate features
        self.data = self._load_data()
        self._calculate_and_cache_features()
        
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
        for symbol, data in self.data.items():
            try:
                # Calculate technical indicators
                features_df = self.technical_indicators.calculate_features(data)
                
                # Add price data to features
                features_df['price'] = data['close']
                
                # Cache the features
                self.feature_store.cache_features(
                    symbol=symbol,
                    start_date=self.start_date.strftime('%Y-%m-%d'),
                    end_date=self.end_date.strftime('%Y-%m-%d'),
                    features_df=features_df
                )
                logger.info(f"Cached features for {symbol}")
            except Exception as e:
                logger.error(f"Error calculating features for {symbol}: {str(e)}")
        
    def _prepare_strategy_data(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """Prepare data for each strategy.
        
        Returns:
            Dictionary mapping strategies to their prepared data for each symbol
        """
        strategy_data = {}
        for strategy_name, strategy in self.strategies.items():
            strategy_data[strategy_name] = {}
            for symbol, data in self.data.items():
                strategy_data[strategy_name][symbol] = strategy.prepare_data(data, symbol)
        return strategy_data
        
    def _get_current_prices(self, timestamp: datetime) -> Dict[str, float]:
        """Get current prices for all symbols at the given timestamp.
        
        Args:
            timestamp: Current timestamp
            
        Returns:
            Dictionary mapping symbols to their current prices
        """
        prices = {}
        for symbol, data in self.data.items():
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
        
        # Prepare data for all strategies
        strategy_data = self._prepare_strategy_data()
        
        # Get all unique timestamps
        all_timestamps = set()
        for data in self.data.values():
            all_timestamps.update(data.index)
        timestamps = sorted(list(all_timestamps))
        
        # Run simulation
        for timestamp in timestamps:
            logger.info(f"Processing timestamp: {timestamp}")
            
            # Get current prices
            current_prices = self._get_current_prices(timestamp)
            
            # Generate signals from all strategies
            signals = {}
            for symbol in self.symbols:
                if symbol not in current_prices:
                    continue
                    
                symbol_signals = []
                for strategy_name, strategy in self.strategies.items():
                    if symbol in strategy_data[strategy_name]:
                        signal = strategy.generate_signals(
                            strategy_data[strategy_name][symbol],
                            symbol,
                            timestamp
                        )
                        symbol_signals.append(signal)
                signals[symbol] = symbol_signals
            
            # Make trade decisions
            trade_decisions = self.trade_decider.decide_trades(
                signals,
                current_prices
            )
            
            # Execute trades
            executed_trades = self.trade_decider.execute_trades(
                trade_decisions,
                timestamp
            )
            
            # Log executed trades
            for trade_dict in executed_trades:
                logger.info(
                    f"Executed {trade_dict['action']} for {trade_dict['symbol']}: "
                    f"{trade_dict['quantity']} shares at ${trade_dict['price']:.2f}"
                )
            
            # Log portfolio summary
            summary = self.portfolio_manager.get_portfolio_summary()
            logger.info(
                f"Portfolio value: ${summary['total_value']:.2f} "
                f"(Return: {summary['return_pct']:.2f}%)"
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
    # Start with just AAPL for testing
    symbols = ['AAPL']
    system = TradingSystem(
        symbols=symbols,
        initial_budget=10000.0,
        start_date=datetime(2023, 12, 1),  # Last month of 2023
        end_date=datetime(2023, 12, 31)
    )
    
    system.run()
    results = system.get_results()
    
    # Print results
    print("\nTrading Results:")
    print(f"Final Portfolio Value: ${results['final_value']:.2f}")
    print(f"Total Return: {results['return_pct']:.2f}%")
    print(f"Number of Trades: {results['num_trades']}")
    print("\nCurrent Positions:")
    for symbol, position in results['positions'].items():
        print(
            f"{symbol}: {position['quantity']} shares "
            f"@ ${position['avg_price']:.2f}"
        )

if __name__ == "__main__":
    main() 