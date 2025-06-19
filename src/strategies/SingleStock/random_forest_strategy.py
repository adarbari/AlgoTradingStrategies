"""
Random Forest Strategy implementation for single stock trading.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from src.data.types.base_types import TimeSeriesData
from src.data.types.data_type import DataType
from src.data.types.ohlcv_types import OHLCVData
from src.strategies.base_strategy import BaseStrategy, StrategySignal
from src.features.core.feature_store import FeatureStore
from src.features.implementations.technical_indicators import TechnicalIndicators
from src.config.strategy_config import RandomForestConfig
from src.config.base_enums import StrategyType

class RandomForestStrategy(BaseStrategy):
    """
    Random Forest Strategy for single stock trading.
    
    This strategy uses a Random Forest classifier to predict price movements
    based on technical indicators and features.
    """
    
    def __init__(
        self,
        config: Optional[RandomForestConfig] = None
    ):
        """
        Initialize the Random Forest Strategy.
        
        Args:
            config (Optional[RandomForestConfig]): Strategy configuration. If None, default config will be used.
       """
        super().__init__(name=StrategyType.RANDOM_FOREST)
        self.config = config or RandomForestConfig()
        self.feature_store = FeatureStore.get_instance()
        self.model = None
        self.scaler = StandardScaler()

        # Use FeatureNames from TechnicalIndicators
        self.feature_columns = self.config.feature_columns
        self.target_columns = self.config.target_columns 
        
    def train_model(self, data: TimeSeriesData, symbol: str):
        """
        Prepare data for the strategy by calculating features.
        
        Args:
            data (pd.DataFrame): Price data
            symbol (str): Stock symbol
            
        Returns:
            pd.DataFrame: Data with features
        """
        if self.model is None:
            # Get all features for the associated symbol
            features = self._get_all_features(data, symbol)
            
            # Select features for training (excluding target)
            X = features[self.feature_columns]
            y = features[self.target_columns]
            
            # Create and train model
            self.model = RandomForestClassifier(
                n_estimators=self.config.n_estimators,
                max_depth=self.config.max_depth,
                min_samples_split=self.config.min_samples_split,
                random_state=self.config.random_state)
        
            # Fit scaler and transform features
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)
    
    def _get_all_features(self, data: TimeSeriesData, symbol: str) -> pd.DataFrame:
        """
        Get training features for the strategy.
        
        Args:
            data (pd.DataFrame): Price data
            symbol (str): Stock symbol
            
        Returns:
            pd.DataFrame: Training features
        """
        # Determine date range
        # Get start and end date from TimeSeriesData object, ensuring timestamps are sorted
        if data.timestamps:
            sorted_timestamps = sorted(data.timestamps)
            start_date = sorted_timestamps[0]#.strftime('%Y-%m-%d')
            end_date = sorted_timestamps[-1]#.strftime('%Y-%m-%d')
        else:
            raise ValueError("No timestamps found in TimeSeriesData; cannot determine start and end date for feature extraction.")
        
        # Get features using the feature store
        features = self.feature_store.get_features(
            symbol=symbol,
            start_timestamp=start_date,
            end_timestamp=end_date
        )
        
        return features

    def generate_signals(
        self,
        features: Dict[str, float],
        symbol: str,
        timestamp: datetime
    ) -> StrategySignal:
        """
        Generate trading signals based on current features.
        
        Args:
            features (Dict[str, float]): Current features
            symbol (str): Stock symbol
            timestamp (datetime): Current timestamp
            
        Returns:
            StrategySignal: Trading signal with probabilities and confidence
        """
        if not self.model or not self.feature_columns:
            # Return HOLD signal with low confidence if model is not trained
            return StrategySignal(
                symbol=symbol,
                action='HOLD',
                probabilities={'BUY': 0.33, 'SELL': 0.33, 'HOLD': 0.34},
                confidence=0.1,
                timestamp=timestamp,
                features=features
            )

        # Call get_features API with the TimeSeriesData
        feature_df = self.feature_store.get_features_at_timestamp(
            symbol=symbol,
            timestamp=timestamp
        )
        
        # Ensure we have all required features
        missing_features = set(self.feature_columns) - set(feature_df.columns)
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")
            
        # Select only the features used during training
        feature_values = feature_df[self.feature_columns]
        
        # Scale features
        scaled_features = self.scaler.transform(feature_values)
        
        # Get prediction probabilities
        probabilities = self.model.predict_proba(scaled_features)[0]
        class_labels = self.model.classes_
        label_map = {-1: 'SELL', 0: 'HOLD', 1: 'BUY'}
        mapped_probs = {label_map.get(int(cls), str(cls)): float(prob) for cls, prob in zip(class_labels, probabilities)}
        action_idx = np.argmax(probabilities)
        action_label = class_labels[action_idx]
        action = label_map.get(int(action_label), str(action_label))
        confidence = probabilities[action_idx]
        
        return StrategySignal(
            symbol=symbol,
            action=action,
            probabilities=mapped_probs,
            confidence=confidence,
            timestamp=timestamp,
            features=features
        )
    
    def update(self, data: pd.DataFrame, symbol: str) -> None:
        """
        Update the strategy with new data.
        
        Args:
            data (pd.DataFrame): New price data
            symbol (str): Stock symbol
        """
        # No state to update for Random Forest
        pass
    
    def get_features(self) -> list:
        """
        Get the list of features used by the strategy.
        
        Returns:
            list: List of feature names
        """
        return self.feature_columns or []
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get the strategy parameters.
        
        Returns:
            Dict[str, Any]: Strategy parameters
        """
        return {
            'n_estimators': self.config.n_estimators,
            'max_depth': self.config.max_depth,
            'min_samples_split': self.config.min_samples_split,
            'lookback_window': self.config.lookback_window,
            'random_state': self.config.random_state,
            'feature_columns': self.config.feature_columns,
            'target_columns': self.config.target_columns
        }
    
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Set the strategy parameters.
        
        Args:
            parameters (Dict[str, Any]): New strategy parameters
        """
        self.config = RandomForestConfig(**parameters) 