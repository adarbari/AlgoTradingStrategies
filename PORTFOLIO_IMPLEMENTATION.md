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

**Implementation Plan**:

1. **Core Components**:

   a. **Trade Execution Orchestrator** (`trade_execution_orchestrator.py`):
   ```python
   class TradeExecutionOrchestrator:
       def __init__(self, config: ExecutionConfig):
           self.position_agent = PositionSizingAgent(config.position_config)
           self.risk_agent = RiskManagementAgent(config.risk_config)
           self.correlation_agent = CorrelationAgent(config.correlation_config)
           self.execution_agent = ExecutionRulesAgent(config.execution_config)
           self.state = ExecutionState()

       def execute_trades(self, signals: Dict[str, StrategySignal], portfolio_state: PortfolioState) -> List[Trade]:
           # Initialize execution state
           self.state.update(signals, portfolio_state)
           
           # Get initial trade proposals from position agent
           trades = self.position_agent.propose_trades(self.state)
           
           # Get risk adjustments
           risk_adjustments = self.risk_agent.analyze_risk(trades, self.state)
           trades = self.risk_agent.adjust_trades(trades, risk_adjustments)
           
           # Get correlation adjustments
           correlation_adjustments = self.correlation_agent.analyze_correlations(trades, self.state)
           trades = self.correlation_agent.adjust_trades(trades, correlation_adjustments)
           
           # Apply execution rules
           trades = self.execution_agent.apply_rules(trades, self.state)
           
           return trades
   ```

   b. **Execution Agents**:
   ```python
   class BaseAgent:
       def __init__(self, config: BaseConfig):
           self.config = config
           self.state = AgentState()

   class PositionSizingAgent(BaseAgent):
       """
       Responsibilities:
       - Calculate initial position sizes
       - Propose trades based on signals
       - Adjust for portfolio constraints
       
       State:
       - Historical position sizes
       - Performance metrics
       - Portfolio allocation history
       """

   class RiskManagementAgent(BaseAgent):
       """
       Responsibilities:
       - Calculate portfolio risk metrics
       - Validate against risk limits
       - Propose risk adjustments
       
       State:
       - Risk metrics history
       - Risk limit violations
       - Risk adjustment history
       """

   class CorrelationAgent(BaseAgent):
       """
       Responsibilities:
       - Calculate asset correlations
       - Identify correlated positions
       - Propose correlation-based adjustments
       
       State:
       - Correlation matrix
       - Historical correlations
       - Adjustment history
       """

   class ExecutionRulesAgent(BaseAgent):
       """
       Responsibilities:
       - Apply execution rules
       - Set order parameters
       - Handle trading restrictions
       
       State:
       - Execution history
       - Rule effectiveness
       - Market impact metrics
       """
   ```

2. **State Management**:

   a. **Execution State** (`execution_state.py`):
   ```python
   class ExecutionState:
       def __init__(self):
           self.signals: Dict[str, StrategySignal]
           self.portfolio_state: PortfolioState
           self.trade_proposals: List[Trade]
           self.risk_metrics: RiskMetrics
           self.correlation_matrix: pd.DataFrame
           self.execution_metrics: ExecutionMetrics
   ```

   b. **Agent State** (`agent_state.py`):
   ```python
   class AgentState:
       def __init__(self):
           self.historical_decisions: List[Decision]
           self.performance_metrics: Dict[str, float]
           self.learning_state: Dict[str, Any]
   ```

