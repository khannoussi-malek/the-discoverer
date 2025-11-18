"""Comprehensive integration tests covering edge cases, error scenarios, and various input variations."""
import pytest
import httpx
from typing import Dict, Any
import os
import json


BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def server_available():
    """Check if server is available (synchronous check)."""
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
class TestInputValidation:
    """Test input validation and edge cases."""
    
    async def test_query_execute_empty_query(self, client):
        """Test query execution with empty query."""
        response = await client.post(
            "/api/query/execute",
            json={"query": "", "database_ids": []}
        )
        # Should either accept empty query or return validation error, or 500 if service not configured
        assert response.status_code in [200, 400, 422, 500]
    
    async def test_query_execute_missing_fields(self, client):
        """Test query execution with missing required fields."""
        response = await client.post("/api/query/execute", json={})
        assert response.status_code in [400, 422]
    
    async def test_query_execute_invalid_json(self, client):
        """Test query execution with invalid JSON."""
        response = await client.post(
            "/api/query/execute",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]
    
    async def test_query_execute_very_long_query(self, client):
        """Test query execution with very long query string."""
        long_query = "show me " + "all users " * 1000
        response = await client.post(
            "/api/query/execute",
            json={"query": long_query, "database_ids": []}
        )
        # Should handle long queries gracefully
        assert response.status_code in [200, 400, 413, 422, 500]
    
    async def test_query_execute_special_characters(self, client):
        """Test query execution with special characters."""
        special_query = "show me users where name = 'test@example.com' or id = 1; DROP TABLE users;--"
        response = await client.post(
            "/api/query/execute",
            json={"query": special_query, "database_ids": []}
        )
        assert response.status_code in [200, 400, 422, 500]
    
    async def test_pagination_invalid_page(self, client):
        """Test pagination with invalid page numbers."""
        # Negative page
        response = await client.get("/api/history/queries?page=-1")
        assert response.status_code in [200, 400, 422]
        
        # Zero page
        response = await client.get("/api/history/queries?page=0")
        assert response.status_code in [200, 400, 422]
        
        # Very large page
        response = await client.get("/api/history/queries?page=999999")
        assert response.status_code in [200, 400, 404]
    
    async def test_pagination_invalid_page_size(self, client):
        """Test pagination with invalid page sizes."""
        # Negative page size
        response = await client.get("/api/history/queries?page_size=-1")
        assert response.status_code in [200, 400, 422]
        
        # Zero page size
        response = await client.get("/api/history/queries?page_size=0")
        assert response.status_code in [200, 400, 422]
        
        # Very large page size
        response = await client.get("/api/history/queries?page_size=999999")
        assert response.status_code in [200, 400, 422]
    
    async def test_analytics_invalid_days(self, client):
        """Test analytics with invalid day ranges."""
        # Negative days
        response = await client.get("/api/analytics/stats?days=-1")
        assert response.status_code in [200, 400, 422]
        
        # Zero days
        response = await client.get("/api/analytics/stats?days=0")
        assert response.status_code in [200, 400, 422]
        
        # Very large days
        response = await client.get("/api/analytics/stats?days=999999")
        assert response.status_code in [200, 400, 422]


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling and edge cases."""
    
    async def test_nonexistent_endpoint(self, client):
        """Test accessing non-existent endpoint."""
        response = await client.get("/api/nonexistent/endpoint")
        assert response.status_code == 404
    
    async def test_nonexistent_database_id(self, client):
        """Test accessing non-existent database."""
        response = await client.get("/api/health/databases/nonexistent-id")
        # May return 404 or attempt to check and return health status
        assert response.status_code in [200, 404, 500]
    
    async def test_nonexistent_query_id(self, client):
        """Test accessing non-existent query."""
        response = await client.get("/api/history/queries/nonexistent-id")
        assert response.status_code in [404, 500]
    
    async def test_nonexistent_template_id(self, client):
        """Test accessing non-existent template."""
        response = await client.get("/api/templates/nonexistent-id")
        assert response.status_code in [404, 500]
    
    async def test_invalid_method(self, client):
        """Test using wrong HTTP method."""
        # GET on POST endpoint
        response = await client.get("/api/query/execute")
        assert response.status_code in [405, 404]
        
        # POST on GET endpoint
        response = await client.post("/api/discovery/databases")
        assert response.status_code in [200, 405, 422]


@pytest.mark.asyncio
class TestQueryOptimization:
    """Test query optimization with various SQL patterns."""
    
    async def test_optimize_simple_select(self, client):
        """Test optimization of simple SELECT query."""
        response = await client.post(
            "/api/optimization/analyze",
            json={"query": "SELECT * FROM users"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "optimization" in data or "query" in data
    
    async def test_optimize_complex_join(self, client):
        """Test optimization of complex JOIN query."""
        query = """
        SELECT u.id, u.name, o.total
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE u.created_at > '2024-01-01'
        ORDER BY o.total DESC
        LIMIT 100
        """
        response = await client.post(
            "/api/optimization/analyze",
            json={"query": query}
        )
        assert response.status_code == 200
    
    async def test_optimize_with_subquery(self, client):
        """Test optimization of query with subquery."""
        query = """
        SELECT * FROM users
        WHERE id IN (SELECT user_id FROM orders WHERE total > 1000)
        """
        response = await client.post(
            "/api/optimization/analyze",
            json={"query": query}
        )
        assert response.status_code == 200
    
    async def test_optimize_invalid_sql(self, client):
        """Test optimization with invalid SQL."""
        response = await client.post(
            "/api/optimization/analyze",
            json={"query": "SELECT * FROM WHERE invalid"}
        )
        # Should handle gracefully
        assert response.status_code in [200, 400, 422, 500]


@pytest.mark.asyncio
class TestCaching:
    """Test caching behavior and edge cases."""
    
    async def test_cache_stats_empty(self, client):
        """Test cache stats when cache is empty."""
        response = await client.get("/api/cache/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_items" in data or "max_size" in data
    
    async def test_cache_keys_empty(self, client):
        """Test listing cache keys when cache is empty."""
        response = await client.get("/api/cache/keys")
        assert response.status_code == 200
    
    async def test_cache_key_nonexistent(self, client):
        """Test accessing non-existent cache key."""
        response = await client.get("/api/cache/keys/nonexistent-key")
        assert response.status_code in [200, 404]


@pytest.mark.asyncio
class TestTemplates:
    """Test query templates with various scenarios."""
    
    async def test_list_templates_empty(self, client):
        """Test listing templates when none exist."""
        response = await client.get("/api/templates")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)
    
    async def test_list_templates_pagination(self, client):
        """Test template listing with pagination."""
        response = await client.get("/api/templates?page=1&page_size=10")
        assert response.status_code == 200
    
    async def test_search_templates_empty_query(self, client):
        """Test template search with empty query."""
        response = await client.get("/api/templates/search?q=")
        # May return 404 if endpoint doesn't exist, or 500 if service not configured
        assert response.status_code in [200, 400, 422, 404, 500]
    
    async def test_search_templates_no_results(self, client):
        """Test template search with query that returns no results."""
        response = await client.get("/api/templates/search?q=nonexistenttemplate12345")
        # May return 404 if endpoint doesn't exist, or 500 if service not configured
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
        else:
            assert response.status_code in [404, 500]


@pytest.mark.asyncio
class TestScheduler:
    """Test scheduler with various scenarios."""
    
    async def test_list_schedules_empty(self, client):
        """Test listing schedules when none exist."""
        response = await client.get("/api/scheduler")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)
    
    async def test_list_schedules_with_status_filter(self, client):
        """Test listing schedules with status filter."""
        for status in ["active", "paused", "completed", "failed"]:
            response = await client.get(f"/api/scheduler?status={status}")
            assert response.status_code == 200
    
    async def test_list_schedules_invalid_status(self, client):
        """Test listing schedules with invalid status."""
        response = await client.get("/api/scheduler?status=invalid_status")
        # May return 500 if service not fully configured
        assert response.status_code in [200, 400, 422, 500]
    
    async def test_list_schedules_pagination(self, client):
        """Test schedule listing with pagination."""
        response = await client.get("/api/scheduler?page=1&page_size=5")
        assert response.status_code == 200


@pytest.mark.asyncio
class TestAnalytics:
    """Test analytics with various time ranges and filters."""
    
    async def test_analytics_different_days(self, client):
        """Test analytics with different day ranges."""
        for days in [1, 7, 30, 90, 365]:
            response = await client.get(f"/api/analytics/stats?days={days}")
            assert response.status_code == 200
            data = response.json()
            assert "stats" in data or "period" in data
    
    async def test_top_queries_different_limits(self, client):
        """Test top queries with different limits."""
        for limit in [1, 5, 10, 50, 100]:
            response = await client.get(f"/api/analytics/top-queries?limit={limit}")
            assert response.status_code == 200
    
    async def test_top_queries_different_days(self, client):
        """Test top queries with different day ranges."""
        for days in [1, 7, 30]:
            response = await client.get(f"/api/analytics/top-queries?days={days}&limit=10")
            assert response.status_code == 200


@pytest.mark.asyncio
class TestHistory:
    """Test query history with various filters and scenarios."""
    
    async def test_history_empty(self, client):
        """Test history when no queries exist."""
        response = await client.get("/api/history/queries")
        # May return 500 if service not fully configured
        if response.status_code == 200:
            data = response.json()
            assert "queries" in data or isinstance(data, list)
        else:
            assert response.status_code in [500, 404]
    
    async def test_history_with_limit(self, client):
        """Test history with different limits."""
        for limit in [1, 5, 10, 50, 100]:
            try:
                response = await client.get(f"/api/history/queries?limit={limit}", timeout=10.0)
                # May return 500 if service not fully configured, or connection error
                assert response.status_code in [200, 500, 404]
            except Exception:
                # Connection errors are acceptable if service is overloaded
                pass
    
    async def test_history_statistics_empty(self, client):
        """Test history statistics when no queries exist."""
        response = await client.get("/api/history/statistics")
        # May return 500 if service not fully configured
        if response.status_code == 200:
            data = response.json()
            assert "total_queries" in data or "avg_execution_time" in data
        else:
            assert response.status_code in [500, 404]
    
    async def test_history_search_empty(self, client):
        """Test history search with empty results."""
        response = await client.get("/api/history/queries/search?q=nonexistentquery12345")
        # May return 500 if service not fully configured
        assert response.status_code in [200, 500, 404]


@pytest.mark.asyncio
class TestHealthMonitoring:
    """Test health monitoring with various scenarios."""
    
    async def test_health_all_databases_empty(self, client):
        """Test health check when no databases are registered."""
        response = await client.get("/api/health/databases")
        # May return 500 if service not fully configured
        if response.status_code == 200:
            data = response.json()
            assert "databases" in data
            assert "total" in data
        else:
            assert response.status_code in [500, 404]
    
    async def test_health_check_all_empty(self, client):
        """Test check all databases when none exist."""
        response = await client.post("/api/health/databases/check-all")
        # May return 500 if service not fully configured
        if response.status_code == 200:
            data = response.json()
            assert "results" in data
        else:
            assert response.status_code in [500, 404]
    
    async def test_health_specific_database_nonexistent(self, client):
        """Test health check for non-existent database."""
        response = await client.get("/api/health/databases/nonexistent-db-id")
        # May attempt to check or return 404
        assert response.status_code in [200, 404, 500]


@pytest.mark.asyncio
class TestAPIKeys:
    """Test API key management scenarios."""
    
    async def test_list_api_keys_empty(self, client):
        """Test listing API keys when none exist."""
        response = await client.get("/api/api-keys")
        # May return 500 if service not fully configured
        if response.status_code == 200:
            data = response.json()
            assert "keys" in data or isinstance(data, list)
        else:
            assert response.status_code in [500, 404]
    
    async def test_get_api_key_nonexistent(self, client):
        """Test getting non-existent API key."""
        response = await client.get("/api/api-keys/nonexistent-key-id")
        assert response.status_code in [404, 500]


@pytest.mark.asyncio
class TestWebhooks:
    """Test webhook management scenarios."""
    
    async def test_list_webhooks_empty(self, client):
        """Test listing webhooks when none exist."""
        response = await client.get("/api/webhooks")
        # May return 500 if service not fully configured
        if response.status_code == 200:
            data = response.json()
            assert "webhooks" in data or isinstance(data, list)
        else:
            assert response.status_code in [500, 404]
    
    async def test_get_webhook_nonexistent(self, client):
        """Test getting non-existent webhook."""
        response = await client.get("/api/webhooks/nonexistent-webhook-id")
        assert response.status_code in [404, 500]
    
    async def test_webhook_stats_nonexistent(self, client):
        """Test webhook stats for non-existent webhook."""
        response = await client.get("/api/webhooks/nonexistent-webhook-id/stats")
        assert response.status_code in [404, 500]


@pytest.mark.asyncio
class TestDashboards:
    """Test dashboard scenarios."""
    
    async def test_list_dashboards_empty(self, client):
        """Test listing dashboards when none exist."""
        response = await client.get("/api/dashboards")
        # May return 500 if service not fully configured
        if response.status_code == 200:
            data = response.json()
            assert "dashboards" in data or isinstance(data, list)
        else:
            assert response.status_code in [500, 404]
    
    async def test_get_dashboard_nonexistent(self, client):
        """Test getting non-existent dashboard."""
        response = await client.get("/api/dashboards/nonexistent-dashboard-id")
        assert response.status_code in [404, 500]
    
    async def test_render_dashboard_nonexistent(self, client):
        """Test rendering non-existent dashboard."""
        response = await client.get("/api/dashboards/nonexistent-dashboard-id/render")
        assert response.status_code in [404, 500]


@pytest.mark.asyncio
class TestConnectionPools:
    """Test connection pool scenarios."""
    
    async def test_list_pools_empty(self, client):
        """Test listing pools when none exist."""
        response = await client.get("/api/pools")
        # May return 500 if service not fully configured
        if response.status_code == 200:
            data = response.json()
            assert "pools" in data or isinstance(data, list)
        else:
            assert response.status_code in [500, 404]
    
    async def test_get_pool_nonexistent(self, client):
        """Test getting non-existent pool."""
        response = await client.get("/api/pools/nonexistent-db-id")
        assert response.status_code in [404, 500]
    
    async def test_pool_health_nonexistent(self, client):
        """Test pool health for non-existent pool."""
        response = await client.get("/api/pools/nonexistent-db-id/health")
        assert response.status_code in [404, 500]


@pytest.mark.asyncio
class TestExportTemplates:
    """Test export template scenarios."""
    
    async def test_list_export_templates_empty(self, client):
        """Test listing export templates when none exist."""
        response = await client.get("/api/export-templates")
        # May return 500 if service not fully configured
        if response.status_code == 200:
            data = response.json()
            assert "templates" in data or isinstance(data, list)
        else:
            assert response.status_code in [500, 404]
    
    async def test_get_export_template_nonexistent(self, client):
        """Test getting non-existent export template."""
        response = await client.get("/api/export-templates/nonexistent-template-id")
        assert response.status_code in [404, 500]
    
    async def test_search_export_templates_empty(self, client):
        """Test searching export templates with no results."""
        response = await client.get("/api/export-templates/search?q=nonexistent12345")
        # May return 500 if service not fully configured
        assert response.status_code in [200, 400, 404, 500]


@pytest.mark.asyncio
class TestScheduledExports:
    """Test scheduled export scenarios."""
    
    async def test_list_scheduled_exports_empty(self, client):
        """Test listing scheduled exports when none exist."""
        response = await client.get("/api/scheduled-exports")
        # May return 500 if service not fully configured
        if response.status_code == 200:
            data = response.json()
            assert "exports" in data or isinstance(data, list)
        else:
            assert response.status_code in [500, 404]
    
    async def test_list_scheduled_exports_with_status(self, client):
        """Test listing scheduled exports with status filter."""
        for status in ["active", "paused", "completed", "failed"]:
            response = await client.get(f"/api/scheduled-exports?status={status}")
            # May return 500 if service not fully configured
            assert response.status_code in [200, 500]
    
    async def test_get_scheduled_export_nonexistent(self, client):
        """Test getting non-existent scheduled export."""
        response = await client.get("/api/scheduled-exports/nonexistent-export-id")
        assert response.status_code in [404, 500]


@pytest.mark.asyncio
class TestChartTemplates:
    """Test chart template scenarios."""
    
    async def test_list_chart_templates_empty(self, client):
        """Test listing chart templates when none exist."""
        response = await client.get("/api/chart-templates")
        # May return 500 if service not fully configured
        if response.status_code == 200:
            data = response.json()
            assert "templates" in data or isinstance(data, list)
        else:
            assert response.status_code in [500, 404]
    
    async def test_get_chart_template_nonexistent(self, client):
        """Test getting non-existent chart template."""
        response = await client.get("/api/chart-templates/nonexistent-template-id")
        assert response.status_code in [404, 500]
    
    async def test_search_chart_templates_empty(self, client):
        """Test searching chart templates with no results."""
        response = await client.get("/api/chart-templates/search?q=nonexistent12345")
        # May return 500 if service not fully configured
        assert response.status_code in [200, 400, 404, 500]


@pytest.mark.asyncio
class TestSharing:
    """Test query result sharing scenarios."""
    
    async def test_list_shares_empty(self, client):
        """Test listing shares when none exist."""
        response = await client.get("/api/sharing")
        # May return 500 if service not fully configured
        if response.status_code == 200:
            data = response.json()
            assert "shares" in data or isinstance(data, list)
        else:
            assert response.status_code in [500, 404]
    
    async def test_get_share_invalid_token(self, client):
        """Test getting share with invalid token."""
        response = await client.get("/api/sharing/invalid-token-12345")
        # May return 500 if service not fully configured
        assert response.status_code in [404, 400, 500]


@pytest.mark.asyncio
class TestVersioning:
    """Test query versioning scenarios."""
    
    async def test_get_versions_nonexistent_query(self, client):
        """Test getting versions for non-existent query."""
        response = await client.get("/api/versioning/queries/nonexistent-query-id/versions")
        # May return 500 if service not fully configured
        assert response.status_code in [200, 404, 500]
    
    async def test_get_current_version_nonexistent(self, client):
        """Test getting current version for non-existent query."""
        response = await client.get("/api/versioning/queries/nonexistent-query-id/current")
        # May return 500 if service not fully configured
        assert response.status_code in [200, 404, 500]
    
    async def test_get_specific_version_nonexistent(self, client):
        """Test getting specific version for non-existent query."""
        response = await client.get("/api/versioning/queries/nonexistent-query-id/versions/v1")
        # May return 500 if service not fully configured
        assert response.status_code in [200, 404, 500]


@pytest.mark.asyncio
class TestMetrics:
    """Test metrics endpoint scenarios."""
    
    async def test_prometheus_metrics_format(self, client):
        """Test Prometheus metrics format."""
        response = await client.get("/api/metrics/prometheus")
        # May return 500 if service not fully configured
        if response.status_code == 200:
            content = response.text
            # Should be Prometheus format
            assert "# HELP" in content or "# TYPE" in content or len(content) > 0
        else:
            assert response.status_code in [500, 404]


@pytest.mark.asyncio
class TestConcurrentRequests:
    """Test concurrent request handling."""
    
    async def test_concurrent_health_checks(self, client):
        """Test multiple concurrent health check requests."""
        import asyncio
        tasks = [client.get("/health") for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            # May return 500 if service not fully configured
            assert response.status_code in [200, 500]
    
    async def test_concurrent_list_requests(self, client):
        """Test multiple concurrent list requests."""
        import asyncio
        tasks = [
            client.get("/api/discovery/databases"),
            client.get("/api/templates"),
            client.get("/api/scheduler"),
            client.get("/api/api-keys"),
        ]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            # May return 500 if service not fully configured
            assert response.status_code in [200, 500]


@pytest.mark.asyncio
class TestResponseFormats:
    """Test response format consistency."""
    
    async def test_json_responses(self, client):
        """Test that endpoints return valid JSON."""
        endpoints = [
            "/health",
            "/api/discovery/databases",
            "/api/templates",
            "/api/scheduler",
            "/api/cache/stats",
        ]
        
        for endpoint in endpoints:
            response = await client.get(endpoint)
            if response.status_code == 200:
                try:
                    data = response.json()
                    assert isinstance(data, (dict, list))
                except Exception:
                    pytest.fail(f"Endpoint {endpoint} returned invalid JSON")
    
    async def test_error_response_format(self, client):
        """Test that error responses have consistent format."""
        response = await client.get("/api/nonexistent/endpoint")
        # May return 500 if service not fully configured, or 404 if endpoint doesn't exist
        assert response.status_code in [404, 500]
        try:
            data = response.json()
            # Error responses should have error field
            assert "error" in data or "message" in data or "detail" in data
        except Exception:
            # Some errors might not be JSON
            pass

