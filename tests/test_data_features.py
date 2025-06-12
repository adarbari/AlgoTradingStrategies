import unittest
from datetime import datetime, timedelta
import pandas as pd
from src.data import YahooFinanceProvider
from src.features import TechnicalIndicators

class TestDataAndFeatures(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.data_provider = YahooFinanceProvider()
        self.feature_engineer = TechnicalIndicators()
        
        # Set up test dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        self.start_date = start_date.strftime('%Y-%m-%d')
        self.end_date = end_date.strftime('%Y-%m-%d')
        
        # Test symbol
        self.symbol = 'AAPL'
    
    def test_data_provider(self):
        """Test data provider functionality."""
        # Test historical data
        df = self.data_provider.get_historical_data(
            self.symbol,
            self.start_date,
            self.end_date
        )
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.assertTrue(isinstance(df.index, pd.DatetimeIndex))
        self.assertTrue(all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume']))
        
        # Test company info
        info = self.data_provider.get_company_info(self.symbol)
        self.assertIsInstance(info, dict)
        self.assertTrue('symbol' in info)
        self.assertTrue('shortName' in info)
    
    def test_feature_engineering(self):
        """Test feature engineering functionality."""
        # Get historical data
        df = self.data_provider.get_historical_data(
            self.symbol,
            self.start_date,
            self.end_date
        )
        
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
        # Get historical data
        df = self.data_provider.get_historical_data(
            self.symbol,
            self.start_date,
            self.end_date
        )
        
        # Calculate features
        df_with_features = self.feature_engineer.calculate_features(df)
        
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