"""
Tests for the retry utility functions.
"""
import unittest
import time
from unittest.mock import patch, MagicMock

from src.utils.retry_utils import (
    exponential_backoff_retry,
    RetryConfig,
    retry_with_config,
    RATE_LIMIT_RETRY_CONFIG,
    NETWORK_RETRY_CONFIG
)


class TestRetryUtils(unittest.TestCase):
    
    def test_retry_config_initialization(self):
        """Test RetryConfig initialization with default values."""
        config = RetryConfig()
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.base_delay, 1.0)
        self.assertEqual(config.max_delay, 60.0)
        self.assertEqual(config.exponential_base, 2.0)
        self.assertTrue(config.jitter)
        self.assertEqual(config.retry_on_exceptions, [Exception])
    
    def test_retry_config_custom_values(self):
        """Test RetryConfig initialization with custom values."""
        config = RetryConfig(
            max_retries=5,
            base_delay=2.0,
            max_delay=120.0,
            exponential_base=3.0,
            jitter=False,
            retry_on_exceptions=[ValueError, TypeError]
        )
        self.assertEqual(config.max_retries, 5)
        self.assertEqual(config.base_delay, 2.0)
        self.assertEqual(config.max_delay, 120.0)
        self.assertEqual(config.exponential_base, 3.0)
        self.assertFalse(config.jitter)
        self.assertEqual(config.retry_on_exceptions, [ValueError, TypeError])

    def test_exponential_backoff_retry_success_first_try(self):
        """Test that successful function calls don't retry."""
        @exponential_backoff_retry(max_retries=3, base_delay=0.1)
        def successful_function():
            return "success"
        
        start_time = time.time()
        result = successful_function()
        end_time = time.time()
        
        self.assertEqual(result, "success")
        # Should complete quickly (no retries)
        self.assertLess(end_time - start_time, 0.1)

    def test_exponential_backoff_retry_success_after_failures(self):
        """Test that function succeeds after some failures."""
        call_count = 0
        
        @exponential_backoff_retry(max_retries=3, base_delay=0.1)
        def failing_then_successful():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        start_time = time.time()
        result = failing_then_successful()
        end_time = time.time()
        
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)
        # Should take some time due to retries
        self.assertGreater(end_time - start_time, 0.2)

    def test_exponential_backoff_retry_max_retries_exceeded(self):
        """Test that function gives up after max retries."""
        call_count = 0
        
        @exponential_backoff_retry(max_retries=2, base_delay=0.1)
        def always_failing():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        with self.assertRaises(ValueError):
            always_failing()
        
        # Should have been called 3 times (2 retries + 1 initial attempt)
        self.assertEqual(call_count, 3)

    def test_exponential_backoff_retry_with_jitter(self):
        """Test that jitter is applied to delays."""
        call_count = 0
        
        @exponential_backoff_retry(max_retries=2, base_delay=1.0, jitter=True)
        def failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Fails")
        
        start_time = time.time()
        with self.assertRaises(ValueError):
            failing_function()
        end_time = time.time()
        
        # Should have taken some time due to delays with jitter
        # Base delay is 1s, so with jitter it should be 0.5-1.0s per retry
        self.assertGreater(end_time - start_time, 1.0)

    def test_exponential_backoff_retry_without_jitter(self):
        """Test that delays are exact when jitter is disabled."""
        call_count = 0
        
        @exponential_backoff_retry(max_retries=1, base_delay=0.5, jitter=False)
        def failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Fails")
        
        start_time = time.time()
        with self.assertRaises(ValueError):
            failing_function()
        end_time = time.time()
        
        # Should have taken approximately 0.5 seconds (base delay)
        # Allow some tolerance for system timing
        self.assertGreater(end_time - start_time, 0.4)
        self.assertLess(end_time - start_time, 0.6)

    def test_exponential_backoff_retry_specific_exceptions(self):
        """Test that only specified exceptions trigger retries."""
        call_count = 0
        
        @exponential_backoff_retry(
            max_retries=2, 
            base_delay=0.1, 
            retry_on_exceptions=[ValueError]
        )
        def function_with_different_exceptions():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("ValueError - should retry")
            elif call_count == 2:
                raise TypeError("TypeError - should not retry")
            return "success"
        
        # Should not retry on TypeError, so it should be raised immediately
        with self.assertRaises(TypeError):
            function_with_different_exceptions()
        
        # Should have been called only 2 times (1 ValueError + 1 TypeError)
        self.assertEqual(call_count, 2)

    def test_retry_with_config(self):
        """Test retry_with_config decorator."""
        call_count = 0
        
        config = RetryConfig(max_retries=2, base_delay=0.1)
        
        @retry_with_config(config)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Fails")
            return "success"
        
        result = failing_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)

    def test_rate_limit_retry_config(self):
        """Test predefined rate limit retry configuration."""
        self.assertEqual(RATE_LIMIT_RETRY_CONFIG.max_retries, 5)
        self.assertEqual(RATE_LIMIT_RETRY_CONFIG.base_delay, 2.0)
        self.assertEqual(RATE_LIMIT_RETRY_CONFIG.max_delay, 120.0)
        self.assertTrue(RATE_LIMIT_RETRY_CONFIG.jitter)

    def test_network_retry_config(self):
        """Test predefined network retry configuration."""
        self.assertEqual(NETWORK_RETRY_CONFIG.max_retries, 3)
        self.assertEqual(NETWORK_RETRY_CONFIG.base_delay, 1.0)
        self.assertEqual(NETWORK_RETRY_CONFIG.max_delay, 30.0)
        self.assertTrue(NETWORK_RETRY_CONFIG.jitter)

    def test_exponential_backoff_calculation(self):
        """Test that exponential backoff delays increase correctly."""
        call_count = 0
        delays = []
        
        original_sleep = time.sleep
        
        def mock_sleep(delay):
            delays.append(delay)
            original_sleep(0)  # Don't actually sleep during test
        
        @exponential_backoff_retry(max_retries=3, base_delay=1.0, jitter=False)
        def failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Fails")
        
        with patch('time.sleep', side_effect=mock_sleep):
            with self.assertRaises(ValueError):
                failing_function()
        
        # Should have been called 4 times (3 retries + 1 initial attempt)
        self.assertEqual(call_count, 4)
        
        # Delays should follow exponential pattern: 1, 2, 4 (capped by max_delay)
        self.assertEqual(len(delays), 3)
        self.assertEqual(delays[0], 1.0)  # First retry
        self.assertEqual(delays[1], 2.0)  # Second retry
        self.assertEqual(delays[2], 4.0)  # Third retry

    def test_max_delay_capping(self):
        """Test that delays are capped by max_delay."""
        call_count = 0
        delays = []
        
        original_sleep = time.sleep
        
        def mock_sleep(delay):
            delays.append(delay)
            original_sleep(0)  # Don't actually sleep during test
        
        @exponential_backoff_retry(max_retries=3, base_delay=10.0, max_delay=25.0, jitter=False)
        def failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Fails")
        
        with patch('time.sleep', side_effect=mock_sleep):
            with self.assertRaises(ValueError):
                failing_function()
        
        # Delays should be capped: 10, 20, 25 (capped)
        self.assertEqual(len(delays), 3)
        self.assertEqual(delays[0], 10.0)  # First retry
        self.assertEqual(delays[1], 20.0)  # Second retry
        self.assertEqual(delays[2], 25.0)  # Third retry (capped)


if __name__ == '__main__':
    unittest.main() 