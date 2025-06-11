import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.utils import StrategyManager
from src.helpers.logger import TradingLogger

def test_strategy_manager():
    """Test the StrategyManager functionality"""
    print("Testing StrategyManager...")
    
    # Initialize TradingLogger and StrategyManager
    trading_logger = TradingLogger()
    strategy_manager = StrategyManager(trading_logger=trading_logger)
    
    # Test strategy initialization
    symbol = "AAPL"
    strategy_type = "ml"
    strategy_manager.initialize_strategy(symbol, strategy_type)
    print(f"Initialized {strategy_type.upper()} strategy for {symbol}")
    
    # Create sample data
    dates = pd.date_range(start='2025-01-01', end='2025-01-10', freq='D')
    prices = np.random.normal(150, 2, len(dates))  # Random prices around $150
    
    # Test trade logging
    portfolio_value = 10000
    position = 0
    
    for i, (date, price) in enumerate(zip(dates, prices)):
        # Simulate some trades
        if i % 3 == 0:  # Buy every 3rd day
            trade_type = "BUY"
            shares = 10
            profit = None
            position = price
            portfolio_value -= price * shares
        elif i % 3 == 1:  # Sell every 3rd day
            trade_type = "SELL"
            shares = 10
            profit = (price - position) * shares if position > 0 else 0
            portfolio_value += price * shares
            position = 0
        else:
            continue
            
        # Log trade
        strategy_manager.log_trade(
            symbol=symbol,
            trade_type=trade_type,
            price=price,
            shares=shares,
            timestamp=date,
            profit=profit,
            portfolio_value=portfolio_value
        )
        
        # Log portfolio value
        strategy_manager.log_portfolio_value(
            symbol=symbol,
            timestamp=date,
            portfolio_value=portfolio_value
        )
    
    # Test strategy summary
    summary = strategy_manager.get_strategy_summary()
    print("\nStrategy Summary:")
    print(f"Total trades: {summary['total_trades']}")
    print(f"Win rate: {summary['win_rate']:.2%}")
    print(f"Total profit: ${summary['total_profit']:.2f}")
    print(f"Portfolio return: {summary['total_return']:.2%}")
    
    # Test strategy comparison
    print("\nTesting strategy comparison...")
    ma_summary = {
        'total_trades': 5,
        'total_profit': 1000.0,
        'win_rate': 0.6,
        'final_portfolio_value': 11000.0,
        'total_return': 0.1
    }
    
    ml_summary = {
        'total_trades': 5,
        'total_profit': 1500.0,
        'win_rate': 0.7,
        'final_portfolio_value': 11500.0,
        'total_return': 0.15
    }
    
    strategy_manager.compare_strategies(ma_summary, ml_summary)
    
    # Verify files were created
    run_dir = strategy_manager.run_dir
    print(f"\nVerifying files in {run_dir}:")
    expected_files = [
        'trades.csv',
        'periods.csv',
        'portfolio_values.csv',
        f'{symbol}_strategy_comparison.txt'
    ]
    
    for file in expected_files:
        file_path = os.path.join(run_dir, file)
        exists = os.path.exists(file_path)
        print(f"{file}: {'✓' if exists else '✗'}")
    
    print("\nTest completed!")

if __name__ == '__main__':
    test_strategy_manager() 