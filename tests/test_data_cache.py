import unittest
import pandas as pd
import numpy as np
import os
import shutil
from datetime import datetime, timedelta
from src.data.base import DataCache
from src.data.vendors.polygon_provider import PolygonProvider
from src.data.vendors.yfinance_provider import YahooFinanceProvider

class TestDataCache(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.test_cache_dir = 'test_data_cache'
        self.cache = DataCache(cache_dir=self.test_cache_dir)
        
        # Create sample data
        self.sample_data = pd.DataFrame({
            'open': np.random.rand(100),
            'high': np.random.rand(100),
            'low': np.random.rand(100),
            'close': np.random.rand(100),
            'volume': np.random.randint(1000, 10000, 100)
        }, index=pd.date_range(start='2024-01-01', periods=100, freq='D'))
        
    def tearDown(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)
    
    def test_cache_and_retrieve_data(self):
        """Test basic caching and retrieval functionality."""
        # Cache the data
        self.cache.cache_data(
            symbol='AAPL',
            start_date='2024-01-01',
            end_date='2024-04-10',
            data=self.sample_data
        )
        
        # Retrieve the data
        retrieved_data = self.cache.get_cached_data(
            symbol='AAPL',
            start_date='2024-01-01',
            end_date='2024-04-10'
        )
        
        self.assertIsNotNone(retrieved_data)
        self.assertTrue(retrieved_data.equals(self.sample_data))
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty DataFrames."""
        empty_df = pd.DataFrame()
        
        # Should not create a cache file for empty DataFrame
        self.cache.cache_data(
            symbol='AAPL',
            start_date='2024-01-01',
            end_date='2024-04-10',
            data=empty_df
        )
        
        # Verify no cache file was created
        cache_path = self.cache._get_cache_path('AAPL', '2024-01-01', '2024-04-10')
        self.assertFalse(os.path.exists(cache_path))
    
    def test_clear_cache(self):
        """Test clearing the cache."""
        # Cache data for multiple symbols
        self.cache.cache_data(
            symbol='AAPL',
            start_date='2024-01-01',
            end_date='2024-04-10',
            data=self.sample_data
        )
        
        self.cache.cache_data(
            symbol='MSFT',
            start_date='2024-01-01',
            end_date='2024-04-10',
            data=self.sample_data
        )
        
        # Clear cache for AAPL only
        self.cache.clear_cache(symbol='AAPL')
        
        # Verify AAPL cache is cleared but MSFT remains
        aapl_path = self.cache._get_cache_path('AAPL', '2024-01-01', '2024-04-10')
        msft_path = self.cache._get_cache_path('MSFT', '2024-01-01', '2024-04-10')
        
        self.assertFalse(os.path.exists(aapl_path))
        self.assertTrue(os.path.exists(msft_path))
        
        # Clear all cache
        self.cache.clear_cache()
        
        # Verify all cache is cleared
        self.assertFalse(os.path.exists(msft_path))

class TestDataProviders(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.test_cache_dir = 'test_data_cache'
        self.cache = DataCache(cache_dir=self.test_cache_dir)
        self.polygon_provider = PolygonProvider(cache=self.cache)
        self.yfinance_provider = YahooFinanceProvider(cache=self.cache)
        
    def tearDown(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)
    
    def test_polygon_provider_caching(self):
        """Test Polygon provider caching functionality."""
        # First request should fetch from API
        data1 = self.polygon_provider.get_historical_data(
            symbol='AAPL',
            start_date='2024-01-01',
            end_date='2024-01-10'
        )
        
        # Second request should use cache
        data2 = self.polygon_provider.get_historical_data(
            symbol='AAPL',
            start_date='2024-01-01',
            end_date='2024-01-10'
        )
        
        self.assertIsNotNone(data1)
        self.assertIsNotNone(data2)
        self.assertTrue(data1.equals(data2))
    
    def test_yfinance_provider_caching(self):
        """Test Yahoo Finance provider caching functionality."""
        # First request should fetch from API
        data1 = self.yfinance_provider.get_historical_data(
            symbol='AAPL',
            start_date='2024-01-01',
            end_date='2024-01-10'
        )
        
        # Second request should use cache
        data2 = self.yfinance_provider.get_historical_data(
            symbol='AAPL',
            start_date='2024-01-01',
            end_date='2024-01-10'
        )
        
        self.assertIsNotNone(data1)
        self.assertIsNotNone(data2)
        
        # Compare dataframes with tolerance for floating-point differences
        pd.testing.assert_frame_equal(data1, data2, check_exact=False, rtol=1e-5)

if __name__ == '__main__':
    unittest.main() 