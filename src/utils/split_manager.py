from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class SplitManager:
    """Manages train/validation/test splits for time series data."""
    
    def __init__(
        self,
        train_ratio: float = 0.6,
        val_ratio: float = 0.2,
        test_ratio: float = 0.2,
        min_train_days: int = 0
    ):
        """Initialize split manager.
        
        Args:
            train_ratio: Ratio of data to use for training (default: 0.6)
            val_ratio: Ratio of data to use for validation (default: 0.2)
            test_ratio: Ratio of data to use for testing (default: 0.2)
            min_train_days: Minimum number of days required for training (default: 30)
            
        Raises:
            ValueError: If ratios don't sum to 1 or if any ratio is negative
        """
        # Validate ratios
        if not (0 <= train_ratio <= 1 and 0 <= val_ratio <= 1 and 0 <= test_ratio <= 1):
            raise ValueError("All ratios must be between 0 and 1")
            
        if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-10:
            raise ValueError("Ratios must sum to 1")
            
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.min_train_days = min_train_days
        
    def get_split_dates(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, datetime]:
        """Calculate split dates for the given date range.
        
        Args:
            start_date: Start date of the data
            end_date: End date of the data
            
        Returns:
            Dictionary containing split dates:
            {
                'train_start': datetime,
                'train_end': datetime,
                'val_end': datetime,
                'test_end': datetime
            }
            
        Raises:
            ValueError: If date range is too short for minimum training days
        """
        # Calculate total days
        total_days = (end_date - start_date).days
        
        # Validate minimum training period
        min_train_period = timedelta(days=self.min_train_days)
        if total_days < self.min_train_days:
            raise ValueError(
                f"Date range ({total_days} days) is shorter than minimum "
                f"training period ({self.min_train_days} days)"
            )
            
        # Calculate split dates
        train_end = start_date + timedelta(days=int(total_days * self.train_ratio))
        val_end = train_end + timedelta(days=int(total_days * self.val_ratio))
        
        # Ensure test_end matches end_date exactly
        test_end = end_date
        
        return {
            'train_start': start_date,
            'train_end': train_end,
            'val_end': val_end,
            'test_end': test_end
        } 