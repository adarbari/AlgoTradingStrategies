from abc import ABC, abstractmethod
from typing import List, Optional
import pandas as pd

from src.data.types.base_types import TimeSeriesData

class FeatureEngineer(ABC):
    """Base class for all feature engineering implementations."""
    
    @abstractmethod
    def calculate_features(
        self,
        data: TimeSeriesData,
        features: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Calculate features for the given data."""
        pass
    
    @abstractmethod
    def get_available_features(self) -> List[str]:
        """Get list of available features that can be calculated."""
        pass
    
    @abstractmethod
    def get_feature_dependencies(self, feature: str) -> List[str]:
        """Get list of features that a given feature depends on."""
        pass 