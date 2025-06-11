import os
import pandas as pd
from typing import List, Optional, Tuple
import joblib
from datetime import datetime
import glob

class FeatureStore:
    """Manages caching of calculated features with support for partial date ranges."""
    
    def __init__(self, cache_dir: str = 'feature_cache'):
        """Initialize the feature store.
        
        Args:
            cache_dir: Directory to store cached features
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_files(self, symbol: str) -> List[str]:
        """Get all cache files for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of cache file paths
        """
        pattern = os.path.join(self.cache_dir, f"{symbol}_*_features.joblib")
        return sorted(glob.glob(pattern))
    
    def _parse_cache_filename(self, filename: str) -> Tuple[str, datetime, datetime]:
        """Parse cache filename to get symbol and date range.
        
        Args:
            filename: Cache filename
            
        Returns:
            Tuple of (symbol, start_date, end_date)
        """
        basename = os.path.basename(filename)
        parts = basename.split('_')
        symbol = parts[0]
        start_date = datetime.strptime(parts[1], '%Y-%m-%d')
        end_date = datetime.strptime(parts[2], '%Y-%m-%d')
        return symbol, start_date, end_date
    
    def _get_cache_path(self, symbol: str, start_date: str, end_date: str) -> str:
        """Get the cache file path for a given symbol and date range."""
        return os.path.join(
            self.cache_dir,
            f"{symbol}_{start_date}_{end_date}_features.joblib"
        )
    
    def _find_missing_date_ranges(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Tuple[datetime, datetime]]:
        """Find date ranges that are not covered by existing cache files.
        
        Args:
            symbol: Stock symbol
            start_date: Requested start date
            end_date: Requested end date
            
        Returns:
            List of (start_date, end_date) tuples for missing ranges
        """
        cache_files = self._get_cache_files(symbol)
        if not cache_files:
            return [(start_date, end_date)]
        
        # Sort cache files by start date
        cache_ranges = []
        for file in cache_files:
            _, file_start, file_end = self._parse_cache_filename(file)
            cache_ranges.append((file_start, file_end))
        
        # Find missing ranges
        missing_ranges = []
        current_date = start_date
        
        for cache_start, cache_end in sorted(cache_ranges):
            if current_date < cache_start:
                missing_ranges.append((current_date, cache_start))
            current_date = max(current_date, cache_end)
        
        if current_date < end_date:
            missing_ranges.append((current_date, end_date))
        
        return missing_ranges
    
    def get_cached_features(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        features: Optional[List[str]] = None
    ) -> Optional[pd.DataFrame]:
        """Get cached features if they exist.
        
        Args:
            symbol: Stock symbol
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            features: List of features to retrieve (if None, return all)
            
        Returns:
            DataFrame with cached features or None if not found
        """
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Find missing date ranges
        missing_ranges = self._find_missing_date_ranges(symbol, start_dt, end_dt)
        
        # If we have missing ranges, return None to trigger recalculation
        if missing_ranges:
            return None
        
        # Get all relevant cache files
        cache_files = self._get_cache_files(symbol)
        if not cache_files:
            return None
        
        # Combine data from all relevant cache files
        combined_data = []
        for file in cache_files:
            try:
                _, file_start, file_end = self._parse_cache_filename(file)
                if (file_start <= end_dt and file_end >= start_dt):
                    cached_data = joblib.load(file)
                    # Filter for requested date range
                    mask = (cached_data.index >= start_dt) & (cached_data.index <= end_dt)
                    filtered_data = cached_data[mask]
                    if not filtered_data.empty:
                        combined_data.append(filtered_data)
            except Exception as e:
                print(f"Error loading cache file {file}: {e}")
                continue
        
        if not combined_data:
            return None
        
        # Combine all data
        result = pd.concat(combined_data)
        result = result.sort_index()
        
        # Remove duplicates (in case of overlapping cache files)
        result = result[~result.index.duplicated(keep='first')]
        
        # Filter for requested features
        if features is not None:
            result = result[features]
        
        return result
    
    def cache_features(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        features_df: pd.DataFrame
    ) -> None:
        """Cache calculated features.
        
        Args:
            symbol: Stock symbol
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            features_df: DataFrame containing the features
        """
        if features_df.empty:
            return
            
        # Ensure the index is datetime
        if not isinstance(features_df.index, pd.DatetimeIndex):
            features_df.index = pd.to_datetime(features_df.index)
        
        # Get the actual date range from the data
        actual_start = features_df.index.min().strftime('%Y-%m-%d')
        actual_end = features_df.index.max().strftime('%Y-%m-%d')
        
        cache_path = self._get_cache_path(symbol, actual_start, actual_end)
        try:
            joblib.dump(features_df, cache_path)
        except Exception as e:
            print(f"Error caching features: {e}")
    
    def clear_cache(self, symbol: Optional[str] = None) -> None:
        """Clear the feature cache.
        
        Args:
            symbol: If provided, only clear cache for this symbol
        """
        if symbol:
            pattern = f"{symbol}_*_features.joblib"
            for file in glob.glob(os.path.join(self.cache_dir, pattern)):
                os.remove(file)
        else:
            for file in glob.glob(os.path.join(self.cache_dir, "*_features.joblib")):
                os.remove(file) 