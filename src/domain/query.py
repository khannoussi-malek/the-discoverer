"""Query domain entities."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid


@dataclass(frozen=True)
class Query:
    """Query entity - KISS: Simple data class."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_query: str
    generated_query: str  # SQL, MongoDB query, etc.
    query_type: str  # "sql", "mongodb", "cql", etc.
    database_id: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    execution_plan: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class QueryPlan:
    """Query plan for multi-database queries."""
    
    databases: List[str]
    sub_queries: Dict[str, Query]  # db_id -> query
    aggregation_strategy: str  # "merge", "join", "aggregate"
    join_keys: Optional[Dict[str, str]] = None
    estimated_time: Optional[float] = None

