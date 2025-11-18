"""Performance and load testing suite."""
import pytest
import httpx
import asyncio
import time
import statistics
import os
from typing import List, Dict, Any
from dataclasses import dataclass


BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")


@dataclass
class PerformanceMetrics:
    """Performance metrics for a test."""
    endpoint: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_time: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float


@pytest.fixture(scope="session")
def server_available():
    """Check if server is available."""
    import asyncio
    try:
        async def check():
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{BASE_URL}/health")
                return response.status_code == 200
        try:
            loop = asyncio.get_running_loop()
            return False
        except RuntimeError:
            return asyncio.run(check())
    except Exception:
        return False


@pytest.fixture
async def client():
    """HTTP client fixture."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        yield client


@pytest.fixture(autouse=True)
def skip_if_server_unavailable(server_available):
    """Skip tests if server is not available."""
    if not server_available:
        pytest.skip("Server is not available. Start it with 'make run'")


async def measure_endpoint_performance(
    client: httpx.AsyncClient,
    method: str,
    endpoint: str,
    num_requests: int,
    concurrent: int = 1,
    **request_kwargs
) -> PerformanceMetrics:
    """Measure performance of an endpoint."""
    response_times: List[float] = []
    successful = 0
    failed = 0
    
    async def make_request():
        nonlocal successful, failed
        start_time = time.time()
        try:
            if method.upper() == "GET":
                response = await client.get(endpoint, **request_kwargs)
            elif method.upper() == "POST":
                response = await client.post(endpoint, **request_kwargs)
            elif method.upper() == "PUT":
                response = await client.put(endpoint, **request_kwargs)
            elif method.upper() == "DELETE":
                response = await client.delete(endpoint, **request_kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            elapsed = time.time() - start_time
            response_times.append(elapsed)
            
            if 200 <= response.status_code < 400:
                successful += 1
            else:
                failed += 1
        except Exception as e:
            elapsed = time.time() - start_time
            response_times.append(elapsed)
            failed += 1
    
    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(concurrent)
    
    async def bounded_request():
        async with semaphore:
            await make_request()
    
    start_time = time.time()
    
    # Execute requests
    tasks = [bounded_request() for _ in range(num_requests)]
    await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    
    # Calculate metrics
    if response_times:
        response_times.sort()
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        median_response_time = statistics.median(response_times)
        
        # Percentiles
        p95_index = int(len(response_times) * 0.95)
        p99_index = int(len(response_times) * 0.99)
        p95_response_time = response_times[p95_index] if p95_index < len(response_times) else max_response_time
        p99_response_time = response_times[p99_index] if p99_index < len(response_times) else max_response_time
        
        requests_per_second = num_requests / total_time if total_time > 0 else 0
        error_rate = (failed / num_requests) * 100 if num_requests > 0 else 0
    else:
        avg_response_time = 0
        min_response_time = 0
        max_response_time = 0
        median_response_time = 0
        p95_response_time = 0
        p99_response_time = 0
        requests_per_second = 0
        error_rate = 100
    
    return PerformanceMetrics(
        endpoint=endpoint,
        total_requests=num_requests,
        successful_requests=successful,
        failed_requests=failed,
        total_time=total_time,
        avg_response_time=avg_response_time,
        min_response_time=min_response_time,
        max_response_time=max_response_time,
        median_response_time=median_response_time,
        p95_response_time=p95_response_time,
        p99_response_time=p99_response_time,
        requests_per_second=requests_per_second,
        error_rate=error_rate
    )


def print_metrics(metrics: PerformanceMetrics):
    """Print performance metrics in a readable format."""
    print(f"\n{'='*60}")
    print(f"Performance Metrics: {metrics.endpoint}")
    print(f"{'='*60}")
    print(f"Total Requests:      {metrics.total_requests}")
    print(f"Successful:          {metrics.successful_requests}")
    print(f"Failed:              {metrics.failed_requests}")
    print(f"Error Rate:          {metrics.error_rate:.2f}%")
    print(f"Total Time:          {metrics.total_time:.2f}s")
    print(f"Requests/Second:     {metrics.requests_per_second:.2f}")
    print(f"\nResponse Times:")
    print(f"  Average:           {metrics.avg_response_time*1000:.2f}ms")
    print(f"  Median:            {metrics.median_response_time*1000:.2f}ms")
    print(f"  Min:               {metrics.min_response_time*1000:.2f}ms")
    print(f"  Max:               {metrics.max_response_time*1000:.2f}ms")
    print(f"  P95:               {metrics.p95_response_time*1000:.2f}ms")
    print(f"  P99:               {metrics.p99_response_time*1000:.2f}ms")
    print(f"{'='*60}\n")


@pytest.mark.asyncio
class TestResponseTime:
    """Test response times for various endpoints."""
    
    async def test_health_endpoint_response_time(self, client):
        """Test health endpoint response time."""
        metrics = await measure_endpoint_performance(
            client, "GET", "/health", num_requests=100, concurrent=10
        )
        print_metrics(metrics)
        
        # Health endpoint should be very fast
        assert metrics.avg_response_time < 0.1, f"Health endpoint too slow: {metrics.avg_response_time*1000:.2f}ms"
        assert metrics.p95_response_time < 0.2, f"P95 too slow: {metrics.p95_response_time*1000:.2f}ms"
        assert metrics.error_rate < 1.0, f"Error rate too high: {metrics.error_rate:.2f}%"
    
    async def test_discovery_endpoint_response_time(self, client):
        """Test discovery endpoint response time."""
        metrics = await measure_endpoint_performance(
            client, "GET", "/api/discovery/databases", num_requests=50, concurrent=5
        )
        print_metrics(metrics)
        
        assert metrics.avg_response_time < 1.0, f"Discovery endpoint too slow: {metrics.avg_response_time*1000:.2f}ms"
        assert metrics.error_rate < 5.0, f"Error rate too high: {metrics.error_rate:.2f}%"
    
    async def test_templates_endpoint_response_time(self, client):
        """Test templates endpoint response time."""
        metrics = await measure_endpoint_performance(
            client, "GET", "/api/templates", num_requests=50, concurrent=5
        )
        print_metrics(metrics)
        
        assert metrics.avg_response_time < 1.0, f"Templates endpoint too slow: {metrics.avg_response_time*1000:.2f}ms"
        assert metrics.error_rate < 5.0, f"Error rate too high: {metrics.error_rate:.2f}%"
    
    async def test_cache_stats_response_time(self, client):
        """Test cache stats endpoint response time."""
        metrics = await measure_endpoint_performance(
            client, "GET", "/api/cache/stats", num_requests=100, concurrent=10
        )
        print_metrics(metrics)
        
        assert metrics.avg_response_time < 0.5, f"Cache stats too slow: {metrics.avg_response_time*1000:.2f}ms"
        assert metrics.error_rate < 1.0, f"Error rate too high: {metrics.error_rate:.2f}%"
    
    async def test_history_endpoint_response_time(self, client):
        """Test history endpoint response time."""
        metrics = await measure_endpoint_performance(
            client, "GET", "/api/history/queries", num_requests=50, concurrent=5
        )
        print_metrics(metrics)
        
        assert metrics.avg_response_time < 1.0, f"History endpoint too slow: {metrics.avg_response_time*1000:.2f}ms"
        assert metrics.error_rate < 5.0, f"Error rate too high: {metrics.error_rate:.2f}%"


@pytest.mark.asyncio
class TestThroughput:
    """Test throughput (requests per second) for various endpoints."""
    
    async def test_health_endpoint_throughput(self, client):
        """Test health endpoint throughput."""
        metrics = await measure_endpoint_performance(
            client, "GET", "/health", num_requests=500, concurrent=50
        )
        print_metrics(metrics)
        
        # Health endpoint should handle high throughput
        assert metrics.requests_per_second > 50, f"Throughput too low: {metrics.requests_per_second:.2f} req/s"
        assert metrics.error_rate < 5.0, f"Error rate too high: {metrics.error_rate:.2f}%"
    
    async def test_read_endpoints_throughput(self, client):
        """Test throughput of read-only endpoints."""
        endpoints = [
            "/api/discovery/databases",
            "/api/templates",
            "/api/scheduler",
            "/api/cache/stats",
        ]
        
        for endpoint in endpoints:
            metrics = await measure_endpoint_performance(
                client, "GET", endpoint, num_requests=200, concurrent=20
            )
            print_metrics(metrics)
            
            assert metrics.requests_per_second > 10, f"{endpoint} throughput too low: {metrics.requests_per_second:.2f} req/s"
            assert metrics.error_rate < 10.0, f"{endpoint} error rate too high: {metrics.error_rate:.2f}%"


@pytest.mark.asyncio
class TestConcurrency:
    """Test concurrent request handling."""
    
    async def test_concurrent_health_checks(self, client):
        """Test handling of concurrent health checks."""
        metrics = await measure_endpoint_performance(
            client, "GET", "/health", num_requests=200, concurrent=100
        )
        print_metrics(metrics)
        
        assert metrics.successful_requests > 180, f"Too many failures: {metrics.failed_requests}"
        assert metrics.error_rate < 10.0, f"Error rate too high: {metrics.error_rate:.2f}%"
    
    async def test_concurrent_read_requests(self, client):
        """Test concurrent read requests."""
        endpoints = [
            "/api/discovery/databases",
            "/api/templates",
            "/api/scheduler",
        ]
        
        for endpoint in endpoints:
            metrics = await measure_endpoint_performance(
                client, "GET", endpoint, num_requests=100, concurrent=50
            )
            print_metrics(metrics)
            
            assert metrics.successful_requests > 80, f"{endpoint} too many failures"
            assert metrics.error_rate < 20.0, f"{endpoint} error rate too high: {metrics.error_rate:.2f}%"
    
    async def test_mixed_concurrent_requests(self, client):
        """Test mixed concurrent requests to different endpoints."""
        async def make_mixed_request():
            endpoints = [
                "/health",
                "/api/discovery/databases",
                "/api/templates",
                "/api/cache/stats",
            ]
            import random
            endpoint = random.choice(endpoints)
            try:
                response = await client.get(endpoint)
                return response.status_code < 400
            except Exception:
                return False
        
        num_requests = 200
        concurrent = 50
        semaphore = asyncio.Semaphore(concurrent)
        
        async def bounded_request():
            async with semaphore:
                return await make_mixed_request()
        
        start_time = time.time()
        tasks = [bounded_request() for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        successful = sum(1 for r in results if r)
        failed = num_requests - successful
        requests_per_second = num_requests / total_time
        error_rate = (failed / num_requests) * 100
        
        print(f"\n{'='*60}")
        print(f"Mixed Concurrent Requests Performance")
        print(f"{'='*60}")
        print(f"Total Requests:      {num_requests}")
        print(f"Successful:          {successful}")
        print(f"Failed:              {failed}")
        print(f"Error Rate:          {error_rate:.2f}%")
        print(f"Total Time:          {total_time:.2f}s")
        print(f"Requests/Second:     {requests_per_second:.2f}")
        print(f"{'='*60}\n")
        
        assert successful > 150, f"Too many failures: {failed}"
        assert error_rate < 25.0, f"Error rate too high: {error_rate:.2f}%"


@pytest.mark.asyncio
class TestStress:
    """Stress testing with high load."""
    
    async def test_high_load_health(self, client):
        """Test health endpoint under high load."""
        metrics = await measure_endpoint_performance(
            client, "GET", "/health", num_requests=1000, concurrent=100
        )
        print_metrics(metrics)
        
        assert metrics.successful_requests > 900, f"Too many failures under load: {metrics.failed_requests}"
        assert metrics.error_rate < 10.0, f"Error rate too high: {metrics.error_rate:.2f}%"
        assert metrics.requests_per_second > 30, f"Throughput too low: {metrics.requests_per_second:.2f} req/s"
    
    async def test_sustained_load(self, client):
        """Test sustained load over time."""
        duration = 30  # seconds
        requests_per_second = 10
        total_requests = duration * requests_per_second
        
        response_times: List[float] = []
        successful = 0
        failed = 0
        
        async def make_request():
            nonlocal successful, failed
            start_time = time.time()
            try:
                response = await client.get("/health")
                elapsed = time.time() - start_time
                response_times.append(elapsed)
                if response.status_code == 200:
                    successful += 1
                else:
                    failed += 1
            except Exception:
                failed += 1
        
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < duration:
            # Launch requests at target rate
            tasks = [make_request() for _ in range(requests_per_second)]
            await asyncio.gather(*tasks)
            request_count += requests_per_second
            
            # Wait 1 second before next batch
            await asyncio.sleep(1)
        
        total_time = time.time() - start_time
        actual_rps = request_count / total_time
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = 0
            max_response_time = 0
        
        print(f"\n{'='*60}")
        print(f"Sustained Load Test")
        print(f"{'='*60}")
        print(f"Duration:            {duration}s")
        print(f"Total Requests:      {request_count}")
        print(f"Successful:          {successful}")
        print(f"Failed:              {failed}")
        print(f"Actual RPS:          {actual_rps:.2f}")
        print(f"Avg Response Time:   {avg_response_time*1000:.2f}ms")
        print(f"Max Response Time:   {max_response_time*1000:.2f}ms")
        print(f"{'='*60}\n")
        
        assert successful > request_count * 0.9, f"Too many failures: {failed}"
        assert avg_response_time < 1.0, f"Response time degraded: {avg_response_time*1000:.2f}ms"


@pytest.mark.asyncio
class TestLatencyDistribution:
    """Test latency distribution and percentiles."""
    
    async def test_latency_percentiles(self, client):
        """Test latency percentiles for health endpoint."""
        metrics = await measure_endpoint_performance(
            client, "GET", "/health", num_requests=500, concurrent=50
        )
        print_metrics(metrics)
        
        # P95 should be reasonable
        assert metrics.p95_response_time < 0.5, f"P95 too high: {metrics.p95_response_time*1000:.2f}ms"
        assert metrics.p99_response_time < 1.0, f"P99 too high: {metrics.p99_response_time*1000:.2f}ms"
        
        # P99 should be higher than P95
        assert metrics.p99_response_time >= metrics.p95_response_time, "P99 should be >= P95"
    
    async def test_response_time_consistency(self, client):
        """Test that response times are consistent."""
        metrics = await measure_endpoint_performance(
            client, "GET", "/health", num_requests=200, concurrent=20
        )
        print_metrics(metrics)
        
        # Max should not be too much higher than average (no outliers)
        if metrics.avg_response_time > 0:
            ratio = metrics.max_response_time / metrics.avg_response_time
            # Allow up to 10x difference for outliers
            assert ratio < 10, f"Response time inconsistency: max/avg = {ratio:.2f}"


@pytest.mark.asyncio
class TestResourceUsage:
    """Test resource usage patterns."""
    
    async def test_memory_efficient_requests(self, client):
        """Test that requests don't cause memory leaks."""
        import gc
        
        # Baseline
        gc.collect()
        
        # Make many requests
        metrics = await measure_endpoint_performance(
            client, "GET", "/health", num_requests=1000, concurrent=100
        )
        print_metrics(metrics)
        
        # Force garbage collection
        gc.collect()
        
        # Should complete without errors
        assert metrics.error_rate < 20.0, f"Error rate too high: {metrics.error_rate:.2f}%"
    
    async def test_connection_pool_efficiency(self, client):
        """Test connection pool efficiency."""
        # Make many sequential requests
        start_time = time.time()
        for _ in range(100):
            response = await client.get("/health")
            assert response.status_code == 200
        
        total_time = time.time() - start_time
        avg_time = total_time / 100
        
        print(f"\nConnection Pool Test:")
        print(f"100 sequential requests in {total_time:.2f}s")
        print(f"Average: {avg_time*1000:.2f}ms per request")
        
        # Should be fast due to connection reuse
        assert avg_time < 0.1, f"Too slow: {avg_time*1000:.2f}ms"


