"""
Tests for the PortfolioManager class.
"""

import pytest
from datetime import datetime
import pandas as pd
import numpy as np

from src.execution.portfolio_manager import PortfolioManager

@pytest.fixture
def portfolio_manager():
    """Create a PortfolioManager instance for testing."""
    return PortfolioManager(initial_budget=10000.0)

def test_initialization(portfolio_manager):
    """Test PortfolioManager initialization."""
    assert portfolio_manager.initial_budget == 10000.0
    assert portfolio_manager.cash == 10000.0
    assert portfolio_manager.positions == {}
    assert portfolio_manager.trade_history == []

def test_get_portfolio_value(portfolio_manager):
    """Test portfolio value calculation."""
    # Initial value should equal initial budget
    assert portfolio_manager.get_portfolio_value() == 10000.0
    
    # Add a position
    portfolio_manager.positions['AAPL'] = {
        'quantity': 10,
        'avg_price': 150.0
    }
    
    # Value should include position
    expected_value = 10000.0 + (10 * 150.0)
    assert portfolio_manager.get_portfolio_value() == expected_value

def test_execute_buy(portfolio_manager):
    """Test buy order execution."""
    timestamp = datetime.now()
    
    # Test successful buy
    success = portfolio_manager.execute_buy(
        symbol='AAPL',
        quantity=5,
        price=150.0,
        timestamp=timestamp
    )
    
    assert success is True
    assert portfolio_manager.cash == 10000.0 - (5 * 150.0)
    assert portfolio_manager.positions['AAPL']['quantity'] == 5
    assert portfolio_manager.positions['AAPL']['avg_price'] == 150.0
    assert len(portfolio_manager.trade_history) == 1
    
    # Test insufficient funds
    success = portfolio_manager.execute_buy(
        symbol='AAPL',
        quantity=1000,  # Too many shares
        price=150.0,
        timestamp=timestamp
    )
    
    assert success is False
    assert len(portfolio_manager.trade_history) == 1  # No new trade

def test_execute_sell(portfolio_manager):
    """Test sell order execution."""
    timestamp = datetime.now()
    
    # First buy some shares
    portfolio_manager.execute_buy(
        symbol='AAPL',
        quantity=10,
        price=150.0,
        timestamp=timestamp
    )
    
    # Test successful sell
    success = portfolio_manager.execute_sell(
        symbol='AAPL',
        quantity=5,
        price=160.0,
        timestamp=timestamp
    )
    
    assert success is True
    assert portfolio_manager.cash == 10000.0 - (10 * 150.0) + (5 * 160.0)
    assert portfolio_manager.positions['AAPL']['quantity'] == 5
    assert len(portfolio_manager.trade_history) == 2
    
    # Test insufficient shares
    success = portfolio_manager.execute_sell(
        symbol='AAPL',
        quantity=10,  # Too many shares
        price=160.0,
        timestamp=timestamp
    )
    
    assert success is False
    assert len(portfolio_manager.trade_history) == 2  # No new trade

def test_get_portfolio_summary(portfolio_manager):
    """Test portfolio summary generation."""
    timestamp = datetime.now()
    
    # Add some positions
    portfolio_manager.execute_buy(
        symbol='AAPL',
        quantity=5,
        price=150.0,
        timestamp=timestamp
    )
    
    portfolio_manager.execute_buy(
        symbol='MSFT',
        quantity=3,
        price=200.0,
        timestamp=timestamp
    )
    
    summary = portfolio_manager.get_portfolio_summary()
    
    assert 'cash' in summary
    assert 'positions_value' in summary
    assert 'total_value' in summary
    assert 'return_pct' in summary
    assert 'num_positions' in summary
    assert 'positions' in summary
    
    expected_positions_value = (5 * 150.0) + (3 * 200.0)
    assert summary['positions_value'] == expected_positions_value
    assert summary['num_positions'] == 2

def test_get_trade_history(portfolio_manager):
    """Test trade history retrieval."""
    timestamp = datetime.now()
    
    # Execute some trades
    portfolio_manager.execute_buy(
        symbol='AAPL',
        quantity=5,
        price=150.0,
        timestamp=timestamp
    )
    
    portfolio_manager.execute_sell(
        symbol='AAPL',
        quantity=3,
        price=160.0,
        timestamp=timestamp
    )
    
    history = portfolio_manager.get_trade_history()
    
    assert isinstance(history, pd.DataFrame)
    assert len(history) == 2
    assert all(col in history.columns for col in ['timestamp', 'symbol', 'action', 'quantity', 'price', 'total']) 