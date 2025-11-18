"""Visualization API routes."""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse, Response
from typing import Optional

from src.api.models.request import VisualizationRequest
from src.api.models.response import VisualizationResponse, ErrorResponse
from src.application.services.visualization_service import VisualizationService
from src.application.services.advanced_visualization_service import AdvancedVisualizationService
from src.domain.visualization import ChartConfig
from src.domain.result import AggregatedResult
from src.utils.chart_exporter import ChartExporter


router = APIRouter(prefix="/api/visualization", tags=["visualization"])


def get_visualization_service() -> VisualizationService:
    """Dependency injection for visualization service."""
    from src.api.main import app
    return app.state.visualization_service


def get_advanced_visualization_service() -> AdvancedVisualizationService:
    """Dependency injection for advanced visualization service."""
    return AdvancedVisualizationService()


@router.post("/generate", response_model=VisualizationResponse)
async def generate_chart(
    request: VisualizationRequest,
    service: VisualizationService = Depends(get_visualization_service),
    advanced_service: AdvancedVisualizationService = Depends(get_advanced_visualization_service)
):
    """Generate a chart from query result."""
    try:
        # Get query result from history
        from src.api.main import app
        history_repo = app.state.query_history_repository
        
        query_history = await history_repo.get_by_id(request.query_id)
        if not query_history:
            raise HTTPException(status_code=404, detail="Query not found")
        
        result_data = query_history.result.get("merged_data", [])
        
        # Check if advanced chart type
        advanced_types = ["heatmap", "box", "violin", "scatter3d", "surface", "sunburst", "treemap", "funnel", "gauge", "waterfall"]
        chart_type = request.chart_type or "bar"
        
        if chart_type.lower() in advanced_types:
            # Use advanced service
            config = request.config or {}
            config.update({
                "x_axis": request.x_axis,
                "y_axis": request.y_axis,
                "z_axis": request.z_axis,
                "title": request.title
            })
            chart = advanced_service.generate_advanced_chart(
                data=result_data,
                chart_type=chart_type,
                config=config
            )
        else:
            # Use basic service - need to create AggregatedResult
            from src.domain.result import AggregatedResult, Result
            aggregated_result = AggregatedResult(
                results={},
                merged_data=result_data,
                aggregation_type="merge",
                total_rows=len(result_data),
                execution_time=0.0,
                databases_queried=[]
            )
            
            chart_config = ChartConfig(
                chart_type=chart_type,
                x_axis=request.x_axis,
                y_axis=request.y_axis,
                title=request.title or "Data Visualization"
            )
            
            visualization = service.generate_chart(aggregated_result, chart_config)
            chart = visualization  # Convert Visualization to Chart format
        
        # Convert to response format
        if hasattr(chart, 'data'):
            chart_data = chart.data
            chart_type_str = chart.chart_config.chart_type
        else:
            chart_data = chart.get("data", {})
            chart_type_str = chart.get("chart_type", chart_type)
        
        return VisualizationResponse(
            visualization_id=request.query_id,
            chart_data=chart_data,
            chart_type=chart_type_str,
            format="json"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{query_id}")
async def export_chart(
    query_id: str,
    format: str = Query("png", description="Export format: png, pdf, html, svg"),
    chart_type: Optional[str] = Query(None, description="Chart type"),
    width: int = Query(1200, ge=100, le=4000),
    height: int = Query(800, ge=100, le=4000),
    service: VisualizationService = Depends(get_visualization_service),
    advanced_service: AdvancedVisualizationService = Depends(get_advanced_visualization_service)
):
    """Export chart to image file."""
    try:
        # Get query result from history
        from src.api.main import app
        history_repo = app.state.query_history_repository
        
        query_history = await history_repo.get_by_id(query_id)
        if not query_history:
            raise HTTPException(status_code=404, detail="Query not found")
        
        result_data = query_history.result.get("merged_data", [])
        
        # Generate chart
        chart_type = chart_type or "bar"
        advanced_types = ["heatmap", "box", "violin", "scatter3d", "surface", "sunburst", "treemap", "funnel", "gauge", "waterfall"]
        
        if chart_type.lower() in advanced_types:
            config = {"title": "Chart"}
            chart = advanced_service.generate_advanced_chart(result_data, chart_type, config)
        else:
            from src.domain.result import AggregatedResult
            aggregated_result = AggregatedResult(
                results={},
                merged_data=result_data,
                aggregation_type="merge",
                total_rows=len(result_data),
                execution_time=0.0,
                databases_queried=[]
            )
            chart_config = ChartConfig(chart_type=chart_type, title="Chart")
            visualization = service.generate_chart(aggregated_result, chart_config)
            chart = visualization
        
        # Get chart data
        chart_data = chart.data if hasattr(chart, 'data') else {}
        
        # Export based on format
        if format.lower() == "png":
            img_data = await ChartExporter.export_to_png(chart_data, width, height)
            return StreamingResponse(
                img_data,
                media_type="image/png",
                headers={"Content-Disposition": f"attachment; filename=chart_{query_id}.png"}
            )
        elif format.lower() == "pdf":
            pdf_data = await ChartExporter.export_to_pdf(chart_data, width, height)
            return StreamingResponse(
                pdf_data,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=chart_{query_id}.pdf"}
            )
        elif format.lower() == "html":
            html_data = await ChartExporter.export_to_html(chart_data)
            return Response(
                content=html_data,
                media_type="text/html",
                headers={"Content-Disposition": f"attachment; filename=chart_{query_id}.html"}
            )
        elif format.lower() == "svg":
            svg_data = await ChartExporter.export_to_svg(chart_data, width, height)
            return Response(
                content=svg_data,
                media_type="image/svg+xml",
                headers={"Content-Disposition": f"attachment; filename=chart_{query_id}.svg"}
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
