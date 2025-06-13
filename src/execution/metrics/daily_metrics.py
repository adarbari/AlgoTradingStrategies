"""
Daily metrics tracking for portfolio performance.
"""

from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime
from enum import Enum

@dataclass
class DailyMetrics:
    """Class to store daily trading metrics."""
    
    class Keys(Enum):
        """Enum for DailyMetrics dictionary keys."""
        DATE = 'date'
        PORTFOLIO_VALUE = 'portfolio_value'
        CASH = 'cash'
        POSITIONS_VALUE = 'positions_value'
        DAILY_RETURN = 'daily_return'
        DAILY_PNL = 'daily_pnl'
        POSITIONS = 'positions'
        TRADES = 'trades'
        UNREALIZED_PNL = 'unrealized_pnl'
        REALIZED_PNL = 'realized_pnl'
        NUM_TRADES = 'num_trades'
        WINNING_TRADES = 'winning_trades'
        LOSING_TRADES = 'losing_trades'

    date: datetime
    portfolio_value: float
    cash: float
    positions_value: float
    daily_return: float
    daily_pnl: float
    positions: Dict
    trades: List[Dict]
    unrealized_pnl: float
    realized_pnl: float
    num_trades: int
    winning_trades: int
    losing_trades: int

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary format."""
        return {
            self.Keys.DATE.value: self.date,
            self.Keys.PORTFOLIO_VALUE.value: self.portfolio_value,
            self.Keys.CASH.value: self.cash,
            self.Keys.POSITIONS_VALUE.value: self.positions_value,
            self.Keys.DAILY_RETURN.value: self.daily_return,
            self.Keys.DAILY_PNL.value: self.daily_pnl,
            self.Keys.POSITIONS.value: self.positions,
            self.Keys.TRADES.value: self.trades,
            self.Keys.UNREALIZED_PNL.value: self.unrealized_pnl,
            self.Keys.REALIZED_PNL.value: self.realized_pnl,
            self.Keys.NUM_TRADES.value: self.num_trades,
            self.Keys.WINNING_TRADES.value: self.winning_trades,
            self.Keys.LOSING_TRADES.value: self.losing_trades
        } 