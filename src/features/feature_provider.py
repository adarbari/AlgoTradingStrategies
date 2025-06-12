"""
Feature provider implementation that handles feature calculation and caching.
"""

from typing import Dict, Optional
import pandas as pd
from datetime import datetime
from .feature_store import FeatureStore
from .technical_indicators import TechnicalIndicators

class FeatureProvider:
    """Feature provider implementation that handles feature calculation and caching."""
    
    def __init__(self, cache: Optional[FeatureStore] = None):
        """Initialize feature provider.
        
        Args:
            cache: Optional FeatureStore instance for caching
        """
        self.cache = cache or FeatureStore()
        self.technical_indicators = TechnicalIndicators()
    
    def get_features(
        self,
        symbol: str,
        data: pd.DataFrame,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """Get features for a symbol, using cache if available.
        
        Args:
            symbol: Stock symbol
            data: Price data
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with features
        """
        # Try to get features from cache first
        features_df = self.cache.get_cached_features(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        # If no cached features found, calculate and cache them
        if features_df is None:
            features_df = self.technical_indicators.calculate_features(
                data,
                None,  # Calculate all available features
                symbol=symbol
            )
            # If the input data has a 'target' column, add it to the features_df
            if 'target' in data.columns:
                features_df['target'] = data['target']
            # Cache the calculated features
            self.cache.cache_features(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                features_df=features_df
            )
        else:
            # If the input data has a 'target' column, add it to the features_df
            if 'target' in data.columns and 'target' not in features_df.columns:
                features_df['target'] = data['target']
        return features_df 