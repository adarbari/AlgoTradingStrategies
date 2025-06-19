"""
Tests for the PolygonProvider retry logic and exponential backoff.
"""
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
import time

from src.data.providers.vendors.polygon.polygon_provider import (
    PolygonProvider, 
    PolygonRateLimitError, 
    PolygonAPIError
)
from src.data.types.data_config_types import OHLCVConfig
from src.data.types.base_types import TimeSeriesData


class TestPolygonProviderRetry(unittest.TestCase):
    def setUp(self):
        # Don't instantiate provider here - do it in each test after mocking
        self.symbol = "AAPL"
        self.start_time = datetime(2024, 1, 1)
        self.end_time = datetime(2024, 1, 10)
        self.config = OHLCVConfig(timeframe="1d")

    @patch("time.sleep", return_value=None)
    @patch("src.data.providers.vendors.polygon.polygon_provider.RESTClient")
    def test_retry_on_rate_limit_error(self, mock_rest, mock_sleep):
        """Test that the provider retries on rate limit errors."""
        # Set up mock client
        mock_client = MagicMock()
        mock_rest.return_value = mock_client
        
        # Create provider after mocking
        provider = PolygonProvider(api_key="test_key")
        
        # Mock the get_aggs method to raise rate limit error first, then succeed
        mock_client.get_aggs.side_effect = [
            PolygonRateLimitError("Rate limit exceeded"),
            MagicMock()  # Success on second call
        ]
        
        # This should retry and eventually succeed
        result = provider.get_data(
            self.symbol, 
            self.start_time, 
            self.end_time, 
            self.config
        )
        
        # Verify get_aggs was called twice (initial + retry)
        self.assertEqual(mock_client.get_aggs.call_count, 2)

    @patch("time.sleep", return_value=None)
    @patch("src.data.providers.vendors.polygon.polygon_provider.RESTClient")
    def test_retry_on_api_error(self, mock_rest, mock_sleep):
        """Test that the provider retries on API errors."""
        # Set up mock client
        mock_client = MagicMock()
        mock_rest.return_value = mock_client
        
        # Create provider after mocking
        provider = PolygonProvider(api_key="test_key")
        
        # Mock the get_aggs method to raise API error first, then succeed
        mock_client.get_aggs.side_effect = [
            PolygonAPIError("API error"),
            MagicMock()  # Success on second call
        ]
        
        # This should retry and eventually succeed
        result = provider.get_data(
            self.symbol, 
            self.start_time, 
            self.end_time, 
            self.config
        )
        
        # Verify get_aggs was called twice (initial + retry)
        self.assertEqual(mock_client.get_aggs.call_count, 2)

    @patch("time.sleep", return_value=None)
    @patch("src.data.providers.vendors.polygon.polygon_provider.RESTClient")
    def test_max_retries_exceeded(self, mock_rest, mock_sleep):
        """Test that the provider gives up after max retries."""
        # Set up mock client
        mock_client = MagicMock()
        mock_rest.return_value = mock_client
        
        # Create provider after mocking
        provider = PolygonProvider(api_key="test_key")
        
        # Mock the get_aggs method to always raise rate limit error
        mock_client.get_aggs.side_effect = PolygonRateLimitError("Rate limit exceeded")
        
        # This should fail after max retries
        with self.assertRaises(PolygonRateLimitError):
            provider.get_data(
                self.symbol, 
                self.start_time, 
                self.end_time, 
                self.config
            )
        
        # Verify get_aggs was called max_retries + 1 times
        self.assertEqual(mock_client.get_aggs.call_count, 6)  # 1 initial + 5 retries

    @patch("src.data.providers.vendors.polygon.polygon_provider.RESTClient")
    def test_successful_request_no_retry(self, mock_rest):
        """Test that successful requests don't trigger retries."""
        # Set up mock client
        mock_client = MagicMock()
        mock_rest.return_value = mock_client
        
        # Create provider after mocking
        provider = PolygonProvider(api_key="test_key")
        
        # Mock successful response
        mock_response = MagicMock()
        mock_client.get_aggs.return_value = mock_response
        
        # This should succeed without retries
        result = provider.get_data(
            self.symbol, 
            self.start_time, 
            self.end_time, 
            self.config
        )
        
        # Verify get_aggs was called only once
        self.assertEqual(mock_client.get_aggs.call_count, 1)

    def test_custom_exceptions(self):
        """Test that custom exceptions are properly defined."""
        # Test PolygonRateLimitError
        rate_limit_error = PolygonRateLimitError("Rate limit exceeded")
        self.assertIsInstance(rate_limit_error, Exception)
        self.assertEqual(str(rate_limit_error), "Rate limit exceeded")
        
        # Test PolygonAPIError
        api_error = PolygonAPIError("API error")
        self.assertIsInstance(api_error, Exception)
        self.assertEqual(str(api_error), "API error")


if __name__ == "__main__":
    unittest.main() 