from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
import pandas as pd

@dataclass
class OHLCVData:
    """Data class representing OHLCV data structure"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None