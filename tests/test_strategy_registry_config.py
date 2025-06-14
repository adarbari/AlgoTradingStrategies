"""
Tests for strategy configuration dataclasses.
"""

import pytest
from src.config.strategy_config import MACrossoverConfig, RandomForestConfig

def test_macrossover_config_defaults():
    config = MACrossoverConfig()
    assert config.short_window == 10
    assert config.long_window == 50

def test_randomforest_config_defaults():
    config = RandomForestConfig()
    assert config.n_estimators == 100
    assert config.max_depth == 5
    assert config.min_samples_split == 2
    assert config.min_samples_leaf == 1 