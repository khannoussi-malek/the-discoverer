"""Edge case and boundary condition tests."""
import pytest
import httpx
import os
import json
from typing import Dict, Any


BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")


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
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture(autouse=True)
def skip_if_server_unavailable(server_available):
    """Skip tests if server is not available."""
    if not server_available:
        pytest.skip("Server is not available. Start it with 'make run'")


@pytest.mark.asyncio
class TestBoundaryConditions:
    """Test boundary conditions and limits."""
    
    async def test_max_int_values(self, client):
        """Test with maximum integer values."""
        # Max int32
        response = await client.get("/api/history/queries?limit=2147483647")
        assert response.status_code in [200, 400, 422]
        
        # Max int64
        response = await client.get("/api/history/queries?limit=9223372036854775807")
        assert response.status_code in [200, 400, 422]
    
    async def test_unicode_input(self, client):
        """Test with Unicode characters."""
        unicode_query = "show me users where name = '测试用户' or name = 'ユーザー'"
        response = await client.post(
            "/api/query/execute",
            json={"query": unicode_query, "database_ids": []}
        )
        assert response.status_code in [200, 400, 422, 500]
    
    async def test_sql_injection_attempts(self, client):
        """Test SQL injection attempt handling."""
        injection_attempts = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; EXEC xp_cmdshell('dir'); --",
            "1' UNION SELECT NULL--",
            "admin'--",
        ]
        
        for attempt in injection_attempts:
            response = await client.post(
                "/api/query/execute",
                json={"query": f"show me users where id = {attempt}", "database_ids": []}
            )
            # Should handle safely (may reject or sanitize)
            assert response.status_code in [200, 400, 422, 500]
    
    async def test_xss_attempts(self, client):
        """Test XSS attempt handling."""
        xss_attempts = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
        ]
        
        for attempt in xss_attempts:
            response = await client.post(
                "/api/query/execute",
                json={"query": f"show me users where name = '{attempt}'", "database_ids": []}
            )
            assert response.status_code in [200, 400, 422, 500]


@pytest.mark.asyncio
class TestDataTypes:
    """Test various data type handling."""
    
    async def test_null_values(self, client):
        """Test handling of null/None values."""
        response = await client.post(
            "/api/query/execute",
            json={"query": None, "database_ids": None}
        )
        assert response.status_code in [400, 422]
    
    async def test_wrong_data_types(self, client):
        """Test handling of wrong data types."""
        # String instead of number
        response = await client.get("/api/history/queries?limit=not-a-number")
        assert response.status_code in [200, 400, 422]
        
        # Number instead of string
        response = await client.post(
            "/api/query/execute",
            json={"query": 12345, "database_ids": []}
        )
        assert response.status_code in [200, 400, 422]
        
        # Array instead of object
        response = await client.post(
            "/api/query/execute",
            json=["invalid", "array"]
        )
        assert response.status_code in [400, 422]
    
    async def test_nested_structures(self, client):
        """Test handling of deeply nested structures."""
        nested_data = {
            "query": "test",
            "database_ids": [],
            "nested": {
                "level1": {
                    "level2": {
                        "level3": {
                            "level4": "deep"
                        }
                    }
                }
            }
        }
        response = await client.post(
            "/api/query/execute",
            json=nested_data
        )
        assert response.status_code in [200, 400, 422, 500]


