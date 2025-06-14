# Algorithmic Trading System

A modular algorithmic trading system that supports multiple strategies, portfolio management, and real-time trading capabilities. The system is designed with service-oriented architecture in mind, allowing components to be extracted into independent services when needed.

## Features

- Multiple trading strategies:
  - Moving Average Crossover
  - Random Forest ML-based strategy
  - Portfolio-based trading
- Advanced portfolio management with position tracking
- Signal aggregation for multi-strategy portfolios
- Support for multiple data providers (Polygon, Yahoo Finance)
- Feature engineering and caching system
- Comprehensive metrics and visualization
- Historical data backtesting
- Real-time trading capabilities

## Architecture

The system is designed with a service-oriented architecture approach, where each component can potentially be extracted into an independent service. This includes:

- **Strategy Services**: Individual trading strategies that can be deployed independently
- **Portfolio Services**: Portfolio management and aggregation services
- **Data Services**: Market data and feature engineering services
- **Execution Services**: Trade execution and risk management services

Each component is designed with:
- Clean interfaces for inter-service communication
- Minimal dependencies
- Independent deployment capability
- Service extraction readiness

## Project Structure

```
src/
├── data/               # Data fetching and processing
│   ├── vendors/       # Data providers (Polygon, Yahoo Finance)
│   └── data_loader.py # Data loading and caching
├── execution/         # Trade execution and portfolio management
│   ├── portfolio_manager.py
│   ├── trade_executor.py
│   └── signal_aggregation/
├── features/          # Feature engineering
│   ├── feature_store.py
│   └── technical_indicators.py
├── strategies/        # Trading strategies
│   ├── SingleStock/   # Single stock strategies
│   └── portfolio/     # Portfolio strategies
├── visualization/     # Results visualization
└── run_trading_system.py  # Main system driver
```

## Installation

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running a Single Strategy

```bash
PYTHONPATH=. python src/run_trading_system.py --symbol AAPL --strategy ma_crossover --start-date 2023-01-01 --end-date 2023-12-31
```

### Running a Portfolio Strategy

```bash
PYTHONPATH=. python src/run_trading_system.py --portfolio default_portfolio --start-date 2023-01-01 --end-date 2023-12-31
```

### Running Backtests

```bash
PYTHONPATH=. python src/scripts/backtest.py --strategy ma_crossover
# or
PYTHONPATH=. python src/scripts/backtest.py --strategy random_forest
```

## Adding New Strategies

To add a new strategy:

1. Create a new strategy class that inherits from `BaseStrategy`
2. Implement the required methods:
   - `prepare_data()`: Prepare data for the strategy
   - `generate_signals()`: Generate trading signals
   - `update()`: Update strategy state with new data

Example:
```python
from src.strategies.base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(name="MyStrategy")
        
    def prepare_data(self, data):
        # Prepare data for your strategy
        return processed_data
        
    def generate_signals(self, data, symbol, timestamp):
        # Generate trading signals
        return signal
```

## Configuration

The system can be configured through:

1. Command line arguments in `run_trading_system.py`
2. Strategy-specific configuration files
3. Portfolio configuration through `PortfolioTradingExecutionConfigFactory`

## Testing

Run tests using pytest:
```bash
pytest tests/
```

For slow tests:
```bash
pytest tests/ -m "slow"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# Moving Average Crossover Strategy Backtester

This application backtests a moving average crossover strategy on multiple stocks and ETFs. The strategy generates buy signals when the 10-day moving average crosses above the 50-day moving average, and sell signals when it crosses below.

## Features

- Tests the strategy on 10 different stocks/ETFs
- Analyzes performance over the last 1000 trading days
- Generates interactive visualizations of results
- Calculates and displays performance metrics
- Shows buy/sell signals on the price chart

## Installation

1. Clone this repository
2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Simply run the backtest script:
```bash
PYTHONPATH=. python src/scripts/backtest.py --strategy ma_crossover OR 
PYTHONPATH=. python src/scripts/backtest.py --strategy random_forest
```

The script will:
1. Download historical data for the selected symbols
2. Calculate moving averages and generate trading signals
3. Calculate strategy returns
4. Display an interactive plot showing the results
5. Print summary statistics for each symbol

## Default Symbols

The script tests the strategy on the following symbols:
- Tech Stocks: AAPL, MSFT, GOOGL, AMZN, META
- ETFs: SPY, QQQ, IWM, DIA, VTI

## Customization

You can modify the following parameters in the code:
- Moving average windows (currently 10 and 50 days)
- List of symbols to test
- Date range for backtesting
- Visualization settings 

## Running the Strategy

To run the strategy and generate results, use the following command:

```bash
PYTHONPATH=. python3 src/run_trading_system.py --symbol AAPL --strategy ml --start-date 2025-01-01 --end-date 2025-04-10
```

This script will execute the strategy and save the results in the `results` directory.

# AlgoTradingModels

This project contains algorithmic trading models and strategies.

## Recent Update
- Updated workflow to use Python 3.9, 3.10, and 3.11 for CI/CD.
- The driver file is now `run_trading_system.py`.

## Implementation Phases

### Phase 2: Signal Aggregation (Current)
- Weighted average signal aggregation
- Multi-strategy portfolio support
- Signal validation and normalization
- Portfolio-level signal generation

### Phase 3: Advanced Orchestration (Planned)
- Risk management and position sizing
- Smart order routing and execution
- Portfolio optimization and rebalancing
- Advanced order management 