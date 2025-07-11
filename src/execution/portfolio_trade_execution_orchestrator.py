from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from src.execution.portfolio_manager import PortfolioManager
from src.execution.signal_aggregation.base_aggregator import BaseAggregator
from src.strategies.base_strategy import BaseStrategy, StrategySignal
from src.helpers.logger import TradingLogger
import logging
from collections import defaultdict
from src.strategies.portfolio.portfolio_trading_execution_config_factory import PortfolioTradingExecutionConfigFactory
from src.config.aggregation_config import WeightedAverageConfig
import pandas as pd

from src.config.base_enums import StrategyType

logger = logging.getLogger(__name__)

@dataclass
class Trade:
    """Class representing a trade."""
    timestamp: datetime
    symbol: str
    action: str  # 'BUY' or 'SELL'
    quantity: int
    price: float
    strategy: str
    confidence: float

class PortfolioTradeExecutionOrchestrator:
    """
    Orchestrates portfolio-wide trade execution by:
    1. Managing multiple trading strategies per symbol
    2. Aggregating signals from different strategies
    3. Making trade decisions based on aggregated signals
    4. Executing trades through the portfolio manager
    5. Maintaining portfolio state and risk management
    """
    def __init__(
        self, 
        portfolio_manager: PortfolioManager, 
        symbols: List[str],
        trading_logger: Optional[TradingLogger] = None
    ):
        self.portfolio_manager = portfolio_manager
        self.symbols = symbols
        self.portfolio_trading_execution_config = PortfolioTradingExecutionConfigFactory.get_instance().create_config('default_portfolio')
        self.strategies: Dict[str, List[BaseStrategy]] = {}  # symbol -> list of strategies
        self.current_prices: Dict[str, float] = {}
        self.current_features: Dict[str, Dict[str, float]] = {}  # symbol -> features
        self.trading_logger = trading_logger if trading_logger is not None else TradingLogger()
        self.max_position_value = 2000
        
        
        self._initialize_strategies()
        logger.info("PortfolioTradeExecutionOrchestrator initialized with %d symbols", len(symbols))

    def _initialize_strategies(self):
        """Initialize strategies for each symbol."""
        for symbol in self.symbols:
            # Get all strategies for each symbol
            self.strategies[symbol] = self.portfolio_trading_execution_config.get_ticker_strategies(symbol)
        logger.info("Initialized strategies for %d symbols", len(self.symbols))

    def train_strategies(self, training_data: Dict[str, pd.DataFrame]):
        """Train all strategies with the provided training data."""
        for symbol, data in training_data.items():
            if symbol in self.strategies:
                for strategy in self.strategies[symbol]:
                    try:
                        #train the model with the data
                        strategy.train_model(data, symbol)
                        logger.info("Trained strategy %s for symbol %s", strategy.name, symbol)

                        #plot the feature importance
                        if hasattr(strategy, 'get_feature_importance'):
                            feature_importance = strategy.get_feature_importance()
                            self.trading_logger.plot_feature_importance(symbol, feature_importance)
                    except Exception as e:
                        logger.error("Error training strategy %s for symbol %s: %s", 
                                   strategy.name, symbol, str(e))

    def update_prices(self, prices: Dict[str, float]):
        """Update current market prices"""
        self.current_prices = prices
        self.portfolio_manager.update_prices(prices)  # Update prices in portfolio manager
        logger.debug("Updated prices for %d symbols", len(prices))
        
    def update_features(self, features: Dict[str, Dict[str, float]]):
        """Update current features for each symbol"""
        self.current_features = features
        logger.debug("Updated features for %d symbols", len(features))
        
    def process(self, timestamp: datetime) -> List[Trade]:
        """Process all strategies and execute trades"""
        logger.info("Processing timestamp: %s", timestamp)
        
        # Get signals from all strategies for all symbols
        all_signals: Dict[str, Dict[StrategyType, StrategySignal]] = {}
        
        for symbol, features in self.current_features.items():
            if symbol not in self.strategies:
                logger.warning("No strategies found for symbol %s", symbol)
                continue
                
            for strategy in self.strategies[symbol]:
                try:
                    if symbol not in self.current_prices:
                        logger.error("Symbol %s not found in current prices", symbol)
                        continue
                        
                    signal = strategy.generate_signals(features, symbol, timestamp)
                    logger.info("Strategy %s generated signal for %s: %s", strategy.name, symbol, signal)
                    if symbol not in all_signals:
                        all_signals[symbol] = {}
                    all_signals[symbol][strategy.name] = signal
                except Exception as e:
                    logger.error("Error generating signals for strategy %s, symbol %s: %s", 
                               strategy.name, symbol, str(e))
                    continue

        if not all_signals:
            logger.info("No signals generated for timestamp %s", timestamp)
            return []
            
        # Aggregate signals per symbol and make trade decisions
        aggregated_signals = {}
        for symbol in all_signals.keys():
            # Get all signals for this symbol from the strategy signals map
            all_signals_for_symbol = all_signals[symbol]
            aggregator = self.portfolio_trading_execution_config.get_ticker_signal_aggregator(symbol)
            aggregated_signals[symbol] = aggregator.aggregate_signals(all_signals_for_symbol)
        
        # Convert aggregated signals to Trade objects
        trades = []
        for symbol, weighted_signal in aggregated_signals.items():
            if symbol not in self.current_prices:
                logger.error("Symbol %s not found in current prices for trade execution", symbol)
                continue
                
            current_price = self.current_prices[symbol]
            action = weighted_signal.action
            confidence = abs(weighted_signal.confidence)
            
            if weighted_signal.confidence < 0.5 or action == 'HOLD':
                continue
                
            quantity = self._calculate_position_size(symbol, current_price, confidence)
            if quantity > 0:
                trade = Trade(
                    timestamp=timestamp,
                    symbol=symbol,
                    action=action,
                    quantity=int(quantity),
                    price=current_price,
                    strategy="Aggregated",
                    confidence=confidence
                )
                trades.append(trade)
                
        logger.info("Generated %d trade decisions", len(trades))
        
        # Execute trades
        executed_trades = []
        for trade in trades:
            try:
                if self._execute_trade(trade, timestamp):
                    executed_trades.append(trade)
                    logger.info("Executed trade: %s %s %.2f shares at $%.2f", 
                              trade.action, trade.symbol, trade.quantity, trade.price)
            except Exception as e:
                logger.error("Error executing trade for %s: %s", trade.symbol, str(e))
                continue        
        logger.info("Successfully executed %d trades", len(executed_trades))

        # Update metrics after all trades are processed
        self.portfolio_manager.update_metrics(timestamp)
       
        return executed_trades
        
        
    def _calculate_position_size(self, symbol: str, price: float, confidence: float) -> float:
        """Calculate position size based on portfolio value and confidence"""
        # Calculate base quantity
        position_value = self.max_position_value * confidence
        quantity = position_value / price
        
        # Round to nearest whole share
        quantity = round(quantity)
        
        logger.info("Position size calculation for %s:", symbol)
        logger.info("  Confidence: %.2f", confidence)
        logger.info("  Position value: $%.2f", position_value)
        logger.info("  Calculated quantity: %d shares", quantity)
        
        return quantity
        
    def _execute_trade(self, trade: Trade, timestamp: datetime) -> bool:
        """Execute a trade through the portfolio manager"""
        try:    
            if trade.action == 'BUY':
                success = self.portfolio_manager.update_position(
                    trade.symbol,
                    trade.quantity,
                    trade.price,
                    timestamp
                )
            else:  # SELL
                success = self.portfolio_manager.update_position(
                    trade.symbol,
                    - trade.quantity,
                    trade.price,
                    timestamp
                )
                
            if success:
                logger.info("Successfully executed %s trade for %s", trade.action, trade.symbol)
                # Log the trade to CSV
                portfolio_value = self.portfolio_manager.get_portfolio_value(self.current_prices)
                cash = self.portfolio_manager.cash
                self.trading_logger.log_trade(
                    symbol=trade.symbol,
                    trade_type=trade.action,
                    price=trade.price,
                    shares=trade.quantity,
                    timestamp=timestamp,
                    portfolio_value=portfolio_value,
                    cash=cash
                )
            else:
                logger.warning("Failed to execute %s trade for %s", trade.action, trade.symbol)
            return success
            
        except Exception as e:
            logger.error("Error executing trade for %s: %s", trade.symbol, str(e), exc_info=True)
            raise
            return False

    def execute_trade(self, trade: Trade) -> None:
        """Execute a trade.
        
        Args:
            trade: Trade to execute
        """
        self.trades.append(trade)
        
    def get_trades(self) -> List[Trade]:
        """Get all executed trades.
        
        Returns:
            List of executed trades
        """
        return self.trades 