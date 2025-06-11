import pandas as pd
from data.indicators import TrendIndicator, MomentumIndicator, VolatilityIndicator, VolumeIndicator

class FeatureStoreManager:
    """Manages the calculation and storage of all indicators."""
    def __init__(self):
        self.trend_indicator = TrendIndicator()
        self.momentum_indicator = MomentumIndicator()
        self.volatility_indicator = VolatilityIndicator()
        self.volume_indicator = VolumeIndicator()

    def calculate_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate all indicators and return a DataFrame with all features."""
        df = data.copy()
        # Calculate each indicator
        df = self.trend_indicator.calculate(df)
        df = self.momentum_indicator.calculate(df)
        df = self.volatility_indicator.calculate(df)
        df = self.volume_indicator.calculate(df)

        # Add missing features
        df['Price_Change'] = df['Close'].pct_change()
        df['Volume_Change'] = df['Volume'].pct_change()
        df['Volatility'] = df['Price_Change'].rolling(window=20).std()
        df['Price_Change_5min'] = df['Close'].pct_change(5)
        df['Price_Change_15min'] = df['Close'].pct_change(15)
        df['Price_Range'] = (df['High'] - df['Low']) / df['Close']
        df['Price_Range_MA'] = df['Price_Range'].rolling(window=10).mean()
        df['Volatility_5min'] = df['Price_Change'].rolling(window=5).std()
        df['Volatility_15min'] = df['Price_Change'].rolling(window=15).std()

        # Calculate target based on local minima and maxima
        df['target'] = 0
        # Local minima: price is lower than both previous and next
        df.loc[(df['Close'] < df['Close'].shift(1)) & (df['Close'] < df['Close'].shift(-1)), 'target'] = 1
        # Local maxima: price is higher than both previous and next
        df.loc[(df['Close'] > df['Close'].shift(1)) & (df['Close'] > df['Close'].shift(-1)), 'target'] = -1

        # Add Price column (equal to Close)
        df['Price'] = df['Close']

        return df 