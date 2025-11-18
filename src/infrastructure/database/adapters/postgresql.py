"""PostgreSQL database adapter."""
import asyncpg
from typing import List, Dict, Any, Optional

from src.infrastructure.database.adapters.base import DatabaseAdapter
from src.domain.schema import Schema, Table, Column, ForeignKey, Index
from src.core.exceptions import DatabaseConnectionError, SchemaExtractionError
from config.settings import get_settings


class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL adapter - KISS: One responsibility."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.pool: Optional[asyncpg.Pool] = None
        self.settings = get_settings()
    
    async def connect(self) -> None:
        """Create connection pool."""
        self.pool = await asyncpg.create_pool(
            host=self.config["host"],
            port=self.config["port"],
            user=self.config.get("user"),
            password=self.config.get("password"),
            database=self.config["database"],
            min_size=self.settings.db_pool_min_size,
            max_size=self.settings.db_pool_max_size,
            max_queries=self.settings.db_pool_max_queries,
            command_timeout=self.settings.db_query_timeout,
        )
        self._connected = True
    
    async def disconnect(self) -> None:
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            self._connected = False
    
    async def extract_schema(self, database_id: str) -> Schema:
        """Extract PostgreSQL schema."""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            tables = await self._get_tables(conn, database_id)
        
        return Schema(
            database_id=database_id,
            tables=tables,
            relationships=await self._get_relationships(database_id),
            indexes=await self._get_indexes(database_id)
        )
    
    async def _get_tables(
        self, 
        conn: asyncpg.Connection, 
        database_id: str
    ) -> List[Table]:
        """Get all tables with columns."""
        # Get table names
        table_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        table_rows = await conn.fetch(table_query)
        
        tables = []
        for row in table_rows:
            table_name = row['table_name']
            
            # Get columns
            columns = await self._get_columns(conn, table_name)
            
            # Get primary keys
            primary_keys = await self._get_primary_keys(conn, table_name)
            
            # Get foreign keys
            foreign_keys = await self._get_foreign_keys(conn, table_name)
            
            # Get row count
            row_count = await self._get_row_count(conn, table_name)
            
            tables.append(Table(
                name=table_name,
                columns=columns,
                primary_keys=primary_keys,
                foreign_keys=foreign_keys,
                row_count=row_count
            ))
        
        return tables
    
    async def _get_columns(
        self, 
        conn: asyncpg.Connection, 
        table_name: str
    ) -> List[Column]:
        """Get columns for a table."""
        query = """
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = 'public' 
            AND table_name = $1
            ORDER BY ordinal_position
        """
        rows = await conn.fetch(query, table_name)
        
        columns = []
        for row in rows:
            columns.append(Column(
                name=row['column_name'],
                data_type=row['data_type'],
                nullable=row['is_nullable'] == 'YES',
                default_value=row['column_default'],
                max_length=row['character_maximum_length']
            ))
        
        return columns
    
    async def _get_primary_keys(
        self, 
        conn: asyncpg.Connection, 
        table_name: str
    ) -> List[str]:
        """Get primary key columns."""
        query = """
            SELECT column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage AS ccu 
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.table_schema = 'public'
            AND tc.table_name = $1
            AND tc.constraint_type = 'PRIMARY KEY'
        """
        rows = await conn.fetch(query, table_name)
        return [row['column_name'] for row in rows]
    
    async def _get_foreign_keys(
        self, 
        conn: asyncpg.Connection, 
        table_name: str
    ) -> List[ForeignKey]:
        """Get foreign key relationships."""
        query = """
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
            AND tc.table_name = $1
        """
        rows = await conn.fetch(query, table_name)
        
        return [
            ForeignKey(
                column=row['column_name'],
                referenced_table=row['foreign_table_name'],
                referenced_column=row['foreign_column_name']
            )
            for row in rows
        ]
    
    async def _get_row_count(
        self, 
        conn: asyncpg.Connection, 
        table_name: str
    ) -> Optional[int]:
        """Get approximate row count."""
        try:
            query = f'SELECT COUNT(*) FROM "{table_name}"'
            count = await conn.fetchval(query)
            return count
        except:
            return None
    
    async def _get_relationships(self, database_id: str) -> List:
        """Get table relationships (simplified)."""
        # Relationships are extracted from foreign keys
        return []
    
    async def _get_indexes(self, database_id: str) -> List[Index]:
        """Get database indexes."""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            query = """
                SELECT
                    indexname,
                    tablename,
                    indexdef
                FROM pg_indexes
                WHERE schemaname = 'public'
            """
            rows = await conn.fetch(query)
            
            indexes = []
            for row in rows:
                # Parse index definition to extract columns
                # This is simplified - could be more sophisticated
                indexes.append(Index(
                    name=row['indexname'],
                    columns=[],  # Would need to parse indexdef
                    unique='UNIQUE' in row['indexdef']
                ))
            
            return indexes
    
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute SQL query."""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]
    
    async def test_connection(self) -> bool:
        """Test database connection."""
        try:
            if not self.pool:
                await self.connect()
            
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            raise DatabaseConnectionError(
                f"Failed to connect to PostgreSQL database: {str(e)}",
                database_id=self.config.get("id")
            )
    
    async def get_sample_data(
        self, 
        table: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get sample data from table."""
        query = f'SELECT * FROM "{table}" LIMIT {limit}'
        return await self.execute_query(query)

