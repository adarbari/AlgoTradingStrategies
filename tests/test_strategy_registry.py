"""
Tests for the portfolio trading execution system.
"""

import pytest
from src.strategies.portfolio.portfolio_trading_execution_config import PortfolioTradingExecutionConfig
from src.strategies.strategy_mappings import StrategyType
from src.strategies.SingleStock.ma_crossover_strategy import MACrossoverStrategy
from src.strategies.SingleStock.random_forest_strategy import RandomForestStrategy


@pytest.fixture
def portfolio_config():
    """Create a portfolio configuration for testing."""
    return PortfolioTradingExecutionConfig('test_portfolio')


def test_create_portfolio_config():
    """Test creating a new portfolio configuration."""
    config = PortfolioTradingExecutionConfig('test_portfolio')
    assert config.portfolio_name == 'test_portfolio'
    assert config.get_tickers() == set()


def test_add_ticker(portfolio_config):
    """Test adding a ticker."""
    portfolio_config.add_ticker('AAPL')
    assert portfolio_config.get_tickers() == {'AAPL'}
    portfolio_config.add_strategy_to_ticker('AAPL', StrategyType.MA_CROSSOVER)
    strategies = portfolio_config.get_ticker_strategies('AAPL')
    assert len(strategies) == 1
    assert isinstance(strategies[0], MACrossoverStrategy)


def test_add_tickers(portfolio_config):
    """Test adding multiple tickers."""
    portfolio_config.add_tickers(['AAPL', 'MSFT'])
    assert portfolio_config.get_tickers() == {'AAPL', 'MSFT'}
    portfolio_config.add_strategy_to_ticker('AAPL', StrategyType.MA_CROSSOVER)
    portfolio_config.add_strategy_to_ticker('MSFT', StrategyType.RANDOM_FOREST)
    assert isinstance(portfolio_config.get_ticker_strategies('AAPL')[0], MACrossoverStrategy)
    assert isinstance(portfolio_config.get_ticker_strategies('MSFT')[0], RandomForestStrategy)


def test_add_strategy_to_ticker(portfolio_config):
    """Test adding a new strategy to an existing ticker."""
    portfolio_config.add_ticker('AAPL')
    portfolio_config.add_strategy_to_ticker('AAPL', StrategyType.MA_CROSSOVER)
    portfolio_config.add_strategy_to_ticker('AAPL', StrategyType.RANDOM_FOREST)
    strategies = portfolio_config.get_ticker_strategies('AAPL')
    assert len(strategies) == 2
    assert isinstance(strategies[0], MACrossoverStrategy)
    assert isinstance(strategies[1], RandomForestStrategy)


def test_get_ticker_strategies(portfolio_config):
    """Test getting all strategies for a ticker."""
    portfolio_config.add_ticker('AAPL')
    portfolio_config.add_strategy_to_ticker('AAPL', StrategyType.MA_CROSSOVER)
    strategies = portfolio_config.get_ticker_strategies('AAPL')
    assert len(strategies) == 1
    assert isinstance(strategies[0], MACrossoverStrategy)


def test_get_strategy_types(portfolio_config):
    """Test getting all strategy types used in the portfolio."""
    portfolio_config.add_ticker('AAPL')
    portfolio_config.add_strategy_to_ticker('AAPL', StrategyType.MA_CROSSOVER)
    portfolio_config.add_strategy_to_ticker('AAPL', StrategyType.RANDOM_FOREST)
    strategies = portfolio_config.get_ticker_strategies('AAPL')
    strategy_types = [s.__class__.__name__ for s in strategies]
    assert 'MACrossoverStrategy' in strategy_types
    assert 'RandomForestStrategy' in strategy_types


def test_invalid_strategy_type(portfolio_config):
    """Test adding a ticker with an invalid strategy type."""
    portfolio_config.add_ticker('AAPL')
    with pytest.raises(ValueError):
        portfolio_config.add_strategy_to_ticker('AAPL', 'invalid_strategy')


def test_add_strategy_to_nonexistent_ticker(portfolio_config):
    """Test adding a strategy to a ticker that doesn't exist."""
    with pytest.raises(ValueError):
        portfolio_config.add_strategy_to_ticker('AAPL', StrategyType.MA_CROSSOVER)


def test_macrossover_config_defaults(portfolio_config):
    """Test default configuration for MA Crossover strategy."""
    portfolio_config.add_ticker('AAPL')
    portfolio_config.add_strategy_to_ticker('AAPL', StrategyType.MA_CROSSOVER)
    strategies = portfolio_config.get_ticker_strategies('AAPL')
    assert len(strategies) == 1
    assert strategies[0].config.short_window == 10
    assert strategies[0].config.long_window == 50


def test_randomforest_config_defaults(portfolio_config):
    """Test default configuration for Random Forest strategy."""
    portfolio_config.add_ticker('AAPL')
    portfolio_config.add_strategy_to_ticker('AAPL', StrategyType.RANDOM_FOREST)
    strategies = portfolio_config.get_ticker_strategies('AAPL')
    assert len(strategies) == 1
    assert strategies[0].config.n_estimators == 100
    assert strategies[0].config.max_depth == 5 