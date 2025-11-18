"""Qdrant vector database client."""
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from typing import List, Dict, Any, Optional
import asyncio

from config.settings import get_settings


class QdrantVectorDBClient:
    """Qdrant client wrapper - KISS: Simple interface."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = QdrantClient(
            url=self.settings.qdrant_url,
            api_key=self.settings.qdrant_api_key if self.settings.qdrant_api_key else None,
            timeout=5,
            prefer_grpc=True  # gRPC is faster
        )
        self._collections_initialized = False
    
    async def initialize_collections(self) -> None:
        """Initialize collections if they don't exist."""
        if self._collections_initialized:
            return
        
        # Initialize schemas collection
        await self._ensure_collection(
            self.settings.qdrant_collection_schemas,
            self.settings.embedding_dimension
        )
        
        # Initialize content collection
        await self._ensure_collection(
            self.settings.qdrant_collection_content,
            self.settings.embedding_dimension
        )
        
        self._collections_initialized = True
    
    async def _ensure_collection(self, collection_name: str, vector_size: int) -> None:
        """Ensure collection exists with optimized settings."""
        # Run in thread pool since Qdrant client is sync
        loop = asyncio.get_event_loop()
        
        try:
            # Check if collection exists
            collections = await loop.run_in_executor(
                None,
                self.client.get_collections
            )
            existing_names = [c.name for c in collections.collections]
            
            if collection_name not in existing_names:
                # Create collection with performance-optimized settings
                await loop.run_in_executor(
                    None,
                    lambda: self.client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(
                            size=vector_size,
                            distance=Distance.COSINE,
                        ),
                        optimizers_config={
                            "indexing_threshold": 10000,  # Fast indexing
                        },
                        hnsw_config={
                            "m": 16,  # Balance between speed and accuracy
                            "ef_construct": 100,
                        }
                    )
                )
        except Exception as e:
            # Collection might already exist, that's okay
            pass
    
    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: float = 0.7,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search vectors with optional filtering."""
        loop = asyncio.get_event_loop()
        
        # Build filter if provided
        query_filter = None
        if filter_dict:
            conditions = []
            for key, value in filter_dict.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            if conditions:
                query_filter = Filter(must=conditions)
        
        # Perform search
        results = await loop.run_in_executor(
            None,
            lambda: self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=query_filter,
                with_payload=True
            )
        )
        
        # Convert to dict format
        return [
            {
                "id": result.id,
                "score": result.score,
                "payload": result.payload
            }
            for result in results
        ]
    
    async def batch_upsert(
        self,
        collection_name: str,
        points: List[Dict[str, Any]]
    ) -> None:
        """Batch upsert points to collection."""
        loop = asyncio.get_event_loop()
        
        # Convert to PointStruct
        point_structs = [
            PointStruct(
                id=point["id"],
                vector=point["vector"],
                payload=point.get("payload", {})
            )
            for point in points
        ]
        
        # Batch upsert
        await loop.run_in_executor(
            None,
            lambda: self.client.upsert(
                collection_name=collection_name,
                points=point_structs
            )
        )
    
    async def delete_points(
        self,
        collection_name: str,
        point_ids: List[str]
    ) -> None:
        """Delete points by IDs."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.client.delete(
                collection_name=collection_name,
                points_selector=point_ids
            )
        )
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get collection information."""
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(
            None,
            lambda: self.client.get_collection(collection_name)
        )
        return {
            "points_count": info.points_count,
            "vectors_count": info.vectors_count,
            "config": info.config.dict() if hasattr(info.config, 'dict') else str(info.config)
        }

