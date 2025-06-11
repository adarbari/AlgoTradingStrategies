from typing import Dict, Optional
from src.execution.trade_executor import Trade

class RiskManager:
    """Class responsible for managing trading risk."""
    
    def __init__(self, max_position_size: float = 0.1, max_drawdown: float = 0.2):
        """Initialize the risk manager.
        
        Args:
            max_position_size: Maximum position size as a fraction of portfolio value
            max_drawdown: Maximum allowed drawdown
        """
        self.max_position_size = max_position_size
        self.max_drawdown = max_drawdown
        self.peak_value = 0.0
        
    def check_trade(self, trade: Trade, portfolio_value: float, current_positions: Dict[str, int], current_prices: Dict[str, float]) -> bool:
        """Check if a trade is within risk limits.
        
        Args:
            trade: Trade to check
            portfolio_value: Current portfolio value
            current_positions: Current positions
            current_prices: Current prices
            
        Returns:
            True if trade is allowed, False otherwise
        """
        # Check position size
        position_value = trade.quantity * trade.price
        if position_value > portfolio_value * self.max_position_size:
            return False
            
        # Check drawdown
        if portfolio_value > self.peak_value:
            self.peak_value = portfolio_value
        drawdown = (self.peak_value - portfolio_value) / self.peak_value
        if drawdown > self.max_drawdown:
            return False
            
        return True 