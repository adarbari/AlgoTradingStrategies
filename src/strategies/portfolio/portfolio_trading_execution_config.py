"""
Portfolio Trading Execution Configuration.
"""

from typing import Dict, List, Any, Optional, Set
from src.config.aggregation_config import AggregationConfig
from src.config.strategy_config import MACrossoverConfig, RandomForestConfig
from src.execution.signal_aggregation.base_aggregator import BaseAggregator
from src.strategies.strategy_mappings import STRATEGY_CLASSES, CONFIG_CLASSES
from src.strategies.base_strategy import BaseStrategy
import logging
from src.execution.signal_aggregation.aggregator_mappings import AGGREGATOR_CLASSES
from src.config.base_enums import AggregatorType

class PortfolioTradingExecutionConfig:
    """
    Configuration for portfolio trading execution.
    """

    def __init__(self, name: str):
        """
        Initialize portfolio trading execution configuration.

        Args:
            name (str): Name of the portfolio configuration
        """
        # Name of the portfolio configuration
        self.portfolio_name = name
        
        # List of tickers in the portfolio
        self.tickers: List[str] = []
        
        # Dictionary mapping tickers to their list of strategy instances
        # Example: {
        #     'AAPL': [MACrossoverStrategy(config1), RandomForestStrategy(config2)],
        #     'MSFT': [MACrossoverStrategy(config3)]
        # }
        self.ticker_strategies: Dict[str, List[BaseStrategy]] = {}

        # Dictionary mapping tickers to their list of aggregator instances
        # Example: {
        #     'AAPL': WeightedAverageAggregator(config1),
        #     'MSFT': WeightedAverageAggregator(config2)
        # }
        self.ticker_aggregators: Dict[str, BaseAggregator] = {}

    def add_ticker(self, ticker: str) -> None:
        """
        Add a ticker to the portfolio.
        
        Args:
            ticker (str): The ticker symbol to add
            strategy_type (Optional[str]): The strategy type to add for this ticker
        """
        if ticker not in self.tickers:
            self.tickers.append(ticker)
            self.ticker_strategies[ticker] = []

    def add_tickers(self, tickers: List[str]) -> None:
        """
        Add multiple tickers with their strategies to the portfolio.
        
        Args:
            tickers (Dict[str, str]): Dictionary mapping tickers to their strategy types
        """
        for ticker in tickers:
            self.add_ticker(ticker)

    def add_strategy_to_ticker(self, ticker: str, strategy_type: str, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a strategy to a ticker.
        
        Args:
            ticker (str): The ticker symbol
            strategy_type (str): The type of strategy to add
            config (Optional[Dict[str, Any]]): Optional configuration for the strategy
        """
        if ticker not in self.tickers:
            raise ValueError(f"Ticker {ticker} not in portfolio.")
        if strategy_type not in STRATEGY_CLASSES:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        
        # Create strategy instance with config
        if config:
            logging.info(f"Adding strategy {strategy_type} to ticker {ticker} with config: {config}")
            # Instantiate the config dataclass with the provided config dict (overrides defaults)
            strategy_config = CONFIG_CLASSES[strategy_type](**config)
            logging.info(f"Instantiated config: {strategy_config}")
            print(f"Config dictionary type: {type(config)}, contents: {config}")
            print(f"Instantiated config: {strategy_config}")
        else:
            logging.info(f"Adding strategy {strategy_type} to ticker {ticker} with default config.")
            strategy_config = CONFIG_CLASSES[strategy_type]()
        
        # Pass config as a positional argument instead of a keyword argument
        strategy_instance = STRATEGY_CLASSES[strategy_type](strategy_config)
        logging.info(f"Created strategy instance: {strategy_instance}")
        print(f"Strategy instance config: {strategy_instance.config}")
        
        # Check if we already have a strategy of this type for this ticker
        existing_strategies = [s for s in self.ticker_strategies[ticker] if s.__class__ == STRATEGY_CLASSES[strategy_type]]
        if not existing_strategies:
            self.ticker_strategies[ticker].append(strategy_instance)

    def add_ticker_signal_aggregator(self, ticker: str, aggregator_type: AggregatorType, config: AggregationConfig) -> None:
        """
        Add a signal aggregator to the portfolio.
        
        Args:
            aggregator_type (str): The type of aggregator to add
            config (Optional[Dict[str, Any]]): Optional configuration for the aggregator
        """
        if ticker not in self.tickers:
            raise ValueError(f"Ticker {ticker} not in portfolio.")
        
        
        if aggregator_type not in AggregatorType.__members__.values():
            raise ValueError(f"Unknown aggregator type: {aggregator_type}")
        
        # Create aggregator instance with config
        aggregator_class = AGGREGATOR_CLASSES[aggregator_type]
        if aggregator_class is None:
            raise ValueError(f"Unknown aggregator type: {aggregator_type}")
        aggregator_instance = aggregator_class(config)
        if ticker not in self.ticker_aggregators:
            self.ticker_aggregators[ticker] = aggregator_instance
        else:
            raise ValueError(f"Aggregator for ticker {ticker} already exists.")

    def get_tickers(self) -> Set[str]:
        """Get all tickers in the portfolio."""
        return set(self.tickers)

    def get_ticker_strategies(self, ticker: str) -> List[BaseStrategy]:
        """Get strategy instances for a ticker."""
        if ticker not in self.tickers:
            raise ValueError(f"Ticker {ticker} not in portfolio.")
        return self.ticker_strategies[ticker]
    
    def get_ticker_signal_aggregator(self, ticker: str) -> BaseAggregator:
        """Get the signal aggregator for a ticker."""
        if ticker not in self.tickers:
            raise ValueError(f"Ticker {ticker} not in portfolio.")
        return self.ticker_aggregators[ticker]
    
    
    
            
