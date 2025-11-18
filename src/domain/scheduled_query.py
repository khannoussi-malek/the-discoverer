"""Scheduled query domain model."""
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ScheduleStatus(str, Enum):
    """Schedule status."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class ScheduleFrequency(str, Enum):
    """Schedule frequency."""
    ONCE = "once"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"  # Cron expression


@dataclass
class ScheduledQuery:
    """Scheduled query entity."""
    id: str
    name: str
    description: Optional[str]
    query: str
    database_ids: Optional[List[str]]
    schedule: str  # Cron expression or frequency
    frequency: ScheduleFrequency
    status: ScheduleStatus
    parameters: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    created_by: Optional[str]
    notify_on_failure: bool = False
    notify_email: Optional[str] = None


