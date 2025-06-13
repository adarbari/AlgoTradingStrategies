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
from src.features.technical_indicators import TechnicalIndicators
from src.config.strategy_config import RandomForestConfig

class RandomForestStrategy(BaseStrategy):
    """
    Random Forest Strategy for single stock trading.
    
    This strategy uses a Random Forest classifier to predict price movements
    based on technical indicators and features.
    """
    
    def __init__(
        self,
        config: Optional[RandomForestConfig] = None,
        feature_store: Optional[FeatureStore] = None,
    ):
        """
        Initialize the Random Forest Strategy.
        
        Args:
            config (Optional[RandomForestConfig]): Strategy configuration. If None, default config will be used.
            feature_store (Optional[FeatureStore]): Feature store instance. If None, a new one will be created.
        """
        super().__init__(name="Random_Forest")
        self.config = config or RandomForestConfig()
        self.feature_store = feature_store or FeatureStore(cache_dir=self.config.cache_dir)
        self.model = None
        self.scaler = StandardScaler()

        # Use FeatureNames from TechnicalIndicators
        self.feature_columns = [
            # Price data
            'open',
            'high',
            'low',
            'close',
            'volume',
            
            # Moving Averages
            TechnicalIndicators.FeatureNames.SMA_20,
            TechnicalIndicators.FeatureNames.SMA_50,
            TechnicalIndicators.FeatureNames.SMA_200,
            TechnicalIndicators.FeatureNames.EMA_20,
            TechnicalIndicators.FeatureNames.EMA_50,
            TechnicalIndicators.FeatureNames.EMA_200,
            TechnicalIndicators.FeatureNames.MA_SHORT,
            TechnicalIndicators.FeatureNames.MA_LONG,
            
            # MACD
            TechnicalIndicators.FeatureNames.MACD,
            TechnicalIndicators.FeatureNames.MACD_SIGNAL,
            TechnicalIndicators.FeatureNames.MACD_HIST,
            
            # Momentum
            TechnicalIndicators.FeatureNames.RSI_14,
            TechnicalIndicators.FeatureNames.RSI,
            TechnicalIndicators.FeatureNames.STOCH_K,
            TechnicalIndicators.FeatureNames.STOCH_D,
            
            # Volatility
            TechnicalIndicators.FeatureNames.BB_UPPER,
            TechnicalIndicators.FeatureNames.BB_MIDDLE,
            TechnicalIndicators.FeatureNames.BB_LOWER,
            TechnicalIndicators.FeatureNames.ATR,
            
            # Volume
            TechnicalIndicators.FeatureNames.VOLUME_MA_5,
            TechnicalIndicators.FeatureNames.VOLUME_MA_15,
            TechnicalIndicators.FeatureNames.VOLUME_CHANGE,
            
            # Price Action
            TechnicalIndicators.FeatureNames.PRICE_CHANGE,
            TechnicalIndicators.FeatureNames.PRICE_CHANGE_5MIN,
            TechnicalIndicators.FeatureNames.PRICE_CHANGE_15MIN,
            TechnicalIndicators.FeatureNames.PRICE_RANGE,
            TechnicalIndicators.FeatureNames.PRICE_RANGE_MA,
            
            # Volatility
            TechnicalIndicators.FeatureNames.VOLATILITY,
            TechnicalIndicators.FeatureNames.VOLATILITY_5MIN,
            TechnicalIndicators.FeatureNames.VOLATILITY_15MIN
        ]
        self.target_columns = [TechnicalIndicators.FeatureNames.TARGET]
        
    def train_model(self, data: pd.DataFrame, symbol: str):
        """
        Prepare data for the strategy by calculating features.
        
        Args:
            data (pd.DataFrame): Price data
            symbol (str): Stock symbol
            
        Returns:
            pd.DataFrame: Data with features
        """
        if self.model is None:
            features = self._get_training_features(data, symbol)
            
            # Select features for training (excluding target)
            X = features[self.feature_columns]
            y = features[self.target_columns]
            
            # Create and train model
            self.model = RandomForestClassifier(
                n_estimators=self.config.n_estimators,
                max_depth=self.config.max_depth,
                min_samples_split=self.config.min_samples_split,
                random_state=42)
        
            # Fit scaler and transform features
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)
    
    def _get_training_features(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Get training features for the strategy.
        
        Args:
            data (pd.DataFrame): Price data
            symbol (str): Stock symbol
            
        Returns:
            pd.DataFrame: Training features
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
        
        # Create DataFrame with features to preserve feature names
        feature_df = pd.DataFrame([features])
        
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
            'lookback_window': self.config.lookback_window
        }
    
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Set the strategy parameters.
        
        Args:
            parameters (Dict[str, Any]): New strategy parameters
        """
        self.config = RandomForestConfig(**parameters) 