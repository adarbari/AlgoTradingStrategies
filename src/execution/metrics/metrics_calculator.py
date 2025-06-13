"""
Metrics calculator for computing portfolio performance metrics.
"""

from typing import List, Dict, Optional
from datetime import datetime
import numpy as np
import pandas as pd
from .daily_metrics import DailyMetrics
from .cumulative_metrics import CumulativeMetrics

class MetricsCalculator:
    """Calculates portfolio performance metrics."""
    
    def __init__(self, risk_free_rate: float = 0.02):
        """Initialize metrics calculator.
        
        Args:
            risk_free_rate: Annual risk-free rate for metrics calculations
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_daily_metrics(
        self,
        date: datetime,
        portfolio_value: float,
        cash: float,
        positions: Dict[str, Dict],
        trades: List[Dict],
        previous_portfolio_value: float,
        current_prices: Dict[str, float]
    ) -> DailyMetrics:
        """Calculate daily performance metrics from raw state."""
        # Calculate daily return and P&L
        if previous_portfolio_value is not None and previous_portfolio_value > 0:
            daily_return = (portfolio_value - previous_portfolio_value) / previous_portfolio_value
            daily_pnl = portfolio_value - previous_portfolio_value
        else:
            daily_return = 0.0
            daily_pnl = 0.0

        # Calculate unrealized and realized P&L
        unrealized_pnl = sum(
            (current_prices[symbol] - positions[symbol]["avg_price"]) * positions[symbol]["quantity"]
            for symbol in positions if symbol in current_prices
        )
        realized_pnl = sum(
            trade["pnl"]
            for trade in trades
            if trade["is_closed"]
        )
        
        # Calculate positions value
        positions_value = sum(
            positions[symbol]["quantity"] * current_prices.get(symbol, 0.0)
            for symbol in positions
        )
        # Calculate trade stats
        num_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.get('pnl', 0) > 0)
        losing_trades = sum(1 for t in trades if t.get('pnl', 0) < 0)

        return DailyMetrics(
            date=date,
            portfolio_value=portfolio_value,
            cash=cash,
            positions_value=positions_value,
            daily_return=daily_return,
            daily_pnl=daily_pnl,
            positions=positions,
            trades=trades,
            unrealized_pnl=unrealized_pnl,
            realized_pnl=realized_pnl,
            num_trades=num_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades
        )
    
    def calculate_cumulative_metrics(
        self,
        daily_metrics: List[DailyMetrics],
        initial_capital: float,
        trades: List[Dict]
    ) -> CumulativeMetrics:
        """Calculate cumulative metrics from daily metrics and trades."""
        if not daily_metrics:
            return None

        start_date = daily_metrics[0].date
        end_date = daily_metrics[-1].date
        final_capital = daily_metrics[-1].portfolio_value

        # Calculate total return
        total_return = (final_capital - initial_capital) / initial_capital

        # Calculate annualized return
        years = (end_date - start_date).days / 365.25
        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0.0

        # Calculate risk metrics from daily returns
        daily_returns = [m.daily_return for m in daily_metrics]
        avg_daily_return = sum(daily_returns) / len(daily_returns)
        
        # Calculate volatility (standard deviation of returns)
        variance = sum((r - avg_daily_return) ** 2 for r in daily_returns) / len(daily_returns)
        volatility = variance ** 0.5
        
        # Annualize volatility
        annualized_volatility = volatility * (252 ** 0.5)  # Assuming 252 trading days
        
        # Calculate Sharpe ratio (assuming risk-free rate of 0 for simplicity)
        sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility != 0 else 0.0
        
        # Calculate Sortino ratio (using only negative returns for downside deviation)
        negative_returns = [r for r in daily_returns if r < 0]
        downside_variance = sum(r ** 2 for r in negative_returns) / len(daily_returns) if daily_returns else 0
        downside_deviation = downside_variance ** 0.5
        annualized_downside_deviation = downside_deviation * (252 ** 0.5)
        sortino_ratio = annualized_return / annualized_downside_deviation if annualized_downside_deviation != 0 else 0.0
        
        # Calculate max drawdown
        cumulative_returns = [1.0]
        for ret in daily_returns:
            cumulative_returns.append(cumulative_returns[-1] * (1 + ret))
        
        max_drawdown = 0.0
        peak = cumulative_returns[0]
        for value in cumulative_returns:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)

        # Calculate trade metrics
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.get('pnl', 0) > 0)
        losing_trades = sum(1 for t in trades if t.get('pnl', 0) < 0)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0

        # Calculate average win/loss
        winning_pnls = [t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0]
        losing_pnls = [t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0]
        average_win = sum(winning_pnls) / len(winning_pnls) if winning_pnls else 0.0
        average_loss = sum(losing_pnls) / len(losing_pnls) if losing_pnls else 0.0

        # Calculate profit factor
        total_profit = sum(winning_pnls)
        total_loss = abs(sum(losing_pnls))
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')

        # Calculate largest win/loss
        largest_win = max(winning_pnls) if winning_pnls else 0.0
        largest_loss = min(losing_pnls) if losing_pnls else 0.0

        # Calculate average holding period
        holding_periods = [
            (t.get('close_time', end_date) - t.get('open_time', start_date)).days
            for t in trades
            if t.get('close_time') and t.get('open_time')
        ]
        average_holding_period = sum(holding_periods) / len(holding_periods) if holding_periods else 0.0

        # Calculate portfolio turnover
        total_traded_value = sum(abs(t.get('quantity', 0) * t.get('price', 0)) for t in trades)
        portfolio_turnover = total_traded_value / initial_capital if initial_capital > 0 else 0.0

        return CumulativeMetrics(
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            annualized_return=annualized_return,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            average_win=average_win,
            average_loss=average_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            average_holding_period=average_holding_period,
            portfolio_turnover=portfolio_turnover
        ) 