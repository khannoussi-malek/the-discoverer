"""The Discoverer Python SDK client."""
import httpx
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DiscovererConfig:
    """SDK configuration."""
    base_url: str = "http://localhost:8000"
    api_key: Optional[str] = None
    timeout: float = 30.0


class DiscovererClient:
    """Python SDK client for The Discoverer."""
    
    def __init__(self, config: Optional[DiscovererConfig] = None):
        self.config = config or DiscovererConfig()
        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers={"Authorization": f"Bearer {self.config.api_key}"} if self.config.api_key else {}
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def close(self):
        """Close the client."""
        await self.client.aclose()
    
    # Discovery methods
    async def register_database(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Register a database."""
        response = await self.client.post("/api/discovery/databases", json=config)
        response.raise_for_status()
        return response.json()
    
    async def list_databases(self) -> List[Dict[str, Any]]:
        """List all databases."""
        response = await self.client.get("/api/discovery/databases")
        response.raise_for_status()
        return response.json()
    
    async def get_database(self, database_id: str) -> Dict[str, Any]:
        """Get database by ID."""
        response = await self.client.get(f"/api/discovery/databases/{database_id}")
        response.raise_for_status()
        return response.json()
    
    async def sync_database(self, database_id: str) -> Dict[str, Any]:
        """Sync database schema."""
        response = await self.client.post(f"/api/discovery/databases/{database_id}/sync")
        response.raise_for_status()
        return response.json()
    
    # Query methods
    async def execute_query(
        self,
        query: str,
        database_ids: Optional[List[str]] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute a natural language query."""
        data = {"query": query}
        if database_ids:
            data["database_ids"] = database_ids
        
        params = {}
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size
        
        response = await self.client.post("/api/query/execute", json=data, params=params)
        response.raise_for_status()
        return response.json()
    
    async def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze a query without executing it."""
        response = await self.client.post("/api/query/analyze", json={"query": query})
        response.raise_for_status()
        return response.json()
    
    # Visualization methods
    async def generate_chart(
        self,
        query_id: str,
        chart_type: str,
        x_axis: Optional[str] = None,
        y_axis: Optional[str] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a chart from query result."""
        data = {
            "query_id": query_id,
            "chart_type": chart_type
        }
        if x_axis:
            data["x_axis"] = x_axis
        if y_axis:
            data["y_axis"] = y_axis
        if title:
            data["title"] = title
        
        response = await self.client.post("/api/visualization/generate", json=data)
        response.raise_for_status()
        return response.json()
    
    # Template methods
    async def create_template(
        self,
        name: str,
        query: str,
        database_ids: Optional[List[str]] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a query template."""
        data = {
            "name": name,
            "user_query": query
        }
        if database_ids:
            data["database_ids"] = database_ids
        if description:
            data["description"] = description
        if tags:
            data["tags"] = tags
        
        response = await self.client.post("/api/templates", json=data)
        response.raise_for_status()
        return response.json()
    
    async def list_templates(
        self,
        page: int = 1,
        page_size: int = 20,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """List query templates."""
        params = {"page": page, "page_size": page_size}
        if tags:
            params["tags"] = ",".join(tags)
        
        response = await self.client.get("/api/templates", params=params)
        response.raise_for_status()
        return response.json()
    
    async def execute_template(
        self,
        template_id: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a query template."""
        data = {"template_id": template_id}
        if parameters:
            data["parameters"] = parameters
        
        response = await self.client.post(f"/api/templates/{template_id}/execute", json=data)
        response.raise_for_status()
        return response.json()
    
    # Export methods
    async def export_query(
        self,
        query_id: str,
        format: str = "csv"
    ) -> bytes:
        """Export query result."""
        response = await self.client.get(
            f"/api/export/query/{query_id}",
            params={"format": format}
        )
        response.raise_for_status()
        return response.content
    
    # Health methods
    async def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        response = await self.client.get("/health")
        response.raise_for_status()
        return response.json()
    
    # Analytics methods
    async def get_analytics(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get usage analytics."""
        response = await self.client.get("/api/analytics/stats", params={"days": days})
        response.raise_for_status()
        return response.json()
    
    async def get_top_queries(
        self,
        limit: int = 10,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get top queries."""
        response = await self.client.get(
            "/api/analytics/top-queries",
            params={"limit": limit, "days": days}
        )
        response.raise_for_status()
        return response.json()


