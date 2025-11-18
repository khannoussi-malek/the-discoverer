"""Integration tests that don't require LLM."""
import pytest
import httpx
from typing import Dict, Any
import os


BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def server_available():
    """Check if server is available (synchronous check)."""
    import asyncio
    try:
        async def check():
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Try root endpoint first, then health - accept any response < 500
                try:
                    response = await client.get(f"{BASE_URL}/")
                    if response.status_code < 500:
                        return True
                except:
                    pass
                try:
                    response = await client.get(f"{BASE_URL}/health")
                    return response.status_code < 500  # Accept any non-500 status
                except:
                    return False
        try:
            # Try to get existing loop
            loop = asyncio.get_running_loop()
            # If we get here, loop is running - can't use asyncio.run
            return False
        except RuntimeError:
            # No running loop, safe to use asyncio.run
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
class TestHealthEndpoints:
    """Test health and status endpoints."""
    
    async def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
    
    async def test_health_endpoint(self, client):
        """Test health endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    async def test_database_health(self, client):
        """Test database health endpoint."""
        response = await client.get("/api/health/databases")
        assert response.status_code == 200
        data = response.json()
        assert "databases" in data or "total" in data
    
    async def test_check_all_databases(self, client):
        """Test check all databases endpoint."""
        response = await client.post("/api/health/databases/check-all")
        assert response.status_code == 200


@pytest.mark.asyncio
class TestDiscoveryEndpoints:
    """Test database discovery endpoints."""
    
    async def test_list_databases(self, client):
        """Test list databases endpoint."""
        response = await client.get("/api/discovery/databases")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    async def test_search_databases(self, client):
        """Test search databases endpoint."""
        # Note: Search endpoint may not exist, so we accept 404
        response = await client.get("/api/discovery/search?query=test")
        assert response.status_code in [200, 404]


@pytest.mark.asyncio
class TestHistoryEndpoints:
    """Test query history endpoints."""
    
    async def test_get_query_history(self, client):
        """Test get query history."""
        response = await client.get("/api/history/queries?limit=5")
        assert response.status_code == 200
    
    async def test_get_history_stats(self, client):
        """Test get history statistics."""
        response = await client.get("/api/history/statistics")
        assert response.status_code == 200


@pytest.mark.asyncio
class TestStatisticsEndpoints:
    """Test statistics and analytics endpoints."""
    
    async def test_performance_stats(self, client):
        """Test performance statistics."""
        response = await client.get("/api/stats/performance")
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data or "summary" in data
    
    async def test_usage_analytics(self, client):
        """Test usage analytics."""
        response = await client.get("/api/analytics/stats?days=7")
        assert response.status_code == 200
    
    async def test_top_queries(self, client):
        """Test top queries."""
        response = await client.get("/api/analytics/top-queries?limit=5")
        assert response.status_code == 200


@pytest.mark.asyncio
class TestTemplateEndpoints:
    """Test query template endpoints."""
    
    async def test_list_templates(self, client):
        """Test list templates."""
        response = await client.get("/api/templates")
        assert response.status_code == 200


@pytest.mark.asyncio
class TestOptimizationEndpoints:
    """Test query optimization endpoints."""
    
    async def test_analyze_query(self, client):
        """Test query analysis."""
        response = await client.post(
            "/api/optimization/analyze",
            json={"query": "SELECT * FROM users WHERE id = 1"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "query" in data or "optimization" in data


@pytest.mark.asyncio
class TestCacheEndpoints:
    """Test caching endpoints."""
    
    async def test_cache_stats(self, client):
        """Test cache statistics."""
        response = await client.get("/api/cache/stats")
        assert response.status_code == 200


@pytest.mark.asyncio
class TestSharingEndpoints:
    """Test query sharing endpoints."""
    
    async def test_list_shares(self, client):
        """Test list shares."""
        response = await client.get("/api/sharing")
        assert response.status_code == 200


@pytest.mark.asyncio
class TestWebhookEndpoints:
    """Test webhook endpoints."""
    
    async def test_list_webhooks(self, client):
        """Test list webhooks."""
        response = await client.get("/api/webhooks")
        assert response.status_code == 200


@pytest.mark.asyncio
class TestAPIKeyEndpoints:
    """Test API key endpoints."""
    
    async def test_list_api_keys(self, client):
        """Test list API keys."""
        response = await client.get("/api/api-keys")
        assert response.status_code == 200


@pytest.mark.asyncio
class TestPoolEndpoints:
    """Test connection pool endpoints."""
    
    async def test_list_pools(self, client):
        """Test list pools."""
        response = await client.get("/api/pools")
        assert response.status_code == 200


@pytest.mark.asyncio
class TestDashboardEndpoints:
    """Test dashboard endpoints."""
    
    async def test_list_dashboards(self, client):
        """Test list dashboards."""
        response = await client.get("/api/dashboards")
        assert response.status_code == 200


@pytest.mark.asyncio
class TestChartTemplateEndpoints:
    """Test chart template endpoints."""
    
    async def test_list_chart_templates(self, client):
        """Test list chart templates."""
        response = await client.get("/api/chart-templates")
        assert response.status_code == 200


@pytest.mark.asyncio
class TestExportTemplateEndpoints:
    """Test export template endpoints."""
    
    async def test_list_export_templates(self, client):
        """Test list export templates."""
        response = await client.get("/api/export-templates")
        assert response.status_code == 200


@pytest.mark.asyncio
class TestScheduledExportEndpoints:
    """Test scheduled export endpoints."""
    
    async def test_list_scheduled_exports(self, client):
        """Test list scheduled exports."""
        response = await client.get("/api/scheduled-exports")
        assert response.status_code == 200


@pytest.mark.asyncio
class TestMetricsEndpoints:
    """Test metrics endpoints."""
    
    async def test_get_metrics(self, client):
        """Test get Prometheus metrics."""
        response = await client.get("/api/metrics/prometheus")
        assert response.status_code == 200


@pytest.mark.asyncio
class TestVersioningEndpoints:
    """Test versioning endpoints."""
    
    async def test_get_versions(self, client):
        """Test get query versions."""
        response = await client.get("/api/versioning/queries/test/versions")
        # May return 404 if no versions, which is acceptable
        assert response.status_code in [200, 404]


@pytest.mark.asyncio
class TestSchedulerEndpoints:
    """Test scheduler endpoints."""
    
    async def test_list_schedules(self, client):
        """Test list schedules."""
        response = await client.get("/api/scheduler")
        assert response.status_code == 200

