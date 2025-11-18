"""Unit tests for domain models."""
import pytest
from datetime import datetime

from src.domain.database import Database
from src.domain.schema import Schema, Table, Column


def test_database_creation():
    """Test database entity creation."""
    database = Database(
        id="test_db",
        type="postgresql",
        name="Test Database",
        host="localhost",
        port=5432,
        database_name="test"
    )
    
    assert database.id == "test_db"
    assert database.type == "postgresql"
    assert database.is_active is True


def test_schema_creation():
    """Test schema entity creation."""
    table = Table(
        name="users",
        columns=[
            Column(name="id", data_type="integer"),
            Column(name="name", data_type="varchar")
        ]
    )
    
    schema = Schema(
        database_id="test_db",
        tables=[table]
    )
    
    assert schema.database_id == "test_db"
    assert schema.total_tables == 1
    assert schema.total_columns == 2

