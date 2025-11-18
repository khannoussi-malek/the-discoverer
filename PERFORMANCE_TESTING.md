# Performance Testing Guide

This document describes the performance testing suite and how to use it.

## Overview

The performance test suite (`tests/integration/test_performance.py`) provides comprehensive performance and load testing capabilities for the API.

## Test Categories

### 1. Response Time Tests (`TestResponseTime`)
Measures response times for various endpoints:
- Health endpoint (< 100ms average)
- Discovery endpoint (< 1s average)
- Templates endpoint (< 1s average)
- Cache stats endpoint (< 500ms average)
- History endpoint (< 1s average)

**Run:** `pytest tests/integration/test_performance.py::TestResponseTime -v -s`

### 2. Throughput Tests (`TestThroughput`)
Measures requests per second (RPS):
- Health endpoint (> 50 req/s)
- Read-only endpoints (> 10 req/s each)

**Run:** `pytest tests/integration/test_performance.py::TestThroughput -v -s`

### 3. Concurrency Tests (`TestConcurrency`)
Tests concurrent request handling:
- Concurrent health checks (100 concurrent)
- Concurrent read requests (50 concurrent)
- Mixed concurrent requests to different endpoints

**Run:** `pytest tests/integration/test_performance.py::TestConcurrency -v -s`

### 4. Stress Tests (`TestStress`)
High load and sustained load testing:
- High load: 1000 requests with 100 concurrent
- Sustained load: 30 seconds at 10 req/s

**Run:** `pytest tests/integration/test_performance.py::TestStress -v -s`

### 5. Latency Distribution Tests (`TestLatencyDistribution`)
Tests latency percentiles:
- P95 and P99 percentiles
- Response time consistency

**Run:** `pytest tests/integration/test_performance.py::TestLatencyDistribution -v -s`

### 6. Resource Usage Tests (`TestResourceUsage`)
Tests resource efficiency:
- Memory efficiency (no leaks)
- Connection pool efficiency

**Run:** `pytest tests/integration/test_performance.py::TestResourceUsage -v -s`

### 7. Scalability Tests (`TestScalability`)
Tests how performance scales:
- Scaling with increasing concurrency
- Graceful degradation under extreme load

**Run:** `pytest tests/integration/test_performance.py::TestScalability -v -s`

## Running Performance Tests

### Run All Performance Tests
```bash
make test-performance
```

### Run Specific Test Category
```bash
# Response time tests only
pytest tests/integration/test_performance.py::TestResponseTime -v -s

# Throughput tests only
pytest tests/integration/test_performance.py::TestThroughput -v -s

# Stress tests only
pytest tests/integration/test_performance.py::TestStress -v -s
```

### Run Specific Test
```bash
# Test health endpoint response time
pytest tests/integration/test_performance.py::TestResponseTime::test_health_endpoint_response_time -v -s

# Test high load
pytest tests/integration/test_performance.py::TestStress::test_high_load_health -v -s
```

## Performance Metrics

Each test reports the following metrics:

- **Total Requests**: Number of requests made
- **Successful Requests**: Number of successful responses
- **Failed Requests**: Number of failed responses
- **Error Rate**: Percentage of failed requests
- **Total Time**: Total time for all requests
- **Requests/Second**: Throughput (RPS)
- **Response Times**:
  - Average: Mean response time
  - Median: Median response time
  - Min: Minimum response time
  - Max: Maximum response time
  - P95: 95th percentile response time
  - P99: 99th percentile response time

## Example Output

```
============================================================
Performance Metrics: /health
============================================================
Total Requests:      100
Successful:          100
Failed:              0
Error Rate:          0.00%
Total Time:          2.45s
Requests/Second:     40.82

Response Times:
  Average:           24.50ms
  Median:            23.00ms
  Min:               15.00ms
  Max:               45.00ms
  P95:               38.00ms
  P99:               42.00ms
============================================================
```

## Performance Benchmarks

### Expected Performance Targets

| Endpoint | Avg Response Time | P95 Response Time | Throughput |
|----------|------------------|-------------------|------------|
| `/health` | < 100ms | < 200ms | > 50 req/s |
| `/api/discovery/databases` | < 1s | < 2s | > 10 req/s |
| `/api/templates` | < 1s | < 2s | > 10 req/s |
| `/api/cache/stats` | < 500ms | < 1s | > 20 req/s |
| `/api/history/queries` | < 1s | < 2s | > 10 req/s |

### Concurrency Targets

- **Low Concurrency (1-10)**: Should handle without degradation
- **Medium Concurrency (10-50)**: Minimal degradation acceptable
- **High Concurrency (50-100)**: Some degradation acceptable, but should not fail completely
- **Extreme Concurrency (100+)**: Graceful degradation expected

## Interpreting Results

### Good Performance
- ✅ Error rate < 5%
- ✅ Response times within targets
- ✅ Throughput meets or exceeds targets
- ✅ P95/P99 within reasonable bounds

### Performance Issues
- ⚠️ Error rate 5-10%: May indicate resource constraints
- ⚠️ Error rate > 10%: Likely performance bottleneck
- ⚠️ Response times 2x target: Performance degradation
- ⚠️ P99 >> P95: Inconsistent performance, possible outliers

### Critical Issues
- ❌ Error rate > 20%: Significant performance problems
- ❌ Complete failure under load: System not scalable
- ❌ Memory leaks: Resource management issues

## Tips for Performance Testing

1. **Run tests on a dedicated machine** to avoid interference
2. **Warm up the server** before running tests
3. **Run tests multiple times** to get average results
4. **Monitor system resources** (CPU, memory, network) during tests
5. **Start with low concurrency** and gradually increase
6. **Compare results** before and after optimizations

## CI/CD Integration

Performance tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Performance Tests
  run: |
    make run &
    sleep 5  # Wait for server to start
    make test-performance
```

Note: Performance tests may take longer to run and should be run separately from unit tests.

## Troubleshooting

### Tests Skipping
If tests are skipped, ensure the server is running:
```bash
make run
```

### High Error Rates
- Check server logs for errors
- Verify server has sufficient resources
- Reduce concurrency in tests
- Check network connectivity

### Slow Response Times
- Check database connection pool settings
- Verify cache is working
- Check for blocking operations
- Monitor system resources

## Customizing Tests

You can customize test parameters:

```python
# In test file, modify:
metrics = await measure_endpoint_performance(
    client, 
    "GET", 
    "/health", 
    num_requests=1000,  # Increase requests
    concurrent=200,      # Increase concurrency
)
```

## Best Practices

1. **Baseline First**: Establish baseline performance before optimization
2. **Incremental Testing**: Test with increasing load to find breaking points
3. **Realistic Scenarios**: Test with realistic request patterns
4. **Monitor Everything**: Track CPU, memory, network, and database metrics
5. **Document Results**: Keep performance test results for comparison
6. **Automate**: Include performance tests in CI/CD where appropriate

