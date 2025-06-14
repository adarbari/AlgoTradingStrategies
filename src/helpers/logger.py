import logging
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional
import json
import numpy as np

class TradingLogger:
    """Manages logging for the trading system."""
    
    def __init__(self):
        # Create base directories
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_timestamp_dir = os.path.join(os.getcwd(), "logs", f"run_{timestamp}")
        os.makedirs(self.run_timestamp_dir, exist_ok=True)
        
        # Create phase-specific directories
        self.phase_dirs = {
            'train': os.path.join(self.run_timestamp_dir, "train"),
            'val': os.path.join(self.run_timestamp_dir, "val"),
            'test': os.path.join(self.run_timestamp_dir, "test")
        }
        
        for phase_dir in self.phase_dirs.values():
            os.makedirs(phase_dir, exist_ok=True)
            os.makedirs(os.path.join(phase_dir, "logs"), exist_ok=True)
            os.makedirs(os.path.join(phase_dir, "visualizations"), exist_ok=True)
            os.makedirs(os.path.join(phase_dir, "ticker"), exist_ok=True)
        
        # Initialize log files for each phase
        self.phase_files = {}
        for phase, phase_dir in self.phase_dirs.items():
            self.phase_files[phase] = {
                'trades': os.path.join(phase_dir, "trades.csv"),
                'periods': os.path.join(phase_dir, "periods.csv")
            }
            # Create headers if files don't exist
            if not os.path.exists(self.phase_files[phase]['trades']):
                pd.DataFrame(columns=['symbol', 'trade_type', 'price', 'shares', 'timestamp', 'profit', 'portfolio_value', 'cash']).to_csv(self.phase_files[phase]['trades'], index=False)
            if not os.path.exists(self.phase_files[phase]['periods']):
                pd.DataFrame(columns=['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'signal', 'returns', 'strategy_returns']).to_csv(self.phase_files[phase]['periods'], index=False)
        
        # Setup root logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        
        # Remove any existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Add file handler for the main log file
        main_log_file = os.path.join(self.run_timestamp_dir, "trading.log")
        file_handler = logging.FileHandler(main_log_file, mode='w')  # Use 'w' mode to overwrite
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Ensure all loggers propagate to root
        for name in logging.root.manager.loggerDict:
            logging.getLogger(name).propagate = True
        
        self.last_timestamp = None
        self.current_phase = 'train'  # Default phase
        
        # Log initialization
        self.logger.info("TradingLogger initialized with timestamp: %s", timestamp)
        self.logger.info("Log directory: %s", self.run_timestamp_dir)
        
    def set_phase(self, phase: str):
        """Set the current phase (train, val, or test)"""
        if phase not in ['train', 'val', 'test']:
            raise ValueError("Phase must be one of: train, val, test")
        self.current_phase = phase
        self.logger.info(f"Switched to {phase} phase")
        
        # Add phase-specific file handler
        phase_log_file = os.path.join(self.phase_dirs[phase], "logs", "trading.log")
        phase_handler = logging.FileHandler(phase_log_file, mode='w')  # Use 'w' mode to overwrite
        phase_handler.setLevel(logging.INFO)
        phase_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        phase_handler.setFormatter(phase_formatter)
        self.logger.addHandler(phase_handler)
        
        # Log phase switch
        self.logger.info("Phase-specific logging initialized for %s", phase)
        
    def log_trade(self, symbol: str, trade_type: str, price: float, shares: float, 
                 timestamp: datetime, profit: Optional[float] = None, 
                 portfolio_value: Optional[float] = None, cash: Optional[float] = None):
        """Log a trade with detailed information"""
        # Convert timestamp to string if it's a pandas Timestamp or datetime
        if hasattr(timestamp, 'isoformat'):
            ts_str = timestamp.isoformat()
        else:
            ts_str = str(timestamp)
            
        def safe_float(val):
            return float(val) if pd.notnull(val) else None
        def safe_int(val, default=0):
            return int(val) if pd.notnull(val) else default
            
        # Calculate profit for SELL trades if not provided
        if trade_type == 'SELL' and profit is None:
            # Read previous trades for this symbol to find the buy price
            trades_file = self.phase_files[self.current_phase]['trades']
            if os.path.exists(trades_file):
                trades_df = pd.read_csv(trades_file)
                symbol_trades = trades_df[trades_df['symbol'] == symbol]
                if not symbol_trades.empty:
                    # Find the last BUY trade for this symbol
                    buy_trades = symbol_trades[symbol_trades['trade_type'] == 'BUY']
                    if not buy_trades.empty:
                        last_buy = buy_trades.iloc[-1]
                        buy_price = last_buy['price']
                        buy_shares = last_buy['shares']
                        # Calculate profit based on the difference in price
                        profit = (price - buy_price) * min(shares, buy_shares)
        
        trade_data = {
            'symbol': symbol,
            'trade_type': trade_type,
            'price': safe_float(price),
            'shares': safe_int(shares),
            'timestamp': ts_str,
            'profit': safe_float(profit),
            'portfolio_value': safe_float(portfolio_value),
            'cash': safe_float(cash)
        }
        
        # Log to file
        self.logger.info(f"Trade: {json.dumps(trade_data)}")
        
        # Append to trades CSV for current phase
        pd.DataFrame([trade_data]).to_csv(self.phase_files[self.current_phase]['trades'], mode='a', header=False, index=False)
        
        # Append to ticker-specific trades CSV
        ticker_trades_file = os.path.join(self.phase_dirs[self.current_phase], "ticker", f"{symbol}_trades.csv")
        if not os.path.exists(ticker_trades_file):
            pd.DataFrame(columns=['symbol', 'trade_type', 'price', 'shares', 'timestamp', 'profit', 'portfolio_value', 'cash']).to_csv(ticker_trades_file, index=False)
        pd.DataFrame([trade_data]).to_csv(ticker_trades_file, mode='a', header=False, index=False)
        
    def log_period(self, symbol: str, timestamp: datetime, data: Dict):
        """Log period information (e.g., OHLCV, indicators, signals)"""
        # Convert timestamp to string if it's a pandas Timestamp or datetime
        if hasattr(timestamp, 'isoformat'):
            ts_str = timestamp.isoformat()
        else:
            ts_str = str(timestamp)
        def safe_float(val):
            return float(val) if pd.notnull(val) else None
        def safe_int(val, default=0):
            return int(val) if pd.notnull(val) else default
        period_data = {
            'symbol': symbol,
            'timestamp': ts_str,
            'open': safe_float(data.get('open')),
            'high': safe_float(data.get('high')),
            'low': safe_float(data.get('low')),
            'close': safe_float(data.get('close')),
            'volume': safe_int(data.get('volume'), default=0),
            'signal': safe_int(data.get('signal'), default=0),
            'returns': safe_float(data.get('returns')),
            'strategy_returns': safe_float(data.get('strategy_returns'))
        }
        
        # Log to file
        self.logger.info(f"Period: {json.dumps(period_data)}")
        
        # Append to periods CSV for current phase
        pd.DataFrame([period_data]).to_csv(self.phase_files[self.current_phase]['periods'], mode='a', header=False, index=False)
        
        # Append to ticker-specific periods CSV
        ticker_periods_file = os.path.join(self.phase_dirs[self.current_phase], "ticker", f"{symbol}_periods.csv")
        if not os.path.exists(ticker_periods_file):
            pd.DataFrame(columns=['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'signal', 'returns', 'strategy_returns']).to_csv(ticker_periods_file, index=False)
        pd.DataFrame([period_data]).to_csv(ticker_periods_file, mode='a', header=False, index=False)
        
    def plot_portfolio_performance(self, symbol: str, trades: pd.DataFrame):
        """Plot portfolio performance using trade data"""
        plt.figure(figsize=(12, 6))
        # Use portfolio_value from trades.csv
        plt.plot(pd.to_datetime(trades['timestamp']), trades['portfolio_value'])
        plt.title(f"Portfolio Performance - {symbol} ({self.current_phase})")
        plt.xlabel("Date")
        plt.ylabel("Portfolio Value ($)")
        plt.grid(True)
        plt.tight_layout()
        
        # Save plot in phase-specific visualizations directory
        plt.savefig(os.path.join(self.phase_dirs[self.current_phase], "visualizations", f"{symbol}_portfolio_performance.png"))
        plt.close()
        
    def plot_trade_distribution(self, symbol: str, trades: pd.DataFrame):
        """Plot trade distribution"""
        plt.figure(figsize=(10, 6))
        profit_col = 'profit'
        sns.histplot(data=trades, x=profit_col, bins=30)
        plt.title(f"Trade Profit Distribution - {symbol} ({self.current_phase})")
        plt.xlabel("Profit ($)")
        plt.ylabel("Count")
        plt.grid(True)
        plt.tight_layout()
        
        # Save plot in phase-specific visualizations directory
        plt.savefig(os.path.join(self.phase_dirs[self.current_phase], "visualizations", f"{symbol}_trade_distribution.png"))
        plt.close()
        
    def generate_performance_report(self, symbol: str, trades: pd.DataFrame) -> Dict:
        """Generate performance report using trade data"""
        profit_col = 'profit'
        pv_col = 'portfolio_value'
        
        if trades.empty:
            self.logger.warning(f"No trades were executed for {symbol} in the {self.current_phase} phase.")
            return {
                "symbol": symbol,
                "phase": self.current_phase,
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "total_profit": 0,
                "average_profit": 0,
                "max_profit": 0,
                "min_profit": 0,
                "final_portfolio_value": 0,
                "initial_portfolio_value": 0,
                "portfolio_return": 0,
                "generated_at": datetime.now().isoformat()
            }
        
        report = {
            "symbol": symbol,
            "phase": self.current_phase,
            "total_trades": len(trades),
            "winning_trades": len(trades[trades[profit_col] > 0]),
            "losing_trades": len(trades[trades[profit_col] < 0]),
            "win_rate": len(trades[trades[profit_col] > 0]) / len(trades) if len(trades) > 0 else 0,
            "total_profit": trades[profit_col].sum(),
            "average_profit": trades[profit_col].mean(),
            "max_profit": trades[profit_col].max(),
            "min_profit": trades[profit_col].min(),
            "final_portfolio_value": trades[pv_col].iloc[-1],
            "initial_portfolio_value": trades[pv_col].iloc[0],
            "portfolio_return": (trades[pv_col].iloc[-1] / trades[pv_col].iloc[0] - 1) * 100 if len(trades) > 0 else 0,
            "generated_at": datetime.now().isoformat()
        }
        
        # Save report in phase-specific directory
        report_file = os.path.join(self.phase_dirs[self.current_phase], f"{symbol}_performance_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=4)
        
        return report

    def publish_returns(self, returns_data: Dict[str, float]):
        """Publish returns for each stage in a file named 'returns.csv' in the run_<timestamp> folder."""
        returns_file = os.path.join(self.run_timestamp_dir, "returns.csv")
        df = pd.DataFrame([returns_data])
        df.to_csv(returns_file, index=False, mode='a', header=not os.path.exists(returns_file))
        self.logger.info(f"Returns published to {returns_file}")

    def plot_feature_importance(self, symbol: str, feature_importance: pd.DataFrame):
        """Plot feature importance for a symbol"""
        plt.figure(figsize=(12, 6))
        
        # Plot horizontal bar chart
        sns.barplot(data=feature_importance, x='importance', y='feature')
        plt.title(f"Feature Importance - {symbol} ({self.current_phase})")
        plt.xlabel("Importance Score")
        plt.ylabel("Features")
        plt.grid(True, axis='x')
        plt.tight_layout()
        
        # Save plot in phase-specific visualizations directory
        plt.savefig(os.path.join(self.phase_dirs[self.current_phase], "visualizations", f"{symbol}_feature_importance.png"))
        plt.close()
        
        # Also save the feature importance data as CSV
        feature_importance.to_csv(
            os.path.join(self.phase_dirs[self.current_phase], "visualizations", f"{symbol}_feature_importance.csv"),
            index=False
        ) 