from typing import List, Dict, Any
from datetime import datetime
import pandas as pd

from ..types.metrics_types import OrderFlowMetrics
from src.data.types.order_flow_types import Trade, OrderBookSnapshot, OrderSide

class OrderFlowMetricsCalculator:
    """Calculates order flow metrics from trades and order book data."""
    
    @staticmethod
    def calculate_metrics(
        trades: List[Trade],
        order_book: OrderBookSnapshot,
        window_size: int = 1000  # Number of trades to consider for metrics
    ) -> OrderFlowMetrics:
        """Calculate order flow metrics from trades and order book data."""
        recent_trades = trades[-window_size:] if len(trades) > window_size else trades
        
        # Calculate volume metrics
        buy_volume = sum(t.quantity for t in recent_trades if t.side == OrderSide.BUY)
        sell_volume = sum(t.quantity for t in recent_trades if t.side == OrderSide.SELL)
        total_volume = buy_volume + sell_volume
        volume_delta = buy_volume - sell_volume
        
        # Calculate order book metrics
        bid_volume = sum(b.quantity for b in order_book.bids)
        ask_volume = sum(a.quantity for a in order_book.asks)
        order_imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume) if (bid_volume + ask_volume) > 0 else 0
        
        # Calculate trade metrics
        buy_trade_count = sum(1 for t in recent_trades if t.side == OrderSide.BUY)
        sell_trade_count = sum(1 for t in recent_trades if t.side == OrderSide.SELL)
        trade_count = buy_trade_count + sell_trade_count
        
        # Calculate VWAP
        vwap = sum(t.price * t.quantity for t in recent_trades) / total_volume if total_volume > 0 else 0
        
        # Calculate large trade count (trades > 2x average size)
        avg_trade_size = total_volume / trade_count if trade_count > 0 else 0
        large_trade_count = sum(1 for t in recent_trades if t.quantity > 2 * avg_trade_size)
        
        # Calculate price impact (price change per unit volume)
        if len(recent_trades) >= 2:
            price_change = recent_trades[-1].price - recent_trades[0].price
            price_impact = price_change / total_volume if total_volume > 0 else 0
        else:
            price_impact = 0
            
        # Calculate liquidity score (based on order book depth and spread)
        liquidity_score = (bid_volume + ask_volume) / (order_book.spread + 1) if order_book.spread > 0 else 0
        
        return OrderFlowMetrics(
            timestamp=recent_trades[-1].timestamp if recent_trades else order_book.timestamp,
            symbol=order_book.symbol,
            volume_delta=volume_delta,
            buy_volume=buy_volume,
            sell_volume=sell_volume,
            total_volume=total_volume,
            order_imbalance=order_imbalance,
            bid_ask_spread=order_book.spread,
            mid_price=order_book.mid_price,
            vwap=vwap,
            trade_count=trade_count,
            buy_trade_count=buy_trade_count,
            sell_trade_count=sell_trade_count,
            large_trade_count=large_trade_count,
            price_impact=price_impact,
            liquidity_score=liquidity_score
        )
    
    @staticmethod
    def calculate_metrics_batch(
        trades_list: List[List[Trade]],
        order_books: List[OrderBookSnapshot],
        window_size: int = 1000
    ) -> List[OrderFlowMetrics]:
        """Calculate metrics for multiple time windows."""
        return [
            OrderFlowMetricsCalculator.calculate_metrics(trades, order_book, window_size)
            for trades, order_book in zip(trades_list, order_books)
        ]
    
    @staticmethod
    def to_dataframe(metrics: List[OrderFlowMetrics]) -> pd.DataFrame:
        """Convert a list of metrics to a DataFrame."""
        return pd.DataFrame([{
            'timestamp': m.timestamp,
            'symbol': m.symbol,
            'volume_delta': m.volume_delta,
            'buy_volume': m.buy_volume,
            'sell_volume': m.sell_volume,
            'total_volume': m.total_volume,
            'order_imbalance': m.order_imbalance,
            'bid_ask_spread': m.bid_ask_spread,
            'mid_price': m.mid_price,
            'vwap': m.vwap,
            'trade_count': m.trade_count,
            'buy_trade_count': m.buy_trade_count,
            'sell_trade_count': m.sell_trade_count,
            'large_trade_count': m.large_trade_count,
            'price_impact': m.price_impact,
            'liquidity_score': m.liquidity_score,
            'metadata': m.metadata
        } for m in metrics]) 