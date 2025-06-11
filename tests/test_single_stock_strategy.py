import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from strategies.SingleStock.single_stock_strategy import SingleStockStrategy

def generate_test_data(days=30):
    """Generate sample price data for testing"""
    # Generate 1-minute data for 30 days (6.5 hours per day)
    minutes_per_day = 6.5 * 60
    total_minutes = days * minutes_per_day
    dates = pd.date_range(start='2024-01-01', periods=total_minutes, freq='1min')
    np.random.seed(42)
    
    # Generate price data with trend and seasonality
    price = 100
    prices = []
    trend = 0.0001  # Slight upward trend
    seasonality = 0.001  # Daily seasonality
    
    for i in range(len(dates)):
        # Add trend
        price += trend
        
        # Add seasonality (higher prices in the morning and afternoon)
        hour = dates[i].hour
        if 9 <= hour <= 11:  # Morning peak
            price *= (1 + seasonality)
        elif 14 <= hour <= 15:  # Afternoon peak
            price *= (1 + seasonality)
        
        # Add random walk
        price += np.random.normal(0, 0.1)
        prices.append(price)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Open': prices,
        'High': [p * (1 + np.random.uniform(0, 0.01)) for p in prices],
        'Low': [p * (1 - np.random.uniform(0, 0.01)) for p in prices],
        'Close': prices,
        'Volume': np.random.randint(1000, 10000, size=len(dates))
    }, index=dates)
    
    return df

def test_strategy():
    """Test both ML and non-ML strategies"""
    data = generate_test_data(days=30)
    split_idx = int(len(data) * 0.8)
    train_data = data.iloc[:split_idx]
    test_data = data.iloc[split_idx:]

    print("\nTesting Moving Average Crossover Strategy (Out-of-sample):")
    strategy_ma = SingleStockStrategy(use_ml=False)
    # Fit moving averages on train_data, but only evaluate on test_data
    signals_ma_full = strategy_ma.generate_signals(pd.concat([train_data, test_data]))
    signals_ma = signals_ma_full.loc[test_data.index]
    final_value_ma = signals_ma['Portfolio_Value'].iloc[-1]
    total_trades_ma = (signals_ma['Signal'].diff().abs() > 0).sum()
    total_profit_ma = final_value_ma - 10000
    print(f"Final Portfolio Value: ${final_value_ma:.2f}")
    print(f"Total Trades: {total_trades_ma}")
    print(f"Total Profit: ${total_profit_ma:.2f}")

    print("\nTesting ML Strategy (Out-of-sample):")
    strategy_ml = SingleStockStrategy(use_ml=True)
    # Train on train_data, generate signals only for test_data
    strategy_ml.train_model(train_data)
    signals_ml_full = strategy_ml.generate_signals(pd.concat([train_data, test_data]))
    signals_ml = signals_ml_full.loc[test_data.index]
    final_value_ml = signals_ml['Portfolio_Value'].iloc[-1]
    total_trades_ml = (signals_ml['Signal'].diff().abs() > 0).sum()
    total_profit_ml = final_value_ml - 10000
    print(f"Final Portfolio Value: ${final_value_ml:.2f}")
    print(f"Total Trades: {total_trades_ml}")
    print(f"Total Profit: ${total_profit_ml:.2f}")

if __name__ == "__main__":
    test_strategy() 