3. **Configuration System**:

   a. **Agent Configs** (`agent_configs.py`):
   ```python
   @dataclass
   class PositionSizingConfig:
       method: str = "equal_weight"
       max_position_size: float = 0.1
       min_position_size: float = 0.01
       learning_rate: float = 0.01
       adaptation_period: int = 20

   @dataclass
   class RiskManagementConfig:
       max_portfolio_risk: float = 0.15
       max_position_risk: float = 0.05
       var_limit: float = 0.02
       risk_adjustment_speed: float = 0.1

   @dataclass
   class CorrelationConfig:
       max_correlation: float = 0.7
       correlation_lookback: int = 252
       adjustment_factor: float = 0.5
       update_frequency: str = "daily"

   @dataclass
   class ExecutionRulesConfig:
       default_order_type: str = "LIMIT"
       time_in_force: str = "DAY"
       price_threshold: float = 0.01
       market_impact_limit: float = 0.005
   ```

4. **Agent Communication**:

   a. **Message Types** (`agent_messages.py`):
   ```python
   @dataclass
   class TradeProposal:
       trades: List[Trade]
       confidence: float
       reasoning: str

   @dataclass
   class RiskAdjustment:
       adjustments: Dict[str, float]
       risk_metrics: RiskMetrics
       warnings: List[str]

   @dataclass
   class CorrelationAdjustment:
       adjustments: Dict[str, float]
       correlation_matrix: pd.DataFrame
       affected_positions: List[str]
   ```

5. **Implementation Phases**:

   a. **Phase 4.1: Core Infrastructure**
   - Implement base agent framework
   - Create state management system
   - Set up agent communication

   b. **Phase 4.2: Basic Agents**
   - Implement position sizing agent
   - Implement risk management agent
   - Add basic execution rules

   c. **Phase 4.3: Advanced Agents**
   - Implement correlation agent
   - Add adaptive learning
   - Add sophisticated execution rules

   d. **Phase 4.4: Testing and Integration**
   - Add comprehensive test suite
   - Integrate with existing components
   - Performance optimization

**Key Benefits of Agentic Architecture**:
1. **Adaptive Behavior**: Agents can learn and adapt to market conditions
2. **Collaborative Decision Making**: Agents can work together to optimize trades
3. **Stateful Processing**: Each agent maintains its own state and history
4. **Parallel Execution**: Agents can work independently where possible
5. **Flexible Communication**: Agents can share information and negotiate

**Example Usage**:
```python
# Create orchestrator with agent configurations
config = ExecutionConfig(
    position_config=PositionSizingConfig(method="risk_parity"),
    risk_config=RiskManagementConfig(max_portfolio_risk=0.15),
    correlation_config=CorrelationConfig(max_correlation=0.7),
    execution_config=ExecutionRulesConfig(default_order_type="LIMIT")
)

orchestrator = TradeExecutionOrchestrator(config)

# Execute trades
trades = orchestrator.execute_trades(signals, portfolio_state)
```

### Phase 5: Portfolio Strategy Base ✅
**Purpose**: Establish foundation for portfolio strategies
**Status**: Completed

**Changes Implemented**:
1. Created portfolio strategy foundation
   - Created: src/strategies/portfolio/portfolio_trading_execution_config.py
     - Implements a configuration and management class for portfolio trading.
     - Allows adding tickers to the portfolio and associating one or more strategies (with optional configs) to each ticker.
     - Allows associating a signal aggregator (with config) to each ticker.
     - Provides methods to retrieve all tickers, all strategies for a ticker, and the aggregator for a ticker.
     - Enforces only one instance of each strategy type per ticker and validates ticker/strategy/aggregator types.
     - Integrates with the project's strategy/aggregator registries and config dataclasses.
     - Does not implement portfolio-level signal aggregation or trade selection logic (reserved for later phases).

2. Added comprehensive test suite
   - Created: tests/test_portfolio_trading_execution_config.py
     - Tests for base portfolio strategy
     - Tests for strategy management
     - Tests for signal aggregation integration
   - Created: tests/test_strategy_mappings.py
     - Tests for strategy type mappings
     - Tests for strategy registration
   - Created: tests/test_portfolio_trading_execution_config_factory.py
     - Tests for factory pattern
     - Tests for configuration creation
     - Tests for strategy combination

