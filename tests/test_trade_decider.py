"""
Tests for the TradeDecider class.
"""

import pytest
from datetime import datetime
import pandas as pd
import numpy as np

from src.execution.portfolio_manager import PortfolioManager
from src.execution.trade_decider import TradeDecider, StrategySignal

@pytest.fixture
def portfolio_manager():
    """Create a PortfolioManager instance for testing."""
    return PortfolioManager(initial_budget=10000.0)

@pytest.fixture
def trade_decider(portfolio_manager):
    """Create a TradeDecider instance for testing."""
    return TradeDecider(
        portfolio_manager=portfolio_manager,
        min_confidence=0.6,
        max_positions=3,
        position_size_pct=0.2
    )

@pytest.fixture
def sample_signals():
    """Create sample strategy signals for testing."""
    timestamp = datetime.now()
    
    # Create signals for AAPL
    aapl_signals = [
        StrategySignal(
            timestamp=timestamp,
            symbol='AAPL',
            features={'price': 150.0},
            probabilities={'BUY': 0.8, 'SELL': 0.1, 'HOLD': 0.1},
            confidence=0.8
        ),
        StrategySignal(
            timestamp=timestamp,
            symbol='AAPL',
            features={'price': 150.0},
            probabilities={'BUY': 0.7, 'SELL': 0.2, 'HOLD': 0.1},
            confidence=0.7
        )
    ]
    
    # Create signals for MSFT
    msft_signals = [
        StrategySignal(
            timestamp=timestamp,
            symbol='MSFT',
            features={'price': 200.0},
            probabilities={'BUY': 0.3, 'SELL': 0.6, 'HOLD': 0.1},
            confidence=0.6
        )
    ]
    
    return {
        'AAPL': aapl_signals,
        'MSFT': msft_signals
    }

def test_initialization(trade_decider):
    """Test TradeDecider initialization."""
    assert trade_decider.min_confidence == 0.6
    assert trade_decider.max_positions == 3
    assert trade_decider.position_size_pct == 0.2
    assert isinstance(trade_decider.portfolio_manager, PortfolioManager)

@pytest.mark.slow
def test_aggregate_signals(trade_decider, sample_signals):
    """Test signal aggregation."""
    # Test AAPL signals
    aapl_probs = trade_decider._aggregate_signals(sample_signals['AAPL'])
    
    # Should be weighted average of probabilities
    assert aapl_probs['BUY'] > 0.7  # Both signals suggest buy
    assert aapl_probs['SELL'] < 0.2  # Low sell probability
    assert aapl_probs['HOLD'] < 0.2  # Low hold probability
    
    # Test MSFT signals
    msft_probs = trade_decider._aggregate_signals(sample_signals['MSFT'])
    
    assert msft_probs['SELL'] > 0.5  # Strong sell signal
    assert msft_probs['BUY'] < 0.4  # Low buy probability

def test_calculate_position_size(trade_decider):
    """Test position size calculation."""
    # Test with different prices
    assert trade_decider._calculate_position_size(100.0) == 20  # 20% of 10000 = 2000, so 20 shares
    assert trade_decider._calculate_position_size(200.0) == 10  # 20% of 10000 = 2000, so 10 shares
    assert trade_decider._calculate_position_size(50.0) == 40   # 20% of 10000 = 2000, so 40 shares

@pytest.mark.slow
def test_decide_trades(trade_decider, sample_signals):
    """Test trade decision making."""
    current_prices = {
        'AAPL': 150.0,
        'MSFT': 200.0
    }
    
    # First add a position for MSFT so we can test selling it
    trade_decider.portfolio_manager.execute_buy(
        symbol='MSFT',
        quantity=10,
        price=200.0,
        timestamp=datetime.now()
    )
    
    decisions = trade_decider.decide_trades(sample_signals, current_prices)
    
    # Should have decisions for both symbols
    assert len(decisions) > 0
    
    # Check AAPL decision (should be buy)
    aapl_decision = next(d for d in decisions if d['symbol'] == 'AAPL')
    assert aapl_decision['action'] == 'BUY'
    assert aapl_decision['price'] == 150.0
    assert aapl_decision['quantity'] > 0
    
    # Check MSFT decision (should be sell)
    msft_decision = next(d for d in decisions if d['symbol'] == 'MSFT')
    assert msft_decision['action'] == 'SELL'
    assert msft_decision['price'] == 200.0
    assert msft_decision['quantity'] == 10  # Should sell all shares

def test_execute_trades(trade_decider, sample_signals):
    """Test trade execution."""
    current_prices = {
        'AAPL': 150.0,
        'MSFT': 200.0
    }
    
    # First buy some MSFT shares
    trade_decider.portfolio_manager.execute_buy(
        symbol='MSFT',
        quantity=10,
        price=200.0,
        timestamp=datetime.now()
    )
    
    # Get trade decisions
    decisions = trade_decider.decide_trades(sample_signals, current_prices)
    
    # Execute trades
    executed_trades = trade_decider.execute_trades(decisions, datetime.now())
    
    # Check execution results
    assert len(executed_trades) > 0
    
    # Check AAPL buy execution
    aapl_trade = next(t for t in executed_trades if t['symbol'] == 'AAPL')
    assert aapl_trade['status'] == 'EXECUTED'
    assert aapl_trade['action'] == 'BUY'
    
    # Check MSFT sell execution
    msft_trade = next(t for t in executed_trades if t['symbol'] == 'MSFT')
    assert msft_trade['status'] == 'EXECUTED'
    assert msft_trade['action'] == 'SELL'

def test_max_positions_constraint(trade_decider, sample_signals):
    """Test maximum positions constraint."""
    current_prices = {
        'AAPL': 150.0,
        'MSFT': 200.0,
        'GOOGL': 250.0,
        'AMZN': 300.0
    }
    
    # Create signals for all symbols
    all_signals = {
        'AAPL': sample_signals['AAPL'],
        'MSFT': sample_signals['MSFT'],
        'GOOGL': sample_signals['AAPL'],  # Reuse AAPL signals
        'AMZN': sample_signals['AAPL']   # Reuse AAPL signals
    }
    
    # Get trade decisions
    decisions = trade_decider.decide_trades(all_signals, current_prices)
    
    # Should not exceed max_positions (3)
    buy_decisions = [d for d in decisions if d['action'] == 'BUY']
    assert len(buy_decisions) <= trade_decider.max_positions 