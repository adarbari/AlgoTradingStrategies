"""
Random Forest Strategy implementation for single stock trading.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from src.strategies.base_strategy import BaseStrategy, StrategySignal
from src.features.feature_store import FeatureStore

class RandomForestStrategy(BaseStrategy):
    """
    Random Forest Strategy for single stock trading.
    
    This strategy uses a Random Forest classifier to predict price movements
    based on technical indicators and features.
    """
    
    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 5,
        min_samples_split: int = 2,
        lookback_window: int = 20,
        cache_dir: str = 'feature_cache'
    ):
        """
        Initialize the Random Forest Strategy.
        
        Args:
            n_estimators (int): Number of trees in the forest
            max_depth (int): Maximum depth of the trees
            min_samples_split (int): Minimum samples required to split a node
            lookback_window (int): Number of days to look back for features
            cache_dir (str): Directory for caching features
        """
        super().__init__(name="Random_Forest")
        self.cache_dir = cache_dir
        self.feature_store = FeatureStore(cache_dir=cache_dir)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.lookback_window = lookback_window
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        
    def prepare_data(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Prepare data for the strategy by calculating features.
        
        Args:
            data (pd.DataFrame): Price data
            symbol (str): Stock symbol
            
        Returns:
            pd.DataFrame: Data with features
        """
        # Determine date range
        start_date = data.index.min().strftime('%Y-%m-%d')
        end_date = data.index.max().strftime('%Y-%m-%d')
        
        # Get features using the feature store
        features = self.feature_store.get_features(
            symbol=symbol,
            data=data,
            start_date=start_date,
            end_date=end_date
        )
        
        # Store feature columns for prediction
        self.feature_columns = [col for col in features.columns if col not in ['target', 'close']]
        
        # Train model and fit scaler if not already done
        if self.model is None:
            self._train_model(features)
            features[self.feature_columns] = self.scaler.fit_transform(features[self.feature_columns])
        else:
            features[self.feature_columns] = self.scaler.transform(features[self.feature_columns])
        
        return features
    
    def _train_model(self, data: pd.DataFrame) -> None:
        """
        Train the Random Forest model.
        
        Args:
            data (pd.DataFrame): Training data with features and target
        """
        # Select features for training
        feature_cols = [col for col in data.columns if col not in ['target', 'close']]
        X = data[feature_cols]
        y = data['target']
        
        # Create and train model
        self.model = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            random_state=42
        )
        self.model.fit(X, y)
    
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
        if not self.model:
            # Return HOLD signal with low confidence if model is not trained
            return StrategySignal(
                symbol=symbol,
                action='HOLD',
                probabilities={'BUY': 0.33, 'SELL': 0.33, 'HOLD': 0.34},
                confidence=0.1,
                timestamp=timestamp,
                features=features
            )
        
        # Scale features
        feature_values = np.array([features[col] for col in self.feature_columns]).reshape(1, -1)
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
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'min_samples_split': self.min_samples_split,
            'lookback_window': self.lookback_window
        }
    
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Set the strategy parameters.
        
        Args:
            parameters (Dict[str, Any]): New strategy parameters
        """
        if 'n_estimators' in parameters:
            self.n_estimators = parameters['n_estimators']
        if 'max_depth' in parameters:
            self.max_depth = parameters['max_depth']
        if 'min_samples_split' in parameters:
            self.min_samples_split = parameters['min_samples_split']
        if 'lookback_window' in parameters:
            self.lookback_window = parameters['lookback_window'] 