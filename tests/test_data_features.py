import unittest
from datetime import datetime, timedelta
import pandas as pd
from src.data.providers.vendors.polygon.polygon_provider import PolygonProvider
from src.features import TechnicalIndicators
from src.data.types.base_types import TimeSeriesData

class TestDataAndFeatures(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.data_provider = PolygonProvider()
        self.feature_engineer = TechnicalIndicators()
        
        # Set up test dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        self.start_date = start_date
        self.end_date = end_date
        
        # Test symbol
        self.symbol = 'AAPL'
    
    def test_data_provider(self):
        """Test data provider functionality."""
        # Test historical data
        data = self.data_provider.get_data(
            symbol=self.symbol,
            start_time=self.start_date,
            end_time=self.end_date
        )
        
        self.assertIsInstance(data, TimeSeriesData)
        self.assertTrue(len(data.timestamps) > 0)
        self.assertTrue(len(data.data) > 0)
        
        # Convert to DataFrame for column checks
        df = pd.DataFrame(data.data, index=data.timestamps)
        self.assertTrue(all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume']))
    
    def test_feature_engineering(self):
        """Test feature engineering functionality."""
        # Get historical data
        data = self.data_provider.get_data(
            symbol=self.symbol,
            start_time=self.start_date,
            end_time=self.end_date
        )
        # Convert to DataFrame for feature calculation
        if hasattr(data, 'to_dataframe'):
            df = data.to_dataframe()
        else:
            df = pd.DataFrame(data.data, index=data.timestamps)
        # Test feature calculation
        features = [
            self.feature_engineer.FeatureNames.SMA_20,
            self.feature_engineer.FeatureNames.RSI_14,
            self.feature_engineer.FeatureNames.MACD
        ]
        df_with_features = self.feature_engineer.calculate_features(df, features)
        self.assertIsInstance(df_with_features, pd.DataFrame)
        self.assertFalse(df_with_features.empty)
        self.assertTrue(all(feature in df_with_features.columns for feature in features))
        
        # Test available features
        available_features = self.feature_engineer.get_available_features()
        self.assertIsInstance(available_features, list)
        self.assertTrue(all(feature in available_features for feature in features))
        
        # Test feature dependencies
        dependencies = self.feature_engineer.get_feature_dependencies(self.feature_engineer.FeatureNames.SMA_20)
        self.assertIsInstance(dependencies, list)
        self.assertTrue('close' in dependencies)
    
    def test_data_consistency(self):
        """Test data consistency across operations."""
        data = self.data_provider.get_data(
            symbol=self.symbol,
            start_time=self.start_date,
            end_time=self.end_date
        )
        if hasattr(data, 'to_dataframe'):
            df = data.to_dataframe()
        else:
            df = pd.DataFrame(data.data, index=data.timestamps)
        df_with_features = self.feature_engineer.calculate_features(df)
        self.assertIsInstance(df_with_features, pd.DataFrame)
        self.assertEqual(len(df_with_features), len(df))
        
        # Verify data consistency
        self.assertTrue(df.index.equals(df_with_features.index))
        self.assertTrue(all(col in df_with_features.columns for col in df.columns))
        
        # Verify no NaN values in original data
        self.assertFalse(df.isnull().any().any())
        
        # Verify feature calculations
        self.assertTrue(df_with_features[self.feature_engineer.FeatureNames.SMA_20].notna().any())
        self.assertTrue(df_with_features[self.feature_engineer.FeatureNames.RSI_14].notna().any())
        self.assertTrue(df_with_features[self.feature_engineer.FeatureNames.MACD].notna().any())

if __name__ == '__main__':
    unittest.main() 