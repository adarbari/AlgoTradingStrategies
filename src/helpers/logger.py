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
    def __init__(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_timestamp_dir = os.path.join(os.getcwd(), "logs", f"run_{timestamp}")
        os.makedirs(self.run_timestamp_dir, exist_ok=True)
        # Initialize log files under the timestamped directory
        self.trades_file = os.path.join(self.run_timestamp_dir, "trades.csv")
        self.periods_file = os.path.join(self.run_timestamp_dir, "periods.csv")
        self.portfolio_file = os.path.join(self.run_timestamp_dir, "portfolio_values.csv")
        # Create headers if files don't exist
        if not os.path.exists(self.trades_file):
            pd.DataFrame(columns=['symbol', 'trade_type', 'price', 'shares', 'timestamp', 'profit', 'portfolio_value']).to_csv(self.trades_file, index=False)
        if not os.path.exists(self.periods_file):
            pd.DataFrame(columns=['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'signal', 'returns', 'strategy_returns']).to_csv(self.periods_file, index=False)
        if not os.path.exists(self.portfolio_file):
            pd.DataFrame(columns=['symbol', 'timestamp', 'portfolio_value']).to_csv(self.portfolio_file, index=False)
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        self.last_timestamp = None
        
    def _setup_logging(self):
        """Setup logging directory and configuration"""
        os.makedirs(self.run_timestamp_dir, exist_ok=True)
        os.makedirs(os.path.join(self.run_timestamp_dir, "logs"), exist_ok=True)
        os.makedirs(os.path.join(self.run_timestamp_dir, "visualizations"), exist_ok=True)
        
        # Setup logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.run_timestamp_dir, "logs", "trading.log")),
                logging.StreamHandler()
            ]
        )
        
    def log_trade(self, symbol: str, trade_type: str, price: float, shares: float, 
                 timestamp: datetime, profit: Optional[float] = None, 
                 portfolio_value: Optional[float] = None):
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
        trade_data = {
            'symbol': symbol,
            'trade_type': trade_type,
            'price': safe_float(price),
            'shares': safe_int(shares),
            'timestamp': ts_str,
            'profit': safe_float(profit),
            'portfolio_value': safe_float(portfolio_value)
        }
        
        # Log to file
        self.logger.info(f"Trade: {json.dumps(trade_data)}")
        
        # Append to trades CSV
        pd.DataFrame([trade_data]).to_csv(self.trades_file, mode='a', header=False, index=False)
        
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
        
        # Append to periods CSV
        pd.DataFrame([period_data]).to_csv(self.periods_file, mode='a', header=False, index=False)
        
    def log_portfolio_value(self, symbol: str, timestamp: datetime, portfolio_value: float):
        """Log portfolio value"""
        # Convert timestamp to string if it's a pandas Timestamp or datetime
        if hasattr(timestamp, 'isoformat'):
            ts_str = timestamp.isoformat()
        else:
            ts_str = str(timestamp)
        def safe_float(val):
            return float(val) if pd.notnull(val) else None
        portfolio_data = {
            'symbol': symbol,
            'timestamp': ts_str,
            'portfolio_value': safe_float(portfolio_value)
        }
        
        # Log to file
        self.logger.info(f"Portfolio Value: {json.dumps(portfolio_data)}")
        
        # Append to portfolio values CSV
        pd.DataFrame([portfolio_data]).to_csv(self.portfolio_file, mode='a', header=False, index=False)
        
        self.last_timestamp = timestamp
        
    def plot_portfolio_performance(self, symbol: str, portfolio_values: pd.DataFrame):
        """Plot portfolio performance"""
        plt.figure(figsize=(12, 6))
        plt.plot(portfolio_values.index, portfolio_values['portfolio_value'])
        plt.title(f"Portfolio Performance - {symbol}")
        plt.xlabel("Date")
        plt.ylabel("Portfolio Value ($)")
        plt.grid(True)
        plt.tight_layout()
        
        # Save plot
        plt.savefig(os.path.join(self.run_timestamp_dir, f"{symbol}_portfolio_performance.png"))
        plt.close()
        
    def plot_trade_distribution(self, symbol: str, trades: pd.DataFrame):
        """Plot trade distribution"""
        plt.figure(figsize=(10, 6))
        profit_col = 'profit'
        sns.histplot(data=trades, x=profit_col, bins=30)
        plt.title(f"Trade Profit Distribution - {symbol}")
        plt.xlabel("Profit ($)")
        plt.ylabel("Count")
        plt.grid(True)
        plt.tight_layout()
        
        # Save plot
        plt.savefig(os.path.join(self.run_timestamp_dir, f"{symbol}_trade_distribution.png"))
        plt.close()
        
    def generate_performance_report(self, symbol: str, trades: pd.DataFrame, 
                                  portfolio_values: pd.DataFrame) -> Dict:
        """Generate performance report"""
        profit_col = 'profit'
        pv_col = 'portfolio_value'
        
        report = {
            "symbol": symbol,
            "total_trades": len(trades),
            "winning_trades": len(trades[trades[profit_col] > 0]),
            "losing_trades": len(trades[trades[profit_col] < 0]),
            "win_rate": len(trades[trades[profit_col] > 0]) / len(trades) if len(trades) > 0 else 0,
            "total_profit": trades[profit_col].sum(),
            "average_profit": trades[profit_col].mean(),
            "max_profit": trades[profit_col].max(),
            "min_profit": trades[profit_col].min(),
            "final_portfolio_value": portfolio_values[pv_col].iloc[-1],
            "initial_portfolio_value": portfolio_values[pv_col].iloc[0],
            "portfolio_return": (portfolio_values[pv_col].iloc[-1] / portfolio_values[pv_col].iloc[0] - 1) * 100 if portfolio_values.shape[0] > 1 else 0,
            "generated_at": datetime.now().isoformat()
        }
        
        # Save report
        report_file = os.path.join(self.run_timestamp_dir, f"{symbol}_performance_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=4)
        
        return report 