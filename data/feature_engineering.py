import pandas as pd
import numpy as np
import os
import logging
from typing import Dict, List, Optional
import json
from datetime import datetime, timedelta
from data.feature_store_manager import FeatureStoreManager

class FeatureEngineer:
    def __init__(self, cache_dir: str = "data_cache"):
        self.cache_dir = cache_dir
        self._setup_cache()
        self.logger = logging.getLogger(__name__)
        self.feature_store_manager = FeatureStoreManager()
        
    def _setup_cache(self):
        """Create cache directory if it doesn't exist"""
        os.makedirs(os.path.join(self.cache_dir, "features"), exist_ok=True)
        
    def _get_cache_path(self, symbol: str, feature_set: str) -> str:
        """Generate cache file path for features"""
        return os.path.join(
            self.cache_dir, "features",
            f"{symbol}_{feature_set}.parquet"
        )
        
    def _is_cached(self, symbol: str, feature_set: str) -> bool:
        """Check if features are already cached"""
        cache_path = self._get_cache_path(symbol, feature_set)
        return os.path.exists(cache_path)
        
    def _save_to_cache(self, features: pd.DataFrame, symbol: str, feature_set: str):
        """Save features to cache"""
        cache_path = self._get_cache_path(symbol, feature_set)
        features.to_parquet(cache_path)
        self.logger.info(f"Saved features for {symbol} to cache: {cache_path}")
        
    def _load_from_cache(self, symbol: str, feature_set: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Load features from cache and filter to requested date range"""
        cache_path = self._get_cache_path(symbol, feature_set)
        features = pd.read_parquet(cache_path)
        
        # Convert dates to datetime if they're not already
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        elif not isinstance(start_date, pd.Timestamp):
            start_date = pd.to_datetime(start_date)
            
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)
        elif not isinstance(end_date, pd.Timestamp):
            end_date = pd.to_datetime(end_date)
            
        # Filter data to requested range
        features = features[(features.index >= start_date) & (features.index <= end_date)]
        self.logger.info(f"Loaded features for {symbol} from cache, filtered to {start_date} - {end_date}")
        return features
        
    def create_features(self, data: pd.DataFrame, symbol: str, feature_type: str) -> pd.DataFrame:
        """Create features using FeatureStoreManager."""
        if data is None or data.empty:
            logging.error("No data provided for feature engineering")
            return None

        # Calculate all indicators using FeatureStoreManager
        features = self.feature_store_manager.calculate_all_indicators(data)
        return features
        
    def create_features_multiple_symbols(self, data_dict: Dict[str, pd.DataFrame], 
                                       feature_set: str = "technical",
                                       force_refresh: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Create features for multiple symbols
        
        Args:
            data_dict: Dictionary mapping symbols to their respective DataFrames
            feature_set: Name of the feature set
            force_refresh: If True, ignore cache and create fresh features
            
        Returns:
            Dictionary mapping symbols to their respective feature DataFrames
        """
        results = {}
        for symbol, data in data_dict.items():
            try:
                # Ensure symbol is a string
                symbol_str = str(symbol)
                # Debug: log index and columns
                self.logger.debug(f"Symbol: {symbol_str}, Data index: {data.index}, Columns: {data.columns}")
                # Ensure index is DatetimeIndex and not MultiIndex
                if isinstance(data.index, pd.MultiIndex):
                    self.logger.warning(f"Data for {symbol_str} has MultiIndex. Resetting index.")
                    data = data.reset_index()
                    # Try to find the date column
                    date_col = None
                    for col in data.columns:
                        if 'date' in col.lower():
                            date_col = col
                            break
                    if date_col:
                        data = data.set_index(date_col)
                        data.index = pd.to_datetime(data.index)
                    else:
                        # Fallback: set index to first column
                        data = data.set_index(data.columns[0])
                        data.index = pd.to_datetime(data.index)
                else:
                    data.index = pd.to_datetime(data.index)

                # Flatten MultiIndex columns if present
                if isinstance(data.columns, pd.MultiIndex):
                    self.logger.warning(f"Data for {symbol_str} has MultiIndex columns. Flattening columns.")
                    # If all columns are for a single ticker, drop the second level
                    if len(set(data.columns.get_level_values(1))) == 1:
                        data.columns = data.columns.get_level_values(0)
                    else:
                        # Otherwise, join the levels with '_'
                        data.columns = ['_'.join(map(str, col)).strip() for col in data.columns.values]

                # Pass start and end date for cache key
                start_date = data.index.min()
                end_date = data.index.max()
                features = self.create_features(data, symbol_str, feature_set)
                if not features.empty:
                    results[symbol_str] = features
                else:
                    self.logger.warning(f"Skipping {symbol_str} due to empty features.")
            except Exception as e:
                self.logger.error(f"Failed to create features for {symbol}: {str(e)}")
                continue
        return results 