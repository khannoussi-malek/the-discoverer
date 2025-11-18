"""Export API routes."""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from typing import Optional

from src.infrastructure.query_history.repository import QueryHistoryRepository
from src.utils.exporters.factory import ExporterFactory


router = APIRouter(prefix="/api/export", tags=["export"])


def get_history_repository() -> QueryHistoryRepository:
    """Dependency injection for history repository."""
    from src.api.main import app
    return app.state.query_history_repository


@router.get("/query/{query_id}")
async def export_query_result(
    query_id: str,
    format: str = Query("csv", description="Export format: csv, json, excel, parquet, avro"),
    repository: QueryHistoryRepository = Depends(get_history_repository)
):
    """Export query result to a file."""
    try:
        # Get query from history
        query_history = await repository.get_by_id(query_id)
        if not query_history:
            raise HTTPException(status_code=404, detail="Query not found")
        
        # Get result data
        result_data = query_history.result.get("merged_data", [])
        if not result_data:
            raise HTTPException(status_code=404, detail="No data to export")
        
        # Create exporter
        exporter = ExporterFactory.create(format)
        
        # Export
        file_data = await exporter.export(result_data)
        
        # Generate filename
        filename = f"query_{query_id}.{exporter.get_file_extension()}"
        
        return StreamingResponse(
            file_data,
            media_type=exporter.get_content_type(),
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data")
async def export_data(
    data: list[dict],
    format: str = Query("csv", description="Export format: csv, json, excel, parquet, avro"),
    filename: Optional[str] = None
):
    """Export arbitrary data to a file."""
    try:
        # Create exporter
        exporter = ExporterFactory.create(format)
        
        # Export
        file_data = await exporter.export(data)
        
        # Generate filename
        if not filename:
            filename = f"export.{exporter.get_file_extension()}"
        elif not filename.endswith(f".{exporter.get_file_extension()}"):
            filename = f"{filename}.{exporter.get_file_extension()}"
        
        return StreamingResponse(
            file_data,
            media_type=exporter.get_content_type(),
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/formats")
async def get_supported_formats():
    """Get supported export formats."""
    return {
        "formats": ExporterFactory.get_supported_formats(),
        "default": "csv"
    }

