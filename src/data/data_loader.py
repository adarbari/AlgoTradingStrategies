from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional

class DataLoader:
    """Class responsible for loading and managing market data."""
    
    def __init__(self, data_dir: str = 'data'):
        """Initialize the data loader.
        
        Args:
            data_dir: Directory containing market data files
        """
        self.data_dir = data_dir
        self.data: Dict[str, pd.DataFrame] = {}
        
    def load_data(self, symbols: List[str], start_date: datetime, end_date: datetime) -> Dict[str, pd.DataFrame]:
        """Load market data for given symbols and date range.
        
        Args:
            symbols: List of stock symbols
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary mapping symbols to their price data
        """
        for symbol in symbols:
            file_path = f"{self.data_dir}/{symbol}.csv"
            try:
                df = pd.read_csv(file_path)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                df = df.loc[start_date:end_date]
                self.data[symbol] = df
            except Exception as e:
                print(f"Error loading data for {symbol}: {e}")
                
        return self.data
        
    def get_latest_data(self, symbol: str, lookback: int = 100) -> pd.DataFrame:
        """Get latest data for a symbol.
        
        Args:
            symbol: Stock symbol
            lookback: Number of periods to look back
            
        Returns:
            DataFrame with latest data
        """
        if symbol not in self.data:
            raise ValueError(f"No data loaded for {symbol}")
            
        return self.data[symbol].iloc[-lookback:] 