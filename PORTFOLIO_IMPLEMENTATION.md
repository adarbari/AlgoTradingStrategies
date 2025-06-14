# Portfolio Trading System Implementation Plan

## Overview
This document outlines the implementation plan for adding portfolio trading capabilities to our algorithmic trading system. The plan is designed to be incremental, with each phase building on the previous one while maintaining backward compatibility.

## Current Architecture
```
src/
├── execution/           # Trade execution and portfolio management
│   ├── portfolio_manager.py
│   ├── trade_executor.py
│   └── metrics/
├── features/           # Feature engineering and storage
├── strategies/         # Trading strategies
│   ├── base_strategy.py
│   └── SingleStock/    # Single stock strategies
└── run_trading_system.py
```

## Key Principles
1. **Backward Compatibility**: Existing code continues to work
2. **Configurability**: New components are configurable via YAML/JSON
3. **Minimal Changes**: Each phase modifies few existing files
4. **Independent Testing**: Each phase includes its own tests
5. **Clear Boundaries**: Each phase has a specific purpose
6. **Comprehensive Documentation**: All variables and complex data structures must be documented with examples

## Documentation Standards

### Variable Documentation
Every variable in the codebase should be documented with:
1. **Purpose**: What the variable represents
2. **Type**: The data type and structure
3. **Example**: A concrete example of the variable's value
4. **Constraints**: Any validation rules or constraints

Example:
```python
# Good documentation
class SignalAggregator:
    def aggregate_signals(self, signals: Dict[str, float], weights: Optional[Dict[str, float]] = None) -> float:
        """
        Aggregate multiple trading signals into a single signal.
        
        Args:
            signals: Dictionary mapping strategy names to their signals
                    Type: Dict[str, float]
                    Example: {
                        'ma_crossover': 1.0,     # Strong buy signal from MA strategy
                        'random_forest': -0.5,   # Moderate sell signal from RF strategy
                        'rsi': 0.0              # Neutral signal from RSI strategy
                    }
                    Constraints: 
                    - Keys must be strategy names (strings)
                    - Values must be between -1.0 and 1.0
                    
            weights: Optional dictionary mapping strategy names to their weights
                    Type: Dict[str, float]
                    Example: {
                        'ma_crossover': 0.5,     # 50% weight for MA strategy
                        'random_forest': 0.3,    # 30% weight for RF strategy
                        'rsi': 0.2              # 20% weight for RSI strategy
                    }
                    Constraints:
                    - Keys must match strategy names in signals
                    - Values must be non-negative
                    - Sum of weights should be 1.0 (will be normalized)
        
        Returns:
            float: Aggregated signal value between -1.0 and 1.0
                  Example: 0.35 (weighted average of signals)
        """
```

### Complex Data Structure Documentation
For complex data structures (e.g., nested dictionaries, custom classes), include:
1. **Structure Diagram**: Visual representation of the data structure
2. **Field Descriptions**: Purpose and constraints for each field
3. **Usage Examples**: Common operations and transformations
4. **Validation Rules**: How to validate the structure

Example:
```python
class PortfolioConfig:
    """
    Configuration for a portfolio trading strategy.
    
    Structure:
    {
        'name': str,                    # Portfolio name
        'stocks': List[str],            # List of stock symbols
        'strategies': {                 # Strategy configuration per stock
            'AAPL': {                   # Stock symbol
                'ma_crossover': {       # Strategy name
                    'weight': 0.6,      # Strategy weight
                    'params': {         # Strategy parameters
                        'short_window': 10,
                        'long_window': 50
                    }
                },
                'random_forest': {
                    'weight': 0.4,
                    'params': {
                        'n_estimators': 100,
                        'max_depth': 5
                    }
                }
            }
        }
    }
    
    Example:
    config = PortfolioConfig({
        'name': 'tech_portfolio',
        'stocks': ['AAPL', 'MSFT', 'GOOGL'],
        'strategies': {
            'AAPL': {
                'ma_crossover': {
                    'weight': 0.6,
                    'params': {
                        'short_window': 10,
                        'long_window': 50
                    }
                },
                'random_forest': {
                    'weight': 0.4,
                    'params': {
                        'n_estimators': 100,
                        'max_depth': 5
                    }
                }
            }
        }
    })
    """
```

