"""
Tests for the RithmicProvider implementation.
"""
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
from src.data.providers.vendors.rithmic.rithmic_provider import (
    RithmicProvider, 
    RithmicConnectionError, 
    RithmicAuthenticationError,
    RithmicDataError
)
from src.data.types.data_config_types import OrderFlowConfig
from src.data.types.base_types import TimeSeriesData

class TestRithmicProvider(unittest.TestCase):
    def setUp(self):
        self.provider = RithmicProvider(
            uri="wss://test.rithmic.com:443",
            system_name="test_system",
            user_id="test_user",
            password="test_password"
        )
        self.symbol = "CME:ES"
        self.start_time = datetime(2024, 1, 1)
        self.end_time = datetime(2024, 1, 10)
        self.config = OrderFlowConfig()

    def test_init_with_params(self):
        """Test initialization with parameters."""
        self.assertEqual(self.provider.uri, "wss://test.rithmic.com:443")
        self.assertEqual(self.provider.system_name, "test_system")
        self.assertEqual(self.provider.user_id, "test_user")
        self.assertEqual(self.provider.password, "test_password")

    def test_init_with_env_vars(self):
        """Test initialization with environment variables."""
        with patch.dict('os.environ', {
            'RITHMIC_URI': 'wss://env.rithmic.com:443',
            'RITHMIC_SYSTEM_NAME': 'env_system',
            'RITHMIC_USER_ID': 'env_user',
            'RITHMIC_PASSWORD': 'env_password'
        }):
            provider = RithmicProvider()
            self.assertEqual(provider.uri, 'wss://env.rithmic.com:443')
            self.assertEqual(provider.system_name, 'env_system')
            self.assertEqual(provider.user_id, 'env_user')
            self.assertEqual(provider.password, 'env_password')

    def test_parse_symbol(self):
        """Test symbol parsing functionality."""
        # Test symbol with exchange
        exchange, symbol = self.provider._parse_symbol("CME:ES")
        self.assertEqual(exchange, "CME")
        self.assertEqual(symbol, "ES")
        
        # Test symbol without exchange (defaults to CME)
        exchange, symbol = self.provider._parse_symbol("ES")
        self.assertEqual(exchange, "CME")
        self.assertEqual(symbol, "ES")

    @patch('src.data.providers.vendors.rithmic.rithmic_provider.HistoricalTickBarProvider')
    def test_get_data_success(self, mock_provider_class):
        """Test successful data retrieval."""
        # Mock the tick bar provider
        mock_provider = MagicMock()
        mock_provider_class.return_value = mock_provider
        
        # Create provider with mocked tick bar provider
        provider = RithmicProvider(
            uri="wss://test.rithmic.com:443",
            system_name="test_system",
            user_id="test_user",
            password="test_password"
        )
        
        # Test get_data
        result = provider.get_data(self.symbol, self.start_time, self.end_time, self.config)
        
        # Verify the result is a TimeSeriesData object
        self.assertIsInstance(result, TimeSeriesData)
        
        # Verify the tick bar provider was called with correct parameters
        mock_provider.get_historical_data.assert_called_once_with(
            uri="wss://test.rithmic.com:443",
            system_name="test_system",
            user_id="test_user",
            password="test_password",
            exchange="CME",
            symbol="ES"
        )

    def test_get_data_missing_credentials(self):
        """Test error handling for missing credentials."""
        provider = RithmicProvider(uri="wss://test.rithmic.com:443")
        
        with self.assertRaises(RithmicAuthenticationError):
            provider.get_data(self.symbol, self.start_time, self.end_time, self.config)

    @patch('src.data.providers.vendors.rithmic.rithmic_provider.HistoricalTickBarProvider')
    def test_get_data_connection_error(self, mock_provider_class):
        """Test handling of connection errors."""
        # Mock the tick bar provider to raise connection error
        mock_provider = MagicMock()
        mock_provider.get_historical_data.side_effect = Exception("connection failed")
        mock_provider_class.return_value = mock_provider
        
        provider = RithmicProvider(
            uri="wss://test.rithmic.com:443",
            system_name="test_system",
            user_id="test_user",
            password="test_password"
        )
        
        with self.assertRaises(RithmicConnectionError):
            provider.get_data(self.symbol, self.start_time, self.end_time, self.config)

    @patch('src.data.providers.vendors.rithmic.rithmic_provider.HistoricalTickBarProvider')
    def test_get_data_auth_error(self, mock_provider_class):
        """Test handling of authentication errors."""
        # Mock the tick bar provider to raise login error
        mock_provider = MagicMock()
        mock_provider.get_historical_data.side_effect = Exception("login failed")
        mock_provider_class.return_value = mock_provider
        
        provider = RithmicProvider(
            uri="wss://test.rithmic.com:443",
            system_name="test_system",
            user_id="test_user",
            password="test_password"
        )
        
        with self.assertRaises(RithmicAuthenticationError):
            provider.get_data(self.symbol, self.start_time, self.end_time, self.config)

    @patch('src.data.providers.vendors.rithmic.rithmic_provider.HistoricalTickBarProvider')
    def test_list_available_systems(self, mock_provider_class):
        """Test listing available systems."""
        mock_provider = MagicMock()
        mock_provider_class.return_value = mock_provider
        
        provider = RithmicProvider(uri="wss://test.rithmic.com:443")
        
        # This should not raise an exception
        provider.list_available_systems()
        
        # Verify the tick bar provider was called
        mock_provider.get_historical_data.assert_called_once_with(uri="wss://test.rithmic.com:443")

    @patch('src.data.providers.vendors.rithmic.rithmic_provider.HistoricalTickBarProvider')
    def test_test_connection_success(self, mock_provider_class):
        """Test successful connection test."""
        mock_provider = MagicMock()
        mock_provider_class.return_value = mock_provider
        
        provider = RithmicProvider(uri="wss://test.rithmic.com:443")
        
        result = provider.test_connection()
        self.assertTrue(result)

    @patch('src.data.providers.vendors.rithmic.rithmic_provider.HistoricalTickBarProvider')
    def test_test_connection_failure(self, mock_provider_class):
        """Test connection test failure."""
        mock_provider = MagicMock()
        mock_provider.get_historical_data.side_effect = Exception("Connection failed")
        mock_provider_class.return_value = mock_provider
        
        provider = RithmicProvider(uri="wss://test.rithmic.com:443")
        
        result = provider.test_connection()
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main() 