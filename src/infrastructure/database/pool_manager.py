"""Database connection pool manager."""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio

from src.domain.database import Database
from src.infrastructure.database.adapters.factory import DatabaseAdapterFactory
from src.infrastructure.database.adapters.base import DatabaseAdapter


class PoolStatus(str, Enum):
    """Pool status."""
    ACTIVE = "active"
    IDLE = "idle"
    ERROR = "error"
    CLOSED = "closed"


@dataclass
class PoolConfig:
    """Connection pool configuration."""
    min_size: int = 2
    max_size: int = 10
    max_queries: int = 50000
    max_inactive_time: float = 300.0  # seconds
    timeout: float = 30.0  # seconds


@dataclass
class PoolStats:
    """Connection pool statistics."""
    database_id: str
    status: PoolStatus
    min_size: int
    max_size: int
    current_size: int = 0
    idle_connections: int = 0
    active_connections: int = 0
    total_queries: int = 0
    failed_queries: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    uptime_seconds: float = 0.0


class ConnectionPoolManager:
    """Manages connection pools per database."""
    
    def __init__(self):
        self._pools: Dict[str, DatabaseAdapter] = {}
        self._pool_configs: Dict[str, PoolConfig] = {}
        self._pool_stats: Dict[str, PoolStats] = {}
        self._lock = asyncio.Lock()
    
    async def get_pool(
        self,
        database: Database,
        config: Optional[PoolConfig] = None
    ) -> DatabaseAdapter:
        """
        Get or create connection pool for database.
        
        Args:
            database: Database entity
            config: Optional pool configuration (uses database defaults if not provided)
        
        Returns:
            Database adapter with active connection pool
        """
        async with self._lock:
            # Check if pool already exists
            if database.id in self._pools:
                adapter = self._pools[database.id]
                if adapter.is_connected:
                    # Update last used
                    if database.id in self._pool_stats:
                        self._pool_stats[database.id].last_used = datetime.utcnow()
                    return adapter
                else:
                    # Pool disconnected, remove it
                    del self._pools[database.id]
            
            # Create new pool
            pool_config = config or self._get_default_config(database)
            self._pool_configs[database.id] = pool_config
            
            # Create adapter
            adapter = DatabaseAdapterFactory.create(
                database.type,
                {
                    "host": database.host,
                    "port": database.port,
                    "database": database.database_name,
                    "user": database.config.get("user"),
                    "password": database.config.get("password"),
                    **database.config
                }
            )
            
            # Override pool settings if adapter supports it
            if hasattr(adapter, 'pool_config'):
                adapter.pool_config = pool_config
            
            # Connect (creates pool)
            try:
                await adapter.connect()
                
                # Initialize stats
                self._pool_stats[database.id] = PoolStats(
                    database_id=database.id,
                    status=PoolStatus.ACTIVE,
                    min_size=pool_config.min_size,
                    max_size=pool_config.max_size,
                    current_size=pool_config.min_size,
                    last_used=datetime.utcnow()
                )
                
                self._pools[database.id] = adapter
                return adapter
            except Exception as e:
                # Update stats on error
                if database.id in self._pool_stats:
                    self._pool_stats[database.id].status = PoolStatus.ERROR
                raise
    
    async def close_pool(self, database_id: str) -> bool:
        """
        Close connection pool for database.
        
        Args:
            database_id: Database ID
        
        Returns:
            True if pool was closed, False if not found
        """
        async with self._lock:
            if database_id not in self._pools:
                return False
            
            adapter = self._pools[database_id]
            try:
                await adapter.disconnect()
                if database_id in self._pool_stats:
                    self._pool_stats[database_id].status = PoolStatus.CLOSED
                del self._pools[database_id]
                if database_id in self._pool_configs:
                    del self._pool_configs[database_id]
                return True
            except Exception:
                return False
    
    async def close_all_pools(self) -> None:
        """Close all connection pools."""
        async with self._lock:
            database_ids = list(self._pools.keys())
            for db_id in database_ids:
                await self.close_pool(db_id)
    
    async def update_pool_config(
        self,
        database_id: str,
        config: PoolConfig
    ) -> bool:
        """
        Update pool configuration.
        
        Args:
            database_id: Database ID
            config: New pool configuration
        
        Returns:
            True if updated, False if pool not found
        """
        async with self._lock:
            if database_id not in self._pools:
                return False
            
            self._pool_configs[database_id] = config
            
            # Update stats
            if database_id in self._pool_stats:
                stats = self._pool_stats[database_id]
                stats.min_size = config.min_size
                stats.max_size = config.max_size
            
            # Note: Actual pool resize would require reconnection
            # This is a limitation - pools are typically created with fixed size
            return True
    
    def get_pool_stats(self, database_id: str) -> Optional[PoolStats]:
        """Get pool statistics."""
        return self._pool_stats.get(database_id)
    
    def get_all_pool_stats(self) -> Dict[str, PoolStats]:
        """Get statistics for all pools."""
        # Update uptime for all pools
        now = datetime.utcnow()
        for stats in self._pool_stats.values():
            if stats.created_at:
                stats.uptime_seconds = (now - stats.created_at).total_seconds()
        
        return self._pool_stats.copy()
    
    def get_pool_config(self, database_id: str) -> Optional[PoolConfig]:
        """Get pool configuration."""
        return self._pool_configs.get(database_id)
    
    async def refresh_pool(self, database_id: str) -> bool:
        """
        Refresh connection pool (close and recreate).
        
        Args:
            database_id: Database ID
        
        Returns:
            True if refreshed, False if not found
        """
        async with self._lock:
            if database_id not in self._pools:
                return False
            
            adapter = self._pools[database_id]
            config = self._pool_configs.get(database_id)
            
            # Disconnect
            try:
                await adapter.disconnect()
            except Exception:
                pass
            
            # Remove from pools
            del self._pools[database_id]
            
            # Reconnect
            try:
                await adapter.connect()
                self._pools[database_id] = adapter
                if database_id in self._pool_stats:
                    self._pool_stats[database_id].status = PoolStatus.ACTIVE
                    self._pool_stats[database_id].last_used = datetime.utcnow()
                return True
            except Exception as e:
                if database_id in self._pool_stats:
                    self._pool_stats[database_id].status = PoolStatus.ERROR
                raise
    
    def _get_default_config(self, database: Database) -> PoolConfig:
        """Get default pool configuration for database."""
        # Use database-specific config if available
        pool_config = database.config.get("pool", {})
        
        return PoolConfig(
            min_size=pool_config.get("min_size", database.connection_pool_size // 2),
            max_size=pool_config.get("max_size", database.connection_pool_size),
            max_queries=pool_config.get("max_queries", 50000),
            max_inactive_time=pool_config.get("max_inactive_time", 300.0),
            timeout=pool_config.get("timeout", 30.0)
        )
    
    async def health_check(self, database_id: str) -> Dict[str, Any]:
        """
        Perform health check on pool.
        
        Args:
            database_id: Database ID
        
        Returns:
            Health check results
        """
        if database_id not in self._pools:
            return {
                "healthy": False,
                "error": "Pool not found"
            }
        
        adapter = self._pools[database_id]
        stats = self._pool_stats.get(database_id)
        
        try:
            # Test connection
            is_healthy = await adapter.test_connection()
            
            return {
                "healthy": is_healthy,
                "status": stats.status.value if stats else "unknown",
                "connected": adapter.is_connected,
                "stats": {
                    "current_size": stats.current_size if stats else 0,
                    "active_connections": stats.active_connections if stats else 0,
                    "idle_connections": stats.idle_connections if stats else 0
                } if stats else {}
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "status": PoolStatus.ERROR.value
            }



