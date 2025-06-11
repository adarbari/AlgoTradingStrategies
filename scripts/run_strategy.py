import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.data_manager import get_cached_data
from data.feature_engineering import FeatureEngineer
from strategies.SingleStock.single_stock_strategy import SingleStockStrategy
from helpers.logger import TradingLogger
import pandas as pd
from datetime import datetime, timedelta
import logging
import argparse
from data import get_cached_data

def split_data(data, train_ratio=0.8):
    """Split data into training and testing sets based on time."""
    n = int(len(data) * train_ratio)
    train = data.iloc[:n]
    test = data.iloc[n:]
    return train, test

def run_strategy_period(strategy, features, logger, symbol, period_name):
    """Run strategy on a specific period and return results."""
    signals = strategy.generate_signals(features, logger, symbol)
    
    # Generate plots from the signals
    portfolio_values = signals[['Portfolio_Value']].copy()
    logger.plot_portfolio_performance(f"{symbol}_{period_name}", portfolio_values)
    
    # Only plot trade distribution if there are trades
    trades = signals[signals['Signal'] != 0].copy()
    if not trades.empty:
        logger.plot_trade_distribution(f"{symbol}_{period_name}", trades)
    
    return trades, portfolio_values

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run trading strategy.")
    parser.add_argument('--symbol', required=True, help='Stock symbol')
    parser.add_argument('--strategy', required=True, choices=['ma', 'ml'], help='Strategy type (ma or ml)')
    parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD)')
    args = parser.parse_args()

    symbol = args.symbol
    strategy_type = args.strategy
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d")

    logger = TradingLogger()

    try:
        logging.info(f"Running strategy for {symbol}")
        features = get_cached_data(symbol, start_date, end_date)
        if features is None or features.empty:
            logging.error(f"No data found for {symbol} in the given period.")
            return

        if strategy_type == 'ml':
            # ML strategy: split, train, test, report only test
            train_features, test_features = split_data(features)
            feature_engineer = FeatureEngineer()
            train_features = feature_engineer.create_features(train_features, symbol, "technical")
            test_features = feature_engineer.create_features(test_features, symbol, "technical")
            strategy = SingleStockStrategy(use_ml=True)
            logging.info(f"Training ML model for {symbol}")
            strategy.train_model(train_features, logger, symbol)
            logging.info(f"Generating signals for test period for {symbol}")
            test_signals = strategy.generate_signals(test_features, logger, symbol)
            test_trades = test_signals[test_signals['Signal'] != 0].copy()
            test_portfolio = test_signals[['Portfolio_Value']].copy()
            logger.plot_portfolio_performance(f"{symbol}_test", test_portfolio)
            if not test_trades.empty:
                logger.plot_trade_distribution(f"{symbol}_test", test_trades)
            test_report = logger.generate_performance_report(f"{symbol}_test", test_trades, test_portfolio)
        else:
            # Non-ML: run on all data
            strategy = SingleStockStrategy(use_ml=False)
            trades, portfolio = run_strategy_period(strategy, features, logger, symbol, "all")
            report = logger.generate_performance_report(f"{symbol}_all", trades, portfolio)

    except Exception as e:
        logging.error(f"Error running strategy: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 