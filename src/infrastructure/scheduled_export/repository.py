"""Scheduled export repository."""
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from src.domain.scheduled_export import ScheduledExport
from src.domain.scheduled_query import ScheduleStatus


class ScheduledExportRepository:
    """Repository for scheduled exports - in-memory implementation."""
    
    def __init__(self):
        self._exports: Dict[str, ScheduledExport] = {}
    
    async def save(self, scheduled_export: ScheduledExport) -> ScheduledExport:
        """Save a scheduled export."""
        if not scheduled_export.id:
            scheduled_export.id = str(uuid.uuid4())
        
        scheduled_export.updated_at = datetime.utcnow()
        self._exports[scheduled_export.id] = scheduled_export
        return scheduled_export
    
    async def get_by_id(self, export_id: str) -> Optional[ScheduledExport]:
        """Get scheduled export by ID."""
        return self._exports.get(export_id)
    
    async def list(
        self,
        status: Optional[ScheduleStatus] = None,
        created_by: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ScheduledExport]:
        """List scheduled exports."""
        exports = list(self._exports.values())
        
        # Filter by status
        if status:
            exports = [e for e in exports if e.status == status]
        
        # Filter by creator
        if created_by:
            exports = [e for e in exports if e.created_by == created_by]
        
        # Sort by next_run_at
        exports.sort(key=lambda e: e.next_run_at or datetime.max)
        
        # Paginate
        return exports[offset:offset + limit]
    
    async def get_due_exports(self) -> List[ScheduledExport]:
        """Get scheduled exports that are due to run."""
        now = datetime.utcnow()
        due = []
        
        for export in self._exports.values():
            if export.status == ScheduleStatus.ACTIVE and export.next_run_at:
                if export.next_run_at <= now:
                    due.append(export)
        
        return due
    
    async def update(
        self,
        export_id: str,
        updates: Dict[str, Any]
    ) -> Optional[ScheduledExport]:
        """Update scheduled export."""
        export = self._exports.get(export_id)
        if not export:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(export, key):
                setattr(export, key, value)
        
        export.updated_at = datetime.utcnow()
        return export
    
    async def delete(self, export_id: str) -> bool:
        """Delete scheduled export."""
        if export_id in self._exports:
            del self._exports[export_id]
            return True
        return False



