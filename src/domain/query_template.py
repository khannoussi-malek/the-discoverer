"""Query template domain model."""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class QueryTemplate:
    """Saved query template."""
    id: str
    name: str
    description: Optional[str]
    user_query: str
    database_ids: Optional[list[str]]
    parameters: Optional[Dict[str, Any]]  # Template parameters
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]  # User ID
    tags: Optional[list[str]]
    is_public: bool = False


