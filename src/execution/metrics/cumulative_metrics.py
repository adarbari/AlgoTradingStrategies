"""
Cumulative metrics tracking for portfolio performance.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import numpy as np
from enum import Enum

@dataclass
class CumulativeMetrics:
    """Class to store cumulative trading metrics."""
    
    class Keys(Enum):
        """Enum for CumulativeMetrics dictionary keys."""
        START_DATE = 'start_date'
        END_DATE = 'end_date'
        INITIAL_CAPITAL = 'initial_capital'
        FINAL_CAPITAL = 'final_capital'
        TOTAL_RETURN = 'total_return'
        ANNUALIZED_RETURN = 'annualized_return'
        SHARPE_RATIO = 'sharpe_ratio'
        SORTINO_RATIO = 'sortino_ratio'
        MAX_DRAWDOWN = 'max_drawdown'
        WIN_RATE = 'win_rate'
        PROFIT_FACTOR = 'profit_factor'
        TOTAL_TRADES = 'total_trades'
        WINNING_TRADES = 'winning_trades'
        LOSING_TRADES = 'losing_trades'
        AVERAGE_WIN = 'average_win'
        AVERAGE_LOSS = 'average_loss'
        LARGEST_WIN = 'largest_win'
        LARGEST_LOSS = 'largest_loss'
        AVERAGE_HOLDING_PERIOD = 'average_holding_period'
        PORTFOLIO_TURNOVER = 'portfolio_turnover'

    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float
    average_holding_period: float
    portfolio_turnover: float

    def __init__(
        self,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float,
        final_capital: float,
        total_return: float,
        annualized_return: float,
        sharpe_ratio: float,
        sortino_ratio: float,
        max_drawdown: float,
        win_rate: float,
        profit_factor: float,
        total_trades: int,
        winning_trades: int,
        losing_trades: int,
        average_win: float,
        average_loss: float,
        largest_win: float,
        largest_loss: float,
        average_holding_period: float,
        portfolio_turnover: float
    ):
        """Initialize cumulative metrics."""
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.final_capital = final_capital
        self.total_return = total_return
        self.annualized_return = annualized_return
        self.sharpe_ratio = sharpe_ratio
        self.sortino_ratio = sortino_ratio
        self.max_drawdown = max_drawdown
        self.win_rate = win_rate
        self.profit_factor = float('inf') if total_trades == 0 else profit_factor
        self.total_trades = total_trades
        self.winning_trades = winning_trades
        self.losing_trades = losing_trades
        self.average_win = average_win
        self.average_loss = average_loss
        self.largest_win = largest_win
        self.largest_loss = largest_loss
        self.average_holding_period = average_holding_period
        self.portfolio_turnover = portfolio_turnover

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary format."""
        return {
            self.Keys.START_DATE.value: self.start_date,
            self.Keys.END_DATE.value: self.end_date,
            self.Keys.INITIAL_CAPITAL.value: self.initial_capital,
            self.Keys.FINAL_CAPITAL.value: self.final_capital,
            self.Keys.TOTAL_RETURN.value: self.total_return,
            self.Keys.ANNUALIZED_RETURN.value: self.annualized_return,
            self.Keys.SHARPE_RATIO.value: self.sharpe_ratio,
            self.Keys.SORTINO_RATIO.value: self.sortino_ratio,
            self.Keys.MAX_DRAWDOWN.value: self.max_drawdown,
            self.Keys.WIN_RATE.value: self.win_rate,
            self.Keys.PROFIT_FACTOR.value: self.profit_factor,
            self.Keys.TOTAL_TRADES.value: self.total_trades,
            self.Keys.WINNING_TRADES.value: self.winning_trades,
            self.Keys.LOSING_TRADES.value: self.losing_trades,
            self.Keys.AVERAGE_WIN.value: self.average_win,
            self.Keys.AVERAGE_LOSS.value: self.average_loss,
            self.Keys.LARGEST_WIN.value: self.largest_win,
            self.Keys.LARGEST_LOSS.value: self.largest_loss,
            self.Keys.AVERAGE_HOLDING_PERIOD.value: self.average_holding_period,
            self.Keys.PORTFOLIO_TURNOVER.value: self.portfolio_turnover
        } 
    
    @staticmethod
    def create_default(initial_capital: float) -> 'CumulativeMetrics':
        """Create default metrics with just initial capital."""
        return CumulativeMetrics(
            start_date=None,
            end_date=None,
            initial_capital=initial_capital,
            final_capital=initial_capital,
            total_return=0.0,
            annualized_return=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            max_drawdown=0.0,
            win_rate=0.0,
            profit_factor=0.0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            average_win=0.0,
            average_loss=0.0,
            largest_win=0.0,
            largest_loss=0.0,
            average_holding_period=0.0,
            portfolio_turnover=0.0
        )