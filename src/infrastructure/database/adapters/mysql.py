"""MySQL database adapter."""
import aiomysql
from typing import List, Dict, Any, Optional

from src.infrastructure.database.adapters.base import DatabaseAdapter
from src.domain.schema import Schema, Table, Column, ForeignKey
from config.settings import get_settings


class MySQLAdapter(DatabaseAdapter):
    """MySQL adapter - Similar to PostgreSQL."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.pool: Optional[aiomysql.Pool] = None
        self.settings = get_settings()
    
    async def connect(self) -> None:
        """Create connection pool."""
        self.pool = await aiomysql.create_pool(
            host=self.config["host"],
            port=self.config["port"],
            user=self.config.get("user"),
            password=self.config.get("password"),
            db=self.config["database"],
            minsize=self.settings.db_pool_min_size,
            maxsize=self.settings.db_pool_max_size
        )
        self._connected = True
    
    async def disconnect(self) -> None:
        """Close connection pool."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self._connected = False
    
    async def extract_schema(self, database_id: str) -> Schema:
        """Extract MySQL schema."""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                # Get tables
                await cur.execute("SHOW TABLES")
                table_rows = await cur.fetchall()
                
                tables = []
                for row in table_rows:
                    table_name = list(row.values())[0]  # Get first value
                    
                    # Get columns
                    columns = await self._get_columns(cur, table_name)
                    
                    # Get primary keys
                    primary_keys = await self._get_primary_keys(cur, table_name)
                    
                    # Get row count
                    row_count = await self._get_row_count(cur, table_name)
                    
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
    
    async def _get_columns(self, cur, table_name: str) -> List[Column]:
        """Get columns for a table."""
        await cur.execute(f"DESCRIBE `{table_name}`")
        rows = await cur.fetchall()
        
        columns = []
        for row in rows:
            columns.append(Column(
                name=row["Field"],
                data_type=row["Type"],
                nullable=row["Null"] == "YES",
                default_value=row["Default"],
                is_primary_key=row["Key"] == "PRI"
            ))
        
        return columns
    
    async def _get_primary_keys(self, cur, table_name: str) -> List[str]:
        """Get primary key columns."""
        await cur.execute(f"SHOW KEYS FROM `{table_name}` WHERE Key_name = 'PRIMARY'")
        rows = await cur.fetchall()
        return [row["Column_name"] for row in rows]
    
    async def _get_row_count(self, cur, table_name: str) -> Optional[int]:
        """Get row count."""
        try:
            await cur.execute(f"SELECT COUNT(*) as count FROM `{table_name}`")
            row = await cur.fetchone()
            return row["count"] if row else None
        except Exception:
            return None
    
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute SQL query."""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query)
                rows = await cur.fetchall()
                return [dict(row) for row in rows]
    
    async def test_connection(self) -> bool:
        """Test database connection."""
        try:
            if not self.pool:
                await self.connect()
            
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    async def get_sample_data(
        self,
        table: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get sample data from table."""
        query = f"SELECT * FROM `{table}` LIMIT {limit}"
        return await self.execute_query(query)

