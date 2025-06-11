"""
RandomForest-based single stock trading strategy implementation.
"""
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
from sklearn.metrics import confusion_matrix
import json
from src.features import TechnicalIndicators
from src.features.feature_store import FeatureStore

class RandomForestSingleStockStrategy:
    def __init__(self, trade_size=1000, total_budget=10000, cache_dir='feature_cache'):
        self.trade_size = Decimal(str(trade_size))
        self.total_budget = Decimal(str(total_budget))
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
        ]
        self.min_probability_threshold = 0.4
        self.min_volume_threshold = 500
        self.max_position_duration = 8  # hours
        self.feature_engineer = TechnicalIndicators()
        self.feature_store = FeatureStore(cache_dir=cache_dir)

    def _create_target_variable(self, data, lookahead_periods=5):
        future_returns = data['close'].shift(-lookahead_periods) / data['close'] - 1
        data['target'] = 0
        data.loc[future_returns > 0.001, 'target'] = 1
        data.loc[future_returns < -0.001, 'target'] = 2
        data = data.dropna()
        return data

    def train_model(self, data, run_manager=None, symbol=None):
        if data is None or data.empty:
            logging.warning("No data provided for training")
            return
        data = self._create_target_variable(data)
        missing_features = set(self.feature_columns) - set(data.columns)
        if missing_features:
            data = self.feature_engineer.calculate_features(data, list(missing_features))
        X = data[self.feature_columns].copy()
        y = data['target'].copy()
        logging.info(f"Training data type: {type(X)}")
        logging.info(f"Training data columns: {X.columns.tolist()}")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        X_train_scaled = pd.DataFrame(self.scaler.fit_transform(X_train), columns=X_train.columns)
        X_test_scaled = pd.DataFrame(self.scaler.transform(X_test), columns=X_test.columns)
        logging.info(f"Scaled training data type: {type(X_train_scaled)}")
        self.model.fit(X_train_scaled, y_train)
        self.test_data = X_test
        self.test_scaled = X_test_scaled
        if run_manager:
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            logging.info(f"Model training complete for {symbol}")
            logging.info(f"Training accuracy: {train_score:.2f}")
            logging.info(f"Testing accuracy: {test_score:.2f}")
        self.is_trained = True

    def generate_signals(self, data, run_manager=None, symbol=None):
        signals = data.copy()
        cached_features = self.feature_store.get_cached_features(
            symbol=symbol,
            start_date=signals.index[0].strftime('%Y-%m-%d'),
            end_date=signals.index[-1].strftime('%Y-%m-%d'),
            features=self.feature_columns
        )
        if cached_features is not None:
            signals = pd.concat([signals, cached_features], axis=1)
        else:
            signals = self.feature_engineer.calculate_features(signals, self.feature_columns)
            self.feature_store.cache_features(
                symbol=symbol,
                start_date=signals.index[0].strftime('%Y-%m-%d'),
                end_date=signals.index[-1].strftime('%Y-%m-%d'),
                features_df=signals[self.feature_columns]
            )
        if not self.is_trained:
            self.train_model(signals, run_manager, symbol)
        X_pred = signals[self.feature_columns]
        logging.info(f"Prediction data type: {type(X_pred)}")
        logging.info(f"Prediction data columns: {X_pred.columns.tolist()}")
        signals['prediction'] = self.model.predict(X_pred)
        signals['signal'] = signals['prediction'].map({1: 1, 0: -1})
        return signals

    def visualize_model(self, symbol, run_dir):
        if not self.is_trained:
            return
        vis_dir = os.path.join(run_dir, 'visualizations')
        os.makedirs(vis_dir, exist_ok=True)
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
        plt.figure(figsize=(10, 8))
        y_pred = self.model.predict(self.test_scaled)
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(self.test_data['target'], y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title(f'Confusion Matrix - {symbol}')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(os.path.join(vis_dir, f'{symbol}_confusion_matrix.png'))
        plt.close()
        metrics = {
            'feature_importance': dict(zip(self.feature_columns, self.model.feature_importances_)),
            'confusion_matrix': cm.tolist(),
            'training_score': self.model.score(self.test_scaled, self.test_data['target'])
        }
        with open(os.path.join(vis_dir, f'{symbol}_model_metrics.json'), 'w') as f:
            json.dump(metrics, f, indent=4) 