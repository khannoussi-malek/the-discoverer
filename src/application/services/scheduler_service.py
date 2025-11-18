"""Scheduled query service."""
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from src.domain.scheduled_query import ScheduledQuery, ScheduleStatus, ScheduleFrequency
from src.infrastructure.scheduler.repository import ScheduledQueryRepository
from src.application.services.query_service import QueryService
from src.utils.cron_parser import CronParser


class SchedulerService:
    """Service for managing scheduled queries."""
    
    def __init__(
        self,
        repository: ScheduledQueryRepository,
        query_service: QueryService
    ):
        self.repository = repository
        self.query_service = query_service
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def create_schedule(
        self,
        name: str,
        query: str,
        frequency: ScheduleFrequency,
        schedule: str,
        database_ids: Optional[List[str]] = None,
        description: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> ScheduledQuery:
        """Create a new scheduled query."""
        now = datetime.utcnow()
        next_run = CronParser.calculate_next_run(frequency, schedule, None)
        
        schedule_obj = ScheduledQuery(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            query=query,
            database_ids=database_ids,
            schedule=schedule,
            frequency=frequency,
            status=ScheduleStatus.ACTIVE,
            parameters=parameters,
            created_at=now,
            updated_at=now,
            last_run_at=None,
            next_run_at=next_run,
            run_count=0,
            success_count=0,
            failure_count=0,
            created_by=created_by,
            notify_on_failure=False
        )
        
        return await self.repository.save(schedule_obj)
    
    async def execute_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """Execute a scheduled query."""
        schedule = await self.repository.get_by_id(schedule_id)
        if not schedule:
            raise ValueError(f"Schedule {schedule_id} not found")
        
        if schedule.status != ScheduleStatus.ACTIVE:
            return {"status": "skipped", "reason": f"Schedule is {schedule.status}"}
        
        try:
            # Execute query
            result = await self.query_service.execute_query(
                user_query=schedule.query,
                database_ids=schedule.database_ids
            )
            
            # Update schedule
            now = datetime.utcnow()
            schedule.last_run_at = now
            schedule.run_count += 1
            schedule.success_count += 1
            schedule.next_run_at = CronParser.calculate_next_run(
                schedule.frequency,
                schedule.schedule,
                now
            )
            
            await self.repository.save(schedule)
            
            return {
                "status": "success",
                "result": {
                    "total_rows": result.total_rows,
                    "execution_time": result.execution_time
                }
            }
        
        except Exception as e:
            # Update failure count
            schedule.run_count += 1
            schedule.failure_count += 1
            await self.repository.save(schedule)
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def start_scheduler(self, check_interval: int = 60):
        """Start the scheduler background task."""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._scheduler_loop(check_interval))
    
    async def stop_scheduler(self):
        """Stop the scheduler."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _scheduler_loop(self, check_interval: int):
        """Main scheduler loop."""
        while self._running:
            try:
                # Get due schedules
                due_schedules = await self.repository.get_due_schedules()
                
                # Execute each due schedule
                for schedule in due_schedules:
                    try:
                        await self.execute_schedule(schedule.id)
                    except Exception as e:
                        # Log error but continue
                        print(f"Error executing schedule {schedule.id}: {e}")
                
                # Wait before next check
                await asyncio.sleep(check_interval)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error but continue
                print(f"Scheduler error: {e}")
                await asyncio.sleep(check_interval)
    
    async def list_schedules(
        self,
        status: Optional[ScheduleStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ScheduledQuery]:
        """List scheduled queries."""
        return await self.repository.list(status, limit, offset)
    
    async def pause_schedule(self, schedule_id: str) -> bool:
        """Pause a schedule."""
        schedule = await self.repository.get_by_id(schedule_id)
        if not schedule:
            return False
        
        schedule.status = ScheduleStatus.PAUSED
        await self.repository.save(schedule)
        return True
    
    async def resume_schedule(self, schedule_id: str) -> bool:
        """Resume a schedule."""
        schedule = await self.repository.get_by_id(schedule_id)
        if not schedule:
            return False
        
        schedule.status = ScheduleStatus.ACTIVE
        # Recalculate next run
        schedule.next_run_at = CronParser.calculate_next_run(
            schedule.frequency,
            schedule.schedule,
            schedule.last_run_at
        )
        await self.repository.save(schedule)
        return True
    
    async def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule."""
        return await self.repository.delete(schedule_id)


