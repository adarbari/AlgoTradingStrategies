"""
Tests for portfolio management functionality.
"""

import pytest
from datetime import datetime
from src.execution.portfolio_manager import PortfolioManager

@pytest.fixture
def portfolio_manager():
    """Create a PortfolioManager instance for testing."""
    return PortfolioManager(initial_capital=100000.0)

def test_portfolio_manager_initialization():
    """Test PortfolioManager initialization."""
    manager = PortfolioManager(initial_capital=100000.0)
    assert manager.initial_capital == 100000.0
    assert manager.cash == 100000.0
    assert manager.positions == {}
    assert manager.trades == []
    assert manager.daily_metrics == []
    assert manager.cumulative_metrics is None

def test_update_position():
    """Test position update functionality."""
    manager = PortfolioManager(initial_capital=100000.0)
    
    # Buy position
    manager.update_position(
        symbol="AAPL",
        quantity=10,
        price=150.0,
        timestamp=datetime(2024, 1, 1)
    )
    
    assert "AAPL" in manager.positions
    assert manager.positions["AAPL"]["quantity"] == 10
    assert manager.positions["AAPL"]["avg_price"] == 150.0
    assert manager.cash == 98500.0  # 100000 - (10 * 150)
    assert len(manager.trades) == 1
    assert not manager.trades[0]["is_closed"]
    
    # Sell some shares
    manager.update_position(
        symbol="AAPL",
        quantity=-5,
        price=160.0,
        timestamp=datetime(2024, 1, 2)
    )
    
    assert manager.positions["AAPL"]["quantity"] == 5
    assert manager.positions["AAPL"]["avg_price"] == 150.0
    assert manager.cash == 99300.0  # 98500 + (5 * 160)
    assert len(manager.trades) == 2

def test_close_position():
    """Test position closing functionality."""
    manager = PortfolioManager(initial_capital=100000.0)
    
    # Open position
    manager.update_position(
        symbol="AAPL",
        quantity=10,
        price=150.0,
        timestamp=datetime(2024, 1, 1)
    )
    
    # Close position
    manager.close_position(
        symbol="AAPL",
        price=160.0,
        timestamp=datetime(2024, 1, 2)
    )
    
    assert "AAPL" not in manager.positions
    assert manager.cash == 100100.0  # 98500 + (10 * 160)
    assert len(manager.trades) == 1
    assert manager.trades[0]["is_closed"]
    assert manager.trades[0]["pnl"] == 100.0  # (160 - 150) * 10

def test_get_portfolio_value():
    """Test portfolio value calculation."""
    manager = PortfolioManager(initial_capital=100000.0)
    
    # Update position
    manager.update_position(
        symbol="AAPL",
        quantity=10,
        price=150.0,
        timestamp=datetime(2024, 1, 1)
    )
    
    current_prices = {"AAPL": 160.0}
    portfolio_value = manager.get_portfolio_value(current_prices)
    
    assert portfolio_value == 100100.0  # 98500 + (10 * 160)

def test_update_daily_metrics():
    """Test daily metrics update."""
    manager = PortfolioManager(initial_capital=100000.0)
    
    # Update position
    manager.update_position(
        symbol="AAPL",
        quantity=10,
        price=150.0,
        timestamp=datetime(2024, 1, 1)
    )
    
    current_prices = {"AAPL": 160.0}
    manager.update_daily_metrics(
        date=datetime(2024, 1, 1),
        current_prices=current_prices
    )
    
    assert len(manager.daily_metrics) == 1
    metrics = manager.daily_metrics[0]
    assert metrics.portfolio_value == 100100.0
    assert metrics.cash == 98500.0
    assert metrics.positions_value == 1600.0
    assert metrics.daily_return == 0.0  # First day, no previous value
    assert metrics.daily_pnl == 0.0  # First day, no previous value
    assert metrics.unrealized_pnl == 100.0  # (160 - 150) * 10
    assert metrics.realized_pnl == 0.0  # No closed trades
    assert metrics.num_trades == 1
    assert metrics.winning_trades == 0
    assert metrics.losing_trades == 0 