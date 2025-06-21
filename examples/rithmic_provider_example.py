#!/usr/bin/env python3
"""
Example usage of the RithmicProvider abstraction.

This example demonstrates how to use the RithmicProvider class to fetch
historical tick bar data from Rithmic systems using the OrderFlowDataProvider interface.
"""

import os
from datetime import datetime, timedelta
from src.data.providers.vendors.rithmic import RithmicProvider
from src.data.types.data_config_types import OrderFlowConfig

def main():
    """
    Example usage of RithmicProvider.
    """
    
    # Method 1: Initialize with parameters
    provider = RithmicProvider(
        uri="wss://rituz00100.rithmic.com:443",
        system_name="Rithmic_Test",
        user_id="your_user_id",
        password="your_password"
    )
    
    # Method 2: Initialize with environment variables
    # Set these environment variables:
    # export RITHMIC_URI="wss://rituz00100.rithmic.com:443"
    # export RITHMIC_SYSTEM_NAME="Rithmic_Test"
    # export RITHMIC_USER_ID="your_user_id"
    # export RITHMIC_PASSWORD="your_password"
    # provider = RithmicProvider()
    
    # Test connection
    print("Testing connection...")
    if provider.test_connection():
        print("✓ Connection successful!")
    else:
        print("✗ Connection failed!")
        return
    
    # List available systems (optional)
    print("\nListing available systems...")
    try:
        provider.list_available_systems()
    except Exception as e:
        print(f"Error listing systems: {e}")
    
    # Configure order flow data request
    config = OrderFlowConfig(
        order_types=['market', 'limit'],
        min_size=1.0,
        max_size=1000.0,
        include_cancellations=True,
        include_modifications=True
    )
    
    # Define time range for historical data
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)  # Last hour
    
    # Fetch historical tick bar data
    print(f"\nFetching tick bar data for ES from {start_time} to {end_time}...")
    try:
        # Symbol can be specified as "CME:ES" or just "ES" (defaults to CME)
        data = provider.get_data(
            symbol="CME:ES",
            start_time=start_time,
            end_time=end_time,
            config=config
        )
        
        print(f"✓ Data retrieved successfully!")
        print(f"  - Data type: {data.data_type}")
        print(f"  - Number of timestamps: {len(data.timestamps)}")
        print(f"  - Number of data points: {len(data.data)}")
        
        # Convert to DataFrame for analysis (if needed)
        if hasattr(data, 'to_dataframe'):
            df = data.to_dataframe()
            print(f"  - DataFrame shape: {df.shape}")
            print(f"  - DataFrame columns: {list(df.columns)}")
        
    except Exception as e:
        print(f"✗ Error fetching data: {e}")
        print(f"  Error type: {type(e).__name__}")
        
        # Handle specific error types
        from src.data.providers.vendors.rithmic.rithmic_provider import (
            RithmicConnectionError,
            RithmicAuthenticationError,
            RithmicDataError
        )
        
        if isinstance(e, RithmicConnectionError):
            print("  This is a connection error. Check your URI and network connection.")
        elif isinstance(e, RithmicAuthenticationError):
            print("  This is an authentication error. Check your credentials.")
        elif isinstance(e, RithmicDataError):
            print("  This is a data retrieval error. Check your symbol and time range.")

def example_with_different_symbols():
    """
    Example showing how to fetch data for different symbols.
    """
    provider = RithmicProvider()
    
    # Different ways to specify symbols
    symbols = [
        "ES",           # Defaults to CME:ES
        "CME:ES",       # Explicit exchange
        "CME:NQ",       # NASDAQ futures
        "NYMEX:CL",     # Crude oil futures
    ]
    
    config = OrderFlowConfig()
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=30)
    
    for symbol in symbols:
        print(f"\nFetching data for {symbol}...")
        try:
            data = provider.get_data(
                symbol=symbol,
                start_time=start_time,
                end_time=end_time,
                config=config
            )
            print(f"✓ Success: {len(data.data)} data points")
        except Exception as e:
            print(f"✗ Failed: {e}")

if __name__ == "__main__":
    print("RithmicProvider Example")
    print("=" * 50)
    
    # Check if credentials are available
    required_env_vars = ['RITHMIC_SYSTEM_NAME', 'RITHMIC_USER_ID', 'RITHMIC_PASSWORD']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print("⚠️  Warning: Missing environment variables:", missing_vars)
        print("   Set these variables or provide credentials directly to the constructor.")
        print("   Example:")
        print("   export RITHMIC_URI='wss://rituz00100.rithmic.com:443'")
        print("   export RITHMIC_SYSTEM_NAME='your_system'")
        print("   export RITHMIC_USER_ID='your_user_id'")
        print("   export RITHMIC_PASSWORD='your_password'")
        print()
    
    try:
        main()
        print("\n" + "=" * 50)
        example_with_different_symbols()
    except KeyboardInterrupt:
        print("\n\nExample interrupted by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        print("Please check your credentials and network connection.") 