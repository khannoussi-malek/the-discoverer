"""Scheduled export domain entity."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from src.domain.scheduled_query import ScheduleStatus, ScheduleFrequency


@dataclass
class ScheduledExport:
    """Scheduled export entity."""
    id: str
    name: str
    description: Optional[str]
    query: str
    database_ids: Optional[List[str]]
    schedule: str  # Cron expression or frequency
    frequency: ScheduleFrequency
    export_format: str  # csv, json, excel, parquet, avro
    export_template_id: Optional[str] = None  # Optional export template
    destination: Optional[str] = None  # Optional destination (email, webhook, storage)
    filename_pattern: Optional[str] = None
    status: ScheduleStatus = ScheduleStatus.ACTIVE
    parameters: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    created_by: Optional[str] = None
    notify_on_failure: bool = False
    notify_email: Optional[str] = None
    last_export_path: Optional[str] = None  # Path to last exported file



