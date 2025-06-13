"""
Tests for cumulative metrics tracking.
"""

import pytest
from datetime import datetime, timedelta
from src.execution.metrics.cumulative_metrics import CumulativeMetrics
from src.execution.metrics.metrics_calculator import MetricsCalculator
from src.execution.metrics.daily_metrics import DailyMetrics

def test_cumulative_metrics_initialization():
    """Test CumulativeMetrics initialization with valid data using the calculator."""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    initial_capital = 100000.0
    final_capital = 110000.0
    # Create dummy daily metrics for two days
    daily_metrics = [
        DailyMetrics(
            date=start_date,
            portfolio_value=100000.0,
            cash=100000.0,
            positions_value=0.0,
            daily_return=0.0,
            daily_pnl=0.0,
            positions={},
            trades=[],
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            num_trades=0,
            winning_trades=0,
            losing_trades=0
        ),
        DailyMetrics(
            date=end_date,
            portfolio_value=final_capital,
            cash=final_capital,
            positions_value=0.0,
            daily_return=0.1,
            daily_pnl=10000.0,
            positions={},
            trades=[],
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            num_trades=0,
            winning_trades=0,
            losing_trades=0
        )
    ]
    trades = []
    calculator = MetricsCalculator()
    metrics = calculator.calculate_cumulative_metrics(
        daily_metrics=daily_metrics,
        initial_capital=initial_capital,
        trades=trades
    )
    assert metrics.start_date == start_date
    assert metrics.end_date == end_date
    assert metrics.initial_capital == initial_capital
    assert metrics.final_capital == final_capital
    assert abs(metrics.total_return - 0.1) < 1e-6
    assert metrics.total_trades == 0
    assert metrics.winning_trades == 0
    assert metrics.losing_trades == 0
    assert metrics.win_rate == 0.0
    assert metrics.profit_factor == float('inf')

def test_cumulative_metrics_to_dict():
    """Test conversion of CumulativeMetrics to dictionary using the calculator."""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    initial_capital = 100000.0
    final_capital = 110000.0
    daily_metrics = [
        DailyMetrics(
            date=start_date,
            portfolio_value=100000.0,
            cash=100000.0,
            positions_value=0.0,
            daily_return=0.0,
            daily_pnl=0.0,
            positions={},
            trades=[],
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            num_trades=0,
            winning_trades=0,
            losing_trades=0
        ),
        DailyMetrics(
            date=end_date,
            portfolio_value=final_capital,
            cash=final_capital,
            positions_value=0.0,
            daily_return=0.1,
            daily_pnl=10000.0,
            positions={},
            trades=[],
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            num_trades=0,
            winning_trades=0,
            losing_trades=0
        )
    ]
    trades = []
    calculator = MetricsCalculator()
    metrics = calculator.calculate_cumulative_metrics(
        daily_metrics=daily_metrics,
        initial_capital=initial_capital,
        trades=trades
    )
    metrics_dict = metrics.to_dict()
    assert metrics_dict['start_date'] == start_date
    assert metrics_dict['end_date'] == end_date
    assert metrics_dict['initial_capital'] == initial_capital
    assert metrics_dict['final_capital'] == final_capital
    assert abs(metrics_dict['total_return'] - 0.1) < 1e-6
    assert metrics_dict['total_trades'] == 0
    assert metrics_dict['winning_trades'] == 0
    assert metrics_dict['losing_trades'] == 0
    assert metrics_dict['win_rate'] == 0.0
    assert metrics_dict['profit_factor'] == float('inf')

def test_cumulative_metrics_zero_trades():
    """Test CumulativeMetrics with zero trades."""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    metrics = CumulativeMetrics(
        start_date=start_date,
        end_date=end_date,
        initial_capital=100000.0,
        final_capital=100000.0,
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
    
    assert metrics.total_return == 0.0
    assert metrics.annualized_return == 0.0
    assert metrics.win_rate == 0.0
    assert metrics.profit_factor == float('inf')  # Division by zero case
    assert metrics.total_trades == 0
    assert metrics.winning_trades == 0
    assert metrics.losing_trades == 0 