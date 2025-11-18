"""Database configuration validators."""
from typing import Dict, Any, List
from src.core.exceptions import DatabaseConnectionError
from src.infrastructure.database.adapters.factory import DatabaseAdapterFactory


def validate_database_config(config: Dict[str, Any]) -> List[str]:
    """Validate database configuration and return list of errors."""
    errors = []
    
    # Required fields
    required_fields = ["id", "type", "host", "port", "database"]
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
    
    # Validate database type
    if "type" in config:
        supported_types = DatabaseAdapterFactory.get_supported_types()
        if config["type"].lower() not in supported_types:
            errors.append(
                f"Unsupported database type: {config['type']}. "
                f"Supported types: {', '.join(supported_types)}"
            )
    
    # Validate port
    if "port" in config:
        try:
            port = int(config["port"])
            if port < 1 or port > 65535:
                errors.append("Port must be between 1 and 65535")
        except (ValueError, TypeError):
            errors.append("Port must be a valid integer")
    
    # Validate host
    if "host" in config and not config["host"]:
        errors.append("Host cannot be empty")
    
    # Validate database name
    if "database" in config and not config["database"]:
        errors.append("Database name cannot be empty")
    
    return errors


async def validate_database_connection(config: Dict[str, Any]) -> None:
    """Validate that database connection works."""
    try:
        adapter = DatabaseAdapterFactory.create(config["type"], config)
        await adapter.connect()
        
        if not await adapter.test_connection():
            raise DatabaseConnectionError(
                f"Connection test failed for database {config.get('id')}",
                database_id=config.get("id")
            )
        
        await adapter.disconnect()
    except Exception as e:
        if isinstance(e, DatabaseConnectionError):
            raise
        raise DatabaseConnectionError(
            f"Failed to validate database connection: {str(e)}",
            database_id=config.get("id")
        )