**Testing Completed**:
- Unit tests for base portfolio strategy
- Unit tests for strategy mappings
- Unit tests for configuration factory
- Integration tests with signal aggregator
- All tests passing

**Next Steps**:
- Proceed with Phase 6: Portfolio Signal Aggregation and Trade Selection
- Begin implementation of portfolio-level signal aggregation

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

**Orchestration Flow**:

1. **System Input**:
   ```python
   class SystemInput:
       signals: Dict[str, StrategySignal]  # Raw signals from strategies
       market_data: MarketData            # Current market data
       portfolio_state: PortfolioState    # Current portfolio state
       execution_context: ExecutionContext # Execution parameters
   ```

2. **Agent Communication Flow**:
   ```
   ┌─────────────────────────────────────────────────────────┐
   │                  Trade Execution Orchestrator           │
   └─────────────────────────────────────────────────────────┘
                           │
                           ▼
   ┌─────────────────────────────────────────────────────────┐
   │                    Position Sizing Agent                │
   │ Input:                                                 │
   │ - Raw signals                                          │
   │ - Portfolio state                                      │
   │ - Market data                                          │
   │ Output:                                                │
   │ - Initial trade proposals                              │
   │ - Position size recommendations                        │
   └─────────────────────────────────────────────────────────┘
                           │
                           ▼
   ┌─────────────────────────────────────────────────────────┐
   │                    Risk Management Agent                │
   │ Input:                                                 │
   │ - Trade proposals                                      │
   │ - Portfolio risk metrics                               │
   │ - Market volatility                                    │
   │ Output:                                                │
   │ - Risk-adjusted trades                                 │
   │ - Risk limit warnings                                  │
   │ - Risk metrics updates                                 │
   └─────────────────────────────────────────────────────────┘
                           │
                           ▼
   ┌─────────────────────────────────────────────────────────┐
   │                    Correlation Agent                    │
   │ Input:                                                 │
   │ - Risk-adjusted trades                                 │
   │ - Correlation matrix                                   │
   │ - Portfolio positions                                  │
   │ Output:                                                │
   │ - Correlation-adjusted trades                          │
   │ - Correlation warnings                                 │
   │ - Diversification recommendations                      │
   └─────────────────────────────────────────────────────────┘
                           │
                           ▼
   ┌─────────────────────────────────────────────────────────┐
   │                    Execution Rules Agent                │
   │ Input:                                                 │
   │ - Final trade proposals                                │
   │ - Market conditions                                    │
   │ - Execution constraints                                │
   │ Output:                                                │
   │ - Executable orders                                    │
   │ - Execution parameters                                 │
   │ - Market impact estimates                              │
   └─────────────────────────────────────────────────────────┘
   ```

