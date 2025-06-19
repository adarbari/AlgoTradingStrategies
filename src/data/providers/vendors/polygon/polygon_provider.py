from datetime import datetime, timedelta
import os
from typing import Optional, List
import pandas as pd
from polygon import RESTClient
from src.data.types.base_types import TimeSeriesData
from src.data.types.data_config_types import OHLCVConfig
from src.data.providers.ohlcv_provider import OHLCVDataProvider
from src.data.types.data_type import DataType
from src.data.types.ohlcv_types import OHLCVData

class PolygonProvider(OHLCVDataProvider):
    """
    Polygon.io implementation of OHLCVDataProvider.
    Provides historical and real-time OHLCV data for stocks and crypto.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Polygon provider.
        
        Args:
            api_key: Polygon.io API key
            cache: Optional cache instance
        """
        super().__init__()
        
        # Try to get API key from environment variable first
        api_key = api_key or os.getenv('POLYGON_API_KEY')

        # Fall back to hardcoded key if not set
        if not api_key:
            api_key = "rD9rEIzrzJOcVlPq1ttiAyRLyZyquFiF"

        self.api_key = api_key
        self.client = RESTClient(api_key)
        
    def get_data(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        config: Optional[OHLCVConfig] = None
    ) -> TimeSeriesData:
        """
        Fetch OHLCV data from Polygon.io with pagination support.
        
        Args:
            symbol: The trading symbol
            start_time: Start time for data
            end_time: End time for data
            config: Optional configuration for the OHLCV data request
            
        Returns:
            TimeSeriesData containing OHLCV data
        """
        if config is None:
            config = OHLCVConfig()
            
        # Convert timeframe to Polygon's multiplier and timespan format
        multiplier, timespan = self._parse_timeframe(config.timeframe)
        
        if start_time is None or end_time is None:
            # Live data request
            # Note: Polygon's real-time data requires a subscription
            raise NotImplementedError("Real-time data requires a Polygon.io subscription")
        else:
            # Historical data request with pagination support
            all_aggs = []
            current_from = start_time
            limit = 50000  # Polygon's maximum results per request
            
            while current_from < end_time:
                # Make API call for current batch
                aggs_response = self.client.get_aggs(
                    ticker=symbol,
                    multiplier=multiplier,
                    timespan=timespan,
                    from_=current_from,
                    to=end_time,
                    adjusted=config.adjust_splits or config.adjust_dividends,
                    limit=limit
                )
                
                # Convert response to list if it's not already
                aggs_list = list(aggs_response)
                all_aggs.extend(aggs_list)
                
                # Check if we got all the data or need to paginate
                if len(aggs_list) < limit:
                    # We got fewer results than the limit, so we're done
                    break
                else:
                    # We hit the limit, need to get the next page
                    # Use the timestamp of the last result as the new start time
                    if aggs_list:
                        last_timestamp = aggs_list[-1].timestamp
                        current_from = datetime.fromtimestamp(last_timestamp / 1000)
                        # Add a small increment to avoid duplicate data
                        current_from += timedelta(seconds=1)
                    else:
                        # No results in this batch, break to avoid infinite loop
                        break
            
            # Convert to TimeSeriesData
            data = []
            timestamps = []
            for agg in all_aggs:
                timestamps.append(datetime.fromtimestamp(agg.timestamp / 1000))
                data.append(OHLCVData(
                    timestamp=datetime.fromtimestamp(agg.timestamp / 1000),
                    open=agg.open,
                    high=agg.high,
                    low=agg.low,
                    close=agg.close,
                    volume=agg.volume if config.include_volume else None
                ))
                
            return TimeSeriesData(timestamps=timestamps, data=data, data_type=DataType.OHLCV)
            
    def _parse_timeframe(self, timeframe: str) -> tuple[int, str]:
        """
        Convert timeframe string to Polygon's multiplier and timespan format.
        
        Args:
            timeframe: Timeframe string (e.g., '1m', '5m', '1h', '1d')
            
        Returns:
            Tuple of (multiplier, timespan)
        """
        # Extract number and unit
        number = int(''.join(filter(str.isdigit, timeframe)))
        unit = ''.join(filter(str.isalpha, timeframe))
        
        # Map unit to Polygon timespan
        timespan_map = {
            'm': 'minute',
            'h': 'hour',
            'd': 'day',
            'w': 'week',
            'M': 'month',
            'q': 'quarter',
            'y': 'year'
        }
        
        if unit not in timespan_map:
            raise ValueError(f"Unsupported timeframe unit: {unit}")
            
        return number, timespan_map[unit] 