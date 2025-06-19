import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pandas as pd

from src.features.core.feature_store import FeatureStore
from src.data.types.symbol import Symbol
from src.features.types.feature_definitions import FeatureNames, FeatureType, FeatureCalculationEngineType

class TestFeatureStoreIntegration(unittest.TestCase):
    def setUp(self):
        self.symbol = Symbol('AAPL')
        self.start_time = datetime(2023, 1, 1, 9, 30)
        self.end_time = datetime(2023, 1, 1, 16, 0)
        
        # Reset the singleton instance to ensure clean state
        FeatureStore.reset_instance()
        self.feature_store = FeatureStore.get_instance()
        
        self.mock_ohlcv_df = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [105, 106, 107],
            'low': [99, 100, 101],
            'close': [104, 105, 106],
            'volume': [1000, 1100, 1200]
        }, index=[
            self.start_time,
            self.start_time + timedelta(minutes=1),
            self.start_time + timedelta(minutes=2)
        ])

    @patch('src.data.data_manager.DataManager.get_ohlcv_data')
    def test_generate_and_retrieve_features(self, mock_get_ohlcv_data):
        # Mock the DataManager to return our fake OHLCV data
        mock_data = MagicMock()
        mock_data.to_dataframe.return_value = self.mock_ohlcv_df
        mock_data.__len__.return_value = len(self.mock_ohlcv_df)
        mock_get_ohlcv_data.return_value = mock_data

        # Generate all features for the symbol and time range
        features_df = self.feature_store.generate_features(self.symbol, self.start_time, self.end_time)
        self.assertIsInstance(features_df, pd.DataFrame)
        self.assertFalse(features_df.empty)
        
        # Check that base features are present
        for col in ['open', 'high', 'low', 'close', 'volume']:
            self.assertIn(col, features_df.columns)
        
        # Retrieve features from the store
        retrieved_df = self.feature_store.get_features(self.symbol, self.start_time, self.end_time)
        self.assertIsInstance(retrieved_df, pd.DataFrame)
        self.assertFalse(retrieved_df.empty)
        pd.testing.assert_frame_equal(features_df, retrieved_df)

    def test_all_feature_names_available(self):
        """Test that all defined feature names are available in the feature store."""
        available_features = self.feature_store.get_available_features()
        
        # Check all base features are available
        base_features = [
            FeatureNames.OPEN,
            FeatureNames.HIGH,
            FeatureNames.LOW,
            FeatureNames.CLOSE,
            FeatureNames.VOLUME
        ]
        for feature in base_features:
            self.assertIn(feature, available_features)
        
        # Check all derived features are available
        derived_features = [
            # Moving Averages
            FeatureNames.SMA_20,
            FeatureNames.SMA_50,
            FeatureNames.SMA_200,
            FeatureNames.EMA_20,
            FeatureNames.EMA_50,
            FeatureNames.EMA_200,
            
            # Momentum
            FeatureNames.RSI_14,
            FeatureNames.RSI_21,
            FeatureNames.RSI,
            FeatureNames.MACD,
            FeatureNames.MACD_SIGNAL,
            FeatureNames.MACD_HIST,
            FeatureNames.MACD_HISTOGRAM,
            FeatureNames.STOCH_K,
            FeatureNames.STOCH_D,
            
            # Volatility
            FeatureNames.ATR_14,
            FeatureNames.ATR,
            FeatureNames.BOLLINGER_UPPER,
            FeatureNames.BOLLINGER_LOWER,
            FeatureNames.BOLLINGER_MIDDLE,
            FeatureNames.BB_UPPER,
            FeatureNames.BB_MIDDLE,
            FeatureNames.BB_LOWER,
            
            # Volume
            FeatureNames.VOLUME_SMA,
            FeatureNames.VOLUME_EMA,
            FeatureNames.VOLUME_MA_5,
            FeatureNames.VOLUME_MA_15,
            
            # Price Action
            FeatureNames.PRICE_CHANGE,
            FeatureNames.VOLUME_CHANGE,
            FeatureNames.VOLATILITY,
            FeatureNames.PRICE_CHANGE_5MIN,
            FeatureNames.PRICE_CHANGE_15MIN,
            FeatureNames.PRICE_RANGE,
            FeatureNames.PRICE_RANGE_MA,
            FeatureNames.VOLATILITY_5MIN,
            FeatureNames.VOLATILITY_15MIN,
            
            # Moving Average Crossover specific
            FeatureNames.MA_SHORT,
            FeatureNames.MA_LONG,
            
            # Additional Indicators
            FeatureNames.TARGET
        ]
        for feature in derived_features:
            self.assertIn(feature, available_features)
        
        # Verify total count matches expected
        expected_total = len(base_features) + len(derived_features)
        self.assertEqual(len(available_features), expected_total)

    def test_feature_categories(self):
        """Test that features are properly categorized."""
        categories = self.feature_store.get_features_by_category()
        
        # Check that expected categories exist
        expected_categories = ['price', 'volume', 'moving_average', 'momentum', 'volatility', 'price_action', 'target']
        for category in expected_categories:
            self.assertIn(category, categories)
            self.assertIsInstance(categories[category], list)
            self.assertGreater(len(categories[category]), 0)

    def test_feature_types(self):
        """Test that features are properly classified by type."""
        base_features = self.feature_store.get_base_features()
        derived_features = self.feature_store.get_derived_features()
        
        # Check base features
        expected_base = ['open', 'high', 'low', 'close', 'volume']
        for feature in expected_base:
            self.assertIn(feature, base_features)
        
        # Check derived features count (should be 44 total features - 5 base = 39 derived)
        expected_derived_count = 39  # All technical indicators and derived features
        self.assertEqual(len(derived_features), expected_derived_count)
        
        # Verify no overlap between base and derived
        overlap = set(base_features) & set(derived_features)
        self.assertEqual(len(overlap), 0)

    def test_feature_metadata(self):
        """Test that feature metadata is accessible."""
        # Test feature descriptions
        self.assertIsNotNone(self.feature_store.get_feature_description(FeatureNames.CLOSE))
        self.assertIsNotNone(self.feature_store.get_feature_description(FeatureNames.RSI_14))
        
        # Test feature categories
        self.assertEqual(self.feature_store.get_feature_category(FeatureNames.CLOSE), 'price')
        self.assertEqual(self.feature_store.get_feature_category(FeatureNames.RSI_14), 'momentum')
        
        # Test feature types
        self.assertEqual(self.feature_store.get_feature_type(FeatureNames.CLOSE), FeatureType.BASE)
        self.assertEqual(self.feature_store.get_feature_type(FeatureNames.RSI_14), FeatureType.DERIVED)
        
        # Test engine types
        self.assertIsNone(self.feature_store.get_feature_engine_type(FeatureNames.CLOSE))  # Base features don't have engine type
        self.assertEqual(self.feature_store.get_feature_engine_type(FeatureNames.RSI_14), FeatureCalculationEngineType.OHLCV_DERIVED)

if __name__ == '__main__':
    unittest.main() 