3. **Detailed Agent Interactions**:

   a. **Position Sizing Agent**:
   ```python
   class PositionSizingAgent:
       def propose_trades(self, input: SystemInput) -> TradeProposal:
           """
           Input:
           - signals: Dict[str, StrategySignal]
               Example: {
                   'AAPL': StrategySignal(signal=1.0, confidence=0.8),
                   'MSFT': StrategySignal(signal=-0.5, confidence=0.6)
               }
           - portfolio_state: PortfolioState
               Example: {
                   'positions': {'AAPL': Position(quantity=100, avg_price=150.0)},
                   'cash': 100000.0
               }
           - market_data: MarketData
               Example: {
                   'prices': {'AAPL': 150.0, 'MSFT': 280.0},
                   'volumes': {'AAPL': 1000000, 'MSFT': 500000}
               }

           Output: TradeProposal
               Example: {
                   'trades': [
                       Trade(symbol='AAPL', quantity=50, type='BUY'),
                       Trade(symbol='MSFT', quantity=30, type='SELL')
                   ],
                   'confidence': 0.85,
                   'reasoning': 'Strong buy signal for AAPL, moderate sell for MSFT'
               }
           """
   ```

   b. **Risk Management Agent**:
   ```python
   class RiskManagementAgent:
       def analyze_risk(self, proposal: TradeProposal, state: ExecutionState) -> RiskAdjustment:
           """
           Input:
           - proposal: TradeProposal
               Example: {
                   'trades': [
                       Trade(symbol='AAPL', quantity=50, type='BUY'),
                       Trade(symbol='MSFT', quantity=30, type='SELL')
                   ]
               }
           - state: ExecutionState
               Example: {
                   'portfolio_risk': 0.15,
                   'position_risks': {'AAPL': 0.05, 'MSFT': 0.03}
               }

           Output: RiskAdjustment
               Example: {
                   'adjustments': {'AAPL': 0.8, 'MSFT': 1.0},  # Scale factors
                   'risk_metrics': {
                       'portfolio_var': 0.02,
                       'max_drawdown': 0.05
                   },
                   'warnings': ['AAPL position exceeds risk limit']
               }
           """
   ```

   c. **Correlation Agent**:
   ```python
   class CorrelationAgent:
       def analyze_correlations(self, proposal: TradeProposal, state: ExecutionState) -> CorrelationAdjustment:
           """
           Input:
           - proposal: TradeProposal
               Example: {
                   'trades': [
                       Trade(symbol='AAPL', quantity=40, type='BUY'),
                       Trade(symbol='MSFT', quantity=30, type='SELL')
                   ]
               }
           - state: ExecutionState
               Example: {
                   'correlation_matrix': pd.DataFrame(...),
                   'portfolio_correlations': {'AAPL-MSFT': 0.7}
               }

           Output: CorrelationAdjustment
               Example: {
                   'adjustments': {'AAPL': 0.7, 'MSFT': 1.0},  # Scale factors
                   'correlation_matrix': pd.DataFrame(...),
                   'affected_positions': ['AAPL', 'MSFT']
               }
           """
   ```

   d. **Execution Rules Agent**:
   ```python
   class ExecutionRulesAgent:
       def apply_rules(self, proposal: TradeProposal, state: ExecutionState) -> List[Order]:
           """
           Input:
           - proposal: TradeProposal
               Example: {
                   'trades': [
                       Trade(symbol='AAPL', quantity=28, type='BUY'),
                       Trade(symbol='MSFT', quantity=30, type='SELL')
                   ]
               }
           - state: ExecutionState
               Example: {
                   'market_conditions': {
                       'volatility': 0.15,
                       'liquidity': 'high'
                   },
                   'execution_constraints': {
                       'max_slippage': 0.001,
                       'time_in_force': 'DAY'
                   }
               }

           Output: List[Order]
               Example: [
                   Order(
                       symbol='AAPL',
                       quantity=28,
                       type='LIMIT',
                       price=150.0,
                       time_in_force='DAY',
                       execution_rules={
                           'max_slippage': 0.001,
                           'min_fill': 0.8
                       }
                   ),
                   Order(
                       symbol='MSFT',
                       quantity=30,
                       type='LIMIT',
                       price=280.0,
                       time_in_force='DAY',
                       execution_rules={
                           'max_slippage': 0.001,
                           'min_fill': 0.8
                       }
                   )
               ]
           """
   ```

4. **State Management**:
   ```python
   class ExecutionState:
       def __init__(self):
           self.signals: Dict[str, StrategySignal]
           self.portfolio_state: PortfolioState
           self.market_data: MarketData
           self.risk_metrics: RiskMetrics
           self.correlation_matrix: pd.DataFrame
           self.execution_metrics: ExecutionMetrics
           self.agent_states: Dict[str, AgentState]
   ```

