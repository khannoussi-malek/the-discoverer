"""Request models (DTOs)."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class DatabaseConfigRequest(BaseModel):
    """Database configuration request."""
    id: str
    type: str
    name: Optional[str] = None
    host: str
    port: int
    database: str
    user: Optional[str] = None
    password: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class QueryRequest(BaseModel):
    """Query request."""
    query: str = Field(..., description="Natural language query")
    database_ids: Optional[List[str]] = Field(
        None,
        description="Specific database IDs to query (optional, will auto-select if not provided)"
    )
    compress: Optional[bool] = Field(
        False,
        description="Compress query results (reduces response size)"
    )
    compression_type: Optional[str] = Field(
        "gzip",
        description="Compression algorithm: gzip, zlib, lzma, or brotli"
    )


class VisualizationRequest(BaseModel):
    """Visualization request."""
    query_id: str
    chart_type: Optional[str] = Field(
        None,
        description="Chart type: bar, line, pie, scatter, table, heatmap, box, violin, scatter3d, surface, sunburst, treemap, funnel, gauge, waterfall"
    )
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    z_axis: Optional[str] = None
    title: Optional[str] = None
    config: Optional[Dict[str, Any]] = None  # Advanced configuration


class QueryTemplateRequest(BaseModel):
    """Query template creation request."""
    name: str
    user_query: str
    database_ids: Optional[List[str]] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_public: bool = False


class ExecuteTemplateRequest(BaseModel):
    """Execute template request."""
    template_id: str
    parameters: Optional[Dict[str, Any]] = None


class APIKeyCreateRequest(BaseModel):
    """API key creation request."""
    name: str
    scopes: Optional[List[str]] = None
    expires_in_days: Optional[int] = None
    rate_limit: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class APIKeyUpdateRequest(BaseModel):
    """API key update request."""
    name: Optional[str] = None
    scopes: Optional[List[str]] = None
    is_active: Optional[bool] = None
    rate_limit: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class ChartTemplateCreateRequest(BaseModel):
    """Chart template creation request."""
    name: str
    chart_type: str
    config: Dict[str, Any]
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: bool = False


class ChartTemplateUpdateRequest(BaseModel):
    """Chart template update request."""
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None


class DashboardCreateRequest(BaseModel):
    """Dashboard creation request."""
    name: str
    description: Optional[str] = None
    widgets: Optional[List[Dict[str, Any]]] = None
    layout: Optional[Dict[str, Any]] = None
    is_public: bool = False
    tags: Optional[List[str]] = None


class DashboardUpdateRequest(BaseModel):
    """Dashboard update request."""
    name: Optional[str] = None
    description: Optional[str] = None
    widgets: Optional[List[Dict[str, Any]]] = None
    layout: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None


class WebhookCreateRequest(BaseModel):
    """Webhook creation request."""
    url: str
    events: List[str]
    headers: Optional[Dict[str, str]] = None
    timeout: Optional[int] = 30


class WebhookUpdateRequest(BaseModel):
    """Webhook update request."""
    url: Optional[str] = None
    events: Optional[List[str]] = None
    active: Optional[bool] = None
    headers: Optional[Dict[str, str]] = None
    timeout: Optional[int] = None


class ExportTemplateCreateRequest(BaseModel):
    """Export template creation request."""
    name: str
    format: str
    description: Optional[str] = None
    filename_pattern: Optional[str] = None
    column_selection: Optional[List[str]] = None
    column_mapping: Optional[Dict[str, str]] = None
    formatting: Optional[Dict[str, Any]] = None
    compression: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    sorting: Optional[List[Dict[str, str]]] = None
    tags: Optional[List[str]] = None
    is_public: bool = False


class ExportTemplateUpdateRequest(BaseModel):
    """Export template update request."""
    name: Optional[str] = None
    format: Optional[str] = None
    description: Optional[str] = None
    filename_pattern: Optional[str] = None
    column_selection: Optional[List[str]] = None
    column_mapping: Optional[Dict[str, str]] = None
    formatting: Optional[Dict[str, Any]] = None
    compression: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    sorting: Optional[List[Dict[str, str]]] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None


class ScheduledExportCreateRequest(BaseModel):
    """Scheduled export creation request."""
    name: str
    query: str
    frequency: str  # hourly, daily, weekly, monthly, custom
    schedule: str  # Cron expression
    export_format: str  # csv, json, excel, parquet, avro
    database_ids: Optional[List[str]] = None
    export_template_id: Optional[str] = None
    destination: Optional[str] = None
    filename_pattern: Optional[str] = None
    description: Optional[str] = None
    notify_on_failure: bool = False
    notify_email: Optional[str] = None

