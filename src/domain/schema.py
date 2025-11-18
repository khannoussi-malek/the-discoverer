"""Schema domain entities."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Any


@dataclass(frozen=True)
class ForeignKey:
    """Foreign key relationship."""
    
    column: str
    referenced_table: str
    referenced_column: str


@dataclass(frozen=True)
class Index:
    """Database index."""
    
    name: str
    columns: List[str]
    unique: bool = False
    index_type: Optional[str] = None


@dataclass(frozen=True)
class Column:
    """Column entity - KISS: Simple structure."""
    
    name: str
    data_type: str
    nullable: bool = True
    default_value: Optional[Any] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    max_length: Optional[int] = None
    description: Optional[str] = None


@dataclass(frozen=True)
class Table:
    """Table entity - KISS: Simple structure."""
    
    name: str
    columns: List[Column]
    primary_keys: List[str] = field(default_factory=list)
    foreign_keys: List[ForeignKey] = field(default_factory=list)
    indexes: List[str] = field(default_factory=list)
    row_count: Optional[int] = None
    description: Optional[str] = None


@dataclass(frozen=True)
class Relationship:
    """Relationship between tables."""
    
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relationship_type: str  # "one-to-many", "many-to-one", "many-to-many"


@dataclass(frozen=True)
class Schema:
    """Schema entity - KISS: Simple structure."""
    
    database_id: str
    tables: List[Table]
    relationships: List[Relationship] = field(default_factory=list)
    indexes: List[Index] = field(default_factory=list)
    version: int = 1
    extracted_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Calculate derived fields."""
        object.__setattr__(self, 'total_tables', len(self.tables))
        object.__setattr__(
            self, 
            'total_columns', 
            sum(len(t.columns) for t in self.tables)
        )

