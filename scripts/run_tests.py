#!/usr/bin/env python3
"""
Script to run tests in slow mode.
"""

import os
import sys
import subprocess
from datetime import datetime

def run_tests():
    """Run tests in slow mode."""
    print(f"Running tests in slow mode at {datetime.now()}")
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Change to project root
    os.chdir(project_root)
    
    # Run tests with slow marker
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "-m", "slow",
        "--cov=src",
        "--cov-report=term-missing"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\nAll tests passed successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\nTests failed with error code {e.returncode}")
        return e.returncode

if __name__ == "__main__":
    sys.exit(run_tests()) 