"""Content indexing to vector database."""
from typing import List, Dict, Any

from src.infrastructure.vector_db.client import QdrantVectorDBClient
from src.infrastructure.embeddings.generator import EmbeddingGenerator
from config.settings import get_settings


class ContentIndexer:
    """Content indexer - KISS: One responsibility."""
    
    def __init__(
        self,
        vector_db_client: QdrantVectorDBClient,
        embedding_generator: EmbeddingGenerator
    ):
        self.vector_db = vector_db_client
        self.embedding_generator = embedding_generator
        self.settings = get_settings()
    
    async def index_table_content(
        self,
        db_id: str,
        table: str,
        data: List[Dict[str, Any]],
        strategy: str = "smart"
    ) -> None:
        """Index table content to vector DB."""
        if strategy == "smart":
            strategy = self._determine_strategy(len(data))
        
        if strategy == "full":
            items = data
        elif strategy == "sampled":
            items = self._sample_data(data, n=1000)
        elif strategy == "aggregated":
            items = self._create_aggregations(data)
        else:
            items = data
        
        if not items:
            return
        
        # Prepare texts for embedding
        texts = [self._create_content_text(item, table) for item in items]
        
        # Batch embed
        embeddings = await self.embedding_generator.generate_batch(texts)
        
        # Create points
        points = []
        for item, embedding in zip(items, embeddings):
            item_id = item.get('id') or str(hash(str(item)))
            points.append({
                "id": f"{db_id}.content.{table}.{item_id}",
                "vector": embedding,
                "payload": {
                    "type": "content",
                    "database_id": db_id,
                    "table": table,
                    "data": item
                }
            })
        
        # Batch upsert
        await self.vector_db.batch_upsert(
            self.settings.qdrant_collection_content,
            points
        )
    
    def _determine_strategy(self, row_count: int) -> str:
        """Determine indexing strategy based on table size."""
        if row_count < 10000:
            return "full"
        elif row_count < 100000:
            return "sampled"
        else:
            return "aggregated"
    
    def _sample_data(self, data: List[Dict[str, Any]], n: int = 1000) -> List[Dict[str, Any]]:
        """Sample diverse rows from data."""
        if len(data) <= n:
            return data
        
        # Simple sampling - take evenly spaced samples
        step = len(data) // n
        return [data[i] for i in range(0, len(data), step)][:n]
    
    def _create_aggregations(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create aggregated summaries from data."""
        # Simplified aggregation - in production, would do more sophisticated aggregation
        if not data:
            return []
        
        # Return first item as sample
        return [data[0]]
    
    def _create_content_text(self, item: Dict[str, Any], table: str) -> str:
        """Create text representation for content embedding."""
        parts = [f"Table: {table}"]
        
        # Add field values (especially text fields)
        for key, value in item.items():
            if isinstance(value, str) and len(value) > 0:
                parts.append(f"{key}: {value}")
            elif isinstance(value, (int, float)):
                parts.append(f"{key}: {value}")
        
        return " ".join(parts)

