from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum

class OrderSide(Enum):
    BUY = 'buy'
    SELL = 'sell'

@dataclass
class Trade:
    timestamp: datetime
    price: float
    quantity: float
    side: OrderSide

@dataclass
class OrderBookLevel:
    price: float
    quantity: float

@dataclass
class OrderBookSnapshot:
    timestamp: datetime
    symbol: str
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    spread: float = 0.0
    mid_price: float = 0.0 