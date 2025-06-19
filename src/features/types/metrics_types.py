from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class OrderFlowMetrics:
    """Represents calculated order flow metrics."""
    timestamp: datetime
    symbol: str
    # Volume metrics
    volume_delta: float  # Buy volume - Sell volume
    buy_volume: float
    sell_volume: float
    total_volume: float
    # Order book metrics
    order_imbalance: float  # (Bid volume - Ask volume) / (Bid volume + Ask volume)
    bid_ask_spread: float
    mid_price: float
    vwap: float
    # Trade metrics
    trade_count: int
    buy_trade_count: int
    sell_trade_count: int
    large_trade_count: int  # Trades larger than average
    # Market impact metrics
    price_impact: float  # Price change per unit volume
    liquidity_score: float  # Measure of market liquidity
    # Additional metrics
    metadata: Dict[str, Any] = None  # Vendor-specific metrics 