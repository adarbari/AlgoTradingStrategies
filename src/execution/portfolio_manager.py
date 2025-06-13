"""
Enhanced portfolio manager with comprehensive metrics tracking.
"""

from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
from .metrics.daily_metrics import DailyMetrics
from .metrics.cumulative_metrics import CumulativeMetrics
from .metrics.metrics_calculator import MetricsCalculator

class PortfolioManager:
    """Manages portfolio positions and tracks performance metrics."""
    
    def __init__(self, initial_capital: float = None, initial_budget: float = None):
        """Initialize the portfolio manager."""
        if initial_capital is not None:
            self.initial_capital = initial_capital
        elif initial_budget is not None:
            self.initial_capital = initial_budget
        else:
            self.initial_capital = 100000.0
        self.cash = self.initial_capital
        self.positions = {}
        self.trades = []
        self.daily_metrics = []
        self.cumulative_metrics = None
        self.metrics_calculator = MetricsCalculator(0.02)
        
    @property
    def trade_history(self) -> pd.DataFrame:
        """Return trade history as a DataFrame."""
        if not self.trades:
            return pd.DataFrame(columns=['timestamp', 'symbol', 'action', 'quantity', 'price', 'total'])
            
        df = pd.DataFrame(self.trades)
        df['action'] = df['quantity'].apply(lambda x: 'BUY' if x > 0 else 'SELL')
        df['total'] = df['quantity'] * df['price']
        return df[['timestamp', 'symbol', 'action', 'quantity', 'price', 'total']]

    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate the total portfolio value."""
        positions_value = sum(
            self.positions[symbol]['quantity'] * current_prices[symbol]
            for symbol in self.positions
        )
        return self.cash + positions_value

    def get_portfolio_summary(self, current_prices: Dict[str, float]) -> Dict:
        """Get a summary of the portfolio state."""
        positions_value = sum(
            self.positions[symbol]['quantity'] * current_prices[symbol]
            for symbol in self.positions
        )
        total_value = self.cash + positions_value
        return_pct = (total_value - self.initial_capital) / self.initial_capital
        return {
            'cash': self.cash,
            'positions': self.positions,
            'positions_value': positions_value,
            'total_value': total_value,
            'return_pct': return_pct,
            'num_positions': len(self.positions),
            'total_trades': len(self.trades),
            'open_trades': sum(1 for trade in self.trades if not trade['is_closed']),
            'closed_trades': sum(1 for trade in self.trades if trade['is_closed'])
        }

    def update_position(self, symbol: str, quantity: int, price: float, timestamp: datetime) -> bool:
        """Update a position in the portfolio."""
        if quantity > 0:  # Buying
            cost = quantity * price
            if self.cash < cost:
                return False  # Not enough cash
            self.cash -= cost
            if symbol in self.positions:
                pos = self.positions[symbol]
                total_quantity = pos['quantity'] + quantity
                pos['avg_price'] = (pos['quantity'] * pos['avg_price'] + quantity * price) / total_quantity
                pos['quantity'] = total_quantity
            else:
                self.positions[symbol] = {'quantity': quantity, 'avg_price': price}
        else:  # Selling
            if symbol not in self.positions or self.positions[symbol]['quantity'] < abs(quantity):
                return False  # Not enough shares to sell
            self.cash += abs(quantity) * price
            self.positions[symbol]['quantity'] += quantity  # quantity is negative
            if self.positions[symbol]['quantity'] == 0:
                del self.positions[symbol]
        # Record trade
        self.trades.append({
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'timestamp': timestamp,
            'is_closed': False,
            'pnl': 0.0
        })
        return True
        
    def close_position(self, symbol: str, price: float, timestamp: datetime) -> None:
        """Close a position and record the trade."""
        if symbol not in self.positions:
            return
        position = self.positions[symbol]
        quantity = position['quantity']
        avg_price = position['avg_price']
        # Calculate P&L
        pnl = quantity * (price - avg_price)
        self.cash += quantity * price
        # Mark trade as closed
        for trade in self.trades:
            if trade['symbol'] == symbol and not trade['is_closed']:
                trade['is_closed'] = True
                trade['pnl'] = pnl
                break
        # Remove position
        del self.positions[symbol]
        
    def update_prices(self, current_prices: Dict[str, float]) -> None:
        """Update current prices for positions without recalculating metrics.
        
        This method should be called at each timestamp to update position values.
        Metrics should be updated separately using update_metrics().
        
        Args:
            current_prices: Dictionary of current prices by symbol
        """
        # Update position values (market value) without changing average prices
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                position['current_price'] = current_prices[symbol]
                position['market_value'] = position['quantity'] * current_prices[symbol]
                
    def update_metrics(self, timestamp: datetime) -> None:
        """Update portfolio metrics for the current timestamp.
        
        This method should be called after trades are processed for a timestamp
        to update daily and cumulative metrics.
        
        Args:
            timestamp: Current timestamp
        """
        # Get current prices from positions
        current_prices = {
            symbol: position.get('current_price', position['avg_price'])
            for symbol, position in self.positions.items()
        }
        
        # Update daily metrics if it's a new day
        if not self.daily_metrics or self.daily_metrics[-1].date.date() != timestamp.date():
            self.update_daily_metrics(timestamp, current_prices)
            
        # Update cumulative metrics
        self.cumulative_metrics = self.get_cumulative_metrics()
        
    def update_daily_metrics(self, date: datetime, current_prices: Dict[str, float]) -> None:
        """Update daily performance metrics.
        
        Args:
            date: Current date
            current_prices: Current prices for each symbol
        """
        portfolio_value = self.get_portfolio_value(current_prices)
        previous_portfolio_value = self.daily_metrics[-1].portfolio_value if self.daily_metrics else None
        metrics = self.metrics_calculator.calculate_daily_metrics(
            date=date,
            portfolio_value=portfolio_value,
            cash=self.cash,
            positions=self.positions,
            trades=self.trades,
            previous_portfolio_value=previous_portfolio_value,
            current_prices=current_prices
        )
        self.daily_metrics.append(metrics)
        # Update cumulative metrics
        self.cumulative_metrics = self.metrics_calculator.calculate_cumulative_metrics(
            daily_metrics=self.daily_metrics,
            initial_capital=self.initial_capital,
            trades=self.trades
        )
        
    def get_cumulative_metrics(self) -> CumulativeMetrics:
        """Get cumulative performance metrics.
        
        Returns:
            CumulativeMetrics object
        """
        return self.metrics_calculator.calculate_cumulative_metrics(self.daily_metrics, self.initial_capital, self.trades)
        
    def get_daily_metrics_df(self) -> pd.DataFrame:
        """Get daily metrics as a DataFrame.
        
        Returns:
            DataFrame with daily metrics
        """
        return pd.DataFrame([m.to_dict() for m in self.daily_metrics])
        
    def get_current_metrics(self) -> Dict:
        """Get current portfolio metrics including both daily and cumulative metrics.
        
        Returns:
            Dictionary containing:
            - daily_metrics: Latest daily metrics
            - cumulative_metrics: Current cumulative metrics
            - portfolio_value: Current total portfolio value
            - positions: Current positions with their values
        """
        # Get latest daily metrics
        latest_daily = self.daily_metrics[-1] if self.daily_metrics else None
        
        # Get current positions with their values
        current_positions = {
            symbol: {
                'quantity': pos['quantity'],
                'avg_price': pos['avg_price'],
                'current_price': pos.get('current_price', pos['avg_price']),
                'market_value': pos.get('market_value', pos['quantity'] * pos['avg_price']),
                'unrealized_pnl': pos.get('market_value', pos['quantity'] * pos['avg_price']) - (pos['quantity'] * pos['avg_price'])
            }
            for symbol, pos in self.positions.items()
        }
        
        return {
            'daily_metrics': latest_daily.to_dict() if latest_daily else None,
            'cumulative_metrics': self.cumulative_metrics.to_dict() if self.cumulative_metrics else None,
            'portfolio_value': self.get_portfolio_value({symbol: pos.get('current_price', pos['avg_price']) for symbol, pos in self.positions.items()}),
            'positions': current_positions,
            'cash': self.cash
        }

    def get_trade_history(self) -> pd.DataFrame:
        """Get the trade history as a DataFrame."""
        return pd.DataFrame(self.trades, columns=['timestamp', 'symbol', 'action', 'quantity', 'price', 'total']) 