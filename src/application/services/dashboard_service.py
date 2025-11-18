"""Dashboard service for creating and managing dashboards."""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Dashboard:
    """Dashboard entity."""
    id: str
    name: str
    description: Optional[str] = None
    widgets: List[Dict[str, Any]] = field(default_factory=list)
    layout: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    is_public: bool = False
    tags: List[str] = field(default_factory=list)


@dataclass
class DashboardWidget:
    """Dashboard widget entity."""
    id: str
    type: str  # "chart", "query", "metric", "text"
    title: str
    config: Dict[str, Any]
    position: Dict[str, Any]  # x, y, width, height
    query_id: Optional[str] = None
    chart_template_id: Optional[str] = None


class DashboardService:
    """Service for managing dashboards."""
    
    def __init__(self):
        self._dashboards: Dict[str, Dashboard] = {}
    
    async def create_dashboard(
        self,
        name: str,
        description: Optional[str] = None,
        widgets: Optional[List[Dict[str, Any]]] = None,
        layout: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None,
        is_public: bool = False,
        tags: Optional[List[str]] = None
    ) -> Dashboard:
        """Create a new dashboard."""
        dashboard = Dashboard(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            widgets=widgets or [],
            layout=layout or {},
            created_by=created_by,
            is_public=is_public,
            tags=tags or []
        )
        
        self._dashboards[dashboard.id] = dashboard
        return dashboard
    
    async def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get a dashboard by ID."""
        return self._dashboards.get(dashboard_id)
    
    async def list_dashboards(
        self,
        public_only: bool = False,
        created_by: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dashboard]:
        """List dashboards with optional filters."""
        dashboards = list(self._dashboards.values())
        
        if public_only:
            dashboards = [d for d in dashboards if d.is_public]
        
        if created_by:
            dashboards = [d for d in dashboards if d.created_by == created_by]
        
        if tags:
            dashboards = [
                d for d in dashboards
                if any(tag in d.tags for tag in tags)
            ]
        
        return dashboards
    
    async def update_dashboard(
        self,
        dashboard_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        widgets: Optional[List[Dict[str, Any]]] = None,
        layout: Optional[Dict[str, Any]] = None,
        is_public: Optional[bool] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Dashboard]:
        """Update a dashboard."""
        dashboard = self._dashboards.get(dashboard_id)
        if not dashboard:
            return None
        
        if name is not None:
            dashboard.name = name
        if description is not None:
            dashboard.description = description
        if widgets is not None:
            dashboard.widgets = widgets
        if layout is not None:
            dashboard.layout = layout
        if is_public is not None:
            dashboard.is_public = is_public
        if tags is not None:
            dashboard.tags = tags
        
        dashboard.updated_at = datetime.utcnow()
        return dashboard
    
    async def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete a dashboard."""
        if dashboard_id in self._dashboards:
            del self._dashboards[dashboard_id]
            return True
        return False
    
    async def add_widget(
        self,
        dashboard_id: str,
        widget: Dict[str, Any]
    ) -> Optional[Dashboard]:
        """Add a widget to a dashboard."""
        dashboard = self._dashboards.get(dashboard_id)
        if not dashboard:
            return None
        
        widget_id = str(uuid.uuid4())
        widget["id"] = widget_id
        dashboard.widgets.append(widget)
        dashboard.updated_at = datetime.utcnow()
        
        return dashboard
    
    async def remove_widget(
        self,
        dashboard_id: str,
        widget_id: str
    ) -> Optional[Dashboard]:
        """Remove a widget from a dashboard."""
        dashboard = self._dashboards.get(dashboard_id)
        if not dashboard:
            return None
        
        dashboard.widgets = [
            w for w in dashboard.widgets
            if w.get("id") != widget_id
        ]
        dashboard.updated_at = datetime.utcnow()
        
        return dashboard
    
    async def update_widget(
        self,
        dashboard_id: str,
        widget_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dashboard]:
        """Update a widget in a dashboard."""
        dashboard = self._dashboards.get(dashboard_id)
        if not dashboard:
            return None
        
        for widget in dashboard.widgets:
            if widget.get("id") == widget_id:
                widget.update(updates)
                dashboard.updated_at = datetime.utcnow()
                break
        
        return dashboard
    
    async def render_dashboard(
        self,
        dashboard_id: str
    ) -> Dict[str, Any]:
        """Render a dashboard with all widget data."""
        dashboard = await self.get_dashboard(dashboard_id)
        if not dashboard:
            raise ValueError(f"Dashboard {dashboard_id} not found")
        
        rendered_widgets = []
        
        for widget in dashboard.widgets:
            widget_data = {
                "id": widget.get("id"),
                "type": widget.get("type"),
                "title": widget.get("title"),
                "config": widget.get("config", {}),
                "position": widget.get("position", {})
            }
            
            # If widget has a query_id, fetch the result
            if widget.get("query_id"):
                from src.api.main import app
                history_repo = app.state.query_history_repository
                query_history = await history_repo.get_by_id(widget["query_id"])
                
                if query_history:
                    widget_data["data"] = query_history.result.get("merged_data", [])
            
            # If widget has a chart_template_id, apply it
            if widget.get("chart_template_id"):
                widget_data["chart_template_id"] = widget["chart_template_id"]
            
            rendered_widgets.append(widget_data)
        
        return {
            "dashboard_id": dashboard.id,
            "name": dashboard.name,
            "description": dashboard.description,
            "widgets": rendered_widgets,
            "layout": dashboard.layout,
            "created_at": dashboard.created_at.isoformat(),
            "updated_at": dashboard.updated_at.isoformat()
        }


