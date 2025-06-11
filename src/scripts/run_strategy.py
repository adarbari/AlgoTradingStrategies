import os
import sys
# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

import argparse
from datetime import datetime
import logging
from src.data.vendors.polygon_provider import PolygonProvider
from src.strategies.SingleStock.ma_crossover_strategy import MACrossOverSingleStockStrategy
from src.strategies.SingleStock.random_forest_strategy import RandomForestSingleStockStrategy
from src.utils.run_manager import StrategyManager
from src.helpers.logger import TradingLogger
from src.visualization.portfolio_visualizer import (
    plot_portfolio_performance,
    plot_trade_distribution,
    plot_backtest_results
)
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description='Run trading strategy')
    parser.add_argument('--symbol', type=str, required=True, help='Stock symbol')
    parser.add_argument('--strategy', type=str, choices=['ml', 'ma'], default='ml', help='Strategy type (ml or ma)')
    parser.add_argument('--start-date', type=str, required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--cache-dir', type=str, default='feature_cache', help='Directory for feature cache')
    args = parser.parse_args()

    # Initialize trading logger
    trading_logger = TradingLogger()
    logger = trading_logger.logger

    try:
        # Initialize data provider
        data_provider = PolygonProvider()

        # Fetch historical data
        logger.info(f"Fetching historical data for {args.symbol}")
        data = data_provider.get_historical_data(
            symbol=args.symbol,
            start_date=datetime.strptime(args.start_date, '%Y-%m-%d'),
            end_date=datetime.strptime(args.end_date, '%Y-%m-%d')
        )

        if data is None or data.empty:
            logger.error("No data received from provider")
            return

        # Initialize strategy based on the --strategy argument
        if args.strategy == 'ml':
            strategy = RandomForestSingleStockStrategy(cache_dir=args.cache_dir)
        else:
            strategy = MACrossOverSingleStockStrategy(cache_dir=args.cache_dir)

        # Initialize strategy manager with existing trading logger
        strategy_manager = StrategyManager(trading_logger=trading_logger)
        strategy_manager.initialize_strategy(args.symbol, args.strategy)

        # Generate signals
        logger.info(f"Generating signals using {args.strategy.upper()} strategy")
        signals = strategy.generate_signals(data, strategy_manager, args.symbol)

        if signals is None or signals.empty:
            logger.error("No signals generated")
            return

        # Calculate returns
        signals['returns'] = signals['close'].pct_change().fillna(0)
        signals['strategy_returns'] = signals['returns'] * signals['signal'].shift(1).fillna(0)
        cumulative_returns = (1 + signals['strategy_returns']).cumprod()
        
        # Initialize portfolio tracking
        initial_capital = 10000  # Initial portfolio value
        portfolio_value = initial_capital
        position = 0  # Current position (shares)
        position_price = 0  # Average price of current position
        
        # Log each period and trade
        for index, row in signals.iterrows():
            # Log period information
            period_data = {
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
                'volume': row['volume'],
                'signal': row['signal'],
                'returns': row['returns'],
                'strategy_returns': row['strategy_returns']
            }
            trading_logger.log_period(args.symbol, index, period_data)
            
            # Handle trades based on signals
            if row['signal'] != 0:
                trade_type = 'BUY' if row['signal'] == 1 else 'SELL'
                shares = 100  # Fixed trade size
                price = row['close']
                
                # Calculate profit for sell trades
                profit = None
                if trade_type == 'SELL' and position > 0:
                    profit = (price - position_price) * shares
                
                # Update position and portfolio value
                if trade_type == 'BUY':
                    cost = price * shares
                    if cost <= portfolio_value:  # Only buy if we have enough cash
                        position = shares
                        position_price = price
                        portfolio_value -= cost
                else:  # SELL
                    if position > 0:
                        portfolio_value += price * shares
                        position = 0
                        position_price = 0
                
                # Log trade
                strategy_manager.log_trade(
                    symbol=args.symbol,
                    trade_type=trade_type,
                    price=price,
                    shares=shares,
                    timestamp=index,
                    profit=profit,
                    portfolio_value=portfolio_value
                )
            
            # Log portfolio value for each period
            strategy_manager.log_portfolio_value(args.symbol, index, portfolio_value)
        
        # Get strategy summary
        summary = strategy_manager.get_strategy_summary()
        
        # Display results
        logger.info("\nStrategy Results:")
        logger.info(f"Total trades: {summary['total_trades']}")
        logger.info(f"Win rate: {summary['win_rate']:.2f}%")
        logger.info(f"Total profit: ${summary['total_profit']:.2f}")
        logger.info(f"Average profit per trade: ${summary['avg_profit_per_trade']:.2f}")
        logger.info(f"Max drawdown: {summary['max_drawdown']:.2f}%")
        logger.info(f"Sharpe ratio: {summary['sharpe_ratio']:.2f}")

        # Save results
        strategy_run_file = os.path.join(trading_logger.run_timestamp_dir, f"strategy_run_{args.symbol.lower()}_{args.strategy}_{args.start_date}_{args.end_date}.csv")
        signals.to_csv(strategy_run_file)
        logger.info(f"Results saved to {strategy_run_file}")

        # Generate visualizations
        portfolio_df = pd.DataFrame(strategy_manager.metrics['portfolio_values'])
        if not portfolio_df.empty:
            if 'value' in portfolio_df.columns:
                portfolio_df = portfolio_df.rename(columns={'value': 'portfolio_value'})
            if 'portfolio_value' in portfolio_df.columns:
                portfolio_save_path = os.path.join(trading_logger.run_timestamp_dir, f"{args.symbol}_portfolio_performance.png")
                plot_portfolio_performance(args.symbol, portfolio_df, portfolio_save_path)
        
        # Plot trade distribution
        trades_df = pd.DataFrame(strategy_manager.metrics['trades'])
        if not trades_df.empty:
            trades_save_path = os.path.join(trading_logger.run_timestamp_dir, f"{args.symbol}_trade_distribution.png")
            plot_trade_distribution(args.symbol, trades_df, trades_save_path)
        
        # Plot backtest results
        if not signals.empty:
            backtest_save_path = os.path.join(trading_logger.run_timestamp_dir, f"{args.symbol}_backtest_results.png")
            plot_backtest_results(args.symbol, signals, backtest_save_path)

    except Exception as e:
        logger.error(f"Error running strategy: {str(e)}")
        raise

if __name__ == '__main__':
    main() 