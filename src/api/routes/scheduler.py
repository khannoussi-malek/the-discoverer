"""Scheduled query API routes."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional

from src.domain.scheduled_query import ScheduleStatus, ScheduleFrequency
from src.application.services.scheduler_service import SchedulerService
from src.api.models.response import PaginatedResponse
from pydantic import BaseModel


router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


class CreateScheduleRequest(BaseModel):
    """Create schedule request."""
    name: str
    query: str
    frequency: str  # ScheduleFrequency
    schedule: str  # Cron expression or frequency string
    database_ids: Optional[List[str]] = None
    description: Optional[str] = None
    parameters: Optional[dict] = None


class ScheduledQueryResponse(BaseModel):
    """Scheduled query response."""
    id: str
    name: str
    description: Optional[str]
    query: str
    database_ids: Optional[List[str]]
    schedule: str
    frequency: str
    status: str
    last_run_at: Optional[str]
    next_run_at: Optional[str]
    run_count: int
    success_count: int
    failure_count: int


def get_scheduler_service() -> SchedulerService:
    """Dependency injection for scheduler service."""
    from src.api.main import app
    return app.state.scheduler_service


@router.post("", response_model=ScheduledQueryResponse)
async def create_schedule(
    request: CreateScheduleRequest,
    service: SchedulerService = Depends(get_scheduler_service)
):
    """Create a new scheduled query."""
    try:
        frequency = ScheduleFrequency(request.frequency)
        schedule = await service.create_schedule(
            name=request.name,
            query=request.query,
            frequency=frequency,
            schedule=request.schedule,
            database_ids=request.database_ids,
            description=request.description,
            parameters=request.parameters
        )
        return ScheduledQueryResponse(
            id=schedule.id,
            name=schedule.name,
            description=schedule.description,
            query=schedule.query,
            database_ids=schedule.database_ids,
            schedule=schedule.schedule,
            frequency=schedule.frequency.value,
            status=schedule.status.value,
            last_run_at=schedule.last_run_at.isoformat() if schedule.last_run_at else None,
            next_run_at=schedule.next_run_at.isoformat() if schedule.next_run_at else None,
            run_count=schedule.run_count,
            success_count=schedule.success_count,
            failure_count=schedule.failure_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=PaginatedResponse)
async def list_schedules(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: SchedulerService = Depends(get_scheduler_service)
):
    """List scheduled queries."""
    try:
        schedule_status = ScheduleStatus(status) if status else None
        offset = (page - 1) * page_size
        
        schedules = await service.list_schedules(
            status=schedule_status,
            limit=page_size,
            offset=offset
        )
        
        total = len(schedules)  # Approximate
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        return PaginatedResponse(
            items=[ScheduledQueryResponse(
                id=s.id,
                name=s.name,
                description=s.description,
                query=s.query,
                database_ids=s.database_ids,
                schedule=s.schedule,
                frequency=s.frequency.value,
                status=s.status.value,
                last_run_at=s.last_run_at.isoformat() if s.last_run_at else None,
                next_run_at=s.next_run_at.isoformat() if s.next_run_at else None,
                run_count=s.run_count,
                success_count=s.success_count,
                failure_count=s.failure_count
            ) for s in schedules],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{schedule_id}/execute")
async def execute_schedule(
    schedule_id: str,
    service: SchedulerService = Depends(get_scheduler_service)
):
    """Manually execute a scheduled query."""
    try:
        result = await service.execute_schedule(schedule_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{schedule_id}/pause")
async def pause_schedule(
    schedule_id: str,
    service: SchedulerService = Depends(get_scheduler_service)
):
    """Pause a scheduled query."""
    try:
        success = await service.pause_schedule(schedule_id)
        if not success:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return {"message": "Schedule paused successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{schedule_id}/resume")
async def resume_schedule(
    schedule_id: str,
    service: SchedulerService = Depends(get_scheduler_service)
):
    """Resume a paused scheduled query."""
    try:
        success = await service.resume_schedule(schedule_id)
        if not success:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return {"message": "Schedule resumed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    service: SchedulerService = Depends(get_scheduler_service)
):
    """Delete a scheduled query."""
    try:
        success = await service.delete_schedule(schedule_id)
        if not success:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return {"message": "Schedule deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


