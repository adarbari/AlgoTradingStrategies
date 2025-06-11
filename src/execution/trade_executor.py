from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

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
    """Class responsible for executing trades."""
    
    def __init__(self):
        """Initialize the trade executor."""
        self.trades: List[Trade] = []
        
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