"""
Tests for metrics calculation functionality.
"""

import pytest
from datetime import datetime
import pandas as pd
from src.execution.metrics.metrics_calculator import MetricsCalculator
from src.execution.metrics.daily_metrics import DailyMetrics

def test_calculate_daily_metrics():
    """Test calculation of daily metrics."""
    calculator = MetricsCalculator()
    
    # Create sample data
    date = datetime(2024, 1, 1)
    portfolio_value = 100000.0
    cash = 50000.0
    positions = {"AAPL": {"quantity": 10, "avg_price": 150.0}}
    trades = [{"symbol": "AAPL", "quantity": 10, "price": 150.0, "timestamp": date, "is_closed": True, "pnl": 100.0}]
    current_prices = {"AAPL": 160.0}
    previous_portfolio_value = 99000.0

    metrics = calculator.calculate_daily_metrics(
        date=date,
        portfolio_value=portfolio_value,
        cash=cash,
        positions=positions,
        trades=trades,
        previous_portfolio_value=previous_portfolio_value,
        current_prices=current_prices
    )
    
    assert metrics.date == date
    assert metrics.portfolio_value == portfolio_value
    assert metrics.cash == cash
    assert metrics.positions == positions
    assert metrics.trades == trades
    assert metrics.num_trades == 1
    assert metrics.winning_trades == 1
    assert metrics.losing_trades == 0
    assert metrics.unrealized_pnl == (160.0 - 150.0) * 10
    assert metrics.realized_pnl == 100.0
    assert metrics.daily_return == (portfolio_value - previous_portfolio_value) / previous_portfolio_value
    assert metrics.daily_pnl == portfolio_value - previous_portfolio_value

def test_calculate_cumulative_metrics():
    """Test calculation of cumulative metrics."""
    calculator = MetricsCalculator()
    
    # Create sample daily metrics
    dates = pd.date_range(start='2024-01-01', end='2024-01-10', freq='D')
    daily_returns = [0.001, -0.002, 0.003, -0.001, 0.002, 0.001, -0.003, 0.002, 0.001, 0.002]
    
    daily_metrics = [
        DailyMetrics(
            date=date,
            portfolio_value=100000.0 * (1 + ret),
            cash=50000.0,
            positions_value=50000.0 * (1 + ret),
            daily_return=ret,
            daily_pnl=100000.0 * ret,
            positions={},
            trades=[],
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            num_trades=2,
            winning_trades=1,
            losing_trades=1
        )
        for date, ret in zip(dates, daily_returns)
    ]
    
    # Create sample trades
    trades = [
        {
            "symbol": "AAPL",
            "quantity": 10,
            "price": 150.0,
            "timestamp": dates[0],
            "is_closed": True,
            "pnl": 100.0,
            "open_time": dates[0],
            "close_time": dates[1]
        },
        {
            "symbol": "MSFT",
            "quantity": 5,
            "price": 200.0,
            "timestamp": dates[1],
            "is_closed": True,
            "pnl": -50.0,
            "open_time": dates[1],
            "close_time": dates[2]
        }
    ]
    
    metrics = calculator.calculate_cumulative_metrics(
        daily_metrics=daily_metrics,
        initial_capital=100000.0,
        trades=trades
    )
    
    assert metrics is not None
    assert metrics.start_date == dates[0]
    assert metrics.end_date == dates[-1]
    assert metrics.initial_capital == 100000.0
    assert abs(metrics.total_return - 0.002) < 1e-6  # Actual calculated value
    assert metrics.total_trades == 2
    assert metrics.winning_trades == 1
    assert metrics.losing_trades == 1
    assert metrics.average_win == 100.0
    assert metrics.average_loss == -50.0
    assert metrics.largest_win == 100.0
    assert metrics.largest_loss == -50.0
    assert metrics.average_holding_period == 1.0
    assert metrics.portfolio_turnover == 0.025

def test_calculate_cumulative_metrics_empty():
    """Test calculation of cumulative metrics with empty data."""
    calculator = MetricsCalculator()
    metrics = calculator.calculate_cumulative_metrics(
        daily_metrics=[],
        initial_capital=100000.0,
        trades=[]
    )
    assert metrics is None

def test_calculate_cumulative_metrics_single_day():
    """Test calculation of cumulative metrics with single day of data."""
    calculator = MetricsCalculator()
    date = datetime(2024, 1, 1)
    
    daily_metrics = [
        DailyMetrics(
            date=date,
            portfolio_value=101000.0,
            cash=50000.0,
            positions_value=51000.0,
            daily_return=0.01,
            daily_pnl=1000.0,
            positions={},
            trades=[],
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            num_trades=1,
            winning_trades=1,
            losing_trades=0
        )
    ]
    
    trades = [
        {
            "symbol": "AAPL",
            "quantity": 10,
            "price": 150.0,
            "timestamp": date,
            "is_closed": True,
            "pnl": 100.0,
            "open_time": date,
            "close_time": date
        }
    ]
    
    metrics = calculator.calculate_cumulative_metrics(
        daily_metrics=daily_metrics,
        initial_capital=100000.0,
        trades=trades
    )
    
    assert metrics is not None
    assert metrics.start_date == date
    assert metrics.end_date == date
    assert metrics.initial_capital == 100000.0
    assert metrics.final_capital == 101000.0
    assert abs(metrics.total_return - 0.01) < 0.001
    assert metrics.total_trades == 1
    assert metrics.winning_trades == 1
    assert metrics.losing_trades == 0 