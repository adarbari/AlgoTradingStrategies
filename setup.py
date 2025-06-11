from setuptools import setup, find_packages

setup(
    name="algo_trading_models",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "scikit-learn>=0.24.0",
        "yfinance>=0.2.36",
        "ta>=0.10.0",
    ],
    python_requires=">=3.9",
) 