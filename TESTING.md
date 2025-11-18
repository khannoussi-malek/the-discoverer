# Testing Guide

This document describes the testing setup and how to run tests for The Discoverer.

## Test Structure

```
tests/
├── unit/              # Unit tests (no external dependencies)
│   └── test_domain.py
├── integration/       # Integration tests
│   ├── test_api_no_llm.py    # API tests that don't require LLM
│   ├── test_database_adapters.py
│   ├── test_llm_generators.py
│   ├── test_query_service.py
│   └── test_vector_db.py
└── conftest.py        # Pytest configuration
```

## Running Tests

### All Tests
```bash
make test
# or
pytest tests/ -v
```

### Non-LLM Tests Only (for CI/CD)
These tests don't require LLM API keys and can run in CI pipelines:

```bash
# Run pytest integration tests
make test-no-llm
# or
pytest tests/integration/test_api_no_llm.py -v

# Run Python feature test script
make test-api
# or
python3 test_features_python.py --skip-llm

# Run shell-based feature tests
make test-all-features
# or
./test_all_features.sh
```

### Individual Test Files
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Specific test file
pytest tests/integration/test_api_no_llm.py -v
```

## Test Scripts

### `test_features_python.py`
Python-based feature testing script that tests all API endpoints systematically.

**Usage:**
```bash
# Test all features (including LLM-required)
python3 test_features_python.py

# Test only non-LLM features (for CI)
python3 test_features_python.py --skip-llm
```

**Features:**
- Tests 20+ feature categories
- Color-coded output
- Detailed test summaries
- Separates LLM vs non-LLM tests

### `test_all_features.sh`
Bash-based feature testing script using curl.

**Usage:**
```bash
./test_all_features.sh
```

**Features:**
- Tests all API endpoints
- Uses curl for HTTP requests
- Provides pass/fail summary
- Can be used in CI/CD pipelines

## CI/CD Integration

### GitHub Actions
The `.github/workflows/test.yml` file defines CI tests that:
- Run non-LLM tests automatically
- Start required services (Qdrant, Redis)
- Test API endpoints
- Run linting checks

### GitLab CI
The `.gitlab-ci.yml` file provides similar functionality for GitLab CI/CD.

## Test Categories

### Non-LLM Tests (CI-Safe)
These tests can run without LLM API keys:
- Health & Status endpoints
- Database Discovery
- Query History
- Statistics & Analytics
- Query Templates (listing)
- Query Optimization (SQL analysis)
- Caching
- Sharing
- Webhooks
- API Keys
- Connection Pools
- Dashboards
- Chart Templates
- Export Templates
- Scheduled Exports
- Metrics
- Versioning
- Scheduler (listing)

### LLM-Required Tests
These tests require valid LLM API keys:
- Query Execution (`/api/query/execute`)
- Batch Queries (`/api/batch/execute`)
- Query generation features

## Environment Setup

For local testing, ensure:
1. Server is running: `make run`
2. Required services are available (Qdrant, Redis)
3. Environment variables are set (see `.env.example`)

For CI testing:
- Services are provided via Docker services
- Test API keys are used (won't make real API calls)
- Server starts automatically in CI pipeline

## Writing New Tests

### Unit Tests
Place in `tests/unit/`:
```python
def test_something():
    # Test logic here
    assert result == expected
```

### Integration Tests
Place in `tests/integration/`:
```python
@pytest.mark.asyncio
async def test_api_endpoint(client):
    response = await client.get("/api/endpoint")
    assert response.status_code == 200
```

### Test Requirements
- Use `pytest` and `pytest-asyncio` for async tests
- Use `httpx.AsyncClient` for API testing
- Mark LLM-required tests appropriately
- Follow existing test patterns

## Troubleshooting

### Server Not Running
```bash
# Start server first
make run
```

### Import Errors
```bash
# Install dependencies
make install
```

### Test Failures
- Check server logs
- Verify environment variables
- Ensure services (Qdrant, Redis) are running
- Check API endpoint availability

## Test Coverage

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