5. **Orchestration Process**:
   ```
   1. Initialize State
      ├── Load portfolio state
      ├── Update market data
      └── Initialize agent states

   2. Position Sizing
      ├── Calculate initial positions
      ├── Apply portfolio constraints
      └── Generate trade proposals

   3. Risk Management
      ├── Calculate risk metrics
      ├── Apply risk limits
      └── Adjust trade sizes

   4. Correlation Analysis
      ├── Calculate correlations
      ├── Identify correlated positions
      └── Adjust for diversification

   5. Execution Rules
      ├── Apply execution constraints
      ├── Set order parameters
      └── Generate final orders

   6. State Update
      ├── Update portfolio state
      ├── Update risk metrics
      └── Update agent states
   ```

6. **Error Handling and Recovery**:
   ```python
   class OrchestrationError(Exception):
       pass

   class AgentError(OrchestrationError):
       pass

   class RecoveryStrategy:
       def handle_error(self, error: AgentError, state: ExecutionState) -> RecoveryAction:
           """
           Handle errors in the orchestration process
           - Retry failed operations
           - Fall back to simpler strategies
           - Notify monitoring system
           """
   ``` 

**Position Resizing and Risk Feedback Loops**:

1. **Risk-Based Resizing Flow**:
   ```
   ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
   │  Position       │     │  Risk           │     │  Position       │
   │  Sizing Agent   │────▶│  Management     │────▶│  Resizing       │
   └─────────────────┘     │  Agent          │     │  Agent          │
         ▲                 └─────────────────┘     └─────────────────┘
         │                         │                       │
         │                         ▼                       │
         │                 ┌─────────────────┐             │
         └─────────────────│  Risk Feedback  │◀────────────┘
                           │  Loop           │
                           └─────────────────┘
   ```

2. **Risk Feedback Loop Implementation**:
   ```python
   class RiskFeedbackLoop:
       def __init__(self, config: RiskFeedbackConfig):
           self.max_iterations = config.max_iterations
           self.risk_tolerance = config.risk_tolerance
           self.resize_threshold = config.resize_threshold

       def process(self, initial_proposal: TradeProposal, state: ExecutionState) -> TradeProposal:
           """
           Process trade proposal through risk feedback loop
           """
           current_proposal = initial_proposal
           iteration = 0

           while iteration < self.max_iterations:
               # Get risk assessment
               risk_assessment = self.risk_agent.analyze_risk(current_proposal, state)
               
               # Check if risk is within tolerance
               if self._is_risk_acceptable(risk_assessment):
                   break
               
               # Calculate required adjustments
               adjustments = self._calculate_risk_adjustments(risk_assessment)
               
               # Apply adjustments
               current_proposal = self._apply_risk_adjustments(current_proposal, adjustments)
               
               iteration += 1

           return current_proposal

       def _is_risk_acceptable(self, risk_assessment: RiskAssessment) -> bool:
           """
           Check if current risk levels are acceptable
           """
           return (
               risk_assessment.portfolio_risk <= self.risk_tolerance.portfolio_risk and
               risk_assessment.max_position_risk <= self.risk_tolerance.position_risk and
               risk_assessment.var <= self.risk_tolerance.var
           )

       def _calculate_risk_adjustments(self, risk_assessment: RiskAssessment) -> Dict[str, float]:
           """
           Calculate position size adjustments based on risk
           """
           adjustments = {}
           for position, risk in risk_assessment.position_risks.items():
               if risk > self.risk_tolerance.position_risk:
                   # Calculate reduction factor
                   reduction = self.risk_tolerance.position_risk / risk
                   adjustments[position] = max(reduction, self.resize_threshold)
           return adjustments
   ```

