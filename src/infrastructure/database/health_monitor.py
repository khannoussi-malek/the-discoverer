"""Database health monitoring and automatic reconnection."""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from src.infrastructure.database.repository import DatabaseRepository
from src.infrastructure.database.adapters.factory import DatabaseAdapterFactory
from src.core.exceptions import DatabaseConnectionError


@dataclass
class DatabaseHealth:
    """Database health status."""
    database_id: str
    is_healthy: bool
    last_check: datetime
    last_success: Optional[datetime] = None
    consecutive_failures: int = 0
    response_time: Optional[float] = None
    error_message: Optional[str] = None


class DatabaseHealthMonitor:
    """Monitor database health and handle automatic reconnection."""
    
    def __init__(
        self,
        db_repository: DatabaseRepository,
        check_interval: int = 60,  # seconds
        failure_threshold: int = 3,
        retry_delay: int = 30  # seconds
    ):
        self.db_repository = db_repository
        self.check_interval = check_interval
        self.failure_threshold = failure_threshold
        self.retry_delay = retry_delay
        self.health_status: Dict[str, DatabaseHealth] = {}
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
    
    async def start_monitoring(self):
        """Start background health monitoring."""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
    
    async def stop_monitoring(self):
        """Stop background health monitoring."""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self._monitoring:
            try:
                await self.check_all_databases()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error but continue monitoring
                print(f"Health monitor error: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def check_all_databases(self):
        """Check health of all registered databases."""
        databases = await self.db_repository.get_all()
        
        for database in databases:
            if not database.is_active:
                continue
            
            await self.check_database(database.id)
    
    async def check_database(self, database_id: str) -> DatabaseHealth:
        """Check health of a specific database."""
        import time
        
        database = await self.db_repository.get_by_id(database_id)
        if not database:
            health = DatabaseHealth(
                database_id=database_id,
                is_healthy=False,
                last_check=datetime.utcnow(),
                error_message="Database not found"
            )
            self.health_status[database_id] = health
            return health
        
        start_time = time.time()
        is_healthy = False
        error_message = None
        
        try:
            adapter = DatabaseAdapterFactory.create(database.type, database.config)
            await adapter.connect()
            
            # Test connection
            await adapter.test_connection()
            
            is_healthy = True
            response_time = time.time() - start_time
            
            await adapter.disconnect()
            
        except Exception as e:
            error_message = str(e)
            response_time = time.time() - start_time
        
        # Update health status
        previous_health = self.health_status.get(database_id)
        
        if is_healthy:
            health = DatabaseHealth(
                database_id=database_id,
                is_healthy=True,
                last_check=datetime.utcnow(),
                last_success=datetime.utcnow(),
                consecutive_failures=0,
                response_time=response_time
            )
        else:
            consecutive_failures = (
                (previous_health.consecutive_failures + 1)
                if previous_health else 1
            )
            
            health = DatabaseHealth(
                database_id=database_id,
                is_healthy=False,
                last_check=datetime.utcnow(),
                last_success=previous_health.last_success if previous_health else None,
                consecutive_failures=consecutive_failures,
                response_time=response_time,
                error_message=error_message
            )
            
            # Attempt automatic reconnection if threshold exceeded
            if consecutive_failures >= self.failure_threshold:
                await self._attempt_reconnection(database_id)
        
        self.health_status[database_id] = health
        return health
    
    async def _attempt_reconnection(self, database_id: str):
        """Attempt to reconnect to a failed database."""
        database = await self.db_repository.get_by_id(database_id)
        if not database:
            return
        
        try:
            # Wait before retry
            await asyncio.sleep(self.retry_delay)
            
            adapter = DatabaseAdapterFactory.create(database.type, database.config)
            await adapter.connect()
            await adapter.test_connection()
            await adapter.disconnect()
            
            # Reset failure count on success
            if database_id in self.health_status:
                self.health_status[database_id].consecutive_failures = 0
                self.health_status[database_id].is_healthy = True
                self.health_status[database_id].last_success = datetime.utcnow()
        
        except Exception:
            # Reconnection failed, will retry on next check
            pass
    
    def get_health(self, database_id: str) -> Optional[DatabaseHealth]:
        """Get health status for a database."""
        return self.health_status.get(database_id)
    
    def get_all_health(self) -> Dict[str, DatabaseHealth]:
        """Get health status for all databases."""
        return self.health_status.copy()
    
    def get_unhealthy_databases(self) -> List[str]:
        """Get list of unhealthy database IDs."""
        return [
            db_id for db_id, health in self.health_status.items()
            if not health.is_healthy
        ]
