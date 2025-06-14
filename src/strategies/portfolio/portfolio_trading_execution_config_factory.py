"""
Portfolio Trading Execution Config Factory.
Singleton factory for managing portfolio trading execution configurations.

Example Usage:
    # Get the factory instance
    factory = PortfolioTradingExecutionConfigFactory.get_instance()
    
    # Create a new portfolio config
    ma_portfolio = factory.create_config('ma_crossover_portfolio')
    
    # Add tickers to the portfolio
    ma_portfolio.add_tickers({
        'AAPL': ['ma_crossover', 'random_forest'],
        'MSFT': ['ma_crossover'],
        'GOOGL': ['random_forest']
    })
    
    # Get an existing portfolio config
    portfolio = factory.get_config('ma_crossover_portfolio')
    
    # Get all portfolio names
    portfolios = factory.get_portfolio_names()
"""

from typing import Dict, Optional
from src.strategies.portfolio.portfolio_trading_execution_config import PortfolioTradingExecutionConfig
from src.strategies.strategy_mappings import STRATEGY_CLASSES, StrategyType

class PortfolioTradingExecutionConfigFactory:
    """
    Singleton factory for managing portfolio trading execution configurations.
    
    The factory maintains:
    - Mapping of portfolio names to their configurations
    - Singleton instance for global access
    
    Example structure:
    {
        'ma_crossover_portfolio': PortfolioTradingExecutionConfig instance,
        'hybrid_portfolio': PortfolioTradingExecutionConfig instance
    }
    """
    
    _instance = None
    
    def __new__(cls):
        """
        Ensure only one instance of the factory exists.
        
        Returns:
            Singleton instance of PortfolioTradingExecutionConfigFactory
            
        Example:
            factory = PortfolioTradingExecutionConfigFactory.get_instance()
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._configs: Dict[str, PortfolioTradingExecutionConfig] = {}
            # Create default portfolio configuration
            cls._instance._create_default_portfolio()
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> 'PortfolioTradingExecutionConfigFactory':
        """
        Get the singleton instance of the factory.
        
        Returns:
            Singleton instance of PortfolioTradingExecutionConfigFactory
            
        Example:
            factory = PortfolioTradingExecutionConfigFactory.get_instance()
        """
        return cls()
    
    def create_config(self, portfolio_name: str) -> PortfolioTradingExecutionConfig:
        """
        Create a new portfolio trading execution configuration.
        
        Args:
            portfolio_name: Name of the portfolio (e.g., 'ma_crossover_portfolio')
            
        Returns:
            New PortfolioTradingExecutionConfig instance
            
        Example:
            # Create a new portfolio config
            ma_portfolio = factory.create_config('ma_crossover_portfolio')
        """
        if portfolio_name in self._configs:
            return self._configs[portfolio_name]
        
        config = PortfolioTradingExecutionConfig(portfolio_name)
        self._configs[portfolio_name] = config
        return config
    
    def get_config(self, portfolio_name: str) -> Optional[PortfolioTradingExecutionConfig]:
        """
        Get an existing portfolio trading execution configuration.
        
        Args:
            portfolio_name: Name of the portfolio (e.g., 'ma_crossover_portfolio')
            
        Returns:
            PortfolioTradingExecutionConfig instance if it exists, None otherwise
            
        Example:
            # Get an existing portfolio config
            portfolio = factory.get_config('ma_crossover_portfolio')
        """
        if portfolio_name not in self._configs:
            raise ValueError(f"Portfolio {portfolio_name} does not exist")
        return self._configs.get(portfolio_name)
    
    def get_portfolio_names(self) -> set:
        """
        Get all portfolio names.
        
        Returns:
            Set of portfolio names
            
        Example:
            # Get all portfolio names
            portfolios = factory.get_portfolio_names()
            # Returns: {'ma_crossover_portfolio', 'hybrid_portfolio'}
        """
        return set(self._configs.keys())
    
    def remove_config(self, portfolio_name: str) -> None:
        """
        Remove a portfolio trading execution configuration.
        
        Args:
            portfolio_name: Name of the portfolio to remove
            
        Example:
            # Remove a portfolio config
            factory.remove_config('ma_crossover_portfolio')
        """
        if portfolio_name in self._configs:
            del self._configs[portfolio_name]
    
    # [NEEDS TO BE UPDATED] Ideally this should be done through a config file
    def _create_default_portfolio(self) -> None:
        """Create the default portfolio configuration."""
        default_config = PortfolioTradingExecutionConfig('default_portfolio')
        
        # Add default tickers
        default_tickers = ['AAPL', 'MSFT', 'GOOGL']
        default_config.add_tickers(default_tickers)
        
        # Add default strategies
        default_strategies = {
            'AAPL': [StrategyType.MA_CROSSOVER, StrategyType.RANDOM_FOREST],
            'MSFT': [StrategyType.MA_CROSSOVER, StrategyType.RANDOM_FOREST],
            'GOOGL': [StrategyType.MA_CROSSOVER, StrategyType.RANDOM_FOREST]
        }
        
        for ticker, strategies in default_strategies.items():
            for strategy_type in strategies:
                default_config.add_strategy_to_ticker(ticker, strategy_type)
        
        self._configs['default_portfolio'] = default_config 