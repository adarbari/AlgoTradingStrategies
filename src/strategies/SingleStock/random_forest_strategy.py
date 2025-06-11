"""
Random Forest Strategy implementation for single stock trading.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from src.strategies.base_strategy import BaseStrategy
from src.execution.trade_decider import StrategySignal
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
        
    def prepare_data(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Prepare data for the strategy by calculating features and training the model.
        
        Args:
            data (pd.DataFrame): Price data
            symbol (str): Stock symbol
            
        Returns:
            pd.DataFrame: Data with features and target
        """
        # Determine date range
        start_date = data.index.min().strftime('%Y-%m-%d')
        end_date = data.index.max().strftime('%Y-%m-%d')
        # Fetch features from feature store
        features = self.feature_store.get_cached_features(symbol, start_date, end_date)
        if features is None:
            raise ValueError(f"No features found in cache for {symbol} from {start_date} to {end_date}.")
        # Create target variable (1 if price goes up, 0 if down)
        features['target'] = (features['price'].shift(-1) > features['price']).astype(int)
        features = features.dropna()
        if self.model is None:
            self._train_model(features)
        return features
    
    def _train_model(self, data: pd.DataFrame) -> None:
        """
        Train the Random Forest model.
        
        Args:
            data (pd.DataFrame): Training data with features and target
        """
        # Select features for training
        feature_cols = [col for col in data.columns if col not in ['target', 'price']]
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
        data: pd.DataFrame,
        symbol: str,
        timestamp: datetime
    ) -> StrategySignal:
        """
        Generate trading signals based on model predictions.
        
        Args:
            data (pd.DataFrame): Price data
            symbol (str): Stock symbol
            timestamp (datetime): Current timestamp
            
        Returns:
            StrategySignal: Trading signal with probabilities and confidence
        """
        # Get latest data point
        latest = data.iloc[-1]
        
        # Select features for prediction
        feature_cols = [col for col in data.columns if col not in ['target', 'price']]
        X = latest[feature_cols].values.reshape(1, -1)
        
        # Get prediction probabilities
        probs = self.model.predict_proba(X)[0]
        
        # Calculate signal probabilities
        if len(probs) == 2:  # Binary classification
            probabilities = {
                'BUY': probs[1],
                'SELL': probs[0],
                'HOLD': 0.0
            }
        else:  # Multi-class classification
            probabilities = {
                'BUY': probs[1],
                'SELL': probs[2],
                'HOLD': probs[0]
            }
        
        # Calculate confidence based on prediction probability
        confidence = max(probabilities.values())
        
        return StrategySignal(
            timestamp=timestamp,
            symbol=symbol,
            features={
                'price': latest['price'],
                **{col: latest[col] for col in feature_cols}
            },
            probabilities=probabilities,
            confidence=confidence
        )
    
    def update(self, data: pd.DataFrame, symbol: str) -> None:
        """
        Update the strategy with new data and retrain the model.
        
        Args:
            data (pd.DataFrame): New price data
            symbol (str): Stock symbol
        """
        # Retrain model with new data
        features = self.prepare_data(data, symbol)
        self._train_model(features)
    
    def get_features(self) -> list:
        """
        Get the list of features used by the strategy.
        
        Returns:
            list: List of feature names
        """
        return self.feature_store.get_feature_names()
    
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