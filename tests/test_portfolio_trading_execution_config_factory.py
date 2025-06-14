"""
Tests for the portfolio trading execution config factory.
"""

import pytest
from src.strategies.portfolio.portfolio_trading_execution_config_factory import PortfolioTradingExecutionConfigFactory
from src.strategies.portfolio.portfolio_trading_execution_config import PortfolioTradingExecutionConfig
from src.config.base_enums import StrategyType
from src.strategies.SingleStock.ma_crossover_strategy import MACrossoverStrategy
from src.strategies.SingleStock.random_forest_strategy import RandomForestStrategy


@pytest.fixture
def factory():
    """Create a factory instance for testing."""
    return PortfolioTradingExecutionConfigFactory()

def test_create_portfolio_config_with_custom_configs(factory):
    """Test creating a portfolio configuration and adding custom strategy configs."""
    config = factory.create_config('test_portfolio 1')
    config.add_ticker('AAPL')
    config.add_strategy_to_ticker('AAPL', StrategyType.MA_CROSSOVER, {'short_window': 5, 'long_window': 20,})
    strategies = config.get_ticker_strategies('AAPL')
    ma_strat = next((s for s in strategies if isinstance(s, MACrossoverStrategy)), None)
    assert ma_strat is not None
    assert ma_strat.config.short_window == 5
    assert ma_strat.config.long_window == 20

def test_create_portfolio_config(factory):
    """Test creating a new portfolio configuration."""
    config = factory.create_config('test_portfolio')
    assert isinstance(config, PortfolioTradingExecutionConfig)
    assert config.portfolio_name == 'test_portfolio'


def test_create_portfolio_config_with_tickers(factory):
    """Test creating a portfolio configuration and adding tickers/strategies."""
    config = factory.create_config('test_portfolio')
    config.add_ticker('AAPL')
    config.add_strategy_to_ticker('AAPL', StrategyType.MA_CROSSOVER)
    config.add_ticker('MSFT')
    config.add_strategy_to_ticker('MSFT', StrategyType.RANDOM_FOREST)
    assert config.get_tickers() == {'AAPL', 'MSFT'}
    assert any(isinstance(s, MACrossoverStrategy) for s in config.get_ticker_strategies('AAPL'))
    assert any(isinstance(s, RandomForestStrategy) for s in config.get_ticker_strategies('MSFT'))





def test_create_portfolio_config_with_invalid_strategy(factory):
    """Test adding an invalid strategy type to a ticker."""
    config = factory.create_config('test_portfolio')
    config.add_ticker('AAPL')
    with pytest.raises(ValueError):
        config.add_strategy_to_ticker('AAPL', 'invalid_strategy')


def test_create_portfolio_config_with_invalid_config(factory):
    """Test adding a strategy with invalid config params."""
    config = factory.create_config('test_portfolio')
    config.add_ticker('AAPL')
    with pytest.raises(TypeError):
        config.add_strategy_to_ticker('AAPL', StrategyType.MA_CROSSOVER, {'invalid_param': 10})


def test_macrossover_config_defaults(factory):
    """Test default configuration for MA Crossover strategy."""
    config = factory.create_config('test_portfolio')
    config.add_ticker('AAPL')
    config.add_strategy_to_ticker('AAPL', StrategyType.MA_CROSSOVER)
    strategies = config.get_ticker_strategies('AAPL')
    ma_strat = next((s for s in strategies if isinstance(s, MACrossoverStrategy)), None)
    assert ma_strat is not None
    assert ma_strat.config.short_window == 10
    assert ma_strat.config.long_window == 50


def test_randomforest_config_defaults(factory):
    """Test default configuration for Random Forest strategy."""
    config = factory.create_config('test_portfolio')
    config.add_ticker('AAPL')
    config.add_strategy_to_ticker('AAPL', StrategyType.RANDOM_FOREST)
    strategies = config.get_ticker_strategies('AAPL')
    rf_strat = next((s for s in strategies if isinstance(s, RandomForestStrategy)), None)
    assert rf_strat is not None
    assert rf_strat.config.n_estimators == 100
    assert rf_strat.config.max_depth == 5 