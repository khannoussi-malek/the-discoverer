"""Performance monitoring utilities."""
import time
from functools import wraps
from typing import Dict, List, Callable, Any
from collections import defaultdict


class PerformanceMonitor:
    """Performance monitor - Track operation timings."""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = defaultdict(list)
    
    def track(self, operation_name: str):
        """Decorator to track operation performance."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.perf_counter() - start
                    self.metrics[operation_name].append(duration)
                    return result
                except Exception as e:
                    duration = time.perf_counter() - start
                    self.metrics[f"{operation_name}_error"].append(duration)
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    duration = time.perf_counter() - start
                    self.metrics[operation_name].append(duration)
                    return result
                except Exception as e:
                    duration = time.perf_counter() - start
                    self.metrics[f"{operation_name}_error"].append(duration)
                    raise
            
            # Return appropriate wrapper based on function type
            if hasattr(func, '__code__') and 'async' in str(func.__code__.co_flags):
                return async_wrapper
            return sync_wrapper
        
        return decorator
    
    def get_stats(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics."""
        stats = {}
        for operation, durations in self.metrics.items():
            if durations:
                sorted_durations = sorted(durations)
                stats[operation] = {
                    "count": len(durations),
                    "avg": sum(durations) / len(durations),
                    "min": min(durations),
                    "max": max(durations),
                    "p50": sorted_durations[int(len(durations) * 0.5)],
                    "p95": sorted_durations[int(len(durations) * 0.95)],
                    "p99": sorted_durations[int(len(durations) * 0.99)]
                }
        return stats
    
    def reset(self) -> None:
        """Reset all metrics."""
        self.metrics.clear()


# Global performance monitor instance
performance_monitor = PerformanceMonitor()

