"""Dashboard API routes."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List, Dict, Any

from src.api.models.request import DashboardCreateRequest, DashboardUpdateRequest
from src.application.services.dashboard_service import DashboardService


router = APIRouter(prefix="/api/dashboards", tags=["dashboards"])


def get_dashboard_service() -> DashboardService:
    """Dependency injection for dashboard service."""
    from src.api.main import app
    if not hasattr(app.state, 'dashboard_service'):
        from src.application.services.dashboard_service import DashboardService
        app.state.dashboard_service = DashboardService()
    return app.state.dashboard_service


@router.post("")
async def create_dashboard(
    request: DashboardCreateRequest,
    service: DashboardService = Depends(get_dashboard_service)
):
    """Create a new dashboard."""
    try:
        dashboard = await service.create_dashboard(
            name=request.name,
            description=request.description,
            widgets=request.widgets,
            layout=request.layout,
            created_by=None,  # Can be set from auth
            is_public=request.is_public,
            tags=request.tags
        )
        
        return {
            "id": dashboard.id,
            "name": dashboard.name,
            "description": dashboard.description,
            "widgets": dashboard.widgets,
            "layout": dashboard.layout,
            "created_at": dashboard.created_at.isoformat(),
            "is_public": dashboard.is_public,
            "tags": dashboard.tags
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_dashboards(
    public_only: bool = Query(False),
    tags: Optional[str] = Query(None),
    service: DashboardService = Depends(get_dashboard_service)
):
    """List dashboards."""
    try:
        tag_list = tags.split(",") if tags else None
        dashboards = await service.list_dashboards(
            public_only=public_only,
            tags=tag_list
        )
        
        return {
            "dashboards": [
                {
                    "id": d.id,
                    "name": d.name,
                    "description": d.description,
                    "widget_count": len(d.widgets),
                    "created_at": d.created_at.isoformat(),
                    "updated_at": d.updated_at.isoformat(),
                    "is_public": d.is_public,
                    "tags": d.tags
                }
                for d in dashboards
            ],
            "total": len(dashboards)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{dashboard_id}")
async def get_dashboard(
    dashboard_id: str,
    service: DashboardService = Depends(get_dashboard_service)
):
    """Get a dashboard by ID."""
    try:
        dashboard = await service.get_dashboard(dashboard_id)
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        return {
            "id": dashboard.id,
            "name": dashboard.name,
            "description": dashboard.description,
            "widgets": dashboard.widgets,
            "layout": dashboard.layout,
            "created_at": dashboard.created_at.isoformat(),
            "updated_at": dashboard.updated_at.isoformat(),
            "is_public": dashboard.is_public,
            "tags": dashboard.tags
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{dashboard_id}/render")
async def render_dashboard(
    dashboard_id: str,
    service: DashboardService = Depends(get_dashboard_service)
):
    """Render a dashboard with all widget data."""
    try:
        rendered = await service.render_dashboard(dashboard_id)
        return rendered
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{dashboard_id}")
async def update_dashboard(
    dashboard_id: str,
    request: DashboardUpdateRequest,
    service: DashboardService = Depends(get_dashboard_service)
):
    """Update a dashboard."""
    try:
        dashboard = await service.update_dashboard(
            dashboard_id=dashboard_id,
            name=request.name,
            description=request.description,
            widgets=request.widgets,
            layout=request.layout,
            is_public=request.is_public,
            tags=request.tags
        )
        
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        return {
            "id": dashboard.id,
            "name": dashboard.name,
            "description": dashboard.description,
            "widgets": dashboard.widgets,
            "layout": dashboard.layout,
            "updated_at": dashboard.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{dashboard_id}")
async def delete_dashboard(
    dashboard_id: str,
    service: DashboardService = Depends(get_dashboard_service)
):
    """Delete a dashboard."""
    try:
        success = await service.delete_dashboard(dashboard_id)
        if not success:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        return {"message": "Dashboard deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{dashboard_id}/widgets")
async def add_widget(
    dashboard_id: str,
    widget: Dict[str, Any],
    service: DashboardService = Depends(get_dashboard_service)
):
    """Add a widget to a dashboard."""
    try:
        dashboard = await service.add_widget(dashboard_id, widget)
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        return {
            "dashboard_id": dashboard.id,
            "widgets": dashboard.widgets,
            "updated_at": dashboard.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{dashboard_id}/widgets/{widget_id}")
async def remove_widget(
    dashboard_id: str,
    widget_id: str,
    service: DashboardService = Depends(get_dashboard_service)
):
    """Remove a widget from a dashboard."""
    try:
        dashboard = await service.remove_widget(dashboard_id, widget_id)
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        return {
            "dashboard_id": dashboard.id,
            "widgets": dashboard.widgets,
            "updated_at": dashboard.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{dashboard_id}/widgets/{widget_id}")
async def update_widget(
    dashboard_id: str,
    widget_id: str,
    updates: Dict[str, Any],
    service: DashboardService = Depends(get_dashboard_service)
):
    """Update a widget in a dashboard."""
    try:
        dashboard = await service.update_widget(dashboard_id, widget_id, updates)
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        return {
            "dashboard_id": dashboard.id,
            "widgets": dashboard.widgets,
            "updated_at": dashboard.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