### Documentation Requirements
1. **Class Variables**: Document all class variables with their purpose and constraints
2. **Method Parameters**: Document each parameter with type, purpose, and example
3. **Return Values**: Document return types and possible values
4. **Exceptions**: Document all possible exceptions and their causes
5. **Complex Logic**: Add comments explaining complex algorithms or business rules

### Documentation Tools
1. **Type Hints**: Use Python type hints for all variables and parameters
2. **Docstrings**: Use Google-style docstrings with Args, Returns, and Raises sections
3. **Examples**: Include runnable examples in docstrings
4. **Validation**: Document validation rules and constraints

## Implementation Phases

### Phase 1: Strategy Registry ✅
**Purpose**: Make strategy creation configurable and dynamic
**Status**: Completed

**Changes Implemented**:
1. Created strategy registry system
   - Created: src/strategies/strategy_mappings.py
     - Added STRATEGY_CLASSES mapping for strategy type to class mapping
     - Added CONFIG_CLASSES mapping for strategy type to config class mapping
   - Created: src/strategies/portfolio/portfolio_trading_execution_config.py
     - Implemented portfolio configuration management
     - Added ticker and strategy management
   - Created: src/strategies/portfolio/portfolio_trading_execution_config_factory.py
     - Implemented factory pattern for creating portfolio configurations
     - Added support for custom strategy configurations
   - Removed: src/strategies/strategy_factory.py (replaced with new implementation)

2. Updated configuration system
   - Modified: src/config/strategy_config.py
     - Added support for strategy type enums
     - Updated configuration classes for strategies

3. Added comprehensive test suite
   - Created: tests/test_portfolio_trading_execution_config_factory.py
   - Created: tests/test_strategy_config.py
   - Created: tests/test_strategy_registry.py
   - Created: tests/test_strategy_registry_config.py

**Testing Completed**:
- Unit tests for portfolio configuration
- Unit tests for strategy mappings
- Integration tests with existing strategies
- Configuration loading tests
- All tests passing (92 tests total)

**Next Steps**:
- Proceed with Phase 2: Single Stock Signal Aggregator
- Begin refactoring trade_executor.py into signal aggregator

### Phase 2: Single Stock Signal Aggregator ✅
**Purpose**: Separate signal generation from trade execution and establish foundation for different aggregation strategies
**Status**: Completed

**Changes Implemented**:
1. Created signal aggregation system
   - Created: src/execution/signal_aggregation/
     - New: base_aggregator.py
       - Abstract base class for all aggregators
       - Standardized signal format
       - Common aggregation utilities
     - New: weighted_average_aggregator.py
       - Weighted by strategy confidence
       - Handles both numeric and string signals
       - Probability-based aggregation
     - New: aggregator_mappings.py
       - Maps aggregator types to their implementations
       - Provides factory pattern for aggregator creation

2. Created configuration system
   - Created: src/config/aggregation_config.py
     - BaseAggregationConfig for common settings
     - WeightedAverageConfig for weighted aggregation
     - Configuration validation and defaults

3. Added comprehensive test suite
   - Created: tests/test_signal_aggregation.py
     - Tests for weighted average aggregator
     - Tests for probability calculations
     - Tests for signal conversion
     - Tests for configuration loading

**Testing Completed**:
- Unit tests for weighted average aggregator
- Integration tests with existing strategies
- Configuration loading tests
- All tests passing

**Next Steps**:
- Proceed with Phase 3: Advanced Signal Aggregation
- Begin implementation of ML-based aggregator

### Phase 3: Advanced Signal Aggregation
**Purpose**: Add more sophisticated signal aggregation methods

