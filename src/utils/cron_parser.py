"""Cron expression parser and scheduler."""
from typing import Optional
from datetime import datetime, timedelta
import re

from src.domain.scheduled_query import ScheduleFrequency


class CronParser:
    """Simple cron expression parser."""
    
    @staticmethod
    def parse_cron(cron_expr: str) -> Dict[str, Any]:
        """Parse cron expression (simplified - supports common patterns)."""
        parts = cron_expr.strip().split()
        
        if len(parts) != 5:
            raise ValueError("Cron expression must have 5 parts: minute hour day month weekday")
        
        return {
            "minute": parts[0],
            "hour": parts[1],
            "day": parts[2],
            "month": parts[3],
            "weekday": parts[4]
        }
    
    @staticmethod
    def calculate_next_run(
        frequency: ScheduleFrequency,
        schedule: str,
        last_run: Optional[datetime] = None
    ) -> datetime:
        """Calculate next run time based on frequency."""
        now = datetime.utcnow()
        base = last_run if last_run else now
        
        if frequency == ScheduleFrequency.ONCE:
            return base + timedelta(days=365)  # Far future
        
        elif frequency == ScheduleFrequency.HOURLY:
            return base + timedelta(hours=1)
        
        elif frequency == ScheduleFrequency.DAILY:
            return base + timedelta(days=1)
        
        elif frequency == ScheduleFrequency.WEEKLY:
            return base + timedelta(weeks=1)
        
        elif frequency == ScheduleFrequency.MONTHLY:
            # Simple monthly - add 30 days
            return base + timedelta(days=30)
        
        elif frequency == ScheduleFrequency.CUSTOM:
            # Parse cron expression (simplified)
            try:
                cron_parts = CronParser.parse_cron(schedule)
                # For now, return hourly as fallback
                # Full cron parsing would be more complex
                return base + timedelta(hours=1)
            except:
                return base + timedelta(hours=1)
        
        return base + timedelta(hours=1)  # Default fallback


