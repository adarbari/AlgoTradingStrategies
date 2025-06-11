# Algorithmic Trading System

A modular algorithmic trading system that supports multiple strategies and real-time portfolio management.

## Features

- Modular strategy architecture
- Portfolio management with position tracking
- Trade decision making with confidence thresholds
- Support for multiple symbols
- Historical data backtesting
- Real-time trading capabilities

## Project Structure

```
src/
├── execution/
│   ├── portfolio_manager.py  # Manages portfolio state and positions
│   └── trade_decider.py      # Makes trade decisions based on signals
├── strategies/
│   ├── base_strategy.py      # Base class for all strategies
│   └── ma_crossover_strategy.py  # Example MA Crossover strategy
└── run_trading_system.py     # Main script to run the system
```

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the trading system:
```bash
python src/run_trading_system.py
```

2. The system will:
   - Load historical data for specified symbols
   - Run the MA Crossover strategy
   - Make trade decisions based on signals
   - Execute trades and manage the portfolio
   - Display results including final portfolio value and returns

## Adding New Strategies

To add a new strategy:

1. Create a new strategy class that inherits from `BaseStrategy`
2. Implement the required methods:
   - `prepare_data()`: Prepare data for the strategy
   - `generate_signals()`: Generate trading signals
   - `update()`: Update strategy state with new data

Example:
```python
from strategies.base_strategy import BaseStrategy

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

The system can be configured by modifying the parameters in `run_trading_system.py`:

- `symbols`: List of stock symbols to trade
- `initial_budget`: Starting portfolio value
- `start_date` and `end_date`: Backtesting period
- Strategy parameters in the strategy classes

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
python backtest.py
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
PYTHONPATH=. python3 src/scripts/run_strategy.py --symbol AAPL --strategy ml --start-date 2025-01-01 --end-date 2025-04-10
```

This script will execute the strategy and save the results in the `results` directory.

# AlgoTradingModels

This project contains algorithmic trading models and strategies.

## Recent Update
- Updated workflow to use Python 3.9, 3.10, and 3.11 for CI/CD. 