**Changes**:
1. Add ML-based aggregator
   - New: src/execution/signal_aggregation/ml_based_aggregator.py
     - Machine learning based aggregation
     - Adaptive weights based on performance
     - Feature engineering for ML model
   - New: src/config/aggregation_config.py
     - MLModelConfig for ML-based aggregation
     - Model parameters and training settings

2. Add volatility-adjusted aggregator
   - New: src/execution/signal_aggregation/volatility_adjusted_aggregator.py
     - Adjusts signals based on stock volatility
     - Reduces signal strength in high volatility
     - Dynamic risk adjustment
   - New: src/config/aggregation_config.py
     - VolatilityConfig for volatility-based adjustments
     - Risk parameters and thresholds

3. Update aggregator mappings
   - Extend: src/execution/signal_aggregation/aggregator_mappings.py
     - Add ML-based aggregator mapping
     - Add volatility-adjusted aggregator mapping
     - Update factory pattern

**Testing**:
- Unit tests for ML-based aggregator
- Unit tests for volatility-adjusted aggregator
- Integration tests with existing strategies
- Performance comparison tests

### Phase 4: Trade Execution System
**Purpose**: Implement portfolio-level trade execution

**Changes**:
1. Create trade execution system
   - Create: src/execution/trade_execution/
     - New: base_executor.py
       - Abstract base class for all executors
       - Portfolio-level decision making
       - Common execution utilities
     - New: simple_portfolio_executor.py
       - Basic position sizing
       - Simple risk checks
     - New: risk_budget_executor.py
       - Risk-based position sizing
       - Portfolio-level risk management

2. Update configuration
   - New: src/config/execution_config.py
     - Executor type selection
     - Risk parameters
     - Position sizing rules

**Testing**:
- Unit tests for each executor type
- Integration tests with signal aggregators
- End-to-end execution tests

### Phase 5: Portfolio Strategy Base
**Purpose**: Establish foundation for portfolio strategies

**Changes**:
1. Create portfolio strategy foundation
   - New: src/strategies/portfolio/base_portfolio_strategy.py
     - Extend existing portfolio_trading_execution_config.py
     - Add strategy management
     - Add signal aggregation interface
   - New: src/strategies/portfolio/portfolio_strategy_registry.py
     - Portfolio strategy registration
     - Configuration validation
   - Update: src/strategies/portfolio/portfolio_trading_execution_config.py
     - Add strategy combination support
     - Add allocation rules

**Testing**:
- Unit tests for base portfolio strategy
- Configuration validation tests
- Integration tests with signal aggregator

### Phase 6: Portfolio Signal Aggregation and Trade Selection
**Purpose**: Enable portfolio-level signal aggregation and trade execution

**Changes**:
1. Implement signal aggregation
   - Create: src/strategies/portfolio/aggregation/
     - New: base_aggregator.py
     - New: weighted_aggregator.py
     - New: portfolio_signal_aggregator.py

2. Implement trade selection
   - Create: src/strategies/portfolio/execution/
     - New: trade_selector.py
     - New: portfolio_trade_executor.py

3. Update configuration
   - New: src/config/portfolio_execution_config.py
     - Aggregation rules
     - Trade selection rules
     - Execution constraints

**Testing**:
- Unit tests for aggregators
- Unit tests for trade selection
- Integration tests with portfolio strategies

### Phase 7: Portfolio Strategy Implementation
**Purpose**: Implement concrete portfolio strategies

**Changes**:
1. Create portfolio strategy implementations
   - Create: src/strategies/portfolio/strategies/
     - New: ma_crossover_portfolio.py
     - New: hybrid_portfolio.py
     - New: multi_strategy_portfolio.py

2. Add strategy configurations
   - New: config/portfolio_strategies/
     - ma_crossover.yaml
     - hybrid.yaml
     - multi_strategy.yaml

3. Update strategy registry
   - Add portfolio strategy support
   - Add strategy combination support

**Testing**:
- Unit tests for each portfolio strategy
- Integration tests with all components
- End-to-end tests with example data

### Phase 8: Benchmark Runner
**Purpose**: Reuse existing code for portfolio benchmarking

