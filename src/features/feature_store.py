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
        
        # Sort ranges by start date
        cache_ranges.sort(key=lambda x: x[0])
        
        # Find missing ranges
        missing_ranges = []
        current_date = start_date
        
        for cache_start, cache_end in cache_ranges:
            # If current date is before this cache range starts
            if current_date < cache_start:
                # Add the gap as a missing range
                missing_ranges.append((current_date, cache_start))
            # Update current date to the end of this cache range
            current_date = max(current_date, cache_end)
        
        # If we haven't covered the entire requested range
        if current_date < end_date:
            missing_ranges.append((current_date, end_date))
        
        # If we have no missing ranges, return empty list
        if not missing_ranges:
            return []
            
        # Check if we have complete coverage
        if cache_ranges:
            min_start = min(r[0] for r in cache_ranges)
            max_end = max(r[1] for r in cache_ranges)
            if min_start <= start_date and max_end >= end_date:
                return []
        
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
        
        print(f"Looking for cache files in {self.cache_dir}")
        cache_files = self._get_cache_files(symbol)
        print(f"Found cache files: {cache_files}")
        
        # Find missing date ranges
        missing_ranges = self._find_missing_date_ranges(symbol, start_dt, end_dt)
        print(f"Missing date ranges: {missing_ranges}")
        
        # If we have missing ranges, return None to trigger recalculation
        if missing_ranges:
            return None
        
        # Get all relevant cache files
        if not cache_files:
            return None
        
        # Combine data from all relevant cache files
        combined_data = []
        for file in cache_files:
            try:
                _, file_start, file_end = self._parse_cache_filename(file)
                print(f"Checking cache file: {file}")
                print(f"File date range: {file_start} to {file_end}")
                # Compare dates without time components
                if (file_start.date() <= end_dt.date() and file_end.date() >= start_dt.date()):
                    cached_data = joblib.load(file)
                    print(f"Loaded data with columns: {cached_data.columns.tolist()}")
                    # Filter for requested date range
                    mask = (cached_data.index.date >= start_dt.date()) & (cached_data.index.date <= end_dt.date())
                    filtered_data = cached_data[mask]
                    if not filtered_data.empty:
                        combined_data.append(filtered_data)
                        print(f"Added data from {file}")
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
        
        # Ensure we have data for the entire requested range
        if result.index.date.min() > start_dt.date() or result.index.date.max() < end_dt.date():
            print(f"Data range mismatch: got {result.index.date.min()} to {result.index.date.max()}, need {start_dt.date()} to {end_dt.date()}")
            return None
        
        # Filter for requested features
        if features is not None:
            # Check which features are available
            available_features = [f for f in features if f in result.columns]
            if not available_features:
                print(f"No requested features available. Requested: {features}, Available: {result.columns.tolist()}")
                return None
            # Only keep the requested features that are available
            result = result[available_features]
            # Verify we have all requested features
            if set(features) != set(available_features):
                print(f"Missing some requested features. Requested: {features}, Available: {available_features}")
                return None
        
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