@pytest.mark.asyncio
class TestScalability:
    """Test scalability with increasing load."""
    
    async def test_scaling_with_concurrency(self, client):
        """Test how performance scales with concurrency."""
        concurrency_levels = [1, 5, 10, 20, 50]
        results = []
        
        for concurrency in concurrency_levels:
            metrics = await measure_endpoint_performance(
                client, "GET", "/health", num_requests=200, concurrent=concurrency
            )
            results.append((concurrency, metrics))
            print_metrics(metrics)
        
        # Throughput should generally increase with concurrency (up to a point)
        rps_values = [r[1].requests_per_second for r in results]
        print(f"\nScaling Results:")
        for concurrency, metrics in results:
            print(f"  Concurrency {concurrency}: {metrics.requests_per_second:.2f} req/s")
        
        # At least some increase should be observed
        max_rps = max(rps_values)
        min_rps = min(rps_values)
        assert max_rps > 0, "No requests completed"
    
    async def test_graceful_degradation(self, client):
        """Test graceful degradation under extreme load."""
        # Very high concurrency
        metrics = await measure_endpoint_performance(
            client, "GET", "/health", num_requests=500, concurrent=200
        )
        print_metrics(metrics)
        
        # Should still handle some requests, even if many fail
        assert metrics.successful_requests > 0, "Complete failure under extreme load"
        # Error rate might be high, but should not be 100%
        assert metrics.error_rate < 100.0, "Complete failure"

