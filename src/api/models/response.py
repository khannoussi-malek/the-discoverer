"""Response models (DTOs)."""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class DatabaseResponse(BaseModel):
    """Database response."""
    id: str
    type: str
    name: str
    host: str
    port: int
    database_name: str
    is_active: bool
    last_synced: Optional[str] = None


class QueryResponse(BaseModel):
    """Query response."""
    query_id: str
    data: Optional[List[Dict[str, Any]]] = None
    compressed_data: Optional[str] = None
    compression_info: Optional[Dict[str, Any]] = None
    total_rows: int
    execution_time: float
    databases_queried: List[str]
    cached: bool = False
    page: Optional[int] = None
    page_size: Optional[int] = None
    total_pages: Optional[int] = None


class VisualizationResponse(BaseModel):
    """Visualization response."""
    visualization_id: str
    chart_data: Dict[str, Any]
    chart_type: str
    format: str = "json"


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None


class QueryTemplateResponse(BaseModel):
    """Query template response."""
    id: str
    name: str
    description: Optional[str]
    user_query: str
    database_ids: Optional[List[str]]
    parameters: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    tags: Optional[List[str]]
    is_public: bool


class PaginatedResponse(BaseModel):
    """Paginated response."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
