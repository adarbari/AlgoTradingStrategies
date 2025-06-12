from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from src.execution.portfolio_manager import PortfolioManager
from src.strategies.base_strategy import BaseStrategy, StrategySignal
from src.helpers.logger import TradingLogger
import logging
from collections import defaultdict
from src.strategies.strategy_factory import StrategyFactory

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

class TradeExecutor:
    """
    Orchestrates strategy signal generation, aggregates signals, decides trades, and executes them via PortfolioManager.
    """
    def __init__(self, portfolio_manager: PortfolioManager, strategies: List[BaseStrategy], trading_logger: Optional[TradingLogger] = None):
        self.portfolio_manager = portfolio_manager
        self.strategy_factory = StrategyFactory()
        self.current_prices: Dict[str, float] = {}
        self.current_features: Dict[str, Dict[str, float]] = {}  # symbol -> features
        self.trading_logger = trading_logger if trading_logger is not None else TradingLogger()
        self.max_position_value = 2000
        logger.info("TradeExecutor initialized with %d strategies", len(strategies))

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
        all_signals: List[StrategySignal] = []
        
        for symbol, features in self.current_features.items():
             # Get both MA and ML strategies for each symbol
            ma_strategy = self.strategy_factory.get_strategy(symbol, 'ma')
            ml_strategy = self.strategy_factory.get_strategy(symbol, 'ml')
            
            for strategy in [ma_strategy, ml_strategy]:
                try:
                    if symbol not in self.current_prices:
                        logger.error("Symbol %s not found in current prices", symbol)
                        continue
                        
                    signal = strategy.generate_signals(features, symbol, timestamp)
                    logger.info("Strategy %s generated signal for %s: %s", strategy.name, symbol, signal)
                    all_signals.append(signal)
                except Exception as e:
                    logger.error("Error generating signals for strategy %s, symbol %s: %s", strategy.name, symbol, str(e))
                    continue
        if not all_signals:
            logger.info("No signals generated for timestamp %s", timestamp)
            return []
            
        # Aggregate signals and make trade decisions
        aggregated_signals = self._aggregate_signals(all_signals)
        logger.info("Aggregated signals: %s", aggregated_signals)
        
        # Convert aggregated signals to Trade objects
        trades = []
        for symbol, weighted_signal in aggregated_signals.items():
            if symbol not in self.current_prices:
                logger.error("Symbol %s not found in current prices for trade execution", symbol)
                continue
                
            current_price = self.current_prices[symbol]
            action = None
            confidence = abs(weighted_signal)
            
            # More lenient signal thresholds
            if weighted_signal >= 0.3:  # Lowered from 0.5
                action = 'BUY'
            elif weighted_signal <= -0.3:  # Raised from -0.5
                action = 'SELL'
            else:
                continue  # No trade if signal is too weak
                
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
        return executed_trades
        
    def _aggregate_signals(self, signals: List[StrategySignal]) -> Dict[str, float]:
        """Aggregate signals from multiple strategies for each symbol."""
        symbol_signals = defaultdict(list)
        
        # Group signals by symbol
        for signal in signals:
            symbol_signals[signal.symbol].append(signal)
        
        # Calculate weighted signals for each symbol
        aggregated_signals = {}
        for symbol, symbol_signals in symbol_signals.items():
            total_confidence = sum(s.confidence for s in symbol_signals)
            if total_confidence == 0:
                continue
            
            # Convert actions to numeric values
            action_values = {
                'BUY': 1.0,
                'SELL': -1.0,
                'HOLD': 0.0
            }
            
            # Calculate weighted signal
            weighted_signal = sum(
                action_values[s.action] * s.confidence 
                for s in symbol_signals
            ) / total_confidence
            
            aggregated_signals[symbol] = weighted_signal
        
        return aggregated_signals
        
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
            # Validate position size before execution
            if not self.portfolio_manager.validate_position_size(trade.symbol, trade.quantity, trade.price):
                logger.warning("Position size validation failed for %s: quantity=%.2f, price=%.2f", 
                             trade.symbol, trade.quantity, trade.price)
                return False
                
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
                portfolio_value = self.portfolio_manager.get_portfolio_value()
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
            logger.error("Error executing trade for %s: %s", trade.symbol, str(e))
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