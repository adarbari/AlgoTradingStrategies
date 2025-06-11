"""
Moving Average Crossover single stock trading strategy implementation.
"""
import pandas as pd
import numpy as np
from decimal import Decimal
from src.features import TechnicalIndicators
from src.features.feature_store import FeatureStore

class MACrossOverSingleStockStrategy:
    def __init__(self, short_window=20, long_window=50, trade_size=1000, total_budget=10000, cache_dir='feature_cache'):
        self.short_window = short_window
        self.long_window = long_window
        self.trade_size = Decimal(str(trade_size))
        self.total_budget = Decimal(str(total_budget))
        self.feature_engineer = TechnicalIndicators()
        self.feature_store = FeatureStore(cache_dir=cache_dir)

    def generate_signals(self, data, run_manager=None, symbol=None):
        signals = data.copy()
        # Calculate moving averages
        signals['SMA_short'] = signals['close'].rolling(window=self.short_window).mean()
        signals['SMA_long'] = signals['close'].rolling(window=self.long_window).mean()
        signals['signal'] = 0
        signals.loc[signals['SMA_short'] > signals['SMA_long'], 'signal'] = 1
        signals.loc[signals['SMA_short'] < signals['SMA_long'], 'signal'] = -1
        return signals 