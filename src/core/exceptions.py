"""Custom exceptions."""
from typing import Optional


class NavoException(Exception):
    """Base exception for Navo."""
    pass


class DatabaseConnectionError(NavoException):
    """Raised when database connection fails."""
    def __init__(self, message: str, database_id: Optional[str] = None):
        self.database_id = database_id
        super().__init__(message)


class SchemaExtractionError(NavoException):
    """Raised when schema extraction fails."""
    def __init__(self, message: str, database_id: Optional[str] = None):
        self.database_id = database_id
        super().__init__(message)


class QueryGenerationError(NavoException):
    """Raised when query generation fails."""
    def __init__(self, message: str, user_query: Optional[str] = None):
        self.user_query = user_query
        super().__init__(message)


class QueryExecutionError(NavoException):
    """Raised when query execution fails."""
    def __init__(self, message: str, query: Optional[str] = None):
        self.query = query
        super().__init__(message)


class VectorDBError(NavoException):
    """Raised when vector DB operation fails."""
    pass


class CacheError(NavoException):
    """Raised when cache operation fails."""
    pass

