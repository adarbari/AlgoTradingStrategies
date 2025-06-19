import time
import random
import logging
from typing import Callable, TypeVar, Optional, Union, List
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')

class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retry_on_exceptions: Optional[List[type]] = None
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds before first retry
            max_delay: Maximum delay in seconds between retries
            exponential_base: Base for exponential backoff calculation
            jitter: Whether to add random jitter to delays
            retry_on_exceptions: List of exception types to retry on
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retry_on_exceptions = retry_on_exceptions or [Exception]

def exponential_backoff_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retry_on_exceptions: Optional[List[type]] = None
) -> Callable:
    """
    Decorator that implements exponential backoff retry logic.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds before first retry
        max_delay: Maximum delay in seconds between retries
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delays
        retry_on_exceptions: List of exception types to retry on
        
    Returns:
        Decorated function with retry logic
    """
    config = RetryConfig(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
        retry_on_exceptions=retry_on_exceptions
    )
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except tuple(config.retry_on_exceptions) as e:
                    last_exception = e
                    
                    if attempt == config.max_retries:
                        # Final attempt failed, re-raise the exception
                        logger.error(f"Function {func.__name__} failed after {config.max_retries + 1} attempts. Final error: {e}")
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )
                    
                    # Add jitter if enabled
                    if config.jitter:
                        delay *= (0.5 + random.random() * 0.5)  # 50-100% of calculated delay
                    
                    logger.warning(
                        f"Function {func.__name__} failed on attempt {attempt + 1}/{config.max_retries + 1}. "
                        f"Error: {e}. Retrying in {delay:.2f} seconds..."
                    )
                    
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            raise last_exception
            
        return wrapper
    return decorator

def retry_with_config(config: RetryConfig) -> Callable:
    """
    Decorator that uses a RetryConfig object for retry behavior.
    
    Args:
        config: RetryConfig object specifying retry behavior
        
    Returns:
        Decorated function with retry logic
    """
    return exponential_backoff_retry(
        max_retries=config.max_retries,
        base_delay=config.base_delay,
        max_delay=config.max_delay,
        exponential_base=config.exponential_base,
        jitter=config.jitter,
        retry_on_exceptions=config.retry_on_exceptions
    )

# Predefined retry configurations for common scenarios
RATE_LIMIT_RETRY_CONFIG = RetryConfig(
    max_retries=5,
    base_delay=2.0,
    max_delay=120.0,
    exponential_base=2.0,
    jitter=True,
    retry_on_exceptions=[Exception]  # Will be overridden for specific HTTP errors
)

NETWORK_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    base_delay=1.0,
    max_delay=30.0,
    exponential_base=2.0,
    jitter=True,
    retry_on_exceptions=[Exception]  # Will be overridden for specific network errors
) 