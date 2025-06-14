from abc import ABC, abstractmethod
from typing import Dict
from datetime import datetime
from src.config.base_enums import StrategyType
from src.strategies.base_strategy import StrategySignal
from src.config.aggregation_config import AggregationConfig


class BaseAggregator(ABC):
    """
    Base class for signal aggregators.
    
    This class defines the interface for aggregating trading signals from multiple strategies.
    All signals must be StrategySignal objects with the following structure:
    - symbol: str - The stock symbol
    - action: str - One of 'BUY', 'SELL', 'HOLD'
    - probabilities: Dict[str, float] - Probability distribution over actions
    - confidence: float - Confidence level between 0.0 and 1.0
    - timestamp: datetime - When the signal was generated
    - features: Dict - Additional features used to generate the signal
    
    Example usage:
    ```python
    # Create aggregator
    aggregator = BaseAggregator()
    
    # Aggregate signals
    signals = {
        'ma_crossover': StrategySignal(
            symbol='AAPL',
            action='BUY',
            probabilities={'BUY': 0.8, 'SELL': 0.1, 'HOLD': 0.1},
            confidence=0.8,
            timestamp=datetime.now(),
            features={...}
        ),
        'random_forest': StrategySignal(...)
    }
    result = aggregator.aggregate_signals(signals)
    ```
    """
    
    def __init__(self, config: AggregationConfig):
        """
        Initialize the aggregator with configuration.
        
        Args:
            config: Configuration for the aggregator
        """
        self.config = config
    
    def validate_signal(self, signal: StrategySignal) -> None:
        """
        Validate a single signal.
        
        Args:
            signal: The signal to validate
                   Type: StrategySignal
                   Example: StrategySignal(
                       symbol='AAPL',
                       action='BUY',
                       probabilities={'BUY': 0.8, 'SELL': 0.1, 'HOLD': 0.1},
                       confidence=0.8,
                       timestamp=datetime.now(),
                       features={...}
                   )
                   Constraints:
                   - action must be one of 'BUY', 'SELL', 'HOLD'
                   - probabilities must sum to 1.0
                   - confidence must be between 0.0 and 1.0
                   
        Raises:
            ValueError: If signal is invalid
                      Examples:
                      - "Invalid action: INVALID (must be one of BUY, SELL, HOLD)"
                      - "Probabilities must sum to 1.0, got 0.9"
                      - "Confidence must be between 0.0 and 1.0, got 1.5"
        """
        if not isinstance(signal, StrategySignal):
            raise ValueError(f"Signal must be a StrategySignal object, got {type(signal)}")
            
        if signal.action not in ['BUY', 'SELL', 'HOLD']:
            raise ValueError(f"Invalid action: {signal.action} (must be one of BUY, SELL, HOLD)")
            
        if not isinstance(signal.probabilities, dict):
            raise ValueError(f"Probabilities must be a dictionary, got {type(signal.probabilities)}")
            
        if not all(isinstance(p, (int, float)) for p in signal.probabilities.values()):
            raise ValueError("All probabilities must be numeric")
            
        if not all(0 <= p <= 1 for p in signal.probabilities.values()):
            raise ValueError("All probabilities must be between 0.0 and 1.0")
            
        if abs(sum(signal.probabilities.values()) - 1.0) > 1e-6:
            raise ValueError(f"Probabilities must sum to 1.0, got {sum(signal.probabilities.values())}")
            
        if not isinstance(signal.confidence, (int, float)):
            raise ValueError(f"Confidence must be numeric, got {type(signal.confidence)}")
            
        if not 0 <= signal.confidence <= 1:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {signal.confidence}")
            
        if not isinstance(signal.symbol, str):
            raise ValueError(f"Symbol must be a string, got {type(signal.symbol)}")
            
    def validate_signals(self, signals: Dict[StrategyType, StrategySignal]) -> None:
        """
        Validate a dictionary of signals.
        
        Args:
            signals: Dictionary mapping strategy types to their signals
                    Type: Dict[StrategyType, StrategySignal]
                    Example: {
                        StrategyType.MA_CROSSOVER: StrategySignal(
                            symbol='AAPL',
                            action='BUY',
                            probabilities={'BUY': 0.8, 'SELL': 0.1, 'HOLD': 0.1},
                            confidence=0.8,
                            timestamp=datetime.now(),
                            features={...}
                        ),
                        StrategyType.RANDOM_FOREST: StrategySignal(...)
                    }
                    Constraints:
                    - Must be a non-empty dictionary
                    - Keys must be StrategyType enum values
                    - Values must be valid StrategySignal objects
                    - All signals must be for the same symbol
                    
        Raises:
            ValueError: If signals are invalid
                      Examples:
                      - "Signals must be a dictionary, got <class 'list'>"
                      - "Signals dictionary cannot be empty"
                      - "Strategy name must be a StrategyType enum, got <class 'str'>"
                      - "Signal for MA_CROSSOVER must be a StrategySignal object, got <class 'dict'>"
                      - "All signals must be for the same symbol, got AAPL and MSFT"
        """
        if not isinstance(signals, dict):
            raise ValueError(f"Signals must be a dictionary, got {type(signals)}")
            
        if not signals:
            raise ValueError("Signals dictionary cannot be empty")
            
        # Validate each signal
        for strategy, signal in signals.items():
            if not isinstance(strategy, StrategyType):
                raise ValueError(f"Strategy name must be a StrategyType enum, got {type(strategy)}")
                
            self.validate_signal(signal)
            
        # Check that all signals are for the same symbol
        first_symbol = next(iter(signals.values())).symbol
        for strategy, signal in signals.items():
            if signal.symbol != first_symbol:
                raise ValueError(f"All signals must be for the same symbol, got {first_symbol} and {signal.symbol}")
                
    @abstractmethod
    def aggregate_signals(self, signals: Dict[str, StrategySignal]) -> StrategySignal:
        """
        Aggregate multiple signals into a single signal.
        
        Args:
            signals: Dictionary mapping strategy names to their signals
                    Type: Dict[str, StrategySignal]
                    Example: {
                        'ma_crossover': StrategySignal(
                            symbol='AAPL',
                            action='BUY',
                            probabilities={'BUY': 0.8, 'SELL': 0.1, 'HOLD': 0.1},
                            confidence=0.8,
                            timestamp=datetime.now(),
                            features={...}
                        ),
                        'random_forest': StrategySignal(...)
                    }
                    Constraints:
                    - Must be a non-empty dictionary
                    - Keys must be strategy names (strings)
                    - Values must be valid StrategySignal objects
                    - All signals must be for the same symbol
            
        Returns:
            StrategySignal: Aggregated signal object
                          Example: StrategySignal(
                              symbol='AAPL',
                              action='BUY',
                              probabilities={'BUY': 0.65, 'SELL': 0.2, 'HOLD': 0.15},
                              confidence=0.65,
                              timestamp=datetime.now(),
                              features={...}
                          )
                  
        Raises:
            ValueError: If signals have invalid structure or values
                      Examples:
                      - "Signals must be a dictionary, got <class 'list'>"
                      - "Signal for ma_crossover must be a StrategySignal object, got <class 'dict'>"
                      - "Signal for random_forest must be a StrategySignal object, got <class 'dict'>"
        """
        pass 