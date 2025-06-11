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
    
    def can_buy(self, symbol: str, quantity: int, price: float) -> bool:
        """Check if we can buy the specified quantity at the given price."""
        required_cash = quantity * price
        return self.cash >= required_cash
    
    def can_sell(self, symbol: str, quantity: int) -> bool:
        """Check if we can sell the specified quantity."""
        position = self.positions.get(symbol)
        return position is not None and position['quantity'] >= quantity
    
    def execute_buy(self, symbol: str, quantity: int, price: float, timestamp: datetime) -> bool:
        """Execute a buy order.
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares to buy
            price: Price per share
            timestamp: Trade timestamp
            
        Returns:
            bool: True if trade was executed successfully
        """
        if not self.can_buy(symbol, quantity, price):
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
            
        # Record trade
        self.trade_history.append({
            'timestamp': timestamp,
            'symbol': symbol,
            'action': 'BUY',
            'quantity': quantity,
            'price': price,
            'total': cost
        })
        
        return True
    
    def execute_sell(self, symbol: str, quantity: int, price: float, timestamp: datetime) -> bool:
        """Execute a sell order.
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares to sell
            price: Price per share
            timestamp: Trade timestamp
            
        Returns:
            bool: True if trade was executed successfully
        """
        if not self.can_sell(symbol, quantity):
            return False
            
        position = self.positions[symbol]
        proceeds = quantity * price
        self.cash += proceeds
        
        # Update position
        new_quantity = position['quantity'] - quantity
        if new_quantity == 0:
            del self.positions[symbol]
        else:
            self.positions[symbol]['quantity'] = new_quantity
            
        # Record trade
        self.trade_history.append({
            'timestamp': timestamp,
            'symbol': symbol,
            'action': 'SELL',
            'quantity': quantity,
            'price': price,
            'total': proceeds
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