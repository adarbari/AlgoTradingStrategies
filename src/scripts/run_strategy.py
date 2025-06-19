import os
import sys
# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

import argparse
from datetime import datetime
import logging
from src.data.vendors.polygon_provider import PolygonProvider
from src.strategies.SingleStock.ma_crossover_strategy import MACrossoverStrategy
# from src.strategies.SingleStock.random_forest_strategy import RandomForestSingleStockStrategy
from src.utils.run_manager import StrategyManager
from src.helpers.logger import TradingLogger
from src.visualization.portfolio_visualizer import (
    plot_trade_distribution,
    plot_backtest_results
)
import pandas as pd
from src.data.cache.base import DataCache
import numpy as np
from src.data.cache.data_manager import DataManager

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
        logger.info("Starting strategy run for %s using %s strategy", args.symbol, args.strategy)
        logger.info("Date range: %s to %s", args.start_date, args.end_date)
        
        # Initialize data provider
        data_cache = DataCache()
        data_manager = DataManager(provider=PolygonProvider(), cache=data_cache)
        
        # Get historical data
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
        
        time_series_data = data_manager.get_data(
            symbol=args.symbol,
            start_time=start_date,
            end_time=end_date
        )
        data = time_series_to_dataframe(time_series_data)
        
        if data.empty:
            logger.error("No data found for %s in the specified date range", args.symbol)
            return
            
        logger.info("Retrieved %d data points for %s", len(data), args.symbol)
        
        # Initialize strategy
        if args.strategy == 'ma':
            strategy = MACrossoverStrategy()
        else:
            logger.error("Unsupported strategy type: %s", args.strategy)
            return
            
        # Initialize strategy manager
        strategy_manager = StrategyManager(trading_logger=trading_logger)
        strategy_manager.initialize_strategy(args.symbol, args.strategy)
        
        # Generate signals
        signals = strategy.generate_signals(data, args.symbol, start_date)
        
        # Calculate returns
        signals['returns'] = signals['close'].pct_change()
        signals['strategy_returns'] = signals['returns'] * (signals['action'] == 'BUY').astype(int)
        cumulative_returns = (1 + signals['strategy_returns']).cumprod()
        
        # Track position for profit calculation
        position = 0  # Current position (shares)
        position_price = 0  # Average price of current position
        
        # Log each period and trade
        for index, row in signals.iterrows():
            # Log period information
            period_data = {
                'close': row['close'],
                'ma_short': row['features']['ma_short'],
                'ma_long': row['features']['ma_long'],
                'action': row['action'],
                'returns': row['returns'],
                'strategy_returns': row['strategy_returns']
            }
            trading_logger.log_period(args.symbol, index, period_data)
            
            # Handle trades based on signals
            if row['action'] in ['BUY', 'SELL']:
                trade_type = row['action']
                shares = 100  # Fixed trade size
                price = row['close']
                
                # Calculate profit for sell trades
                profit = None
                if trade_type == 'SELL' and position > 0:
                    profit = (price - position_price) * shares
                
                # Update position
                if trade_type == 'BUY':
                    position = shares
                    position_price = price
                else:  # SELL
                    position = 0
                    position_price = 0
                
                # Log trade
                strategy_manager.log_trade(
                    symbol=args.symbol,
                    trade_type=trade_type,
                    price=price,
                    shares=shares,
                    timestamp=index,
                    profit=profit
                )
        
        # Calculate strategy summary
        total_trades = len(signals[signals['action'].isin(['BUY', 'SELL'])])
        winning_trades = len(signals[(signals['action'] == 'SELL') & (signals['strategy_returns'] > 0)])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        total_profit = signals['strategy_returns'].sum()
        avg_profit_per_trade = total_profit / total_trades if total_trades > 0 else 0
        
        # Calculate drawdown
        cumulative_returns = (1 + signals['strategy_returns']).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = drawdowns.min() * 100
        
        # Calculate Sharpe ratio
        returns = signals['strategy_returns']
        sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std() if len(returns) > 0 else 0
        
        summary = {
            'total_trades': total_trades,
            'win_rate': win_rate * 100,
            'total_profit': total_profit,
            'avg_profit_per_trade': avg_profit_per_trade,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio
        }
        
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

if __name__ == "__main__":
    main() 