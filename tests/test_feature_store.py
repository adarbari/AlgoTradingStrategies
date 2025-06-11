import unittest
import pandas as pd
import numpy as np
import os
import shutil
from datetime import datetime, timedelta
from src.features.feature_store import FeatureStore

class TestFeatureStore(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.test_cache_dir = 'test_feature_cache'
        self.feature_store = FeatureStore(cache_dir=self.test_cache_dir)
        
        # Create sample feature data
        self.sample_features = pd.DataFrame({
            'RSI': np.random.rand(100),
            'MACD': np.random.rand(100),
            'SMA_20': np.random.rand(100)
        }, index=pd.date_range(start='2024-01-01', periods=100, freq='D'))
        
        # Create sample feature data with gaps
        self.sample_features_with_gaps = pd.DataFrame({
            'RSI': np.random.rand(60),
            'MACD': np.random.rand(60),
            'SMA_20': np.random.rand(60)
        }, index=pd.date_range(start='2024-01-01', periods=60, freq='D'))
        
    def tearDown(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)
    
    def test_cache_and_retrieve_full_range(self):
        """Test caching and retrieving features for a full date range."""
        # Cache the features
        start_date = self.sample_features.index.min().strftime('%Y-%m-%d')
        end_date = self.sample_features.index.max().strftime('%Y-%m-%d')
        self.feature_store.cache_features(
            symbol='AAPL',
            start_date=start_date,
            end_date=end_date,
            features_df=self.sample_features
        )
        
        # Retrieve the features
        retrieved_features = self.feature_store.get_cached_features(
            symbol='AAPL',
            start_date=start_date,
            end_date=end_date
        )
        
        self.assertIsNotNone(retrieved_features)
        self.assertTrue(retrieved_features.equals(self.sample_features))
    
    def test_cache_and_retrieve_partial_range(self):
        """Test retrieving features for a partial date range."""
        # Cache the features
        self.feature_store.cache_features(
            symbol='AAPL',
            start_date='2024-01-01',
            end_date='2024-04-10',
            features_df=self.sample_features
        )
        
        # Retrieve a partial range
        retrieved_features = self.feature_store.get_cached_features(
            symbol='AAPL',
            start_date='2024-02-01',
            end_date='2024-02-28'
        )
        
        self.assertIsNotNone(retrieved_features)
        expected_features = self.sample_features['2024-02-01':'2024-02-28']
        self.assertTrue(retrieved_features.equals(expected_features))
    
    def test_multiple_cache_files(self):
        """Test handling multiple cache files for the same symbol."""
        # Create two separate cache files with continuous data
        first_half = self.sample_features[:50]
        second_half = self.sample_features[49:]  # Overlap by one day to ensure continuity
        
        self.feature_store.cache_features(
            symbol='AAPL',
            start_date='2024-01-01',
            end_date='2024-02-19',
            features_df=first_half
        )
        
        self.feature_store.cache_features(
            symbol='AAPL',
            start_date='2024-02-19',  # Start from the same day as first file ends
            end_date='2024-04-10',
            features_df=second_half
        )
        
        # Retrieve data spanning both cache files
        retrieved_features = self.feature_store.get_cached_features(
            symbol='AAPL',
            start_date='2024-02-15',
            end_date='2024-02-25'
        )
        
        self.assertIsNotNone(retrieved_features)
        expected_features = self.sample_features['2024-02-15':'2024-02-25']
        self.assertTrue(retrieved_features.equals(expected_features))
    
    def test_missing_date_ranges(self):
        """Test handling of missing date ranges."""
        # Cache data with gaps
        self.feature_store.cache_features(
            symbol='AAPL',
            start_date='2024-01-01',
            end_date='2024-02-29',
            features_df=self.sample_features_with_gaps
        )
        
        # Try to retrieve data including a gap
        retrieved_features = self.feature_store.get_cached_features(
            symbol='AAPL',
            start_date='2024-01-01',
            end_date='2024-04-10'
        )
        
        # Should return None because of missing data
        self.assertIsNone(retrieved_features)
    
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
            features=['RSI', 'MACD']
        )
        
        self.assertIsNotNone(retrieved_features)
        self.assertEqual(set(retrieved_features.columns), {'RSI', 'MACD'})
        self.assertTrue(retrieved_features.equals(self.sample_features[['RSI', 'MACD']]))
    
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
        msft_files = self.feature_store._get_cache_files('MSFT')
        self.assertEqual(len(msft_files), 0)
    
    def test_overlapping_cache_files(self):
        """Test handling of overlapping cache files."""
        # Create overlapping cache files
        first_file = self.sample_features[:60]
        second_file = self.sample_features[40:]
        
        self.feature_store.cache_features(
            symbol='AAPL',
            start_date='2024-01-01',
            end_date='2024-02-29',
            features_df=first_file
        )
        
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
        self.assertTrue(retrieved_features.equals(expected_features))
    
    def test_invalid_date_format(self):
        """Test handling of invalid date formats."""
        with self.assertRaises(ValueError):
            self.feature_store.get_cached_features(
                symbol='AAPL',
                start_date='invalid-date',
                end_date='2024-04-10'
            )
    
    def test_nonexistent_symbol(self):
        """Test retrieving features for a nonexistent symbol."""
        retrieved_features = self.feature_store.get_cached_features(
            symbol='NONEXISTENT',
            start_date='2024-01-01',
            end_date='2024-04-10'
        )
        
        self.assertIsNone(retrieved_features)

if __name__ == '__main__':
    unittest.main() 