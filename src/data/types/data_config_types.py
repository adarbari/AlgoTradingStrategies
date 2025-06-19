from abc import ABC
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class DataConfig(ABC):
    """Base class for all data configurations."""
    pass

@dataclass
class OHLCVConfig(DataConfig):
    """Configuration for OHLCV data."""
    timeframe: str = '5m'  # e.g., '1m', '5m', '1h', '1d'
    adjust_splits: bool = True
    adjust_dividends: bool = True
    include_volume: bool = True

@dataclass
class OrderFlowConfig(DataConfig):
    """Configuration for Order Flow data."""
    order_types: Optional[List[str]] = None  # e.g., ['market', 'limit']
    min_size: Optional[float] = None
    max_size: Optional[float] = None
    include_cancellations: bool = True
    include_modifications: bool = True 