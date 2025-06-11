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