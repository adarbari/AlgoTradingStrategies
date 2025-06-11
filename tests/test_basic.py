"""
Basic tests for the trading system.
"""

def test_src_import():
    """Test that we can import the main src package."""
    try:
        import src
        assert True
    except ImportError as e:
        assert False, f"Failed to import src: {str(e)}"

def test_features_import():
    """Test that we can import the features package."""
    try:
        import src.features
        assert True
    except ImportError as e:
        assert False, f"Failed to import src.features: {str(e)}"

def test_utils_import():
    """Test that we can import the utils package."""
    try:
        import src.utils
        assert True
    except ImportError as e:
        assert False, f"Failed to import src.utils: {str(e)}"

def test_basic():
    """Basic test that should always pass."""
    assert True 