# CI/CD Pipeline Test Configuration

This document describes which tests are included in the CI/CD pipelines and how they're organized.

## Test Suites Included

All non-LLM tests are now included in the CI/CD pipelines:

### 1. Basic Integration Tests
- **File:** `tests/integration/test_api_no_llm.py`
- **Tests:** 25 tests
- **Status:** Required (must pass)
- **Coverage:** All major API endpoints

### 2. Comprehensive Integration Tests
- **File:** `tests/integration/test_api_comprehensive.py`
- **Tests:** 70+ tests
- **Status:** Optional (continue-on-error: true)
- **Coverage:** 
  - Input validation
  - Error handling
  - Query optimization
  - Caching
  - Templates
  - Scheduler
  - Analytics
  - History
  - Health monitoring
  - API keys, webhooks, dashboards, pools, exports, charts, sharing, versioning, metrics
  - Concurrent requests
  - Response formats

### 3. Edge Case Tests
- **File:** `tests/integration/test_edge_cases.py`
- **Tests:** 20+ tests
- **Status:** Optional (continue-on-error: true)
- **Coverage:**
  - Boundary conditions
  - Data type validation
  - Rate limiting
  - HTTP headers
  - Query parameters
  - Response times
  - Error recovery
  - CORS
  - Content negotiation

### 4. Performance Tests (Quick Subset)
- **File:** `tests/integration/test_performance.py`
- **Tests:** 2 quick tests (subset)
- **Status:** Optional (continue-on-error: true)
- **Coverage:**
  - Health endpoint response time
  - Cache stats response time

### 5. Feature Tests
- **File:** `test_features_python.py`
- **Status:** Optional (continue-on-error: true)
- **Flags:** `--skip-llm`

### 6. API Endpoint Tests
- **File:** `test_all_features.sh`
- **Status:** Optional (continue-on-error: true)

## GitHub Actions

### Main Workflow: `.github/workflows/test.yml`

**Job: `test-no-llm`**
- Runs on: `ubuntu-latest`
- Services: Qdrant, Redis
- Steps:
  1. Install dependencies
  2. Start server
  3. Wait for server health
  4. Run basic integration tests (required)
  5. Run comprehensive tests (optional)
  6. Run edge case tests (optional)
  7. Run feature tests (optional)
  8. Check server health
  9. Test API endpoints (optional)
  10. Run quick performance tests (optional)

### Extended Workflow: `.github/workflows/test-all-no-llm.yml`

**Job: `test-all-no-llm`**
- Runs on: Push, PR, Schedule (daily at 2 AM UTC), Manual dispatch
- Timeout: 30 minutes
- More comprehensive test execution
- Includes test report generation

## GitLab CI

### Job: `test:no-llm`

**Configuration:**
- Stage: `test`
- Image: `python:3.10`
- Timeout: 30 minutes
- Services: Qdrant, Redis

**Test Execution Order:**
1. Basic integration tests (required)
2. Comprehensive integration tests (optional)
3. Edge case tests (optional)
4. Performance tests - quick subset (optional)
5. Feature tests (optional)
6. API endpoint tests (optional)
7. Test summary

## Test Execution Strategy

### Required Tests
- **Basic Integration Tests** (`test_api_no_llm.py`)
  - Must pass for CI to succeed
  - Fast execution (< 5 seconds)
  - Covers all critical endpoints

### Optional Tests
- **Comprehensive Tests** (`test_api_comprehensive.py`)
  - May fail if services aren't fully configured
  - Tests edge cases and error scenarios
  - Continue on error to allow partial failures

- **Edge Case Tests** (`test_edge_cases.py`)
  - Tests boundary conditions and unusual scenarios
  - May require specific configurations
  - Continue on error

- **Performance Tests** (subset)
  - Only quick tests included (2 tests)
  - Full performance suite excluded (too slow for CI)
  - Continue on error

- **Feature Tests** (`test_features_python.py --skip-llm`)
  - Python-based feature tests
  - Continue on error

- **API Endpoint Tests** (`test_all_features.sh`)
  - Shell-based endpoint tests
  - Continue on error

## Environment Variables

All pipelines set:
- `QDRANT_URL`: http://localhost:6333 (or http://qdrant:6333 for GitLab)
- `REDIS_URL`: redis://localhost:6379 (or redis://redis:6379 for GitLab)
- `LLM_PROVIDER`: openai
- `OPENAI_API_KEY`: test-key (dummy key for non-LLM tests)
- `PERPLEXITY_API_KEY`: test-key (dummy key for non-LLM tests)
- `TEST_BASE_URL`: http://localhost:8000

## Test Statistics

### Total Non-LLM Tests
- **Basic:** 25 tests (required)
- **Comprehensive:** 70+ tests (optional)
- **Edge Cases:** 20+ tests (optional)
- **Performance (subset):** 2 tests (optional)
- **Total:** 115+ tests

### Execution Time
- **Basic tests:** ~2-5 seconds
- **Comprehensive tests:** ~5-10 seconds
- **Edge case tests:** ~3-5 seconds
- **Performance subset:** ~5-10 seconds
- **Total pipeline:** ~30-60 seconds (depending on optional tests)

## Running Tests Locally

### Run all non-LLM tests (same as CI)
```bash
# Start server first
make run

# In another terminal, run tests
make test-no-llm              # Basic tests
make test-comprehensive        # Comprehensive tests
pytest tests/integration/test_edge_cases.py -v  # Edge cases
make test-performance          # Full performance suite (not in CI)
```

### Run specific test suite
```bash
pytest tests/integration/test_api_no_llm.py -v
pytest tests/integration/test_api_comprehensive.py -v
pytest tests/integration/test_edge_cases.py -v
```

## CI/CD Best Practices

1. **Fast Feedback:** Basic tests run first and must pass
2. **Comprehensive Coverage:** Optional tests provide additional validation
3. **Graceful Degradation:** Optional tests continue on error
4. **Resource Efficiency:** Performance tests limited to quick subset
5. **Clear Reporting:** Test summaries generated for visibility

## Troubleshooting

### Tests Skipping
- Ensure server is running and accessible
- Check `TEST_BASE_URL` environment variable
- Verify server health endpoint responds

### Optional Tests Failing
- These are expected to fail if services aren't fully configured
- Check logs for specific error messages
- Basic tests must still pass

### Performance Tests Timing Out
- Only quick subset included in CI
- Full performance suite should run locally
- Adjust timeout if needed

## Future Enhancements

- Add test coverage reporting
- Add test result artifacts
- Add performance benchmarks
- Add test result notifications
- Add parallel test execution

