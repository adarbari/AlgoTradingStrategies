import pandas as pd
import numpy as np
from decimal import Decimal
from datetime import datetime, timedelta
import logging
from data import (
    is_market_hours,
    is_end_of_day,
    round_decimal,
    SHARE_PRECISION,
    CASH_PRECISION
)
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
from data.feature_engineering import FeatureEngineer

class SingleStockStrategy:
    def __init__(self, short_window=10, long_window=100, trade_size=1000, total_budget=10000, use_ml=True):
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
                'SMA_20', 'SMA_50', 'RSI', 'MACD', 'MACD_Signal',
                'BB_Upper', 'BB_Middle', 'BB_Lower',
                'Price_Change', 'Volume_Change', 'Volatility',
                'Price_Change_5min', 'Price_Change_15min',
                'Volume_MA_5', 'Volume_MA_15',
                'Price_Range', 'Price_Range_MA',
                'Volatility_5min', 'Volatility_15min'
            ]
            
        # Trading constraints
        self.min_probability_threshold = 0.4  # Lowered from 0.6 to 0.4
        self.min_volume_threshold = 500      # Lowered from 1000 to 500
        self.max_position_duration = 8        # Increased from 4 to 8 hours

    def train_model(self, data, run_manager=None, symbol=None):
        """Train the ML model if ML strategy is enabled"""
        if not self.use_ml:
            return
        
        # Use features directly from data
        X = data.loc[:, self.feature_columns].copy()
        y = data['target']
        
        # Debug: log feature columns used for training
        print(f"[DEBUG] Training feature columns: {list(X.columns)}")
        
        # Split into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Store test data for later use
        self.test_data = pd.DataFrame(X_test, columns=self.feature_columns)
        self.test_data['target'] = y_test
        self.test_scaled = X_test_scaled
        
        self.is_trained = True
        
        if run_manager and symbol:
            self.visualize_model(symbol, run_manager.run_dir)

    def generate_signals(self, data, run_manager=None, symbol=None):
        """Generate trading signals based on the strategy type"""
        if data is None or data.empty:
            self.logger.warning("No data provided for signal generation")
            return None
        
        # Create a copy of the data to avoid modifying the original
        signals = data.copy()
        
        # For ML mode, assume features are already present
        if self.use_ml:
            # Train the model if not already trained
            if not self.is_trained:
                self.train_model(signals, run_manager, symbol)
            
            # Ensure only the required feature columns are used and in the correct order
            feature_data = signals.loc[:, self.feature_columns].copy()
            # Debug: log feature columns used for prediction
            print(f"[DEBUG] Prediction feature columns: {list(feature_data.columns)}")
            scaled_features = self.scaler.transform(feature_data)
            
            # Generate probability predictions
            probabilities = self.model.predict_proba(scaled_features)
            signals['Buy_Probability'] = probabilities[:, 1]  # Probability of price increase
            signals['Sell_Probability'] = probabilities[:, 2]  # Probability of price decrease
            signals['Hold_Probability'] = probabilities[:, 0]  # Probability of no change
            
            # Generate signals based on probabilities and thresholds
            signals['Signal'] = 0  # Default to hold
            signals.loc[signals['Buy_Probability'] > self.min_probability_threshold, 'Signal'] = 1
            signals.loc[signals['Sell_Probability'] > self.min_probability_threshold, 'Signal'] = -1
            
            # Log ML strategy details
            if run_manager:
                logging.info(f"\nML Strategy Details for {symbol}:")
                logging.info(f"Feature columns: {self.feature_columns}")
                logging.info(f"Signal distribution: {signals['Signal'].value_counts().to_dict()}")
                logging.info(f"Average probabilities - Buy: {signals['Buy_Probability'].mean():.2f}, "
                           f"Sell: {signals['Sell_Probability'].mean():.2f}, "
                           f"Hold: {signals['Hold_Probability'].mean():.2f}")
        else:
            # Moving Average Crossover signal generation (requires raw OHLCV data)
            signals['MA_short'] = signals['Close'].rolling(window=self.short_window, min_periods=1).mean()
            signals['MA_long'] = signals['Close'].rolling(window=self.long_window, min_periods=1).mean()
            signals['ma_diff'] = signals['MA_short'] - signals['MA_long']
            signals['Signal'] = np.where(signals['ma_diff'] > 0, 1, -1)
            
            # Log MA strategy details
            if run_manager:
                logging.info(f"\nMA Strategy Details for {symbol}:")
                logging.info(f"Short window: {self.short_window}")
                logging.info(f"Long window: {self.long_window}")
                logging.info(f"Signal distribution: {signals['Signal'].value_counts().to_dict()}")
                logging.info(f"Average MA difference: {signals['ma_diff'].mean():.2f}")
        
        # Initialize position tracking
        signals['Position'] = 0
        signals['Shares'] = 0.0
        signals['Cash'] = float(self.total_budget)
        signals['Portfolio_Value'] = float(self.total_budget)
        signals['Trade_Profit'] = 0.0
        
        current_position = 0
        current_shares = Decimal('0.0')
        current_cash = self.total_budget
        last_buy_price = Decimal('0.0')
        position_start_time = None
        
        def safe_decimal(val, default=Decimal('0.0')):
            try:
                if pd.isna(val):
                    return default
                return Decimal(str(val))
            except Exception:
                return default
        
        for i in range(len(signals)):
            current_time = signals.index[i]
            next_time = signals.index[i+1] if i+1 < len(signals) else None
            price_val = safe_decimal(signals['Price'].iloc[i])
            # For ML mode, use Volume_MA_5 as a proxy for volume
            if self.use_ml:
                volume = safe_decimal(signals['Volume_MA_5'].iloc[i])
            else:
                volume = safe_decimal(signals['Volume'].iloc[i])
            
            # Check for end of day position closing
            if current_position == 1 and is_end_of_day(current_time, next_time):
                if current_shares > 0:
                    sell_price = price_val
                    trade_profit = round_decimal(current_shares * (sell_price - last_buy_price), CASH_PRECISION)
                    current_cash = round_decimal(current_cash + current_shares * sell_price, CASH_PRECISION)
                    signals.loc[signals.index[i], 'Trade_Profit'] = float(trade_profit)
                    signals.loc[signals.index[i], 'Signal'] = -1
                    signals.loc[signals.index[i], 'Position'] = 0
                    signals.loc[signals.index[i], 'Shares'] = 0.0
                    signals.loc[signals.index[i], 'Cash'] = float(current_cash)
                    signals.loc[signals.index[i], 'Portfolio_Value'] = float(current_cash)
                    current_shares = Decimal('0.0')
                    current_position = 0
                    last_buy_price = Decimal('0.0')
                    position_start_time = None
                    
                    # Log end of day trade
                    if run_manager:
                        run_manager.log_trade(
                            symbol=symbol,
                            trade_type='SELL',
                            price=float(sell_price),
                            shares=float(current_shares),
                            timestamp=current_time,
                            profit=float(trade_profit)
                        )
            
            # Check for maximum position duration
            if current_position == 1 and position_start_time is not None:
                position_duration = (current_time - position_start_time).total_seconds() / 3600  # hours
                if position_duration >= self.max_position_duration:
                    if current_shares > 0:
                        sell_price = price_val
                        trade_profit = round_decimal(current_shares * (sell_price - last_buy_price), CASH_PRECISION)
                        current_cash = round_decimal(current_cash + current_shares * sell_price, CASH_PRECISION)
                        signals.loc[signals.index[i], 'Trade_Profit'] = float(trade_profit)
                        signals.loc[signals.index[i], 'Signal'] = -1
                        signals.loc[signals.index[i], 'Position'] = 0
                        signals.loc[signals.index[i], 'Shares'] = 0.0
                        signals.loc[signals.index[i], 'Cash'] = float(current_cash)
                        signals.loc[signals.index[i], 'Portfolio_Value'] = float(current_cash)
                        current_shares = Decimal('0.0')
                        current_position = 0
                        last_buy_price = Decimal('0.0')
                        position_start_time = None
                        
                        # Log max duration trade
                        if run_manager:
                            run_manager.log_trade(
                                symbol=symbol,
                                trade_type='SELL',
                                price=float(sell_price),
                                shares=float(current_shares),
                                timestamp=current_time,
                                profit=float(trade_profit)
                            )
            
            # Generate buy signal
            if (current_position == 0 and 
                current_cash >= self.trade_size and 
                is_market_hours(current_time) and 
                volume >= self.min_volume_threshold):
                
                if signals['Signal'].iloc[i] == 1:
                    current_position = 1
                    price = price_val
                    current_shares = round_decimal(self.trade_size / price, SHARE_PRECISION) if price > 0 else Decimal('0.0')
                    current_cash = round_decimal(current_cash - self.trade_size, CASH_PRECISION)
                    last_buy_price = price
                    position_start_time = current_time
                    
                    # Log buy trade
                    if run_manager:
                        run_manager.log_trade(
                            symbol=symbol,
                            trade_type='BUY',
                            price=float(price),
                            shares=float(current_shares),
                            timestamp=current_time,
                            profit=None
                        )
            
            # Generate sell signal
            if (current_position == 1 and 
                current_shares > 0 and 
                signals['Signal'].iloc[i] == -1 and 
                volume >= self.min_volume_threshold):
                
                sell_price = price_val
                trade_profit = round_decimal(current_shares * (sell_price - last_buy_price), CASH_PRECISION)
                current_cash = round_decimal(current_cash + current_shares * sell_price, CASH_PRECISION)
                signals.loc[signals.index[i], 'Trade_Profit'] = float(trade_profit)
                shares_to_sell = float(current_shares)  # Store shares before setting to zero
                current_shares = Decimal('0.0')
                current_position = 0
                last_buy_price = Decimal('0.0')
                position_start_time = None
                
                # Log sell trade
                if run_manager:
                    run_manager.log_trade(
                        symbol=symbol,
                        trade_type='SELL',
                        price=float(sell_price),
                        shares=shares_to_sell,  # Use stored shares
                        timestamp=current_time,
                        profit=float(trade_profit)
                    )
            
            # Update position tracking
            signals.loc[signals.index[i], 'Position'] = current_position
            signals.loc[signals.index[i], 'Shares'] = float(current_shares)
            signals.loc[signals.index[i], 'Cash'] = float(current_cash)
            signals.loc[signals.index[i], 'Portfolio_Value'] = float(current_cash + (current_shares * price_val))
            
            # Log portfolio value
            if run_manager:
                run_manager.log_portfolio_value(
                    symbol=symbol,
                    timestamp=current_time,
                    portfolio_value=float(current_cash + (current_shares * price_val))
                )
        
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