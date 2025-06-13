"""
Tests for daily metrics tracking.
"""

import pytest
from datetime import datetime
from src.execution.metrics.daily_metrics import DailyMetrics

def test_daily_metrics_initialization():
    """Test DailyMetrics initialization with valid data."""
    date = datetime(2024, 1, 1)
    metrics = DailyMetrics(
        date=date,
        portfolio_value=100000.0,
        cash=50000.0,
        positions_value=50000.0,
        daily_return=0.01,
        daily_pnl=1000.0,
        positions={"AAPL": {"quantity": 10, "avg_price": 150.0}},
        trades=[{"symbol": "AAPL", "quantity": 10, "price": 150.0, "timestamp": date, "is_closed": True, "pnl": 100.0}],
        unrealized_pnl=500.0,
        realized_pnl=100.0,
        num_trades=1,
        winning_trades=1,
        losing_trades=0
    )
    
    assert metrics.date == date
    assert metrics.portfolio_value == 100000.0
    assert metrics.cash == 50000.0
    assert metrics.positions_value == 50000.0
    assert metrics.daily_return == 0.01
    assert metrics.daily_pnl == 1000.0
    assert metrics.num_trades == 1
    assert metrics.winning_trades == 1
    assert metrics.losing_trades == 0
    assert metrics.positions == {"AAPL": {"quantity": 10, "avg_price": 150.0}}
    assert metrics.trades == [{"symbol": "AAPL", "quantity": 10, "price": 150.0, "timestamp": date, "is_closed": True, "pnl": 100.0}]
    assert metrics.unrealized_pnl == 500.0
    assert metrics.realized_pnl == 100.0

def test_daily_metrics_to_dict():
    """Test conversion of DailyMetrics to dictionary."""
    date = datetime(2024, 1, 1)
    metrics = DailyMetrics(
        date=date,
        portfolio_value=100000.0,
        cash=50000.0,
        positions_value=50000.0,
        daily_return=0.01,
        daily_pnl=1000.0,
        positions={"AAPL": {"quantity": 10, "avg_price": 150.0}},
        trades=[{"symbol": "AAPL", "quantity": 10, "price": 150.0, "timestamp": date, "is_closed": True, "pnl": 100.0}],
        unrealized_pnl=500.0,
        realized_pnl=100.0,
        num_trades=1,
        winning_trades=1,
        losing_trades=0
    )
    
    metrics_dict = metrics.to_dict()
    
    assert metrics_dict['date'] == date
    assert metrics_dict['portfolio_value'] == 100000.0
    assert metrics_dict['cash'] == 50000.0
    assert metrics_dict['positions_value'] == 50000.0
    assert metrics_dict['daily_return'] == 0.01
    assert metrics_dict['daily_pnl'] == 1000.0
    assert metrics_dict['num_trades'] == 1
    assert metrics_dict['winning_trades'] == 1
    assert metrics_dict['losing_trades'] == 0
    assert metrics_dict['positions'] == {"AAPL": {"quantity": 10, "avg_price": 150.0}}
    assert metrics_dict['trades'] == [{"symbol": "AAPL", "quantity": 10, "price": 150.0, "timestamp": date, "is_closed": True, "pnl": 100.0}]
    assert metrics_dict['unrealized_pnl'] == 500.0
    assert metrics_dict['realized_pnl'] == 100.0

def test_daily_metrics_zero_values():
    """Test DailyMetrics with zero values."""
    date = datetime(2024, 1, 1)
    metrics = DailyMetrics(
        date=date,
        portfolio_value=0.0,
        cash=0.0,
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
    )
    
    assert metrics.date == date
    assert metrics.portfolio_value == 0.0
    assert metrics.cash == 0.0
    assert metrics.positions_value == 0.0
    assert metrics.daily_return == 0.0
    assert metrics.daily_pnl == 0.0
    assert metrics.num_trades == 0
    assert metrics.winning_trades == 0
    assert metrics.losing_trades == 0
    assert metrics.positions == {}
    assert metrics.trades == []
    assert metrics.unrealized_pnl == 0.0
    assert metrics.realized_pnl == 0.0 