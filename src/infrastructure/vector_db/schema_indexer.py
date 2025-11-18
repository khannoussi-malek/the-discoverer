"""Schema indexing to vector database."""
from typing import List, Dict, Any

from src.domain.schema import Schema, Table, Column
from src.infrastructure.vector_db.client import QdrantVectorDBClient
from src.infrastructure.embeddings.generator import EmbeddingGenerator
from config.settings import get_settings


class SchemaIndexer:
    """Schema indexer - KISS: One responsibility."""
    
    def __init__(
        self,
        vector_db_client: QdrantVectorDBClient,
        embedding_generator: EmbeddingGenerator
    ):
        self.vector_db = vector_db_client
        self.embedding_generator = embedding_generator
        self.settings = get_settings()
    
    async def index_schema(self, database_id: str, schema: Schema) -> None:
        """Index schema to vector DB."""
        points = []
        
        # Table-level embeddings
        table_texts = []
        table_metadata = []
        for table in schema.tables:
            text = self._create_table_text(table)
            table_texts.append(text)
            table_metadata.append({
                "id": f"{database_id}.table.{table.name}",
                "type": "table",
                "database_id": database_id,
                "table_name": table.name,
                "description": table.description or "",
                "column_count": len(table.columns),
                "columns": [c.name for c in table.columns]
            })
        
        # Batch embed tables
        if table_texts:
            table_embeddings = await self.embedding_generator.generate_batch(table_texts)
            for embedding, metadata in zip(table_embeddings, table_metadata):
                points.append({
                    "id": metadata["id"],
                    "vector": embedding,
                    "payload": metadata
                })
        
        # Column-level embeddings
        column_texts = []
        column_metadata = []
        for table in schema.tables:
            for column in table.columns:
                text = self._create_column_text(table, column)
                column_texts.append(text)
                column_metadata.append({
                    "id": f"{database_id}.column.{table.name}.{column.name}",
                    "type": "column",
                    "database_id": database_id,
                    "table_name": table.name,
                    "column_name": column.name,
                    "data_type": column.data_type,
                    "description": column.description or ""
                })
        
        # Batch embed columns
        if column_texts:
            column_embeddings = await self.embedding_generator.generate_batch(column_texts)
            for embedding, metadata in zip(column_embeddings, column_metadata):
                points.append({
                    "id": metadata["id"],
                    "vector": embedding,
                    "payload": metadata
                })
        
        # Batch upsert to vector DB
        if points:
            await self.vector_db.batch_upsert(
                self.settings.qdrant_collection_schemas,
                points
            )
    
    async def update_schema(
        self,
        database_id: str,
        changes: Dict[str, Any]
    ) -> None:
        """Incrementally update schema - only changed tables."""
        # Delete removed tables
        if changes.get("removed_tables"):
            point_ids = [
                f"{database_id}.table.{table_name}"
                for table_name in changes["removed_tables"]
            ]
            await self.vector_db.delete_points(
                self.settings.qdrant_collection_schemas,
                point_ids
            )
        
        # Re-index added/modified tables
        # This would require the full table objects, so we'll handle it in the service layer
    
    def _create_table_text(self, table: Table) -> str:
        """Create text representation for table embedding."""
        parts = [f"Table: {table.name}"]
        
        if table.description:
            parts.append(table.description)
        
        if table.columns:
            column_names = ", ".join([c.name for c in table.columns])
            parts.append(f"Columns: {column_names}")
        
        return " ".join(parts)
    
    def _create_column_text(self, table: Table, column: Column) -> str:
        """Create text representation for column embedding."""
        parts = [
            f"Table: {table.name}",
            f"Column: {column.name}",
            f"Type: {column.data_type}"
        ]
        
        if column.description:
            parts.append(column.description)
        
        return " ".join(parts)

