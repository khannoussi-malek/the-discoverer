"""Query API routes."""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from typing import Optional
import json

from src.api.models.request import QueryRequest
from src.api.models.response import QueryResponse, ErrorResponse
from src.application.services.query_service import QueryService
from src.application.services.pagination_service import PaginationService
from src.utils.query_analyzer import QueryAnalyzer
from src.api.routes.websocket import get_connection_manager
from src.utils.compression import CompressionService, CompressionType
from src.utils.streaming import StreamingFormat, QueryResultStreamer, ProgressStreamer


router = APIRouter(prefix="/api/query", tags=["query"])


def get_query_service() -> QueryService:
    """Dependency injection for query service."""
    from src.api.main import app
    return app.state.query_service


@router.post("/execute")
async def execute_query(
    request: QueryRequest,
    stream: bool = False,
    stream_format: str = Query("ndjson", description="Streaming format: ndjson, json, csv, tsv"),
    stream_progress: bool = Query(False, description="Include progress updates in stream"),
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    service: QueryService = Depends(get_query_service)
):
    """Execute a natural language query."""
    try:
        # Analyze query first
        analysis = QueryAnalyzer.analyze_query(request.query)
        
        result = await service.execute_query(
            user_query=request.query,
            database_ids=request.database_ids
        )
        
        # Get first query ID from results
        query_id = list(result.results.values())[0].query_id if result.results else ""
        
        # Trigger webhook for query completion
        if query_id:
            try:
                from src.api.main import app
                if hasattr(app.state, 'webhook_service'):
                    from src.utils.webhooks import WebhookEvent
                    await app.state.webhook_service.trigger_webhook(
                        WebhookEvent.QUERY_COMPLETED,
                        {
                            "query_id": query_id,
                            "query": request.query,
                            "total_rows": result.total_rows,
                            "execution_time": result.execution_time,
                            "databases_queried": result.databases_queried
                        }
                    )
            except Exception:
                # Don't fail query if webhook fails
                pass
        
        # If streaming requested, return streaming response
        if stream:
            return StreamingResponse(
                _stream_query_result_improved(
                    result,
                    stream_format=stream_format,
                    include_progress=stream_progress
                ),
                media_type=_get_stream_media_type(stream_format)
            )
        
        # Apply pagination if requested
        data = result.merged_data
        total_pages = None
        if page is not None and page_size is not None:
            paginated = PaginationService.paginate(result.merged_data, page, page_size)
            data = paginated.items
            total_pages = paginated.total_pages
            
            # Notify WebSocket subscribers if any
            if query_id:
                manager = get_connection_manager()
                await manager.notify_query_update(query_id, {
                    "status": "completed",
                    "total_rows": result.total_rows,
                    "page": page,
                    "page_size": page_size
                })
        
        # Apply compression if requested
        compressed_data = None
        compression_info = None
        if request.compress:
            try:
                compression_type = CompressionType(request.compression_type.lower())
                compressed_result = CompressionService.compress_json(data, compression_type)
                compressed_data = compressed_result["data"]
                compression_info = {
                    "compression_type": compressed_result["compression_type"],
                    "original_size": compressed_result["original_size"],
                    "compressed_size": compressed_result["compressed_size"],
                    "compression_ratio": compressed_result["compression_ratio"],
                    "space_saved": compressed_result["space_saved"]
                }
                data = None  # Don't send uncompressed data if compressed
            except Exception:
                # If compression fails, fall back to uncompressed
                pass
        
        return QueryResponse(
            query_id=query_id,
            data=data,
            compressed_data=compressed_data,
            compression_info=compression_info,
            total_rows=result.total_rows,
            execution_time=result.execution_time,
            databases_queried=result.databases_queried,
            cached=False,  # Could check cache status
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _stream_query_result(result):
    """Stream query results as NDJSON (legacy)."""
    # Send metadata first
    metadata = {
        "query_id": list(result.results.values())[0].query_id if result.results else "",
        "total_rows": result.total_rows,
        "databases_queried": result.databases_queried
    }
    yield json.dumps(metadata) + "\n"
    
    # Stream data rows
    for row in result.merged_data:
        yield json.dumps(row) + "\n"


async def _stream_query_result_improved(
    result,
    stream_format: str = "ndjson",
    include_progress: bool = False
):
    """Improved streaming with format options and progress."""
    from src.utils.streaming import StreamingFormat, QueryResultStreamer, ProgressStreamer
    
    # Prepare metadata
    metadata = {
        "query_id": list(result.results.values())[0].query_id if result.results else "",
        "total_rows": result.total_rows,
        "databases_queried": result.databases_queried,
        "execution_time": result.execution_time,
        "format": stream_format
    }
    
    # Create async iterator from merged data
    async def data_iterator():
        for row in result.merged_data:
            yield row
    
    # Choose streamer
    if include_progress:
        streamer = ProgressStreamer(
            total_rows=result.total_rows,
            format=StreamingFormat(stream_format.lower())
        )
        async for chunk in streamer.stream_with_progress(data_iterator(), metadata):
            yield chunk
    else:
        streamer = QueryResultStreamer(StreamingFormat(stream_format.lower()))
        async for chunk in streamer.stream_results(data_iterator(), metadata):
            yield chunk


def _get_stream_media_type(format: str) -> str:
    """Get media type for streaming format."""
    format_map = {
        "ndjson": "application/x-ndjson",
        "json": "application/json",
        "csv": "text/csv",
        "tsv": "text/tab-separated-values"
    }
    return format_map.get(format.lower(), "application/x-ndjson")


@router.post("/analyze")
async def analyze_query(
    request: QueryRequest
):
    """Analyze a query without executing it."""
    try:
        analysis = QueryAnalyzer.analyze_query(request.query)
        return {
            "query": request.query,
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
