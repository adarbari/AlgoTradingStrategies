import argparse
from datetime import datetime
import logging
from src.data.vendors.polygon_provider import PolygonProvider
from src.strategies.SingleStock import RandomForestSingleStockStrategy, MACrossOverSingleStockStrategy
from src.utils.run_manager import RunManager
from src.helpers.logger import TradingLogger
import os
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description='Run trading strategy')
    parser.add_argument('--symbol', type=str, required=True, help='Stock symbol')
    parser.add_argument('--strategy', type=str, choices=['ml', 'ma'], default='ml', help='Strategy type (ml or ma)')
    parser.add_argument('--start-date', type=str, required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--cache-dir', type=str, default='feature_cache', help='Directory for feature cache')
    args = parser.parse_args()

    # Set up logging
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(filename=os.path.join(log_dir, 'run_strategy.log'), level=logging.INFO)
    logger = logging.getLogger(__name__)

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

        # Initialize run manager and trading logger
        run_manager = RunManager()
        trading_logger = TradingLogger()

        # Generate signals
        logger.info(f"Generating signals using {args.strategy.upper()} strategy")
        signals = strategy.generate_signals(data, run_manager, args.symbol)

        if signals is None or signals.empty:
            logger.error("No signals generated")
            return

        # Calculate returns
        signals['returns'] = signals['close'].pct_change().fillna(0)
        signals['strategy_returns'] = signals['returns'] * signals['signal'].shift(1).fillna(0)
        cumulative_returns = (1 + signals['strategy_returns']).cumprod()
        
        # Initialize portfolio tracking
        portfolio_value = 10000  # Initial portfolio value
        position = 0  # Current position (shares)
        
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
                    profit = (price - position) * shares
                
                # Update position and portfolio value
                if trade_type == 'BUY':
                    position = price
                    portfolio_value -= price * shares
                else:  # SELL
                    if position > 0:
                        portfolio_value += price * shares
                        position = 0
                
                # Log trade
                trading_logger.log_trade(
                    symbol=args.symbol,
                    trade_type=trade_type,
                    price=price,
                    shares=shares,
                    timestamp=index,
                    profit=profit,
                    portfolio_value=portfolio_value
                )
            
            # Log portfolio value for each period
            trading_logger.log_portfolio_value(args.symbol, index, portfolio_value)
        
        # Display returns
        print(f"Cumulative Returns: {cumulative_returns.iloc[-1]:.2f}")
        print(f"Total Returns: {cumulative_returns.iloc[-1] - 1:.2%}")

        # Generate performance report
        trades_df = pd.read_csv(os.path.join(trading_logger.run_dir, "logs", "trades.csv"))
        portfolio_df = pd.read_csv(os.path.join(trading_logger.run_dir, "logs", "portfolio_values.csv"))
        performance_report = trading_logger.generate_performance_report(args.symbol, trades_df, portfolio_df)
        
        # Log performance metrics
        logger.info("\nStrategy Results:")
        logger.info(f"Total trades: {performance_report['total_trades']}")
        logger.info(f"Win rate: {performance_report['win_rate']:.2%}")
        logger.info(f"Total profit: ${performance_report['total_profit']:.2f}")
        logger.info(f"Portfolio return: {performance_report['portfolio_return']:.2%}")

        # Save results
        output_file = os.path.join(log_dir, f"results_{args.symbol}_{args.strategy}_{args.start_date}_{args.end_date}.csv")
        signals.to_csv(output_file)
        logger.info(f"Results saved to {output_file}")

        # Generate visualizations
        trading_logger.plot_portfolio_performance(args.symbol, portfolio_df)
        trading_logger.plot_trade_distribution(args.symbol, trades_df)

    except Exception as e:
        logger.error(f"Error running strategy: {str(e)}")
        raise

if __name__ == '__main__':
    main() 