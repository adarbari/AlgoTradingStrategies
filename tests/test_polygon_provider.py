"""
Tests for the PolygonProvider implementation.
"""
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
from src.data.providers.vendors.polygon.polygon_provider import PolygonProvider
from src.data.types.data_config_types import OHLCVConfig
from src.data.types.base_types import TimeSeriesData

class TestPolygonProvider(unittest.TestCase):
    def setUp(self):
        self.provider = PolygonProvider(api_key="test_key")
        self.symbol = "AAPL"
        self.start_time = datetime(2024, 1, 1)
        self.end_time = datetime(2024, 1, 10)
        self.config = OHLCVConfig(timeframe="1d")

    @patch("src.data.providers.vendors.polygon.polygon_provider.RESTClient")
    def test_get_data_success(self, mock_rest):
        # Mock the RESTClient's get_aggs method
        mock_client = MagicMock()
        mock_aggs = [
            MagicMock(timestamp=1704067200000, open=100, high=110, low=90, close=105, volume=1000),
            MagicMock(timestamp=1704153600000, open=106, high=112, low=104, close=110, volume=1200)
        ]
        mock_client.get_aggs.return_value = mock_aggs
        mock_rest.return_value = mock_client

        provider = PolygonProvider(api_key="test_key")
        result = provider.get_data(self.symbol, self.start_time, self.end_time, self.config)
        self.assertIsInstance(result, TimeSeriesData)
        self.assertEqual(len(result.data), 2)
        self.assertEqual(result.data[0].open, 100)
        self.assertEqual(result.data[1].close, 110)

    def test_parse_timeframe(self):
        self.assertEqual(self.provider._parse_timeframe("1d"), (1, "day"))
        self.assertEqual(self.provider._parse_timeframe("5m"), (5, "minute"))
        self.assertEqual(self.provider._parse_timeframe("1h"), (1, "hour"))
        with self.assertRaises(ValueError):
            self.provider._parse_timeframe("10x")

    @patch("src.data.providers.vendors.polygon.polygon_provider.RESTClient")
    def test_get_data_invalid_symbol(self, mock_rest):
        mock_client = MagicMock()
        mock_client.get_aggs.side_effect = Exception("Invalid symbol")
        mock_rest.return_value = mock_client
        provider = PolygonProvider(api_key="test_key")
        with self.assertRaises(Exception):
            provider.get_data("INVALID", self.start_time, self.end_time, self.config)

    def test_get_data_not_implemented_for_live(self):
        with self.assertRaises(NotImplementedError):
            self.provider.get_data(self.symbol, None, None, self.config)

if __name__ == "__main__":
    unittest.main() 