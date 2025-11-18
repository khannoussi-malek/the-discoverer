"""Elasticsearch database adapter."""
from elasticsearch import AsyncElasticsearch
from typing import List, Dict, Any, Optional

from src.infrastructure.database.adapters.base import DatabaseAdapter
from src.domain.schema import Schema, Table, Column
from src.core.exceptions import DatabaseConnectionError
from config.settings import get_settings


class ElasticsearchAdapter(DatabaseAdapter):
    """Elasticsearch adapter - Search engine database."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client: Optional[AsyncElasticsearch] = None
        self.settings = get_settings()
    
    async def connect(self) -> None:
        """Create Elasticsearch client."""
        hosts = [f"{self.config['host']}:{self.config.get('port', 9200)}"]
        
        http_auth = None
        if self.config.get("user") and self.config.get("password"):
            http_auth = (self.config["user"], self.config["password"])
        
        self.client = AsyncElasticsearch(
            hosts=hosts,
            http_auth=http_auth,
            timeout=30,
            max_retries=3
        )
        self._connected = True
    
    async def disconnect(self) -> None:
        """Close Elasticsearch client."""
        if self.client:
            await self.client.close()
            self._connected = False
    
    async def extract_schema(self, database_id: str) -> Schema:
        """Extract Elasticsearch schema (indices and mappings)."""
        if not self.client:
            await self.connect()
        
        # Get all indices
        indices = await self.client.indices.get_alias(index="*")
        
        tables = []
        for index_name in indices.keys():
            # Skip system indices
            if index_name.startswith("."):
                continue
            
            # Get mapping
            mapping = await self.client.indices.get_mapping(index=index_name)
            index_mapping = mapping[index_name]["mappings"]
            
            # Extract fields from mapping
            columns = self._extract_fields_from_mapping(index_mapping)
            
            # Get document count
            try:
                count_result = await self.client.count(index=index_name)
                row_count = count_result["count"]
            except:
                row_count = None
            
            tables.append(Table(
                name=index_name,
                columns=columns,
                row_count=row_count
            ))
        
        return Schema(
            database_id=database_id,
            tables=tables
        )
    
    def _extract_fields_from_mapping(
        self,
        mapping: Dict[str, Any],
        prefix: str = ""
    ) -> List[Column]:
        """Recursively extract fields from Elasticsearch mapping."""
        columns = []
        
        if "properties" in mapping:
            for field_name, field_mapping in mapping["properties"].items():
                full_name = f"{prefix}.{field_name}" if prefix else field_name
                
                field_type = field_mapping.get("type", "object")
                
                columns.append(Column(
                    name=full_name,
                    data_type=field_type,
                    nullable=True
                ))
                
                # Recursively extract nested fields
                if "properties" in field_mapping:
                    nested_columns = self._extract_fields_from_mapping(
                        field_mapping,
                        full_name
                    )
                    columns.extend(nested_columns)
        
        return columns
    
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute Elasticsearch query."""
        if not self.client:
            await self.connect()
        
        # Parse query (can be JSON string or dict)
        import json
        if isinstance(query, str):
            try:
                query_dict = json.loads(query)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid Elasticsearch query format: {query}")
        else:
            query_dict = query
        
        # Extract index and query
        index = query_dict.get("index", "_all")
        es_query = query_dict.get("query", {"match_all": {}})
        size = query_dict.get("size", 100)
        
        # Execute search
        response = await self.client.search(
            index=index,
            body={
                "query": es_query,
                "size": size
            }
        )
        
        # Extract hits
        hits = response.get("hits", {}).get("hits", [])
        results = []
        
        for hit in hits:
            result = hit["_source"]
            result["_id"] = hit["_id"]
            result["_index"] = hit["_index"]
            results.append(result)
        
        return results
    
    async def test_connection(self) -> bool:
        """Test Elasticsearch connection."""
        try:
            if not self.client:
                await self.connect()
            
            await self.client.ping()
            return True
        except Exception as e:
            raise DatabaseConnectionError(
                f"Failed to connect to Elasticsearch: {str(e)}",
                database_id=self.config.get("id")
            )
    
    async def get_sample_data(
        self,
        table: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get sample data from index."""
        query = {
            "index": table,
            "query": {"match_all": {}},
            "size": limit
        }
        return await self.execute_query(query)


