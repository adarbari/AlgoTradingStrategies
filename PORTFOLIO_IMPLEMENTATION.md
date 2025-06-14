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

## Implementation Phases

### Phase 1: Strategy Registry
**Purpose**: Make strategy creation configurable and dynamic
```
Changes:
1. Create strategy registry system
   - New: src/strategies/strategy_registry.py
   - New: src/config/strategy_registry_config.py
   - Modify: src/strategies/strategy_factory.py (to use registry)

Files to modify:
- src/strategies/strategy_factory.py (minimal changes)
- src/config/strategy_config.py (add registry config)

Testing:
- Unit tests for registry
- Integration tests with existing strategies
- Configuration loading tests
```

### Phase 2: Single Stock Signal Aggregator
**Purpose**: Separate signal generation from trade execution 
```
Changes:
- Rename: src/execution/trade_executor.py -> src/execution/portfolio_stocks_signal_aggregator.py
- New: src/execution/base_signal_aggregator.py

Testing:
- Unit tests for signal aggregation
- Integration tests with existing strategies
- End-to-end test with minimal setup
```

### Phase 3: Portfolio Strategy Base
**Purpose**: Establish foundation for portfolio strategies
```
Changes:
1. Create portfolio strategy foundation
   - New: src/strategies/portfolio/base_portfolio.py
     - Configuration management
     - PortfolioManager instance
     - Strategy creation via registry
     - Signal aggregation interface
   - New: src/config/portfolio_config.py
     - Stock list
     - Strategy mapping
     - Allocation rules
   - New: src/strategies/portfolio/strategy_registry.py
     - Portfolio strategy registration
     - Configuration validation

Testing:
- Unit tests for base portfolio
- Configuration validation tests
- Integration tests with signal aggregator
```

### Phase 4A: Basic Signal Aggregation
**Purpose**: Enable basic portfolio signal aggregation
```
Changes:
- New: src/strategies/portfolio/aggregation/base_aggregator.py
- New: src/strategies/portfolio/aggregation/weighted_aggregator.py
- New: src/config/aggregation_config.py

Testing:
- Unit tests for aggregators
- Integration tests with portfolio base
```

### Phase 4B: Portfolio Trade Selection
**Purpose**: Handle portfolio-level constraints and trade selection
```
Changes:
- New: src/strategies/portfolio/trade_selection/base_selector.py
- New: src/strategies/portfolio/trade_selection/constraint_selector.py
- New: src/config/trade_selection_config.py

Testing:
- Unit tests for selectors
- Integration tests with portfolio strategies
```

### Phase 5: Portfolio Strategy Implementation
**Purpose**: Implement concrete portfolio strategies
```
Changes:
1. MACrossover Portfolio
   - New: src/strategies/portfolio/ma_crossover_portfolio.py
   - New: tests/strategies/portfolio/test_ma_crossover_portfolio.py
   - New: config/portfolio_strategies/ma_crossover.yaml

2. Hybrid Portfolio
   - New: src/strategies/portfolio/hybrid_portfolio.py
   - New: tests/strategies/portfolio/test_hybrid_portfolio.py
   - New: config/portfolio_strategies/hybrid.yaml

Testing:
- Unit tests for each portfolio strategy
- Integration tests with all components
- End-to-end tests with example data
```

### Phase 6: Benchmark Runner
**Purpose**: Reuse existing code for portfolio benchmarking
```
Changes:
1. Refactor existing benchmark code
   - Move: src/utils/run_manager.py -> src/benchmark/benchmark_runner.py
   - Extract: Data splitting logic
   - Reuse: Existing metrics calculation
   - Reuse: Existing visualization

2. Add portfolio-specific features
   - New: src/benchmark/portfolio_benchmark.py
   - New: src/benchmark/portfolio_metrics.py

Testing:
- Unit tests for new components
- Integration tests with existing code
- End-to-end benchmark tests
```

### Phase 7: Performance Comparison
**Purpose**: Enable strategy comparison and visualization
```
Changes:
- New: src/benchmark/comparison/metrics_comparator.py
- New: src/benchmark/comparison/visualization.py
- New: src/config/comparison_config.py

Testing:
- Unit tests for comparison tools
- Integration tests with benchmark runner
```

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
│   ├── trade_executor.py         # [EXISTING] To be refactored into single_stock_signal_aggregator.py
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