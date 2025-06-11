def test_imports():
    """Test that we can import our main modules."""
    try:
        import src
        import src.features
        import src.strategies
        import src.utils
        assert True
    except ImportError as e:
        assert False, f"Failed to import: {str(e)}"

def test_basic():
    """Basic test that should always pass."""
    assert True 