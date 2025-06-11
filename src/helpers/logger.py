import logging
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional
import json

class TradingLogger:
    def __init__(self, run_dir: Optional[str] = None):
        self.run_dir = run_dir or os.path.join("logs", f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        self.last_timestamp = None
        
    def _setup_logging(self):
        """Setup logging directory and configuration"""
        os.makedirs(self.run_dir, exist_ok=True)
        os.makedirs(os.path.join(self.run_dir, "logs"), exist_ok=True)
        os.makedirs(os.path.join(self.run_dir, "visualizations"), exist_ok=True)
        
        # Setup logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.run_dir, "logs", "trading.log")),
                logging.StreamHandler()
            ]
        )
        
    def log_trade(self, symbol: str, trade_type: str, price: float, shares: float, 
                 timestamp: datetime, profit: Optional[float] = None):
        """Log a trade"""
        trade_info = {
            "symbol": symbol,
            "type": trade_type,
            "price": price,
            "shares": shares,
            "timestamp": timestamp.isoformat(),
            "profit": profit
        }
        
        # Log to file
        self.logger.info(f"Trade: {json.dumps(trade_info)}")
        
        # Append to trades CSV
        trades_file = os.path.join(self.run_dir, "logs", "trades.csv")
        trade_df = pd.DataFrame([trade_info])
        trade_df.to_csv(trades_file, mode='a', header=not os.path.exists(trades_file), index=False)
        
        # Ensure portfolio value is logged for this timestamp
        if self.last_timestamp != timestamp:
            self.last_timestamp = timestamp
            # Read the last portfolio value
            values_file = os.path.join(self.run_dir, "logs", "portfolio_values.csv")
            if os.path.exists(values_file):
                portfolio_values = pd.read_csv(values_file)
                if not portfolio_values.empty:
                    last_value = portfolio_values.iloc[-1]['portfolio_value']
                    self.log_portfolio_value(symbol, timestamp, last_value)
        
    def log_portfolio_value(self, symbol: str, timestamp: datetime, portfolio_value: float):
        """Log portfolio value"""
        value_info = {
            "symbol": symbol,
            "timestamp": timestamp.isoformat(),
            "portfolio_value": portfolio_value
        }
        
        # Log to file
        self.logger.info(f"Portfolio Value: {json.dumps(value_info)}")
        
        # Append to portfolio values CSV
        values_file = os.path.join(self.run_dir, "logs", "portfolio_values.csv")
        value_df = pd.DataFrame([value_info])
        value_df.to_csv(values_file, mode='a', header=not os.path.exists(values_file), index=False)
        
        self.last_timestamp = timestamp
        
    def plot_portfolio_performance(self, symbol: str, portfolio_values: pd.DataFrame):
        """Plot portfolio performance"""
        plt.figure(figsize=(12, 6))
        plt.plot(portfolio_values.index, portfolio_values['Portfolio_Value'])
        plt.title(f"Portfolio Performance - {symbol}")
        plt.xlabel("Date")
        plt.ylabel("Portfolio Value ($)")
        plt.grid(True)
        plt.tight_layout()
        
        # Save plot
        plt.savefig(os.path.join(self.run_dir, "visualizations", f"{symbol}_portfolio_performance.png"))
        plt.close()
        
    def plot_trade_distribution(self, symbol: str, trades: pd.DataFrame):
        """Plot trade distribution"""
        plt.figure(figsize=(10, 6))
        # Use the correct column for profit
        profit_col = 'Trade_Profit' if 'Trade_Profit' in trades.columns else 'profit'
        sns.histplot(data=trades, x=profit_col, bins=30)
        plt.title(f"Trade Profit Distribution - {symbol}")
        plt.xlabel("Profit ($)")
        plt.ylabel("Count")
        plt.grid(True)
        plt.tight_layout()
        
        # Save plot
        plt.savefig(os.path.join(self.run_dir, "visualizations", f"{symbol}_trade_distribution.png"))
        plt.close()
        
    def generate_performance_report(self, symbol: str, trades: pd.DataFrame, 
                                  portfolio_values: pd.DataFrame) -> Dict:
        """Generate performance report"""
        # Use the correct column for profit
        profit_col = 'Trade_Profit' if 'Trade_Profit' in trades.columns else 'profit'
        # Find the correct portfolio value column
        if 'portfolio_value' in portfolio_values.columns:
            pv_col = 'portfolio_value'
        elif 'Portfolio_Value' in portfolio_values.columns:
            pv_col = 'Portfolio_Value'
        else:
            print(f"[ERROR] Portfolio values columns: {portfolio_values.columns.tolist()}")
            raise KeyError("'portfolio_value' column not found in portfolio_values DataFrame. Available columns: " + str(portfolio_values.columns.tolist()))
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
            "portfolio_return": (portfolio_values[pv_col].iloc[-1] / portfolio_values[pv_col].iloc[0] - 1) * 100 if portfolio_values.shape[0] > 1 else 0
        }
        
        # Save report
        report_file = os.path.join(self.run_dir, "logs", f"{symbol}_performance_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=4)
        
        return report 