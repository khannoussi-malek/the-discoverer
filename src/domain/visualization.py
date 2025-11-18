"""Visualization domain entities."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import uuid


@dataclass(frozen=True)
class ChartConfig:
    """Chart configuration - KISS: Simple structure."""
    
    chart_type: str  # "bar", "line", "pie", "scatter", "table"
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    title: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    colors: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class Visualization:
    """Visualization entity - KISS: Simple data class."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query_id: str
    chart_config: ChartConfig
    data: List[Dict[str, Any]]
    format: str = "json"  # "json", "html", "png"
    created_at: datetime = field(default_factory=datetime.now)

