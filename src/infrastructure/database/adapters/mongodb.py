"""MongoDB database adapter."""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any, Optional

from src.infrastructure.database.adapters.base import DatabaseAdapter
from src.domain.schema import Schema, Table, Column
from config.settings import get_settings


class MongoDBAdapter(DatabaseAdapter):
    """MongoDB adapter - Same interface, different implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client: Optional[AsyncIOMotorClient] = None
        self.settings = get_settings()
    
    async def connect(self) -> None:
        """Create MongoDB client."""
        connection_string = (
            f"mongodb://{self.config.get('user', '')}:{self.config.get('password', '')}"
            f"@{self.config['host']}:{self.config['port']}"
        )
        self.client = AsyncIOMotorClient(
            connection_string,
            maxPoolSize=self.settings.db_pool_max_size,
            minPoolSize=self.settings.db_pool_min_size
        )
        self._connected = True
    
    async def disconnect(self) -> None:
        """Close MongoDB client."""
        if self.client:
            self.client.close()
            self._connected = False
    
    async def extract_schema(self, database_id: str) -> Schema:
        """Extract MongoDB schema from collections."""
        if not self.client:
            await self.connect()
        
        db = self.client[self.config["database"]]
        collections = await db.list_collection_names()
        
        tables = []
        for collection_name in collections:
            collection = db[collection_name]
            
            # Sample documents to infer schema
            sample_docs = await collection.find().limit(10).to_list(length=10)
            
            # Infer columns from sample documents
            columns = self._infer_columns(sample_docs)
            
            # Get document count
            row_count = await collection.count_documents({})
            
            tables.append(Table(
                name=collection_name,
                columns=columns,
                row_count=row_count
            ))
        
        return Schema(
            database_id=database_id,
            tables=tables
        )
    
    def _infer_columns(self, sample_docs: List[Dict]) -> List[Column]:
        """Infer column structure from sample documents."""
        if not sample_docs:
            return []
        
        # Collect all field names and types
        field_types = {}
        for doc in sample_docs:
            for key, value in doc.items():
                if key not in field_types:
                    field_types[key] = set()
                field_types[key].add(type(value).__name__)
        
        columns = []
        for field_name, types in field_types.items():
            # Determine most common type
            data_type = list(types)[0] if types else "mixed"
            if len(types) > 1:
                data_type = "mixed"
            
            columns.append(Column(
                name=field_name,
                data_type=data_type,
                nullable=True  # MongoDB fields are always nullable
            ))
        
        return columns
    
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute MongoDB query."""
        if not self.client:
            await self.connect()
        
        # Parse query (can be JSON string or dict)
        import json
        if isinstance(query, str):
            try:
                query_dict = json.loads(query)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid MongoDB query format: {query}")
        else:
            query_dict = query
        
        # Query format: {"collection": "users", "filter": {...}, "limit": 100, "operation": "count"}
        collection_name = query_dict.get("collection")
        if not collection_name:
            raise ValueError("MongoDB query must include 'collection' field")
        
        collection = self.client[self.config["database"]][collection_name]
        
        # Handle different operations
        operation = query_dict.get("operation", "find")
        filter_dict = query_dict.get("filter", {})
        limit = query_dict.get("limit", 100)
        
        if operation == "count":
            count = await collection.count_documents(filter_dict)
            return [{"count": count}]
        else:
            # Default: find operation
            cursor = collection.find(filter_dict).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string
            for result in results:
                if "_id" in result:
                    result["_id"] = str(result["_id"])
            
            return results
    
    async def test_connection(self) -> bool:
        """Test MongoDB connection."""
        try:
            if not self.client:
                await self.connect()
            await self.client.admin.command('ping')
            return True
        except Exception:
            return False
    
    async def get_sample_data(
        self,
        table: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get sample data from collection."""
        collection = self.client[self.config["database"]][table]
        cursor = collection.find().limit(limit)
        results = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for result in results:
            if "_id" in result:
                result["_id"] = str(result["_id"])
        
        return results

