"""
Strategy factory for creating and managing ticker-specific strategy instances.
"""

from typing import Dict, Type, List
from src.strategies.base_strategy import BaseStrategy
from src.strategies.SingleStock.ma_crossover_strategy import MACrossoverStrategy
from src.strategies.SingleStock.random_forest_strategy import RandomForestStrategy

class StrategyFactory:
    """Factory class for creating and managing ticker-specific strategy instances."""
    
    def __init__(self):
        """Initialize the strategy factory."""
        self._strategy_instances: Dict[str, Dict[str, BaseStrategy]] = {}
        self._strategy_classes = {
            'ma': MACrossoverStrategy,
            'ml': RandomForestStrategy
        }
    
    def get_strategy(self, symbol: str, strategy_type: str) -> BaseStrategy:
        """Get or create a strategy instance for a specific ticker.
        
        Args:
            symbol: Stock symbol
            strategy_type: Type of strategy ('ma' or 'ml')
            
        Returns:
            Strategy instance specific to the ticker
        """
        if symbol not in self._strategy_instances:
            self._strategy_instances[symbol] = {}
            
        if strategy_type not in self._strategy_instances[symbol]:
            strategy_class = self._strategy_classes.get(strategy_type)
            if strategy_class is None:
                raise ValueError(f"Unknown strategy type: {strategy_type}")
            
            # Create a new instance for this ticker
            self._strategy_instances[symbol][strategy_type] = strategy_class()
            
        return self._strategy_instances[symbol][strategy_type]
    
    def get_all_strategies(self, symbol: str) -> List[BaseStrategy]:
        """Get all strategy instances for a specific ticker.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of strategy instances for the ticker
        """
        if symbol not in self._strategy_instances:
            return []
        return list(self._strategy_instances[symbol].values())
    
    def clear_strategies(self, symbol: str = None):
        """Clear strategy instances.
        
        Args:
            symbol: Optional stock symbol to clear strategies for.
                    If None, clears all strategies.
        """
        if symbol is None:
            self._strategy_instances.clear()
        elif symbol in self._strategy_instances:
            del self._strategy_instances[symbol] 