"""
Base types for data structures.
"""

from datetime import datetime
from typing import List, TypeVar, Generic, NamedTuple, Dict, Any
import pandas as pd
import dataclasses

from src.data.types.data_type import DataType

SegmentID = str

T = TypeVar('T')

class TimeSeriesData(Generic[T]):
    """Generic time series data container."""
    def __init__(self, timestamps: List[datetime], data: List[T], data_type: DataType):
        self.timestamps = timestamps
        self.data = data
        self.data_type = data_type

    def __len__(self) -> int:
        return len(self.timestamps)

    def to_dataframe(self):
        """
        Convert the time series data to a pandas DataFrame.
        Ensures all columns are primitive types (not dicts) by unwrapping single-key dicts.
        Returns:
            pd.DataFrame: DataFrame with timestamps as index.
        """
        def extract_single_value(val):
            # If val is a dict with one key, return its value
            if isinstance(val, dict) and len(val) == 1:
                return next(iter(val.values()))
            return val

        if not self.data:
            return pd.DataFrame(index=self.timestamps)
        if hasattr(self.data[0], '__dataclass_fields__'):
            records = [dataclasses.asdict(d) for d in self.data]
        else:
            records = self.data
        # Unwrap single-key dicts for all fields in all records
        cleaned_records = [
            {k: extract_single_value(v) for k, v in r.items()} if isinstance(r, dict) else r
            for r in records
        ]
        return pd.DataFrame(cleaned_records, index=self.timestamps)

class MissingDataRange(NamedTuple):
    """Represents a range of missing data."""
    start_time: datetime
    end_time: datetime

class OrderBookLevel(NamedTuple):
    """Represents a single level in the order book."""
    price: float
    size: int
    num_orders: int

class OrderBookSnapshot(NamedTuple):
    """Represents a snapshot of the order book."""
    timestamp: datetime
    symbol: str
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]

class TradeFlags(NamedTuple):
    """Flags associated with a trade."""
    is_buy: bool
    is_sell: bool
    is_aggressive: bool
    is_passive: bool
    is_cross: bool
    is_auction: bool

class Trade(NamedTuple):
    """Represents a single trade."""
    timestamp: datetime
    symbol: str
    price: float
    size: int
    flags: TradeFlags
    trade_id: str
    buyer_id: str
    seller_id: str 