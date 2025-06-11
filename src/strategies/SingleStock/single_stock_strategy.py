import pandas as pd
import numpy as np
from decimal import Decimal
from datetime import datetime, timedelta
import logging
from src.helpers.market_utils import is_market_hours, is_end_of_day, round_decimal, SHARE_PRECISION, CASH_PRECISION
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import tree
import graphviz
import json
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import learning_curve
import joblib
from src.features import TechnicalIndicators
from src.features.feature_store import FeatureStore

class SingleStockStrategy:
    def __init__(self, short_window=10, long_window=100, trade_size=1000, total_budget=10000, use_ml=True, cache_dir='feature_cache'):
        self.short_window = short_window
        self.long_window = long_window
        self.trade_size = Decimal(str(trade_size))
        self.total_budget = Decimal(str(total_budget))
        self.use_ml = use_ml
        
        # ML-specific attributes
        if self.use_ml:
            self.model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
            self.scaler = StandardScaler()
            self.is_trained = False
            self.test_data = None
            self.test_scaled = None
            self.feature_columns = [
                'rsi_14', 'macd', 'macd_signal', 'macd_hist',
                'sma_20', 'sma_50', 'sma_200',
                'ema_20', 'ema_50', 'ema_200',
                'bb_upper', 'bb_middle', 'bb_lower',
                # Add more if needed, but only those implemented in TechnicalIndicators
            ]
            
        # Trading constraints
        self.min_probability_threshold = 0.4
        self.min_volume_threshold = 500
        self.max_position_duration = 8  # hours
        
        # Initialize feature engineer
        self.feature_engineer = TechnicalIndicators()
        
        # Initialize feature store
        self.feature_store = FeatureStore(cache_dir=cache_dir)
    
    def _create_target_variable(self, data, lookahead_periods=5):
        """Create target variable based on future price movements."""
        # Calculate future returns
        future_returns = data['close'].shift(-lookahead_periods) / data['close'] - 1
        
        # Create target variable (0: hold, 1: buy, 2: sell)
        data['target'] = 0  # Default to hold
        data.loc[future_returns > 0.001, 'target'] = 1  # Buy if return > 0.1%
        data.loc[future_returns < -0.001, 'target'] = 2  # Sell if return < -0.1%
        
        # Drop NaN values at the end of the dataset
        data = data.dropna()
        
        return data
    
    def train_model(self, data, run_manager=None, symbol=None):
        """Train the ML model if in ML mode."""
        if not self.use_ml:
            return
            
        if data is None or data.empty:
            self.logger.warning("No data provided for training")
            return
            
        # Create target variable
        data = self._create_target_variable(data)
            
        # Ensure all required features are present
        missing_features = set(self.feature_columns) - set(data.columns)
        if missing_features:
            data = self.feature_engineer.calculate_features(data, list(missing_features))
        
        # Prepare features and target
        X = data[self.feature_columns].copy()
        y = data['target'].copy()
        
        # Log data types and structures
        logging.info(f"Training data type: {type(X)}")
        logging.info(f"Training data columns: {X.columns.tolist()}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = pd.DataFrame(self.scaler.fit_transform(X_train), columns=X_train.columns)
        X_test_scaled = pd.DataFrame(self.scaler.transform(X_test), columns=X_test.columns)
        
        # Log scaled data types and structures
        logging.info(f"Scaled training data type: {type(X_train_scaled)}")
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Store test data for later use
        self.test_data = X_test
        self.test_scaled = X_test_scaled
        
        # Log training results
        if run_manager:
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            logging.info(f"Model training complete for {symbol}")
            logging.info(f"Training accuracy: {train_score:.2f}")
            logging.info(f"Testing accuracy: {test_score:.2f}")
        
        self.is_trained = True
    
    def generate_signals(self, data, run_manager=None, symbol=None):
        """Generate trading signals based on the strategy."""
        # Create a copy of the data to avoid modifying the original
        signals = data.copy()
        
        # For ML mode, ensure features are present
        if self.use_ml:
            # Try to get cached features first
            cached_features = self.feature_store.get_cached_features(
                symbol=symbol,
                start_date=signals.index[0].strftime('%Y-%m-%d'),
                end_date=signals.index[-1].strftime('%Y-%m-%d'),
                features=self.feature_columns
            )
            
            if cached_features is not None:
                signals = pd.concat([signals, cached_features], axis=1)
            else:
                # Calculate features if not cached
                signals = self.feature_engineer.calculate_features(signals, self.feature_columns)
                # Cache the calculated features
                self.feature_store.cache_features(
                    symbol=symbol,
                    start_date=signals.index[0].strftime('%Y-%m-%d'),
                    end_date=signals.index[-1].strftime('%Y-%m-%d'),
                    features_df=signals[self.feature_columns]
                )
            
            # Train the model if not already trained
            if not self.is_trained:
                self.train_model(signals, run_manager, symbol)
            
            # Ensure the input data for prediction is a DataFrame with feature names
            X_pred = signals[self.feature_columns]
            # Log data types and structures
            logging.info(f"Prediction data type: {type(X_pred)}")
            logging.info(f"Prediction data columns: {X_pred.columns.tolist()}")
            # Generate predictions
            signals['prediction'] = self.model.predict(X_pred)
            signals['signal'] = signals['prediction'].map({1: 1, 0: -1})
        else:
            # Non-ML mode: use moving average crossover
            signals['SMA_20'] = signals['Close'].rolling(window=20).mean()
            signals['SMA_50'] = signals['Close'].rolling(window=50).mean()
            signals['signal'] = 0
            signals.loc[signals['SMA_20'] > signals['SMA_50'], 'signal'] = 1
            signals.loc[signals['SMA_20'] < signals['SMA_50'], 'signal'] = -1
        
        return signals

    def visualize_model(self, symbol, run_dir):
        """Visualize the ML model's structure and feature importance"""
        if not self.use_ml or not self.is_trained:
            return
            
        vis_dir = os.path.join(run_dir, 'visualizations')
        os.makedirs(vis_dir, exist_ok=True)
        
        # Plot feature importance
        plt.figure(figsize=(12, 6))
        importances = pd.Series(
            self.model.feature_importances_,
            index=self.feature_columns
        ).sort_values(ascending=True)
        
        importances.plot(kind='barh')
        plt.title(f'Feature Importance - {symbol}')
        plt.xlabel('Importance')
        plt.tight_layout()
        plt.savefig(os.path.join(vis_dir, f'{symbol}_feature_importance.png'))
        plt.close()
        
        # Plot confusion matrix
        plt.figure(figsize=(10, 8))
        y_pred = self.model.predict(self.test_scaled)
        cm = confusion_matrix(self.test_data['target'], y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title(f'Confusion Matrix - {symbol}')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(os.path.join(vis_dir, f'{symbol}_confusion_matrix.png'))
        plt.close()
        
        # Save model performance metrics
        metrics = {
            'feature_importance': dict(zip(self.feature_columns, self.model.feature_importances_)),
            'confusion_matrix': cm.tolist(),
            'training_score': self.model.score(self.test_scaled, self.test_data['target'])
        }
        
        with open(os.path.join(vis_dir, f'{symbol}_model_metrics.json'), 'w') as f:
            json.dump(metrics, f, indent=4) 