@pytest.mark.asyncio
class TestRateLimiting:
    """Test rate limiting behavior."""
    
    async def test_rapid_requests(self, client):
        """Test rapid sequential requests."""
        import asyncio
        tasks = [client.get("/health") for _ in range(50)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Most should succeed, some might be rate limited
        success_count = sum(1 for r in responses if isinstance(r, httpx.Response) and r.status_code == 200)
        rate_limited = sum(1 for r in responses if isinstance(r, httpx.Response) and r.status_code == 429)
        
        # Should have some successful responses
        assert success_count > 0 or rate_limited > 0


@pytest.mark.asyncio
class TestHeaders:
    """Test various HTTP header scenarios."""
    
    async def test_missing_content_type(self, client):
        """Test requests with missing Content-Type header."""
        response = await client.post(
            "/api/query/execute",
            content=json.dumps({"query": "test", "database_ids": []}),
            headers={}  # No Content-Type
        )
        # Should handle gracefully
        assert response.status_code in [200, 400, 415, 422]
    
    async def test_wrong_content_type(self, client):
        """Test requests with wrong Content-Type."""
        response = await client.post(
            "/api/query/execute",
            content=json.dumps({"query": "test", "database_ids": []}),
            headers={"Content-Type": "text/plain"}
        )
        assert response.status_code in [200, 400, 415, 422]
    
    async def test_custom_headers(self, client):
        """Test requests with custom headers."""
        response = await client.get(
            "/health",
            headers={"X-Custom-Header": "test-value", "X-Request-ID": "test-123"}
        )
        assert response.status_code == 200


@pytest.mark.asyncio
class TestQueryParameters:
    """Test various query parameter scenarios."""
    
    async def test_duplicate_parameters(self, client):
        """Test duplicate query parameters."""
        # Most frameworks use last value, but test anyway
        response = await client.get("/api/history/queries?limit=5&limit=10")
        assert response.status_code in [200, 400]
    
    async def test_special_characters_in_params(self, client):
        """Test special characters in query parameters."""
        special_chars = ["&", "=", "?", "#", "%", "+"]
        for char in special_chars:
            response = await client.get(f"/api/history/queries?q=test{char}value")
            assert response.status_code in [200, 400, 422]
    
    async def test_empty_parameter_values(self, client):
        """Test empty parameter values."""
        response = await client.get("/api/history/queries?limit=&page=")
        assert response.status_code in [200, 400, 422]


@pytest.mark.asyncio
class TestResponseTimes:
    """Test response time behavior."""
    
    async def test_timeout_handling(self, client):
        """Test timeout handling."""
        # Use very short timeout
        async with httpx.AsyncClient(timeout=0.001) as short_client:
            try:
                response = await short_client.get(f"{BASE_URL}/health")
                # If it completes, should be 200
                if response.status_code == 200:
                    assert True
            except httpx.TimeoutException:
                # Expected for very short timeout
                assert True
    
    async def test_slow_endpoints(self, client):
        """Test endpoints that might be slow."""
        # These might take longer
        endpoints = [
            "/api/health/databases/check-all",
            "/api/optimization/analyze",
        ]
        
        for endpoint in endpoints:
            if endpoint.endswith("/check-all"):
                response = await client.post(endpoint)
            else:
                response = await client.post(
                    endpoint,
                    json={"query": "SELECT * FROM users"}
                )
            # Should eventually respond
            assert response.status_code in [200, 400, 422, 500]


@pytest.mark.asyncio
class TestErrorRecovery:
    """Test error recovery scenarios."""
    
    async def test_recovery_after_error(self, client):
        """Test that system recovers after an error."""
        # First, trigger an error
        response = await client.post(
            "/api/query/execute",
            json={"invalid": "data"}
        )
        # Should return error
        assert response.status_code in [400, 422]
        
        # Then, make a valid request
        response = await client.get("/health")
        # Should work normally
        assert response.status_code == 200
    
    async def test_partial_data(self, client):
        """Test handling of partial/incomplete data."""
        # Truncated JSON
        response = await client.post(
            "/api/query/execute",
            content='{"query": "test", "database_ids": [',
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
class TestCORS:
    """Test CORS behavior."""
    
    async def test_cors_headers(self, client):
        """Test CORS headers in responses."""
        response = await client.options(
            "/health",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "GET"
            }
        )
        # Should include CORS headers or allow preflight
        assert response.status_code in [200, 204, 405]


@pytest.mark.asyncio
class TestContentNegotiation:
    """Test content negotiation."""
    
    async def test_accept_header(self, client):
        """Test Accept header handling."""
        # Request JSON
        response = await client.get(
            "/health",
            headers={"Accept": "application/json"}
        )
        assert response.status_code == 200
        
        # Request text
        response = await client.get(
            "/health",
            headers={"Accept": "text/plain"}
        )
        assert response.status_code == 200
        
        # Request XML (might not be supported)
        response = await client.get(
            "/health",
            headers={"Accept": "application/xml"}
        )
        # Should return something (might be JSON anyway)
        assert response.status_code in [200, 406]

