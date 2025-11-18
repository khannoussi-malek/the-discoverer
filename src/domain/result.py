"""Result domain entities."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List
import uuid


@dataclass(frozen=True)
class Result:
    """Query result entity - KISS: Simple data class."""
    
    query_id: str
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)  # row_count, execution_time, etc.
    cached: bool = False
    execution_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class AggregatedResult:
    """Aggregated result from multiple databases."""
    
    results: Dict[str, Result]  # db_id -> result
    merged_data: List[Dict[str, Any]]
    aggregation_type: str
    total_rows: int
    execution_time: float
    databases_queried: List[str] = field(default_factory=list)