**Changes**:
1. Refactor existing benchmark code
   - Move: src/utils/run_manager.py -> src/benchmark/benchmark_runner.py
   - Extract: Data splitting logic
   - Reuse: Existing metrics calculation
   - Reuse: Existing visualization

2. Add portfolio-specific features
   - New: src/benchmark/portfolio_benchmark.py
   - New: src/benchmark/portfolio_metrics.py

**Testing**:
- Unit tests for new components
- Integration tests with existing code
- End-to-end benchmark tests

### Phase 9: Performance Comparison
**Purpose**: Enable strategy comparison and visualization

**Changes**:
- New: src/benchmark/comparison/metrics_comparator.py
- New: src/benchmark/comparison/visualization.py
- New: src/config/comparison_config.py

**Testing**:
- Unit tests for comparison tools
- Integration tests with benchmark runner

## Configuration Examples

### Strategy Registry
```yaml
strategies:
  ma_crossover:
    type: "MACrossoverStrategy"
    params:
      short_window: 10
      long_window: 50
  random_forest:
    type: "RandomForestStrategy"
    params:
      n_estimators: 100
      max_depth: 5
```

### Portfolio Strategy
```yaml
portfolio_strategies:
  ma_portfolio:
    type: "MACrossoverPortfolio"
    stocks: ["AAPL", "MSFT", "GOOGL"]
    strategies:
      AAPL: "ma_crossover"
      MSFT: "ma_crossover"
      GOOGL: "ma_crossover"
    allocation:
      AAPL: 0.4
      MSFT: 0.3
      GOOGL: 0.3

  hybrid_portfolio:
    type: "HybridPortfolio"
    stocks: ["AAPL", "MSFT", "GOOGL"]
    strategies:
      AAPL: "random_forest"
      MSFT: "ma_crossover"
      GOOGL: "ma_crossover"
    allocation:
      AAPL: 0.4
      MSFT: 0.3
      GOOGL: 0.3
    aggregation:
      type: "weighted"
      weights:
        random_forest: 0.6
        ma_crossover: 0.4
```

## Testing Strategy
For each phase:
1. **Unit Tests**
   - Test new components in isolation
   - Mock dependencies
   - Test configuration loading

2. **Integration Tests**
   - Test with existing components
   - End-to-end test with minimal setup
   - Test configuration changes

3. **Example Usage**
   - Add example configuration
   - Add example script
   - Document usage

## Dependencies
- Python 3.8+
- pandas
- numpy
- scikit-learn
- pytest
- pyyaml

## Directory Structure
```
src/
├── execution/                    # [EXISTING] Trade execution and portfolio management
│   ├── portfolio_manager.py      # [EXISTING] Portfolio state management
│   ├── trade_executor.py         # [EXISTING - TO BE REFACTORED]
│   └── metrics/                  # [EXISTING] Performance metrics
│
├── features/                     # [EXISTING] Feature engineering and storage
│
├── strategies/                   # [EXISTING] Trading strategies
│   ├── base_strategy.py         # [EXISTING] Base strategy interface
│   ├── strategy_registry.py     # [NEW] Strategy registration system
│   ├── SingleStock/             # [EXISTING] Single stock strategies
│   └── portfolio/               # [NEW] Portfolio strategies
│       ├── base_portfolio.py    # [NEW] Base portfolio interface
│       ├── aggregation/         # [NEW] Signal aggregation
│       │   ├── base_aggregator.py
│       │   └── weighted_aggregator.py
│       └── trade_selection/     # [NEW] Portfolio trade selection
│           ├── base_selector.py
│           └── constraint_selector.py
│
├── benchmark/                    # [NEW] Benchmarking system
│   ├── benchmark_runner.py      # [NEW] Main benchmark orchestration
│   ├── data_splitter.py         # [NEW] Data splitting logic
│   ├── portfolio_benchmark.py   # [NEW] Portfolio-specific benchmarking
│   └── comparison/              # [NEW] Strategy comparison
│       ├── metrics_comparator.py
│       └── visualization.py
│
└── config/                      # [EXISTING] Configuration
    ├── strategy_config.py       # [EXISTING] To be extended
    ├── portfolio_config.py      # [NEW] Portfolio configuration
    └── benchmark_config.py      # [NEW] Benchmark configuration
```

