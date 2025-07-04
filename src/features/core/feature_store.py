import os
import pandas as pd
from typing import List, Optional, Tuple, Dict, Any
import joblib
from datetime import datetime
import json
import pickle

from src.data.data_manager import DataManager
from src.data.providers.vendors.polygon.polygon_provider import PolygonProvider
from src.data.types.base_types import TimeSeriesData
from src.data.types.data_type import DataType
from src.data.types.symbol import Symbol
from ..implementations.technical_indicators import TechnicalIndicators
from .feature_metadata import FeatureStoreMetadata, FeatureFileMetadata
from ..types.feature_definitions import FeatureMetadata, FeatureType, FeatureCalculationEngineType

import sys
import inspect


class FeatureStore:
    """Manages caching of calculated features with metadata tracking."""
    
    _instance = None
    _initialized = False
    _cache_dir = 'feature_cache'

    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FeatureStore, cls).__new__(cls)
            os.makedirs(cls._cache_dir, exist_ok=True)
        return cls._instance
    
    def __init__(self):
        """Initialize the feature store."""
        if not self._initialized:
            self.cache_dir = self._cache_dir
            self.technical_indicators = TechnicalIndicators()
            self.metadata = FeatureStoreMetadata()
            
            # Initialize in-memory cache before loading from metadata
            self._in_memory_features = {}
            
            # Migrate existing metadata to use relative paths
            self.metadata.migrate_to_relative_paths()
            self.load_in_memory_Features_from_metadata()
            
            self._initialized = True
            self._data_manager = DataManager()
            
            # Load feature mapping from feature definitions
            self._feature_mapping = FeatureMetadata.get_feature_mapping()
    
    @classmethod
    def get_instance(cls) -> 'FeatureStore':
        """Get the singleton instance of FeatureStore."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    
    def generate_features(self, symbol: Symbol, start_time: datetime, end_time: datetime, 
                         feature_names: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Generate features for a symbol within a time range.
        
        Args:
            symbol: Trading symbol
            start_time: Start timestamp
            end_time: End timestamp
            feature_names: List of feature names to generate. If None, generates all available features.
            
        Returns:
            DataFrame with requested features
        """
        # Check if features already exist in cache for this symbol and time range
        cached_features = self.get_features(symbol, start_time, end_time)
        if cached_features is not None and not cached_features.empty:
            # If specific features are requested, filter the cached features
            if feature_names is not None:
                available_features = [f for f in feature_names if f in cached_features.columns]
                if available_features:
                    return cached_features[available_features]
            else:
                # Return all cached features if no specific features requested
                return cached_features

        # If no specific features requested, generate all available
        if feature_names is None:
            feature_names = list(self._feature_mapping.keys())
        
        # Validate feature names
        invalid_features = [f for f in feature_names if f not in self._feature_mapping]
        if invalid_features:
            raise ValueError(f"Unknown features: {invalid_features}. Available features: {list(self._feature_mapping.keys())}")
        
        # Group features by data type and dependencies
        feature_groups = self._group_features_by_dependencies(feature_names)
        
        # Generate features for each group
        for group in feature_groups:
            self._generate_feature_group(symbol, start_time, end_time, group)
        
        # Get the combined features from cache
        features = self.get_features(symbol, start_time, end_time)
        self.store_features_in_metadata(symbol=symbol,features_df=features,start_timestamp=start_time, end_timestamp=end_time)
        return features
    
    def _group_features_by_dependencies(self, feature_names: List[str]) -> List[List[str]]:
        """
        Group features by their dependencies to ensure proper generation order.
        
        Args:
            feature_names: List of feature names to group
            
        Returns:
            List of feature groups, ordered by dependencies
        """
        # First group: base features (no dependencies)
        base_features = []
        derived_features = []
        
        for feature in feature_names:
            feature_info = self._feature_mapping[feature]
            if feature_info.get('feature_type') == FeatureType.BASE:
                base_features.append(feature)
            else:
                derived_features.append(feature)
        
        # Return groups in dependency order
        groups = []
        if base_features:
            groups.append(base_features)
        if derived_features:
            groups.append(derived_features)
        
        return groups
    
    def _generate_feature_group(self, symbol: Symbol, start_time: datetime, end_time: datetime, 
                               feature_names: List[str]):
        """
        Generate a group of features that share the same data type and generation method.
        
        Args:
            symbol: Trading symbol
            start_time: Start timestamp
            end_time: End timestamp
            feature_names: List of feature names to generate
        """
        if not feature_names:
            return
        
        # Get the first feature's info to determine data type and method
        first_feature = feature_names[0]
        feature_info = self._feature_mapping[first_feature]
        feature_type = feature_info.get('feature_type')
        
        # Handle base features 
        if feature_type == FeatureType.BASE:
            data_type = feature_info['data_type']
            if data_type == DataType.OHLCV:
                data = self._data_manager.get_ohlcv_data(
                    symbol=str(symbol),
                    start_time=start_time,
                    end_time=end_time
                )
                
                if data is not None and len(data) > 0:
                    data_df = data.to_dataframe()
                    self._add_to_memory_cache(symbol, data_df)
            else:
                raise NotImplementedError(f"Data Type '{data_type}' not implemented for base features")
        
        # Handle derived features (calculated indicators)
        elif feature_type == FeatureType.DERIVED:
            engine_type = feature_info.get('feature_generation_engine_type')
            if engine_type == FeatureCalculationEngineType.OHLCV_DERIVED:
                # Get OHLCV data first (dependency)
                ohlcv_data = self._data_manager.get_ohlcv_data(
                    symbol=str(symbol),
                    start_time=start_time,
                    end_time=end_time
                )
                
                if ohlcv_data is not None and len(ohlcv_data) > 0:
                    # Generate technical indicators
                    technical_features_df = self.technical_indicators.calculate_features(
                        ohlcv_data, feature_names, symbol=str(symbol)
                    )
                    
                    if technical_features_df is not None and not technical_features_df.empty:
                        self._add_to_memory_cache(symbol, technical_features_df)
            
            elif engine_type == FeatureCalculationEngineType.ORDER_FLOW_DERIVED:
                # Future: Handle order flow derived features
                # This would use order flow data and calculate metrics like VWAP, order imbalance, etc.
                raise NotImplementedError(
                    f"Order flow derived features not yet implemented. "
                    f"Feature engine type: {engine_type}"
                )
                pass
        else:
            raise NotImplementedError(f"Feature type '{feature_type}' not implemented")

    
    def get_available_features(self) -> List[str]:
        """
        Get list of all available feature names.
        
        Returns:
            List of available feature names
        """
        return list(self._feature_mapping.keys())
    
    def get_features_by_category(self) -> Dict[str, List[str]]:
        """
        Get features grouped by category.
        
        Returns:
            Dictionary mapping categories to feature lists
        """
        return FeatureMetadata.get_features_by_category()
    
    def get_base_features(self) -> List[str]:
        """
        Get list of base features (no dependencies).
        
        Returns:
            List of base feature names
        """
        return FeatureMetadata.get_base_features()
    
    def get_derived_features(self) -> List[str]:
        """
        Get list of derived features (with dependencies).
        
        Returns:
            List of derived feature names
        """
        return FeatureMetadata.get_derived_features()
    
    def get_features_by_type(self, feature_type: FeatureType) -> List[str]:
        """
        Get features by their type (BASE or DERIVED).
        
        Args:
            feature_type: The type of features to retrieve
            
        Returns:
            List of feature names of the specified type
        """
        features = []
        for feature_name, feature_info in self._feature_mapping.items():
            if feature_info.get('feature_type') == feature_type:
                features.append(feature_name)
        return features
    
    def get_features_by_engine_type(self, engine_type: FeatureCalculationEngineType) -> List[str]:
        """
        Get features by their calculation engine type.
        
        Args:
            engine_type: The calculation engine type
            
        Returns:
            List of feature names using the specified engine
        """
        features = []
        for feature_name, feature_info in self._feature_mapping.items():
            if feature_info.get('feature_generation_engine_type') == engine_type:
                features.append(feature_name)
        return features
    
    def get_feature_type(self, feature_name: str) -> Optional[FeatureType]:
        """
        Get the type of a specific feature.
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            FeatureType or None if feature not found
        """
        if feature_name in self._feature_mapping:
            return self._feature_mapping[feature_name].get('feature_type')
        return None
    
    def get_feature_engine_type(self, feature_name: str) -> Optional[FeatureCalculationEngineType]:
        """
        Get the calculation engine type of a specific feature.
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            FeatureCalculationEngineType or None if feature not found
        """
        if feature_name in self._feature_mapping:
            return self._feature_mapping[feature_name].get('feature_generation_engine_type')
        return None
    
    def get_feature_description(self, feature_name: str) -> Optional[str]:
        """
        Get description for a specific feature.
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            Feature description or None if not found
        """
        if feature_name in self._feature_mapping:
            return self._feature_mapping[feature_name].get('description')
        return None
    
    def get_feature_category(self, feature_name: str) -> Optional[str]:
        """
        Get category for a specific feature.
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            Feature category or None if not found
        """
        if feature_name in self._feature_mapping:
            return self._feature_mapping[feature_name].get('category')
        return None
    
    def add_feature_mapping(self, feature_name: str, data_type: DataType, method: str, 
                           feature_type: FeatureType = FeatureType.DERIVED,
                           engine_type: Optional[FeatureCalculationEngineType] = None,
                           depends_on: Optional[List[str]] = None, description: str = "", 
                           category: str = "other"):
        """
        Add a new feature mapping.
        
        Args:
            feature_name: Name of the feature
            data_type: Data type required for this feature
            method: Method to call for generating this feature
            feature_type: Type of feature (BASE or DERIVED)
            engine_type: Calculation engine type (for derived features)
            depends_on: List of features this depends on (optional)
            description: Description of the feature
            category: Category of the feature
        """
        feature_mapping = {
            'data_type': data_type,
            'method': method,
            'feature_type': feature_type,
            'description': description,
            'category': category
        }
        
        if engine_type:
            feature_mapping['feature_generation_engine_type'] = engine_type
        
        if depends_on:
            feature_mapping['depends_on'] = depends_on
        
        self._feature_mapping[feature_name] = feature_mapping
    
    def store_features_in_metadata(self, symbol: Symbol, features_df: pd.DataFrame, 
                      start_timestamp: datetime, end_timestamp: datetime) -> str:
        """
        Store calculated features to file.
        
        Args:
            symbol: Trading symbol
            features_df: DataFrame with features
            start_timestamp: Start timestamp of the data
            end_timestamp: End timestamp of the data
            
        Returns:
            Path to the stored file
        """
        if features_df.empty:
            raise ValueError("Cannot store empty DataFrame")
        
        # Create filename with timestamps
        filename = f"{symbol}_{start_timestamp.strftime('%Y%m%d_%H%M%S')}_{end_timestamp.strftime('%Y%m%d_%H%M%S')}_features.joblib"
        file_path = os.path.join(self.cache_dir, filename)
        
        # Store the features
        joblib.dump(features_df, file_path)
        
        # Create and store metadata with only the filename (relative path)
        metadata = FeatureFileMetadata(
            symbol=symbol,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            file_path=filename,  # Store only filename, not full path
            feature_count=len(features_df.columns),
            created_at=datetime.now()
        )
        self.metadata.add_file_metadata(symbol, metadata)   
        
        return file_path
    
    def store_features(self, symbol: Symbol, features_df: pd.DataFrame, 
                      start_timestamp: datetime, end_timestamp: datetime) -> str:
        """
        Alias for store_features_in_metadata to maintain backward compatibility.
        
        Args:
            symbol: Trading symbol
            features_df: DataFrame with features
            start_timestamp: Start timestamp of the data
            end_timestamp: End timestamp of the data
            
        Returns:
            Path to the stored file
        """
        return self.store_features_in_metadata(symbol, features_df, start_timestamp, end_timestamp)
    
    def _add_to_memory_cache(self, symbol: Symbol, features_df: pd.DataFrame):
        """Add features to in-memory cache."""
        if symbol not in self._in_memory_features:
            self._in_memory_features[symbol] = {}
        
        for timestamp in features_df.index:
            if timestamp in self._in_memory_features[symbol]:
                # Update existing features with new ones (new features take precedence)
                existing_features = self._in_memory_features[symbol][timestamp]
                new_features = features_df.loc[timestamp].to_dict()
                existing_features.update(new_features)
                self._in_memory_features[symbol][timestamp] = existing_features
            else:
                # Add new features for this timestamp
                self._in_memory_features[symbol][timestamp] = features_df.loc[timestamp].to_dict()
    
    def get_features(self, symbol: Symbol, start_timestamp: datetime, 
                             end_timestamp: datetime) -> Optional[pd.DataFrame]:
        """
        Get features within a timestamp range.
        
        Args:
            symbol: Trading symbol
            start_timestamp: Start timestamp
            end_timestamp: End timestamp
            
        Returns:
            DataFrame with features or None if not found
        """
        # First check in-memory cache
        memory_data = self._get_from_memory_cache(symbol, start_timestamp, end_timestamp)
        
        # Then check file cache
        file_data = self._get_from_file_cache(symbol, start_timestamp, end_timestamp)
        
        # Combine data if both sources have data
        if memory_data is not None and file_data is not None:
            combined = pd.concat([memory_data, file_data])
            return combined[~combined.index.duplicated(keep='first')]
        elif memory_data is not None:
            return memory_data
        elif file_data is not None:
            return file_data
        
        return None
    
    def get_features_at_timestamp(self, symbol: Symbol, timestamp: datetime) -> Optional[pd.DataFrame]:
        """
        Get features for a single timestamp.
        
        Args:
            symbol: Trading symbol
            timestamp: Specific timestamp
            
        Returns:
            DataFrame with features for the timestamp or None if not found
        """
        # Call the range-based get_features with the same timestamp for start and end
        return self.get_features(symbol, timestamp, timestamp)
    
    def _get_from_memory_cache(self, symbol: Symbol, start_timestamp: datetime, 
                              end_timestamp: datetime) -> Optional[pd.DataFrame]:
        """Get features from in-memory cache."""
        if symbol not in self._in_memory_features:
            return None
        
        data_points = []
        timestamps = []
        
        for ts, features in self._in_memory_features[symbol].items():
            if start_timestamp <= ts <= end_timestamp:
                data_points.append(features)
                timestamps.append(ts)
        
        if not data_points:
            return None
        
        return pd.DataFrame(data_points, index=timestamps)
    
    def _get_from_file_cache(self, symbol: str, start_timestamp: datetime, 
                            end_timestamp: datetime) -> Optional[pd.DataFrame]:
        """Get features from file cache."""
        file_metadata_list = self.metadata.get_file_metadata(symbol)
        
        if not file_metadata_list:
            return None
        
        combined_data = []
        
        for metadata in file_metadata_list:
            # Check if file overlaps with requested range
            if (metadata.start_timestamp <= end_timestamp and 
                metadata.end_timestamp >= start_timestamp):
                
                # Construct full file path from filename stored in metadata
                full_file_path = os.path.join(self.cache_dir, metadata.file_path)
                
                try:
                    cached_data = joblib.load(full_file_path)
                    
                    # Filter for requested range
                    mask = (cached_data.index >= start_timestamp) & (cached_data.index <= end_timestamp)
                    filtered_data = cached_data[mask]
                    
                    if not filtered_data.empty:
                        combined_data.append(filtered_data)
                        
                except Exception as e:
                    print(f"Error loading cache file {full_file_path}: {e}")
                    continue
        
        if not combined_data:
            return None
        
        # Combine and sort data
        result = pd.concat(combined_data)
        result = result.sort_index()
        result = result[~result.index.duplicated(keep='first')]
        
        return result
    
    def clear_memory_cache(self, symbol: str, start_timestamp: Optional[datetime] = None, 
                          end_timestamp: Optional[datetime] = None):
        """
        Clear in-memory cache for a given range.
        
        Args:
            symbol: Trading symbol
            start_timestamp: Start timestamp (if None, clear all for symbol)
            end_timestamp: End timestamp (if None, clear all for symbol)
        """
        if symbol not in self._in_memory_features:
            return
        
        if start_timestamp is None and end_timestamp is None:
            # Clear all data for symbol
            del self._in_memory_features[symbol]
        else:
            # Clear specific range
            timestamps_to_remove = []
            for ts in self._in_memory_features[symbol].keys():
                if start_timestamp is None or ts >= start_timestamp:
                    if end_timestamp is None or ts <= end_timestamp:
                        timestamps_to_remove.append(ts)
            
            for ts in timestamps_to_remove:
                del self._in_memory_features[symbol][ts]
    
    def clear_file_cache(self, symbol: str):
        """Clear all file cache for a symbol."""
        file_metadata_list = self.metadata.get_file_metadata(symbol)
        
        for metadata in file_metadata_list:
            try:
                # Construct full file path from filename stored in metadata
                full_file_path = os.path.join(self.cache_dir, metadata.file_path)
                if os.path.exists(full_file_path):
                    os.remove(full_file_path)
            except Exception as e:
                print(f"Error removing cache file {full_file_path}: {e}")
        
        self.metadata.clear_symbol_metadata(symbol)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        memory_stats = {
            'symbols_in_memory': len(self._in_memory_features),
            'total_timestamps_in_memory': sum(len(data) for data in self._in_memory_features.values())
        }
        
        file_stats = {}
        for symbol in self.metadata._metadata.keys():
            file_metadata_list = self.metadata.get_file_metadata(symbol)
            file_stats[symbol] = {
                'file_count': len(file_metadata_list),
                'total_features': sum(meta.feature_count for meta in file_metadata_list)
            }
        
        return {
            'memory_cache': memory_stats,
            'file_cache': file_stats
        }
    
    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance. Only allowed in test environments."""
        # Check if called from a test context
        stack = inspect.stack()
        for frame in stack:
            # Check for pytest or unittest in the call stack
            if (
                'pytest' in frame.filename or
                'unittest' in frame.filename or
                'test' in frame.filename.lower()
            ):
                cls._instance = None
                cls._initialized = False
                return
        raise RuntimeError("reset_instance() can only be called from a test context (pytest/unittest). Do not use in production code.")
    
    def load_in_memory_Features_from_metadata(self):
        """
        Load features from metadata into in-memory cache during initialization.
        
        This method loads all available feature files from the metadata into the
        in-memory cache to improve performance for subsequent feature requests.
        """
        print("Loading features from metadata into memory cache...")
        
        # Get all symbols from metadata
        all_symbols = list(self.metadata._metadata.keys())
        
        if not all_symbols:
            print("No metadata found. Memory cache will remain empty.")
            return
        
        loaded_count = 0
        error_count = 0
        
        for symbol in all_symbols:
            file_metadata_list = self.metadata.get_file_metadata(symbol)
            
            for metadata in file_metadata_list:
                try:
                    # Construct full file path from filename stored in metadata
                    full_file_path = os.path.join(self.cache_dir, metadata.file_path)
                    
                    # Check if file exists
                    if not os.path.exists(full_file_path):
                        print(f"Warning: Cache file not found for {symbol}: {metadata.file_path}")
                        continue
                    
                    # Load features from file
                    cached_data = joblib.load(full_file_path)
                    
                    if cached_data is not None and not cached_data.empty:
                        # Add to in-memory cache
                        self._add_to_memory_cache(symbol, cached_data)
                        loaded_count += 1
                        print(f"Loaded {len(cached_data)} timestamps for {symbol} from {metadata.file_path}")
                    else:
                        print(f"Warning: Empty or invalid data for {symbol}: {metadata.file_path}")
                        
                except Exception as e:
                    error_count += 1
                    print(f"Error loading features for {symbol} from {metadata.file_path}: {e}")
                    continue
        
        print(f"Memory cache loading completed: {loaded_count} files loaded, {error_count} errors")
        
        # Print memory cache statistics
        total_symbols = len(self._in_memory_features)
        total_timestamps = sum(len(data) for data in self._in_memory_features.values())
        print(f"Memory cache stats: {total_symbols} symbols, {total_timestamps} total timestamps")
    
   