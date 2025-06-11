import argparse
from datetime import datetime, timedelta
import pandas as pd
from src.data import PolygonProvider
from src.features import TechnicalIndicators
from strategies.SingleStock.single_stock_strategy import SingleStockStrategy
from helpers.logger import TradingLogger
import logging

def run_strategy(symbol: str, strategy_type: str, start_date: str, end_date: str):
    """Run the trading strategy for a given symbol and date range."""
    # Initialize components
    data_provider = PolygonProvider()
    feature_engineer = TechnicalIndicators()
    strategy = SingleStockStrategy(use_ml=(strategy_type == 'ml'))
    logger = TradingLogger()
    
    # Fetch historical data
    df = data_provider.get_historical_data(symbol, start_date, end_date)
    if df.empty:
        print(f"No data available for {symbol}")
        return
    
    # Debug: Print DataFrame info
    print("\nDataFrame Info:")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Shape: {df.shape}")
    print("\nFirst few rows:")
    print(df.head())
    
    # Calculate features
    df = feature_engineer.calculate_features(df)
    
    # Generate signals and run strategy
    signals = strategy.generate_signals(df, logger, symbol)
    
    # Log results
    logger.plot_portfolio_performance(f"{symbol}_{strategy_type}", signals[['Portfolio_Value']])
    trades = signals[signals['Signal'] != 0]
    if not trades.empty:
        logger.plot_trade_distribution(f"{symbol}_{strategy_type}", trades)

def main():
    parser = argparse.ArgumentParser(description='Run trading strategy')
    parser.add_argument('--symbol', required=True, help='Stock symbol')
    parser.add_argument('--strategy', required=True, choices=['ml', 'ma'], help='Strategy type')
    parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    run_strategy(args.symbol, args.strategy, args.start_date, args.end_date)

if __name__ == '__main__':
    main() 