"""Validation utilities."""
import re
from typing import Any, List, Optional


def validate_sql_query(query: str) -> List[str]:
    """Validate SQL query for safety."""
    from src.utils.sql_safety import SQLSafetyChecker
    
    is_safe, warnings = SQLSafetyChecker.is_safe(query)
    
    if not is_safe:
        return warnings
    
    return []


def validate_database_id(db_id: str) -> bool:
    """Validate database ID format."""
    # Alphanumeric, underscore, hyphen, max 50 chars
    pattern = r'^[a-zA-Z0-9_-]{1,50}$'
    return bool(re.match(pattern, db_id))


def validate_table_name(table_name: str) -> bool:
    """Validate table name format."""
    # Alphanumeric, underscore, max 100 chars
    pattern = r'^[a-zA-Z0-9_]{1,100}$'
    return bool(re.match(pattern, table_name))


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Sanitize string input."""
    # Remove null bytes and limit length
    sanitized = value.replace('\x00', '')
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    return sanitized

