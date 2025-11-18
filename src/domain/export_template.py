"""Export template domain entity."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List


@dataclass
class ExportTemplate:
    """Export template entity."""
    id: str
    name: str
    format: str  # csv, json, excel, parquet, avro
    description: Optional[str] = None
    filename_pattern: Optional[str] = None  # e.g., "export_{date}_{query_id}.csv"
    column_selection: Optional[List[str]] = None  # Selected columns
    column_mapping: Optional[Dict[str, str]] = None  # Rename columns
    formatting: Optional[Dict[str, Any]] = None  # Formatting options
    compression: Optional[Dict[str, Any]] = None  # Compression settings
    filters: Optional[Dict[str, Any]] = None  # Data filters
    sorting: Optional[List[Dict[str, str]]] = None  # Sort configuration
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    is_public: bool = False
    usage_count: int = 0



