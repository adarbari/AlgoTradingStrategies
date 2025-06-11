"""
Data package.
Contains data management and interaction functionality.
"""

from .data_manager import (
    get_cached_data,
    is_market_hours,
    is_end_of_day,
    round_decimal,
    SHARE_PRECISION,
    CASH_PRECISION
)

__all__ = [
    'get_cached_data',
    'is_market_hours',
    'is_end_of_day',
    'round_decimal',
    'SHARE_PRECISION',
    'CASH_PRECISION'
] 