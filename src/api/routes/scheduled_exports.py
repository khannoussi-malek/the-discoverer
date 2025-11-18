"""Scheduled export API routes."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List

from src.application.services.scheduled_export_service import ScheduledExportService
from src.api.models.request import ScheduledExportCreateRequest
from src.domain.scheduled_query import ScheduleStatus, ScheduleFrequency


router = APIRouter(prefix="/api/scheduled-exports", tags=["scheduled-exports"])


def get_scheduled_export_service() -> ScheduledExportService:
    """Dependency injection for scheduled export service."""
    from src.api.main import app
    if not hasattr(app.state, 'scheduled_export_service'):
        from src.infrastructure.scheduled_export.repository import ScheduledExportRepository
        from src.application.services.scheduled_export_service import ScheduledExportService
        from src.application.services.export_template_service import ExportTemplateService
        
        repository = ScheduledExportRepository()
        query_service = app.state.query_service
        
        # Get export template service if available
        export_template_service = None
        if hasattr(app.state, 'export_template_service'):
            export_template_service = app.state.export_template_service
        
        # Get webhook service if available
        webhook_service = None
        if hasattr(app.state, 'webhook_service'):
            webhook_service = app.state.webhook_service
        
        app.state.scheduled_export_service = ScheduledExportService(
            repository=repository,
            query_service=query_service,
            export_template_service=export_template_service,
            webhook_service=webhook_service
        )
    return app.state.scheduled_export_service


@router.post("")
async def create_scheduled_export(
    request: ScheduledExportCreateRequest,
    service: ScheduledExportService = Depends(get_scheduled_export_service)
):
    """Create a scheduled export."""
    try:
        frequency = ScheduleFrequency(request.frequency.lower())
        
        scheduled_export = await service.create_scheduled_export(
            name=request.name,
            query=request.query,
            frequency=frequency,
            schedule=request.schedule,
            export_format=request.export_format,
            database_ids=request.database_ids,
            export_template_id=request.export_template_id,
            destination=request.destination,
            filename_pattern=request.filename_pattern,
            description=request.description
        )
        
        return {
            "id": scheduled_export.id,
            "name": scheduled_export.name,
            "export_format": scheduled_export.export_format,
            "frequency": scheduled_export.frequency.value,
            "next_run_at": scheduled_export.next_run_at.isoformat() if scheduled_export.next_run_at else None,
            "status": scheduled_export.status.value,
            "created_at": scheduled_export.created_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_scheduled_exports(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: ScheduledExportService = Depends(get_scheduled_export_service)
):
    """List scheduled exports."""
    try:
        status_filter = ScheduleStatus(status.lower()) if status else None
        offset = (page - 1) * page_size
        
        exports = await service.repository.list(
            status=status_filter,
            limit=page_size,
            offset=offset
        )
        
        return {
            "exports": [
                {
                    "id": e.id,
                    "name": e.name,
                    "export_format": e.export_format,
                    "frequency": e.frequency.value,
                    "status": e.status.value,
                    "next_run_at": e.next_run_at.isoformat() if e.next_run_at else None,
                    "last_run_at": e.last_run_at.isoformat() if e.last_run_at else None,
                    "run_count": e.run_count,
                    "success_count": e.success_count,
                    "failure_count": e.failure_count,
                    "last_export_path": e.last_export_path
                }
                for e in exports
            ],
            "page": page,
            "page_size": page_size,
            "total": len(exports)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{export_id}")
async def get_scheduled_export(
    export_id: str,
    service: ScheduledExportService = Depends(get_scheduled_export_service)
):
    """Get scheduled export by ID."""
    try:
        export = await service.repository.get_by_id(export_id)
        if not export:
            raise HTTPException(status_code=404, detail="Scheduled export not found")
        
        return {
            "id": export.id,
            "name": export.name,
            "description": export.description,
            "query": export.query,
            "database_ids": export.database_ids,
            "export_format": export.export_format,
            "export_template_id": export.export_template_id,
            "destination": export.destination,
            "filename_pattern": export.filename_pattern,
            "frequency": export.frequency.value,
            "schedule": export.schedule,
            "status": export.status.value,
            "next_run_at": export.next_run_at.isoformat() if export.next_run_at else None,
            "last_run_at": export.last_run_at.isoformat() if export.last_run_at else None,
            "run_count": export.run_count,
            "success_count": export.success_count,
            "failure_count": export.failure_count,
            "last_export_path": export.last_export_path,
            "created_at": export.created_at.isoformat(),
            "updated_at": export.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{export_id}/execute")
async def execute_scheduled_export(
    export_id: str,
    service: ScheduledExportService = Depends(get_scheduled_export_service)
):
    """Manually execute a scheduled export."""
    try:
        result = await service.execute_export(export_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{export_id}/pause")
async def pause_scheduled_export(
    export_id: str,
    service: ScheduledExportService = Depends(get_scheduled_export_service)
):
    """Pause a scheduled export."""
    try:
        export = await service.repository.get_by_id(export_id)
        if not export:
            raise HTTPException(status_code=404, detail="Scheduled export not found")
        
        await service.repository.update(export_id, {"status": ScheduleStatus.PAUSED})
        return {"message": "Scheduled export paused"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{export_id}/resume")
async def resume_scheduled_export(
    export_id: str,
    service: ScheduledExportService = Depends(get_scheduled_export_service)
):
    """Resume a paused scheduled export."""
    try:
        export = await service.repository.get_by_id(export_id)
        if not export:
            raise HTTPException(status_code=404, detail="Scheduled export not found")
        
        await service.repository.update(export_id, {"status": ScheduleStatus.ACTIVE})
        return {"message": "Scheduled export resumed"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{export_id}")
async def delete_scheduled_export(
    export_id: str,
    service: ScheduledExportService = Depends(get_scheduled_export_service)
):
    """Delete a scheduled export."""
    try:
        success = await service.repository.delete(export_id)
        if not success:
            raise HTTPException(status_code=404, detail="Scheduled export not found")
        
        return {"message": "Scheduled export deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



