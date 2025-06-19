"""
Tests for the FeatureStore class.
"""

import unittest
import pandas as pd
import numpy as np
import os
import shutil
from datetime import datetime, timedelta
from src.features.core.feature_store import FeatureStore
from src.features.implementations.technical_indicators import TechnicalIndicators

class TestFeatureStore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test class fixtures."""
        # Reset the FeatureStore singleton before all tests
        FeatureStore.reset_instance()
    
    def setUp(self):
        """Set up test fixtures."""
        # Clean up any existing cache directory
        self.cache_dir = 'test_cache'
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
        
        # Reset the FeatureStore singleton and set cache directory
        FeatureStore.reset_instance()
        FeatureStore._cache_dir = self.cache_dir
        self.feature_store = FeatureStore.get_instance()
        self.technical_indicators = TechnicalIndicators()
        
        # Create sample features DataFrame with at least 100 days
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        self.sample_features = pd.DataFrame({
            'price': np.random.normal(150, 5, len(dates)),
            self.technical_indicators.FeatureNames.MA_SHORT: np.random.normal(150, 2, len(dates)),
            self.technical_indicators.FeatureNames.MA_LONG: np.random.normal(148, 2, len(dates)),
            self.technical_indicators.FeatureNames.RSI_14: np.random.uniform(30, 70, len(dates)),
            self.technical_indicators.FeatureNames.MACD: np.random.normal(0, 1, len(dates)),
            self.technical_indicators.FeatureNames.MACD_SIGNAL: np.random.normal(0, 1, len(dates))
        }, index=dates)
        
        # Create sample feature data with gaps
        self.sample_features_with_gaps = pd.DataFrame({
            'RSI': np.random.rand(60),
            'MACD': np.random.rand(60),
            'SMA_20': np.random.rand(60)
        }, index=pd.date_range(start='2024-01-01', periods=60, freq='D'))
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
    
    def test_cache_features(self):
        """Test caching features."""
        # Cache the features
        start_date = self.sample_features.index.min().strftime('%Y-%m-%d')
        end_date = self.sample_features.index.max().strftime('%Y-%m-%d')
        self.feature_store.cache_features(
            symbol='AAPL',
            start_date=start_date,
            end_date=end_date,
            features_df=self.sample_features
        )
        
        # Verify cache file exists
        cache_files = self.feature_store._get_cache_files('AAPL')
        self.assertEqual(len(cache_files), 1)
        
        # Verify cache file content
        cached_features = self.feature_store.get_cached_features(
            symbol='AAPL',
            start_date=start_date,
            end_date=end_date
        )
        self.assertIsNotNone(cached_features)
        pd.testing.assert_frame_equal(cached_features, self.sample_features)
    
    def test_get_cached_features(self):
        """Test retrieving cached features."""
        # Cache the features
        start_date = self.sample_features.index.min().strftime('%Y-%m-%d')
        end_date = self.sample_features.index.max().strftime('%Y-%m-%d')
        self.feature_store.cache_features(
            symbol='AAPL',
            start_date=start_date,
            end_date=end_date,
            features_df=self.sample_features
        )
        
        # Test retrieving features
        cached_features = self.feature_store.get_cached_features(
            symbol='AAPL',
            start_date=start_date,
            end_date=end_date
        )
        self.assertIsNotNone(cached_features)
        pd.testing.assert_frame_equal(cached_features, self.sample_features)
        
        # Test retrieving non-existent features
        non_existent = self.feature_store.get_cached_features(
            symbol='MSFT',
            start_date=start_date,
            end_date=end_date
        )
        self.assertIsNone(non_existent)
    
    def test_get_missing_ranges(self):
        """Test finding missing date ranges in cache."""
        # Cache some features
        start_date = '2024-01-01'
        end_date = '2024-01-10'
        self.feature_store.cache_features(
            symbol='AAPL',
            start_date=start_date,
            end_date=end_date,
            features_df=self.sample_features
        )
        
        # Test finding missing ranges
        missing_ranges = self.feature_store._get_missing_ranges(
            symbol='AAPL',
            start_date='2024-01-05',
            end_date='2024-01-15'
        )
        self.assertEqual(len(missing_ranges), 1)
        self.assertEqual(missing_ranges[0], ('2024-01-10', '2024-01-15'))
    
    def test_specific_features_retrieval(self):
        """Test retrieving specific features only."""
        # Cache the features
        start_date = self.sample_features.index.min().strftime('%Y-%m-%d')
        end_date = self.sample_features.index.max().strftime('%Y-%m-%d')
        self.feature_store.cache_features(
            symbol='AAPL',
            start_date=start_date,
            end_date=end_date,
            features_df=self.sample_features
        )
        
        # Retrieve only RSI and MACD
        retrieved_features = self.feature_store.get_cached_features(
            symbol='AAPL',
            start_date=start_date,
            end_date=end_date,
            features=[
                self.technical_indicators.FeatureNames.RSI_14,
                self.technical_indicators.FeatureNames.MACD
            ]
        )
        
        self.assertIsNotNone(retrieved_features)
        self.assertEqual(set(retrieved_features.columns), {
            self.technical_indicators.FeatureNames.RSI_14,
            self.technical_indicators.FeatureNames.MACD
        })
        pd.testing.assert_frame_equal(
            retrieved_features,
            self.sample_features[[
                self.technical_indicators.FeatureNames.RSI_14,
                self.technical_indicators.FeatureNames.MACD
            ]]
        )
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty DataFrames."""
        empty_df = pd.DataFrame()
        
        # Should not create a cache file for empty DataFrame
        self.feature_store.cache_features(
            symbol='AAPL',
            start_date='2024-01-01',
            end_date='2024-04-10',
            features_df=empty_df
        )
        
        # Verify no cache file was created
        cache_files = self.feature_store._get_cache_files('AAPL')
        self.assertEqual(len(cache_files), 0)
    
    def test_clear_cache(self):
        """Test clearing the cache."""
        # Cache features for multiple symbols
        self.feature_store.cache_features(
            symbol='AAPL',
            start_date='2024-01-01',
            end_date='2024-04-10',
            features_df=self.sample_features
        )
        
        self.feature_store.cache_features(
            symbol='MSFT',
            start_date='2024-01-01',
            end_date='2024-04-10',
            features_df=self.sample_features
        )
        
        # Clear cache for AAPL only
        self.feature_store.clear_cache(symbol='AAPL')
        
        # Verify AAPL cache is cleared but MSFT remains
        aapl_files = self.feature_store._get_cache_files('AAPL')
        msft_files = self.feature_store._get_cache_files('MSFT')
        
        self.assertEqual(len(aapl_files), 0)
        self.assertEqual(len(msft_files), 1)
        
        # Clear all cache
        self.feature_store.clear_cache()
        
        # Verify all cache is cleared
        aapl_files = self.feature_store._get_cache_files('AAPL')
        msft_files = self.feature_store._get_cache_files('MSFT')
        
        self.assertEqual(len(aapl_files), 0)
        self.assertEqual(len(msft_files), 0)
    
    def test_overlapping_cache_files(self):
        """Test handling of overlapping cache files."""
        # Create overlapping cache files with consistent date ranges
        first_file = self.sample_features[:60].copy()
        second_file = self.sample_features[40:].copy()
        
        # Ensure both DataFrames have the same frequency
        first_file.index.freq = 'D'
        second_file.index.freq = 'D'
        
        # Cache the first file
        self.feature_store.cache_features(
            symbol='AAPL',
            start_date='2024-01-01',
            end_date='2024-02-29',
            features_df=first_file
        )
        
        # Cache the second file
        self.feature_store.cache_features(
            symbol='AAPL',
            start_date='2024-02-10',
            end_date='2024-04-10',
            features_df=second_file
        )
        
        # Retrieve data from the overlapping period
        retrieved_features = self.feature_store.get_cached_features(
            symbol='AAPL',
            start_date='2024-02-10',
            end_date='2024-02-29'
        )
        
        self.assertIsNotNone(retrieved_features)
        # Should use the first file's data for the overlapping period
        expected_features = first_file['2024-02-10':'2024-02-29']
        
        # Compare the DataFrames
        pd.testing.assert_frame_equal(
            retrieved_features,
            expected_features,
            check_freq=False  # Don't check frequency as it may be lost during caching
        )
    
    def test_invalid_date_format(self):
        """Test handling of invalid date formats."""
        with self.assertRaises(ValueError):
            self.feature_store.get_cached_features(
                symbol='AAPL',
                start_date='invalid-date',
                end_date='2024-01-10'
            )
    
    def test_nonexistent_symbol(self):
        """Test handling of nonexistent symbols."""
        result = self.feature_store.get_cached_features(
            symbol='NONEXISTENT',
            start_date='2024-01-01',
            end_date='2024-01-10'
        )
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main() 