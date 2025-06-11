import argparse
from datetime import datetime
import logging
from src.data.vendors.polygon_provider import PolygonProvider
from src.strategies.SingleStock.single_stock_strategy import SingleStockStrategy
from src.utils.run_manager import RunManager
import os

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

        # Initialize strategy
        strategy = SingleStockStrategy(
            use_ml=(args.strategy == 'ml'),
            cache_dir=args.cache_dir
        )

        # Initialize run manager
        run_manager = RunManager()

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
        
        # Display returns
        print(f"Cumulative Returns: {cumulative_returns.iloc[-1]:.2f}")
        print(f"Total Returns: {cumulative_returns.iloc[-1] - 1:.2%}")

        # Log results
        logger.info("\nStrategy Results:")
        logger.info(f"Total trades: {len(signals[signals['signal'] != 0])}")
        logger.info(f"Buy signals: {len(signals[signals['signal'] == 1])}")
        logger.info(f"Sell signals: {len(signals[signals['signal'] == -1])}")
        
        if 'Trade_Profit' in signals.columns:
            total_profit = signals['Trade_Profit'].sum()
            logger.info(f"Total profit: ${total_profit:.2f}")

        # Save results
        output_file = os.path.join(log_dir, f"results_{args.symbol}_{args.strategy}_{args.start_date}_{args.end_date}.csv")
        signals.to_csv(output_file)
        logger.info(f"Results saved to {output_file}")

        # Save trades and portfolio logs
        run_manager.save_logs(args.symbol)

    except Exception as e:
        logger.error(f"Error running strategy: {str(e)}")
        raise

if __name__ == '__main__':
    main() 