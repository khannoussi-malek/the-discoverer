"""SQLite database adapter."""
import aiosqlite
from typing import List, Dict, Any, Optional

from src.infrastructure.database.adapters.base import DatabaseAdapter
from src.domain.schema import Schema, Table, Column, ForeignKey
from src.core.exceptions import DatabaseConnectionError
from config.settings import get_settings


class SQLiteAdapter(DatabaseAdapter):
    """SQLite adapter - KISS: One responsibility."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.connection: Optional[aiosqlite.Connection] = None
        self.settings = get_settings()
    
    async def connect(self) -> None:
        """Create SQLite connection."""
        db_path = self.config.get("database") or self.config.get("path")
        if not db_path:
            raise ValueError("SQLite requires 'database' or 'path' in config")
        
        self.connection = await aiosqlite.connect(
            db_path,
            timeout=self.settings.db_query_timeout
        )
        self.connection.row_factory = aiosqlite.Row
        self._connected = True
    
    async def disconnect(self) -> None:
        """Close SQLite connection."""
        if self.connection:
            await self.connection.close()
            self._connected = False
    
    async def extract_schema(self, database_id: str) -> Schema:
        """Extract SQLite schema."""
        if not self.connection:
            await self.connect()
        
        tables = []
        
        # Get table names
        async with self.connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ) as cursor:
            table_rows = await cursor.fetchall()
            
            for row in table_rows:
                table_name = row[0]
                
                # Get columns
                columns = await self._get_columns(table_name)
                
                # Get primary keys
                primary_keys = await self._get_primary_keys(table_name)
                
                # Get row count
                row_count = await self._get_row_count(table_name)
                
                tables.append(Table(
                    name=table_name,
                    columns=columns,
                    primary_keys=primary_keys,
                    row_count=row_count
                ))
        
        return Schema(
            database_id=database_id,
            tables=tables
        )
    
    async def _get_columns(self, table_name: str) -> List[Column]:
        """Get columns for a table."""
        async with self.connection.execute(
            f"PRAGMA table_info({table_name})"
        ) as cursor:
            rows = await cursor.fetchall()
            
            columns = []
            for row in rows:
                columns.append(Column(
                    name=row[1],  # name
                    data_type=row[2],  # type
                    nullable=not row[3],  # notnull (inverted)
                    default_value=row[4],  # dflt_value
                    is_primary_key=row[5] == 1  # pk
                ))
            
            return columns
    
    async def _get_primary_keys(self, table_name: str) -> List[str]:
        """Get primary key columns."""
        columns = await self._get_columns(table_name)
        return [c.name for c in columns if c.is_primary_key]
    
    async def _get_row_count(self, table_name: str) -> Optional[int]:
        """Get row count."""
        try:
            async with self.connection.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
        except Exception:
            return None
    
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute SQL query."""
        if not self.connection:
            await self.connect()
        
        async with self.connection.execute(query) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def test_connection(self) -> bool:
        """Test database connection."""
        try:
            if not self.connection:
                await self.connect()
            
            async with self.connection.execute("SELECT 1") as cursor:
                await cursor.fetchone()
            return True
        except Exception as e:
            raise DatabaseConnectionError(
                f"Failed to connect to SQLite database: {str(e)}",
                database_id=self.config.get("id")
            )
    
    async def get_sample_data(
        self,
        table: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get sample data from table."""
        query = f"SELECT * FROM {table} LIMIT {limit}"
        return await self.execute_query(query)

