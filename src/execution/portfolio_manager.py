"""
Portfolio management module for tracking positions, cash, and overall portfolio state.
"""

from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
import numpy as np

class PortfolioManager:
    """Manages portfolio state, positions, and budget."""
    
    def __init__(self, initial_budget: float = 10000.0):
        """Initialize portfolio manager.
        
        Args:
            initial_budget: Initial cash available for trading
        """
        self.initial_budget = initial_budget
        self.cash = initial_budget
        self.positions: Dict[str, Dict] = {}  # {symbol: {'quantity': int, 'avg_price': float}}
        self.trade_history: List[Dict] = []
        
    def get_portfolio_value(self) -> float:
        """Get current total portfolio value (cash + positions)."""
        positions_value = sum(
            pos['quantity'] * pos['avg_price'] 
            for pos in self.positions.values()
        )
        return self.cash + positions_value
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get current position for a symbol."""
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> Dict[str, Dict]:
        """Get all current positions."""
        return self.positions
    
    def validate_position_size(self, symbol: str, quantity: int, price: float) -> bool:
        """Validate if a position size is acceptable.
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares
            price: Price per share
            
        Returns:
            bool: True if position size is valid
        """
        # Check if we have enough cash
        if not self.can_buy(symbol, quantity, price):
            return False
            
        # Check if position size is within limits (e.g., max 20% of portfolio)
        position_value = quantity * price
        portfolio_value = self.get_portfolio_value()
        max_position_value = portfolio_value * 0.2  # 20% limit
        
        return position_value <= max_position_value
    
    def can_buy(self, symbol: str, quantity: int, price: float) -> bool:
        """Check if we can buy the specified quantity at the given price."""
        required_cash = quantity * price
        return self.cash >= required_cash
    
    def can_sell(self, symbol: str, quantity: int) -> bool:
        """Check if we can sell the specified quantity."""
        position = self.positions.get(symbol)
        return position is not None and position['quantity'] >= abs(quantity)
    
    def update_position(self, symbol: str, quantity: int, price: float, timestamp: datetime) -> bool:
        """Update position after a trade is executed.
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares (positive for buy, negative for sell)
            price: Price per share
            timestamp: Trade timestamp
            
        Returns:
            bool: True if position was updated successfully
        """
        if quantity > 0:  # Buy
            if not self.validate_position_size(symbol, quantity, price):
                return False
                
            cost = quantity * price
            self.cash -= cost
            
            if symbol in self.positions:
                # Update existing position
                current_pos = self.positions[symbol]
                total_quantity = current_pos['quantity'] + quantity
                total_cost = (current_pos['quantity'] * current_pos['avg_price']) + cost
                self.positions[symbol] = {
                    'quantity': total_quantity,
                    'avg_price': total_cost / total_quantity
                }
            else:
                # Create new position
                self.positions[symbol] = {
                    'quantity': quantity,
                    'avg_price': price
                }
                
        else:  # Sell
            if not self.can_sell(symbol, quantity):
                return False
                
            position = self.positions[symbol]
            proceeds = abs(quantity) * price
            self.cash += proceeds
            
            # Update position
            new_quantity = position['quantity'] - abs(quantity)
            if new_quantity == 0:
                del self.positions[symbol]
            else:
                self.positions[symbol]['quantity'] = new_quantity
        
        # Record trade
        self.trade_history.append({
            'timestamp': timestamp,
            'symbol': symbol,
            'action': 'BUY' if quantity > 0 else 'SELL',
            'quantity': abs(quantity),
            'price': price,
            'total': abs(quantity) * price
        })
        
        return True
    
    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio summary."""
        positions_value = sum(
            pos['quantity'] * pos['avg_price'] 
            for pos in self.positions.values()
        )
        total_value = self.cash + positions_value
        
        return {
            'cash': self.cash,
            'positions_value': positions_value,
            'total_value': total_value,
            'return_pct': ((total_value - self.initial_budget) / self.initial_budget) * 100,
            'num_positions': len(self.positions),
            'positions': self.positions
        }
    
    def get_trade_history(self) -> pd.DataFrame:
        """Get trade history as a DataFrame."""
        return pd.DataFrame(self.trade_history) 