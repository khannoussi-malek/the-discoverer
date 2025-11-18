"""Schema change detection utilities."""
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json

from src.domain.schema import Schema


@dataclass
class SchemaChange:
    """Schema change entity."""
    database_id: str
    change_type: str  # "table_added", "table_removed", "table_modified", "column_added", "column_removed", "column_modified"
    table_name: Optional[str] = None
    column_name: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    detected_at: datetime = None
    
    def __post_init__(self):
        if self.detected_at is None:
            self.detected_at = datetime.utcnow()


class SchemaChangeDetector:
    """Detect changes in database schemas."""
    
    def __init__(self):
        self._schema_snapshots: Dict[str, Dict[str, Any]] = {}  # database_id -> schema_hash
    
    def _hash_schema(self, schema: Schema) -> str:
        """Generate hash for schema."""
        schema_dict = {
            "tables": [
                {
                    "name": table.name,
                    "columns": [
                        {
                            "name": col.name,
                            "type": col.type,
                            "nullable": col.nullable,
                            "default": col.default
                        }
                        for col in table.columns
                    ],
                    "primary_key": table.primary_key,
                    "foreign_keys": [
                        {
                            "column": fk.column,
                            "references_table": fk.references_table,
                            "references_column": fk.references_column
                        }
                        for fk in table.foreign_keys
                    ]
                }
                for table in schema.tables
            ]
        }
        
        schema_str = json.dumps(schema_dict, sort_keys=True, default=str)
        return hashlib.sha256(schema_str.encode()).hexdigest()
    
    def _normalize_schema(self, schema: Schema) -> Dict[str, Any]:
        """Normalize schema to dictionary for comparison."""
        return {
            "tables": {
                table.name: {
                    "columns": {
                        col.name: {
                            "type": col.type,
                            "nullable": col.nullable,
                            "default": col.default
                        }
                        for col in table.columns
                    },
                    "primary_key": table.primary_key,
                    "foreign_keys": [
                        {
                            "column": fk.column,
                            "references_table": fk.references_table,
                            "references_column": fk.references_column
                        }
                        for fk in table.foreign_keys
                    ]
                }
                for table in schema.tables
            }
        }
    
    async def detect_changes(
        self,
        database_id: str,
        current_schema: Schema
    ) -> List[SchemaChange]:
        """Detect changes between stored and current schema."""
        changes = []
        
        # Normalize schemas
        current_normalized = self._normalize_schema(current_schema)
        previous_normalized = self._schema_snapshots.get(database_id, {})
        
        if not previous_normalized:
            # First time seeing this schema, store it
            self._schema_snapshots[database_id] = current_normalized
            return []
        
        # Compare tables
        current_tables = set(current_normalized.get("tables", {}).keys())
        previous_tables = set(previous_normalized.get("tables", {}).keys())
        
        # Tables added
        for table_name in current_tables - previous_tables:
            changes.append(SchemaChange(
                database_id=database_id,
                change_type="table_added",
                table_name=table_name
            ))
        
        # Tables removed
        for table_name in previous_tables - current_tables:
            changes.append(SchemaChange(
                database_id=database_id,
                change_type="table_removed",
                table_name=table_name
            ))
        
        # Tables modified
        for table_name in current_tables & previous_tables:
            current_table = current_normalized["tables"][table_name]
            previous_table = previous_normalized["tables"][table_name]
            
            # Compare columns
            current_columns = set(current_table.get("columns", {}).keys())
            previous_columns = set(previous_table.get("columns", {}).keys())
            
            # Columns added
            for col_name in current_columns - previous_columns:
                changes.append(SchemaChange(
                    database_id=database_id,
                    change_type="column_added",
                    table_name=table_name,
                    column_name=col_name,
                    new_value=current_table["columns"][col_name]
                ))
            
            # Columns removed
            for col_name in previous_columns - current_columns:
                changes.append(SchemaChange(
                    database_id=database_id,
                    change_type="column_removed",
                    table_name=table_name,
                    column_name=col_name,
                    old_value=previous_table["columns"][col_name]
                ))
            
            # Columns modified
            for col_name in current_columns & previous_columns:
                current_col = current_table["columns"][col_name]
                previous_col = previous_table["columns"][col_name]
                
                if current_col != previous_col:
                    changes.append(SchemaChange(
                        database_id=database_id,
                        change_type="column_modified",
                        table_name=table_name,
                        column_name=col_name,
                        old_value=previous_col,
                        new_value=current_col
                    ))
            
            # Check for table-level changes (primary key, foreign keys)
            if current_table.get("primary_key") != previous_table.get("primary_key"):
                changes.append(SchemaChange(
                    database_id=database_id,
                    change_type="table_modified",
                    table_name=table_name,
                    old_value={"primary_key": previous_table.get("primary_key")},
                    new_value={"primary_key": current_table.get("primary_key")}
                ))
        
        # Update snapshot
        self._schema_snapshots[database_id] = current_normalized
        
        return changes
    
    def get_schema_snapshot(self, database_id: str) -> Optional[Dict[str, Any]]:
        """Get stored schema snapshot."""
        return self._schema_snapshots.get(database_id)
    
    def clear_snapshot(self, database_id: str):
        """Clear schema snapshot for a database."""
        if database_id in self._schema_snapshots:
            del self._schema_snapshots[database_id]


