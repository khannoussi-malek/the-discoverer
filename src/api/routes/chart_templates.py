"""Chart template API routes."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List

from src.api.models.request import ChartTemplateCreateRequest, ChartTemplateUpdateRequest
from src.application.services.chart_template_service import ChartTemplateService


router = APIRouter(prefix="/api/chart-templates", tags=["chart-templates"])


def get_chart_template_service() -> ChartTemplateService:
    """Dependency injection for chart template service."""
    from src.api.main import app
    if not hasattr(app.state, 'chart_template_service'):
        from src.application.services.chart_template_service import ChartTemplateService
        app.state.chart_template_service = ChartTemplateService()
    return app.state.chart_template_service


@router.post("")
async def create_chart_template(
    request: ChartTemplateCreateRequest,
    service: ChartTemplateService = Depends(get_chart_template_service)
):
    """Create a new chart template."""
    try:
        template = await service.create_template(
            name=request.name,
            chart_type=request.chart_type,
            config=request.config,
            description=request.description,
            tags=request.tags,
            created_by=None,  # Can be set from auth
            is_public=request.is_public
        )
        
        return {
            "id": template.id,
            "name": template.name,
            "chart_type": template.chart_type,
            "config": template.config,
            "description": template.description,
            "tags": template.tags,
            "created_at": template.created_at.isoformat(),
            "is_public": template.is_public,
            "usage_count": template.usage_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_chart_templates(
    chart_type: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    public_only: bool = Query(False),
    service: ChartTemplateService = Depends(get_chart_template_service)
):
    """List chart templates."""
    try:
        tag_list = tags.split(",") if tags else None
        templates = await service.list_templates(
            chart_type=chart_type,
            tags=tag_list,
            public_only=public_only
        )
        
        return {
            "templates": [
                {
                    "id": t.id,
                    "name": t.name,
                    "chart_type": t.chart_type,
                    "description": t.description,
                    "tags": t.tags,
                    "created_at": t.created_at.isoformat(),
                    "is_public": t.is_public,
                    "usage_count": t.usage_count
                }
                for t in templates
            ],
            "total": len(templates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{template_id}")
async def get_chart_template(
    template_id: str,
    service: ChartTemplateService = Depends(get_chart_template_service)
):
    """Get a chart template by ID."""
    try:
        template = await service.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "id": template.id,
            "name": template.name,
            "chart_type": template.chart_type,
            "config": template.config,
            "description": template.description,
            "tags": template.tags,
            "created_at": template.created_at.isoformat(),
            "is_public": template.is_public,
            "usage_count": template.usage_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{template_id}")
async def update_chart_template(
    template_id: str,
    request: ChartTemplateUpdateRequest,
    service: ChartTemplateService = Depends(get_chart_template_service)
):
    """Update a chart template."""
    try:
        template = await service.update_template(
            template_id=template_id,
            name=request.name,
            config=request.config,
            description=request.description,
            tags=request.tags,
            is_public=request.is_public
        )
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "id": template.id,
            "name": template.name,
            "chart_type": template.chart_type,
            "config": template.config,
            "description": template.description,
            "tags": template.tags,
            "is_public": template.is_public
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{template_id}")
async def delete_chart_template(
    template_id: str,
    service: ChartTemplateService = Depends(get_chart_template_service)
):
    """Delete a chart template."""
    try:
        success = await service.delete_template(template_id)
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {"message": "Template deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{template_id}/apply")
async def apply_chart_template(
    template_id: str,
    query_id: str = Query(..., description="Query ID to apply template to"),
    overrides: Optional[Dict[str, Any]] = None,
    service: ChartTemplateService = Depends(get_chart_template_service)
):
    """Apply a chart template to a query result."""
    try:
        result = await service.apply_template(template_id, query_id, overrides)
        
        # Generate chart using the template config
        from src.api.main import app
        from src.application.services.visualization_service import VisualizationService
        from src.application.services.advanced_visualization_service import AdvancedVisualizationService
        from src.domain.result import AggregatedResult
        
        history_repo = app.state.query_history_repository
        query_history = await history_repo.get_by_id(query_id)
        
        if not query_history:
            raise HTTPException(status_code=404, detail="Query not found")
        
        result_data = query_history.result.get("merged_data", [])
        chart_type = result["chart_type"]
        config = result["config"]
        
        # Use appropriate visualization service
        advanced_service = AdvancedVisualizationService()
        advanced_types = ["heatmap", "box", "violin", "scatter3d", "surface", "sunburst", "treemap", "funnel", "gauge", "waterfall"]
        
        if chart_type.lower() in advanced_types:
            chart = advanced_service.generate_advanced_chart(result_data, chart_type, config)
        else:
            viz_service = VisualizationService()
            aggregated_result = AggregatedResult(
                results={},
                merged_data=result_data,
                aggregation_type="merge",
                total_rows=len(result_data),
                execution_time=0.0,
                databases_queried=[]
            )
            from src.domain.visualization import ChartConfig
            chart_config = ChartConfig(
                chart_type=chart_type,
                title=config.get("title", "Chart"),
                x_axis=config.get("x_axis"),
                y_axis=config.get("y_axis")
            )
            chart = viz_service.generate_chart(aggregated_result, chart_config)
        
        return {
            "template_id": template_id,
            "query_id": query_id,
            "chart_data": chart.data if hasattr(chart, 'data') else {},
            "chart_type": chart.chart_config.chart_type if hasattr(chart, 'chart_config') else chart_type
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_chart_templates(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=100),
    service: ChartTemplateService = Depends(get_chart_template_service)
):
    """Search chart templates."""
    try:
        templates = await service.search_templates(q, limit)
        
        return {
            "templates": [
                {
                    "id": t.id,
                    "name": t.name,
                    "chart_type": t.chart_type,
                    "description": t.description,
                    "tags": t.tags,
                    "usage_count": t.usage_count
                }
                for t in templates
            ],
            "total": len(templates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


