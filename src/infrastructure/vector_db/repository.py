"""Vector database repository."""
from typing import List, Dict, Any, Optional

from src.infrastructure.vector_db.client import QdrantVectorDBClient
from src.infrastructure.embeddings.generator import EmbeddingGenerator
from config.settings import get_settings


class VectorDBRepository:
    """Vector DB repository - Repository pattern."""
    
    def __init__(
        self,
        vector_db_client: QdrantVectorDBClient,
        embedding_generator: EmbeddingGenerator
    ):
        self.vector_db = vector_db_client
        self.embedding_generator = embedding_generator
        self.settings = get_settings()
    
    async def search_schema(
        self,
        query: str,
        database_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search schema using natural language query."""
        # Generate query embedding
        query_embedding = await self.embedding_generator.generate(query)
        
        # Build filter
        filter_dict = None
        if database_id:
            filter_dict = {"database_id": database_id}
        
        # Search
        results = await self.vector_db.search(
            collection_name=self.settings.qdrant_collection_schemas,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=self.settings.vector_search_threshold,
            filter_dict=filter_dict
        )
        
        return results
    
    async def search_content(
        self,
        query: str,
        database_id: Optional[str] = None,
        table: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search content using natural language query."""
        # Generate query embedding
        query_embedding = await self.embedding_generator.generate(query)
        
        # Build filter
        filter_dict = {}
        if database_id:
            filter_dict["database_id"] = database_id
        if table:
            filter_dict["table"] = table
        
        # Search
        results = await self.vector_db.search(
            collection_name=self.settings.qdrant_collection_content,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=self.settings.vector_search_threshold,
            filter_dict=filter_dict if filter_dict else None
        )
        
        return results