## Component Responsibilities

### Existing Components

1. **PortfolioManager** [EXISTING]
   - Manages portfolio state (positions, cash)
   - Tracks trades and metrics
   - Handles position updates
   - Calculates portfolio value

2. **TradeExecutor** [EXISTING - TO BE REFACTORED]
   - Currently: Handles signal aggregation and trade execution
   - Will be refactored into: Single stock signal aggregation only

3. **BaseStrategy** [EXISTING]
   - Defines strategy interface
   - Handles signal generation
   - Manages strategy state

### New Components

1. **StrategyRegistry** [NEW]
   - Manages strategy registration
   - Creates strategy instances
   - Validates strategy configurations

2. **BasePortfolioStrategy** [NEW]
   - Manages portfolio configuration
   - Owns PortfolioManager instance
   - Coordinates signal aggregation
   - Handles trade execution

3. **SignalAggregator** [NEW]
   - Aggregates signals from multiple strategies
   - Applies aggregation rules
   - Generates final signals

4. **TradeSelector** [NEW]
   - Applies portfolio constraints
   - Selects trades based on rules
   - Manages trade priorities

5. **BenchmarkRunner** [NEW]
   - Manages data splitting
   - Runs portfolio strategies
   - Tracks performance
   - Generates comparisons

## System Architecture

### Layer Diagram
```
┌─────────────────────────────────────────────────────────┐
│                    Benchmark Layer                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Portfolio   │  │ Portfolio   │  │ Portfolio   │     │
│  │ Strategy 1  │  │ Strategy 2  │  │ Strategy N  │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                    Portfolio Layer                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Signal      │  │ Trade       │  │ Portfolio   │     │
│  │ Aggregator  │  │ Selector    │  │ Manager     │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                    Strategy Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Single      │  │ Single      │  │ Single      │     │
│  │ Stock       │  │ Stock       │  │ Stock       │     │
│  │ Strategy 1  │  │ Strategy 2  │  │ Strategy N  │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### Data Flow
```
BenchmarkRunner
    │
    ├── Data Split (Train/Val/Test)
    │
    └── For each Portfolio Strategy:
        │
        ├── Get Data for Timestamp
        │
        ├── For each Stock:
        │   ├── Get Single Stock Strategy Signals
        │   └── Apply Aggregation Rules
        │
        ├── Apply Portfolio Constraints
        │
        ├── Execute Trades
        │
        └── Track Performance
```

### Component Interactions
```
[Portfolio Strategy]
    │
    ├── Uses StrategyRegistry to create strategies
    │
    ├── Uses SignalAggregator to combine signals
    │
    ├── Uses TradeSelector to apply constraints
    │
    └── Uses PortfolioManager to execute trades
        │
        └── Updates metrics and state
```

## Implementation Notes

### Refactoring Points
1. **TradeExecutor** → **SingleStockSignalAggregator**
   - Remove trade execution responsibility
   - Focus on signal aggregation
   - Update all references

2. **StrategyFactory** → **StrategyRegistry**
   - Make strategy creation configurable
   - Add validation
   - Update strategy creation calls

3. **RunManager** → **BenchmarkRunner**
   - Extract data splitting logic
   - Add portfolio support
   - Update benchmark execution

### Integration Points
1. **Portfolio Strategy Integration**
   - Connect with StrategyRegistry
   - Integrate with SignalAggregator
   - Link with PortfolioManager

2. **Benchmark Integration**
   - Connect with data splitting
   - Integrate with metrics
   - Link with visualization

## Notes
- Each phase should be independently pushable
- Maintain backward compatibility
- Document all changes
- Include tests with each phase
- Add example configurations
- Update documentation 