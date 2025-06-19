import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_ccxt(monkeypatch):
    """Fixture to mock ccxt module."""
    mock = MagicMock()
    monkeypatch.setattr("src.data.providers.ohlcv_provider.ccxt", mock)
    return mock

# Removed mock_cache fixture as CacheClass does not exist 