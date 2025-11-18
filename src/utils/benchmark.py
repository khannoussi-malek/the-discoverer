"""Performance benchmarking utilities."""
import time
import asyncio
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from statistics import mean, median, stdev


@dataclass
class BenchmarkResult:
    """Benchmark result."""
    name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    median_time: float
    std_dev: float
    success_count: int
    error_count: int
    errors: List[str] = field(default_factory=list)


class BenchmarkRunner:
    """Performance benchmark runner."""
    
    @staticmethod
    async def benchmark(
        func: Callable,
        iterations: int = 10,
        name: Optional[str] = None,
        *args,
        **kwargs
    ) -> BenchmarkResult:
        """Run benchmark on async function."""
        name = name or func.__name__
        times = []
        success_count = 0
        error_count = 0
        errors = []
        
        for i in range(iterations):
            try:
                start = time.time()
                await func(*args, **kwargs)
                elapsed = time.time() - start
                times.append(elapsed)
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"Iteration {i+1}: {str(e)}")
        
        if not times:
            return BenchmarkResult(
                name=name,
                iterations=iterations,
                total_time=0.0,
                avg_time=0.0,
                min_time=0.0,
                max_time=0.0,
                median_time=0.0,
                std_dev=0.0,
                success_count=0,
                error_count=error_count,
                errors=errors
            )
        
        return BenchmarkResult(
            name=name,
            iterations=iterations,
            total_time=sum(times),
            avg_time=mean(times),
            min_time=min(times),
            max_time=max(times),
            median_time=median(times),
            std_dev=stdev(times) if len(times) > 1 else 0.0,
            success_count=success_count,
            error_count=error_count,
            errors=errors
        )
    
    @staticmethod
    async def compare(
        functions: List[Callable],
        iterations: int = 10,
        names: Optional[List[str]] = None,
        *args,
        **kwargs
    ) -> List[BenchmarkResult]:
        """Compare multiple functions."""
        if names and len(names) != len(functions):
            raise ValueError("Names list must match functions list length")
        
        results = []
        for i, func in enumerate(functions):
            name = names[i] if names else func.__name__
            result = await BenchmarkRunner.benchmark(
                func, iterations, name, *args, **kwargs
            )
            results.append(result)
        
        return results


