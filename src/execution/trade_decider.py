"""
Trade decision module for processing strategy signals and making trade decisions.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np
from dataclasses import dataclass

from .portfolio_manager import PortfolioManager

@dataclass
class StrategySignal:
    """Standardized signal output from strategies."""
    timestamp: datetime
    symbol: str
    features: Dict[str, float]
    probabilities: Dict[str, float]  # {'BUY': float, 'SELL': float, 'HOLD': float}
    confidence: float  # Overall confidence in the signal

class TradeDecider:
    """Makes trade decisions based on strategy signals and portfolio state."""
    
    def __init__(
        self,
        portfolio_manager: PortfolioManager,
        min_confidence: float = 0.6,
        max_positions: int = 5,
        position_size_pct: float = 0.2  # 20% of portfolio per position
    ):
        """Initialize trade decider.
        
        Args:
            portfolio_manager: Portfolio manager instance
            min_confidence: Minimum confidence threshold for trades
            max_positions: Maximum number of concurrent positions
            position_size_pct: Target position size as percentage of portfolio
        """
        self.portfolio_manager = portfolio_manager
        self.min_confidence = min_confidence
        self.max_positions = max_positions
        self.position_size_pct = position_size_pct
        
    def _aggregate_signals(self, signals: List[StrategySignal]) -> Dict[str, float]:
        """Aggregate multiple strategy signals into a single decision.
        
        Args:
            signals: List of signals from different strategies
            
        Returns:
            Dict with aggregated probabilities for each action
        """
        if not signals:
            return {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 1.0}
            
        # Weight signals by their confidence
        total_confidence = sum(s.confidence for s in signals)
        if total_confidence == 0:
            return {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 1.0}
            
        weighted_probs = {
            action: sum(
                s.probabilities[action] * s.confidence 
                for s in signals
            ) / total_confidence
            for action in ['BUY', 'SELL', 'HOLD']
        }
        
        return weighted_probs
    
    def _calculate_position_size(self, price: float) -> int:
        """Calculate position size based on portfolio value and target percentage.
        
        Args:
            price: Current price of the stock
            
        Returns:
            Number of shares to buy/sell
        """
        portfolio_value = self.portfolio_manager.get_portfolio_value()
        target_position_value = portfolio_value * self.position_size_pct
        return int(target_position_value / price)
    
    def decide_trades(
        self,
        signals: Dict[str, List[StrategySignal]],  # {symbol: [signals]}
        current_prices: Dict[str, float]  # {symbol: price}
    ) -> List[Dict]:
        """Make trade decisions based on signals and current prices.
        
        Args:
            signals: Dictionary mapping symbols to their strategy signals
            current_prices: Dictionary mapping symbols to their current prices
            
        Returns:
            List of trade decisions to execute
        """
        trade_decisions = []
        
        # Process each symbol
        for symbol, symbol_signals in signals.items():
            if symbol not in current_prices:
                continue
                
            current_price = current_prices[symbol]
            current_position = self.portfolio_manager.get_position(symbol)
            
            # Aggregate signals for this symbol
            aggregated_probs = self._aggregate_signals(symbol_signals)
            
            # Get the highest probability action
            action = max(aggregated_probs.items(), key=lambda x: x[1])[0]
            confidence = aggregated_probs[action]
            
            # Skip if confidence is too low
            if confidence < self.min_confidence:
                continue
                
            # Make trade decision
            if action == 'BUY':
                # Check if we can add more positions
                if len(self.portfolio_manager.get_all_positions()) >= self.max_positions:
                    continue
                    
                # Calculate position size
                quantity = self._calculate_position_size(current_price)
                if quantity > 0:
                    trade_decisions.append({
                        'symbol': symbol,
                        'action': 'BUY',
                        'quantity': quantity,
                        'price': current_price,
                        'confidence': confidence
                    })
                    
            elif action == 'SELL':
                # For sell signals, we need to check if we have a position
                if current_position is not None:
                    # Sell entire position
                    trade_decisions.append({
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': current_position['quantity'],
                        'price': current_price,
                        'confidence': confidence
                    })
                else:
                    # If we don't have a position, we can't sell
                    continue
                
        return trade_decisions
    
    def execute_trades(self, trade_decisions: List[Dict], timestamp: datetime) -> List[Dict]:
        """Execute the trade decisions.
        
        Args:
            trade_decisions: List of trade decisions from decide_trades
            timestamp: Current timestamp
            
        Returns:
            List of executed trades
        """
        executed_trades = []
        
        for decision in trade_decisions:
            symbol = decision['symbol']
            action = decision['action']
            quantity = decision['quantity']
            price = decision['price']
            
            if action == 'BUY':
                success = self.portfolio_manager.execute_buy(
                    symbol, quantity, price, timestamp
                )
            else:  # SELL
                success = self.portfolio_manager.execute_sell(
                    symbol, quantity, price, timestamp
                )
                
            if success:
                executed_trades.append({
                    **decision,
                    'timestamp': timestamp,
                    'status': 'EXECUTED'
                })
            else:
                executed_trades.append({
                    **decision,
                    'timestamp': timestamp,
                    'status': 'FAILED'
                })
                
        return executed_trades 