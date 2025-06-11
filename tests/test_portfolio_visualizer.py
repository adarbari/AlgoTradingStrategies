import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.visualization.portfolio_visualizer import (
    plot_portfolio_performance,
    plot_trade_distribution,
    plot_backtest_results,
    plot_strategy_comparison
)

@pytest.fixture
def sample_portfolio_data():
    """Create sample portfolio data for testing."""
    dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
    return pd.DataFrame({
        'portfolio_value': np.random.normal(10000, 100, len(dates))
    }, index=dates)

@pytest.fixture
def sample_trades_data():
    """Create sample trades data for testing."""
    dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
    return pd.DataFrame({
        'profit': np.random.normal(100, 20, len(dates)),
        'shares': np.random.randint(1, 100, len(dates))
    }, index=dates)

@pytest.fixture
def sample_backtest_data():
    """Create sample backtest data for testing."""
    dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
    return pd.DataFrame({
        'Price': np.random.normal(150, 2, len(dates)),
        'MA_short': np.random.normal(148, 2, len(dates)),
        'MA_long': np.random.normal(145, 2, len(dates)),
        'Signal': np.random.choice([-1, 0, 1], len(dates)),
        'cash': np.random.normal(10000, 100, len(dates)),
        'shares': np.random.randint(0, 100, len(dates))
    }, index=dates)

@pytest.fixture
def sample_strategy_results():
    """Create sample strategy comparison results."""
    return [
        {
            'Timestamp': datetime(2023, 1, 1),
            'Total Return': 5.2,
            'Win Rate': 65.0,
            'Number of Trades': 100,
            'Total Profit': 5200
        },
        {
            'Timestamp': datetime(2023, 1, 2),
            'Total Return': 4.8,
            'Win Rate': 62.0,
            'Number of Trades': 95,
            'Total Profit': 4800
        }
    ]

@pytest.mark.slow
def test_plot_portfolio_performance(sample_portfolio_data):
    """Test plotting portfolio performance."""
    # Test basic plotting
    plot_portfolio_performance('AAPL', sample_portfolio_data)

@pytest.mark.slow
def test_plot_trade_distribution():
    """Test plotting trade distribution."""
    # Create a mock trades DataFrame with required columns
    trades = pd.DataFrame({
        'profit': [10, -5, 20, 0, 15],
        'shares': [100, 50, 200, 150, 120],
        'cumulative_profit': [10, 5, 25, 25, 40],
        'win': [True, False, True, False, True],
        'win_rate': [1.0, 0.5, 0.67, 0.5, 0.6]
    })
    plot_trade_distribution('AAPL', trades)

@pytest.mark.slow
def test_plot_backtest_results(sample_backtest_data):
    """Test plotting backtest results."""
    # Test basic plotting
    plot_backtest_results('AAPL', sample_backtest_data)

@pytest.mark.slow
def test_plot_strategy_comparison(sample_strategy_results):
    """Test plotting strategy comparison."""
    # Test basic plotting
    plot_strategy_comparison('AAPL', sample_strategy_results)

def test_plot_portfolio_performance_invalid_inputs():
    """Test error handling for invalid inputs."""
    # Test with empty DataFrame
    with pytest.raises(KeyError):
        plot_portfolio_performance(
            symbol='AAPL',
            portfolio_values=pd.DataFrame()
        )

def test_plot_trade_distribution_invalid_inputs():
    """Test error handling for invalid inputs."""
    # Test with empty DataFrame
    with pytest.raises(KeyError):
        plot_trade_distribution(
            symbol='AAPL',
            trades=pd.DataFrame()
        )

def test_plot_backtest_results_invalid_inputs():
    """Test that plotting with empty DataFrame does not raise."""
    # Should not raise
    plot_backtest_results(
        symbol='AAPL',
        df=pd.DataFrame()
    )

def test_plot_strategy_comparison_invalid_inputs():
    """Test that plotting with empty results does not raise."""
    # Should not raise
    plot_strategy_comparison(
        symbol='AAPL',
        results=[]
    ) 