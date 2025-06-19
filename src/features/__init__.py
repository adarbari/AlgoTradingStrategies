"""
Features package for algorithmic trading models.

This package provides a comprehensive feature engineering system for financial data,
including technical indicators, order flow metrics, and feature management.
"""

# Core feature management
from .core import FeatureStore, FeatureFileMetadata, FeatureStoreMetadata

# Feature definitions and metadata
from .types import (
    FeatureNames,
    FeatureType,
    FeatureCalculationEngineType,
    FeatureMetadata
)

# Feature implementations
from .implementations import (
    # Technical indicators
    TechnicalIndicators,
    
    # Order flow metrics
    OrderFlowMetricsCalculator
)

# Types and base classes
from .interfaces.base import FeatureEngineer
from .types import OrderFlowMetrics

__all__ = [
    # Core
    'FeatureStore',
    'FeatureFileMetadata',
    'FeatureStoreMetadata',
    
    # Definitions
    'FeatureNames',
    'FeatureType',
    'FeatureCalculationEngineType',
    'FeatureMetadata',
    
    # Technical indicators
    'TechnicalIndicators',
    
    # Order flow metrics
    'OrderFlowMetricsCalculator',
    
    # Types
    'FeatureEngineer',
    'OrderFlowMetrics'
] 