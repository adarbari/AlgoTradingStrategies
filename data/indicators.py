import pandas as pd
import numpy as np

class Indicator:
    """Generic interface for all indicators."""
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate the indicator and return a DataFrame with the results."""
        raise NotImplementedError("Subclasses must implement calculate method.")


class TrendIndicator(Indicator):
    """Trend indicators like SMA, EMA, MACD."""
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        # SMA
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        return df


class MomentumIndicator(Indicator):
    """Momentum indicators like RSI."""
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        return df


class VolatilityIndicator(Indicator):
    """Volatility indicators like Bollinger Bands."""
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        df['BB_Std'] = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * 2)
        df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * 2)
        return df


class VolumeIndicator(Indicator):
    """Volume indicators like Volume MA."""
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        # Volume Moving Averages
        df['Volume_MA_5'] = df['Volume'].rolling(window=5).mean()
        df['Volume_MA_15'] = df['Volume'].rolling(window=15).mean()
        return df 