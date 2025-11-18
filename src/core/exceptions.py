"""Custom exceptions."""
from typing import Optional


class DiscovererException(Exception):
    """Base exception for The Discoverer."""
    pass


class DatabaseConnectionError(DiscovererException):
    """Raised when database connection fails."""
    def __init__(self, message: str, database_id: Optional[str] = None):
        self.database_id = database_id
        super().__init__(message)


class SchemaExtractionError(DiscovererException):
    """Raised when schema extraction fails."""
    def __init__(self, message: str, database_id: Optional[str] = None):
        self.database_id = database_id
        super().__init__(message)


class QueryGenerationError(DiscovererException):
    """Raised when query generation fails."""
    def __init__(self, message: str, user_query: Optional[str] = None):
        self.user_query = user_query
        super().__init__(message)


class QueryExecutionError(DiscovererException):
    """Raised when query execution fails."""
    def __init__(self, message: str, query: Optional[str] = None):
        self.query = query
        super().__init__(message)


class VectorDBError(DiscovererException):
    """Raised when vector DB operation fails."""
    pass


class CacheError(DiscovererException):
    """Raised when cache operation fails."""
    pass