3. **Position Resizing Agent**:
   ```python
   class PositionResizingAgent(BaseAgent):
       def resize_positions(self, proposal: TradeProposal, risk_assessment: RiskAssessment) -> TradeProposal:
           """
           Resize positions based on risk assessment
           """
           resized_trades = []
           for trade in proposal.trades:
               # Get risk metrics for this position
               position_risk = risk_assessment.position_risks[trade.symbol]
               
               # Calculate new size
               new_size = self._calculate_new_size(
                   trade.quantity,
                   position_risk,
                   risk_assessment.portfolio_risk
               )
               
               # Create resized trade
               resized_trade = Trade(
                   symbol=trade.symbol,
                   quantity=new_size,
                   type=trade.type,
                   price=trade.price
               )
               resized_trades.append(resized_trade)
           
           return TradeProposal(
               trades=resized_trades,
               confidence=proposal.confidence,
               reasoning=f"Resized based on risk assessment: {risk_assessment.summary}"
           )

       def _calculate_new_size(self, current_size: int, position_risk: float, portfolio_risk: float) -> int:
           """
           Calculate new position size based on risk metrics
           """
           # Example risk-based sizing logic
           if position_risk > self.config.max_position_risk:
               # Reduce size proportionally to risk
               reduction_factor = self.config.max_position_risk / position_risk
               new_size = int(current_size * reduction_factor)
           elif portfolio_risk > self.config.max_portfolio_risk:
               # Reduce size to maintain portfolio risk
               portfolio_reduction = self.config.max_portfolio_risk / portfolio_risk
               new_size = int(current_size * portfolio_reduction)
           else:
               new_size = current_size
           
           return max(new_size, self.config.min_position_size)
   ```

4. **Risk-Based Resizing Configuration**:
   ```python
   @dataclass
   class RiskFeedbackConfig:
       max_iterations: int = 3
       risk_tolerance: RiskTolerance = field(default_factory=lambda: RiskTolerance(
           portfolio_risk=0.15,
           position_risk=0.05,
           var=0.02
       ))
       resize_threshold: float = 0.5  # Minimum position size as fraction of original

   @dataclass
   class RiskTolerance:
       portfolio_risk: float
       position_risk: float
       var: float
   ```

5. **Integration with Orchestration**:
   ```python
   class TradeExecutionOrchestrator:
       def execute_trades(self, signals: Dict[str, StrategySignal], portfolio_state: PortfolioState) -> List[Trade]:
           # Initialize state
           self.state.update(signals, portfolio_state)
           
           # Get initial trade proposals
           initial_proposal = self.position_agent.propose_trades(self.state)
           
           # Process through risk feedback loop
           risk_loop = RiskFeedbackLoop(self.config.risk_feedback)
           final_proposal = risk_loop.process(initial_proposal, self.state)
           
           # Apply correlation adjustments
           correlation_adjustments = self.correlation_agent.analyze_correlations(final_proposal, self.state)
           final_proposal = self.correlation_agent.adjust_trades(final_proposal, correlation_adjustments)
           
           # Apply execution rules
           orders = self.execution_agent.apply_rules(final_proposal, self.state)
           
           return orders
   ```

6. **Example Risk-Based Resizing Flow**:
   ```
   Initial Proposal:
   - AAPL: Buy 100 shares
   - MSFT: Sell 50 shares

   Risk Assessment:
   - AAPL position risk: 0.07 (exceeds limit of 0.05)
   - MSFT position risk: 0.03 (within limits)
   - Portfolio risk: 0.12 (within limits)

   First Iteration:
   - AAPL: Reduce to 71 shares (0.07 → 0.05 risk)
   - MSFT: Keep 50 shares

   Final Proposal:
   - AAPL: Buy 71 shares
   - MSFT: Sell 50 shares
   ```

7. **Monitoring and Logging**:
   ```python
   class RiskResizingMonitor:
       def log_resizing_event(self, event: ResizingEvent):
           """
           Log position resizing events for monitoring and analysis
           """
           self.logger.info(
               f"Position resized: {event.symbol} "
               f"from {event.original_size} to {event.new_size} "
               f"due to {event.reason}"
           )
           self.metrics.record_resizing(
               symbol=event.symbol,
               original_size=event.original_size,
               new_size=event.new_size,
               risk_metrics=event.risk_metrics
           )
   ``` 