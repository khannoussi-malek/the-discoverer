"""Cassandra database adapter."""
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
from typing import List, Dict, Any, Optional
import asyncio

from src.infrastructure.database.adapters.base import DatabaseAdapter
from src.domain.schema import Schema, Table, Column
from src.core.exceptions import DatabaseConnectionError
from config.settings import get_settings


class CassandraAdapter(DatabaseAdapter):
    """Cassandra adapter - CQL database."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.cluster: Optional[Cluster] = None
        self.session = None
        self.settings = get_settings()
    
    async def connect(self) -> None:
        """Create Cassandra cluster connection."""
        # Cassandra driver is synchronous, so we run in executor
        loop = asyncio.get_event_loop()
        
        contact_points = [self.config["host"]]
        port = self.config.get("port", 9042)
        
        auth_provider = None
        if self.config.get("user") and self.config.get("password"):
            auth_provider = PlainTextAuthProvider(
                username=self.config["user"],
                password=self.config["password"]
            )
        
        self.cluster = await loop.run_in_executor(
            None,
            lambda: Cluster(
                contact_points=contact_points,
                port=port,
                auth_provider=auth_provider
            )
        )
        
        keyspace = self.config.get("database") or self.config.get("keyspace")
        if keyspace:
            self.session = await loop.run_in_executor(
                None,
                lambda: self.cluster.connect(keyspace)
            )
        else:
            self.session = await loop.run_in_executor(
                None,
                lambda: self.cluster.connect()
            )
        
        self._connected = True
    
    async def disconnect(self) -> None:
        """Close Cassandra connection."""
        if self.session:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.session.shutdown)
        if self.cluster:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.cluster.shutdown)
        self._connected = False
    
    async def extract_schema(self, database_id: str) -> Schema:
        """Extract Cassandra schema."""
        if not self.session:
            await self.connect()
        
        loop = asyncio.get_event_loop()
        
        # Get keyspaces
        keyspace = self.config.get("database") or self.config.get("keyspace")
        
        # Get tables (column families)
        query = """
            SELECT columnfamily_name 
            FROM system_schema.tables 
            WHERE keyspace_name = %s
        """
        
        rows = await loop.run_in_executor(
            None,
            lambda: self.session.execute(query, [keyspace])
        )
        
        tables = []
        for row in rows:
            table_name = row.columnfamily_name
            
            # Get columns
            columns = await self._get_columns(keyspace, table_name, loop)
            
            tables.append(Table(
                name=table_name,
                columns=columns
            ))
        
        return Schema(
            database_id=database_id,
            tables=tables
        )
    
    async def _get_columns(
        self,
        keyspace: str,
        table_name: str,
        loop: asyncio.AbstractEventLoop
    ) -> List[Column]:
        """Get columns for a table."""
        query = """
            SELECT column_name, type, kind
            FROM system_schema.columns
            WHERE keyspace_name = %s AND table_name = %s
        """
        
        rows = await loop.run_in_executor(
            None,
            lambda: self.session.execute(query, [keyspace, table_name])
        )
        
        columns = []
        for row in rows:
            columns.append(Column(
                name=row.column_name,
                data_type=str(row.type),
                is_primary_key=(row.kind == "partition_key" or row.kind == "clustering")
            ))
        
        return columns
    
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute CQL query."""
        if not self.session:
            await self.connect()
        
        loop = asyncio.get_event_loop()
        
        # Execute CQL query
        statement = SimpleStatement(query, fetch_size=100)
        rows = await loop.run_in_executor(
            None,
            lambda: self.session.execute(statement)
        )
        
        # Convert to dict
        return [dict(row._asdict()) for row in rows]
    
    async def test_connection(self) -> bool:
        """Test database connection."""
        try:
            if not self.session:
                await self.connect()
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.session.execute("SELECT now() FROM system.local")
            )
            return True
        except Exception as e:
            raise DatabaseConnectionError(
                f"Failed to connect to Cassandra database: {str(e)}",
                database_id=self.config.get("id")
            )
    
    async def get_sample_data(
        self,
        table: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get sample data from table."""
        keyspace = self.config.get("database") or self.config.get("keyspace")
        query = f"SELECT * FROM {keyspace}.{table} LIMIT {limit}"
        return await self.execute_query(query)


