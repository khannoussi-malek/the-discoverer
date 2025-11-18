"""Scheduled query repository."""
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from src.domain.scheduled_query import ScheduledQuery, ScheduleStatus


class ScheduledQueryRepository:
    """Repository for scheduled queries - in-memory implementation."""
    
    def __init__(self):
        self._schedules: Dict[str, ScheduledQuery] = {}
    
    async def save(self, schedule: ScheduledQuery) -> ScheduledQuery:
        """Save a scheduled query."""
        if not schedule.id:
            schedule.id = str(uuid.uuid4())
        
        schedule.updated_at = datetime.utcnow()
        self._schedules[schedule.id] = schedule
        return schedule
    
    async def get_by_id(self, schedule_id: str) -> Optional[ScheduledQuery]:
        """Get schedule by ID."""
        return self._schedules.get(schedule_id)
    
    async def list(
        self,
        status: Optional[ScheduleStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ScheduledQuery]:
        """List scheduled queries."""
        schedules = list(self._schedules.values())
        
        # Filter by status
        if status:
            schedules = [s for s in schedules if s.status == status]
        
        # Sort by next_run_at
        schedules.sort(key=lambda s: s.next_run_at or datetime.max)
        
        # Paginate
        return schedules[offset:offset + limit]
    
    async def get_due_schedules(self) -> List[ScheduledQuery]:
        """Get schedules that are due to run."""
        now = datetime.utcnow()
        due = []
        
        for schedule in self._schedules.values():
            if schedule.status == ScheduleStatus.ACTIVE and schedule.next_run_at:
                if schedule.next_run_at <= now:
                    due.append(schedule)
        
        return due
    
    async def update(self, schedule_id: str, updates: Dict[str, Any]) -> Optional[ScheduledQuery]:
        """Update a schedule."""
        schedule = self._schedules.get(schedule_id)
        if not schedule:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(schedule, key):
                setattr(schedule, key, value)
        
        schedule.updated_at = datetime.utcnow()
        return schedule
    
    async def delete(self, schedule_id: str) -> bool:
        """Delete a schedule."""
        if schedule_id in self._schedules:
            del self._schedules[schedule_id]
            return True
        return False


