import unittest
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from src.run_trading_system import TradingSystem

class TestTradingSystem(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.symbols = ['AAPL', 'MSFT']
        self.start_date = datetime(2023, 1, 1)
        self.end_date = datetime(2023, 12, 31)
        self.initial_budget = 10000.0
        
    def test_initialization(self):
        """Test TradingSystem initialization with different split ratios."""
        # Test default split ratios
        system = TradingSystem(
            symbols=self.symbols,
            initial_budget=self.initial_budget,
            start_date=self.start_date,
            end_date=self.end_date
        )
        self.assertEqual(system.split_manager.train_ratio, 0.6)
        self.assertEqual(system.split_manager.val_ratio, 0.2)
        self.assertEqual(system.split_manager.test_ratio, 0.2)
        
        # Test custom split ratios
        custom_ratios = {'train': 0.7, 'val': 0.15, 'test': 0.15}
        system = TradingSystem(
            symbols=self.symbols,
            initial_budget=self.initial_budget,
            start_date=self.start_date,
            end_date=self.end_date,
            split_ratios=custom_ratios
        )
        self.assertEqual(system.split_manager.train_ratio, 0.7)
        self.assertEqual(system.split_manager.val_ratio, 0.15)
        self.assertEqual(system.split_manager.test_ratio, 0.15)
        
    def test_split_dates(self):
        """Test that split dates are correctly calculated and ordered."""
        system = TradingSystem(
            symbols=self.symbols,
            initial_budget=self.initial_budget,
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        # Verify split dates exist and are ordered
        self.assertIn('train_start', system.split_dates)
        self.assertIn('train_end', system.split_dates)
        self.assertIn('val_end', system.split_dates)
        self.assertIn('test_end', system.split_dates)
        
        # Verify date ordering
        self.assertEqual(system.split_dates['train_start'], self.start_date)
        self.assertLess(system.split_dates['train_end'], system.split_dates['val_end'])
        self.assertLess(system.split_dates['val_end'], system.split_dates['test_end'])
        self.assertEqual(system.split_dates['test_end'], self.end_date)
        
    def test_get_data_for_split(self):
        """Test that data is correctly split and no overlap exists."""
        system = TradingSystem(
            symbols=self.symbols,
            initial_budget=self.initial_budget,
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        # Get data for each split
        train_data = system.get_data_for_split('train')
        val_data = system.get_data_for_split('val')
        test_data = system.get_data_for_split('test')
        
        # Verify each split has data
        self.assertTrue(all(len(data) > 0 for data in train_data.values()))
        self.assertTrue(all(len(data) > 0 for data in val_data.values()))
        self.assertTrue(all(len(data) > 0 for data in test_data.values()))
        
        # Verify no overlap between splits
        for symbol in self.symbols:
            train_dates = set(train_data[symbol].index)
            val_dates = set(val_data[symbol].index)
            test_dates = set(test_data[symbol].index)
            
            self.assertTrue(train_dates.isdisjoint(val_dates))
            self.assertTrue(val_dates.isdisjoint(test_dates))
            self.assertTrue(train_dates.isdisjoint(test_dates))
            
    def test_run_splits(self):
        """Test running the trading system on each split."""
        system = TradingSystem(
            symbols=self.symbols,
            initial_budget=self.initial_budget,
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        # Run on each split
        for split_name in ['train', 'val', 'test']:
            system.run(split_name)
            results = system.get_results()
            
            # Verify results exist
            self.assertIn('final_value', results)
            self.assertIn('return_pct', results)
            self.assertIn('num_trades', results)
            self.assertIn('positions', results)
            
            # Verify portfolio value is non-negative
            self.assertGreaterEqual(results['final_value'], 0)
            
            # Verify we have some trading activity
            self.assertGreaterEqual(results['num_trades'], 0)
            
    def test_minimum_training_period(self):
        """Test that minimum training period is enforced."""
        # Try with insufficient data
        short_end_date = self.start_date + timedelta(days=20)  # Less than min_train_days
        with self.assertRaises(ValueError):
            TradingSystem(
                symbols=self.symbols,
                initial_budget=self.initial_budget,
                start_date=self.start_date,
                end_date=short_end_date,
                min_train_days=30
            )
            
        # Try with sufficient data
        long_end_date = self.start_date + timedelta(days=100)  # More than min_train_days
        system = TradingSystem(
            symbols=self.symbols,
            initial_budget=self.initial_budget,
            start_date=self.start_date,
            end_date=long_end_date,
            min_train_days=30
        )
        train_days = (system.split_dates['train_end'] - system.split_dates['train_start']).days
        self.assertGreaterEqual(train_days, 30)

if __name__ == '__main__':
    unittest.main() 