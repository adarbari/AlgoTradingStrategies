import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.data_fetcher import DataFetcher
from data.feature_engineering import FeatureEngineer
import pandas as pd
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_data_fetcher():
    """Test the DataFetcher's smart caching functionality"""
    logger.info("Testing DataFetcher smart caching...")
    
    # Initialize DataFetcher
    data_fetcher = DataFetcher()
    
    # Test case 1: Fetch data for a large date range (last 60 days)
    symbol = "AAPL"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    
    logger.info(f"Test 1: Fetching data for {symbol} from {start_date.date()} to {end_date.date()}")
    data1 = data_fetcher.fetch_data(symbol, start_date, end_date)
    logger.info(f"Data shape: {data1.shape}")
    
    # Test case 2: Fetch subset of cached data
    subset_start = start_date + timedelta(days=15)
    subset_end = end_date - timedelta(days=15)
    
    logger.info(f"Test 2: Fetching subset from {subset_start.date()} to {subset_end.date()}")
    data2 = data_fetcher.fetch_data(symbol, subset_start, subset_end)
    logger.info(f"Subset data shape: {data2.shape}")
    
    # Verify subset is correct
    assert data2.index.min() >= pd.to_datetime(subset_start), "Subset start date incorrect"
    assert data2.index.max() <= pd.to_datetime(subset_end), "Subset end date incorrect"
    
    return data1, data2

def test_feature_engineering(data):
    """Test the FeatureEngineer's smart caching functionality"""
    logger.info("\nTesting FeatureEngineer smart caching...")
    
    # Initialize FeatureEngineer
    feature_engineer = FeatureEngineer()
    
    # Test case 1: Calculate features for full dataset
    symbol = "AAPL"
    start_date = data.index.min()
    end_date = data.index.max()
    
    logger.info(f"Test 1: Calculating features for full dataset")
    features1 = feature_engineer.create_features(data, symbol, "technical", 
                                               start_date=start_date, end_date=end_date)
    logger.info(f"Features shape: {features1.shape}")
    
    # Test case 2: Calculate features for subset
    subset_start = start_date + timedelta(days=15)
    subset_end = end_date - timedelta(days=15)
    
    logger.info(f"Test 2: Calculating features for subset")
    features2 = feature_engineer.create_features(data, symbol, "technical",
                                               start_date=subset_start, end_date=subset_end)
    logger.info(f"Subset features shape: {features2.shape}")
    
    # Verify subset is correct
    assert features2.index.min() >= subset_start, "Feature subset start date incorrect"
    assert features2.index.max() <= subset_end, "Feature subset end date incorrect"
    
    return features1, features2

def main():
    try:
        # Test DataFetcher
        data1, data2 = test_data_fetcher()
        
        # Test FeatureEngineer
        features1, features2 = test_feature_engineering(data1)
        
        logger.info("\nAll tests passed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 