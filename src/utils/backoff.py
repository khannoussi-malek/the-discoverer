"""Exponential backoff utilities."""
import asyncio
import random
from typing import Callable, TypeVar, Optional
from functools import wraps

T = TypeVar('T')


def exponential_backoff(
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    multiplier: float = 2.0,
    jitter: bool = True
):
    """
    Decorator for exponential backoff retry logic.
    
    Args:
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        multiplier: Backoff multiplier
        jitter: Add random jitter to prevent thundering herd
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            delay = initial_delay
            attempt = 0
            
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    
                    if delay >= max_delay:
                        raise
                    
                    # Add jitter
                    if jitter:
                        actual_delay = delay + random.uniform(0, delay * 0.1)
                    else:
                        actual_delay = delay
                    
                    await asyncio.sleep(actual_delay)
                    delay = min(delay * multiplier, max_delay)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            import time
            delay = initial_delay
            attempt = 0
            
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    
                    if delay >= max_delay:
                        raise
                    
                    # Add jitter
                    if jitter:
                        actual_delay = delay + random.uniform(0, delay * 0.1)
                    else:
                        actual_delay = delay
                    
                    time.sleep(actual_delay)
                    delay = min(delay * multiplier, max_delay)
        
        # Return appropriate wrapper
        if hasattr(func, '__code__') and 'async' in str(func.__code__.co_flags):
            return async_wrapper
        return sync_wrapper
    
    return decorator

