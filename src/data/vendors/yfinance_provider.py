from typing import Dict, List, Union, Optional
import pandas as pd
import yfinance as yf
from ..base import DataProvider, DataCache
import logging

logger = logging.getLogger(__name__)

class YahooFinanceProvider(DataProvider):
    """Yahoo Finance data provider implementation."""
    
    def __init__(self, cache: Optional[DataCache] = None):
        """Initialize the Yahoo Finance provider."""
        super().__init__(cache=cache)
    
    def get_historical_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = '1d'
    ) -> pd.DataFrame:
        """Fetch historical data from Yahoo Finance."""
        logger.info(f"Fetching historical data for {symbol} from {start_date} to {end_date}")
        
        # Try to get from cache first
        if self.cache:
            cached_data = self.cache.get_cached_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date
            )
            if cached_data is not None:
                logger.info("Retrieved data from cache")
                return self._process_historical_data(cached_data)
        
        # Fetch from API if not in cache
        logger.info("Fetching data from Yahoo Finance API")
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date, interval=interval)
        logger.info(f"Raw data shape: {df.shape}")
        logger.info(f"Raw data columns: {df.columns.tolist()}")
        logger.info(f"Raw data sample:\n{df.head()}")
        
        # Cache the data
        if self.cache:
            self.cache.cache_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                data=df
            )
        
        processed_df = self._process_historical_data(df)
        logger.info(f"Processed data shape: {processed_df.shape}")
        logger.info(f"Processed data columns: {processed_df.columns.tolist()}")
        logger.info(f"Processed data sample:\n{processed_df.head()}")
        return processed_df
    
    def get_realtime_data(
        self,
        symbol: str,
        interval: str = '1m'
    ) -> pd.DataFrame:
        """Fetch real-time data from Yahoo Finance."""
        ticker = yf.Ticker(symbol)
        df = ticker.history(period='1d', interval=interval)
        return self._process_historical_data(df)
    
    def get_market_data(
        self,
        symbols: List[str],
        data_types: List[str]
    ) -> Dict[str, pd.DataFrame]:
        """Fetch market data for multiple symbols."""
        result = {}
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            data = {}
            for data_type in data_types:
                if data_type == 'info':
                    data[data_type] = ticker.info
                elif data_type == 'history':
                    data[data_type] = self._process_historical_data(
                        ticker.history(period='1d')
                    )
            result[symbol] = data
        return result
    
    def get_company_info(
        self,
        symbol: str
    ) -> Dict[str, Union[str, float, int]]:
        """Fetch company information from Yahoo Finance."""
        ticker = yf.Ticker(symbol)
        return ticker.info
    
    def _process_historical_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process historical data to ensure consistent format."""
        if df.empty:
            logger.warning("Received empty DataFrame")
            return df
        
        # Ensure index is datetime
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # Always convert to UTC
        df.index = df.index.tz_convert('UTC') if df.index.tz else df.index.tz_localize('UTC')
        
        # Rename columns to lowercase
        df.columns = [col.lower() for col in df.columns]
        
        # Ensure required columns exist
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Fill any missing values with forward fill, then backward fill
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        return df 