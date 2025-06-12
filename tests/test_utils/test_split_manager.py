import unittest
from datetime import datetime, timedelta
from src.utils.split_manager import SplitManager

class TestSplitManager(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.start_date = datetime(2023, 1, 1)
        self.end_date = datetime(2023, 12, 31)
        
    def test_initialization(self):
        """Test initialization with valid and invalid ratios."""
        # Test valid initialization
        split_manager = SplitManager(
            train_ratio=0.6,
            val_ratio=0.2,
            test_ratio=0.2
        )
        self.assertEqual(split_manager.train_ratio, 0.6)
        self.assertEqual(split_manager.val_ratio, 0.2)
        self.assertEqual(split_manager.test_ratio, 0.2)
        
        # Test invalid ratios
        with self.assertRaises(ValueError):
            SplitManager(train_ratio=1.2, val_ratio=0.2, test_ratio=0.2)
            
        with self.assertRaises(ValueError):
            SplitManager(train_ratio=0.6, val_ratio=0.6, test_ratio=0.2)
            
    def test_get_split_dates(self):
        """Test split date calculation."""
        split_manager = SplitManager()
        split_dates = split_manager.get_split_dates(self.start_date, self.end_date)
        
        # Test all dates are present
        self.assertIn('train_start', split_dates)
        self.assertIn('train_end', split_dates)
        self.assertIn('val_end', split_dates)
        self.assertIn('test_end', split_dates)
        
        # Test date ordering
        self.assertEqual(split_dates['train_start'], self.start_date)
        self.assertLess(split_dates['train_end'], split_dates['val_end'])
        self.assertLess(split_dates['val_end'], split_dates['test_end'])
        self.assertEqual(split_dates['test_end'], self.end_date)
        
        # Test split durations
        train_days = (split_dates['train_end'] - split_dates['train_start']).days
        val_days = (split_dates['val_end'] - split_dates['train_end']).days
        test_days = (split_dates['test_end'] - split_dates['val_end']).days
        total_days = (self.end_date - self.start_date).days
        
        # Allow for small rounding differences
        self.assertAlmostEqual(train_days / total_days, 0.6, delta=0.01)
        self.assertAlmostEqual(val_days / total_days, 0.2, delta=0.01)
        self.assertAlmostEqual(test_days / total_days, 0.2, delta=0.01)
        
    def test_minimum_training_period(self):
        """Test minimum training period validation."""
        # Test with sufficient data
        split_manager = SplitManager(min_train_days=30)
        split_dates = split_manager.get_split_dates(self.start_date, self.end_date)
        train_days = (split_dates['train_end'] - split_dates['train_start']).days
        self.assertGreaterEqual(train_days, 30)
        
        # Test with insufficient data
        short_end_date = self.start_date + timedelta(days=20)
        with self.assertRaises(ValueError):
            split_manager.get_split_dates(self.start_date, short_end_date)

if __name__ == '__main__':
    unittest.main() 