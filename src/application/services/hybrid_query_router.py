"""Hybrid query router - Smart routing between content and schema vector DB."""
from typing import Dict, Any, Optional, List

from src.domain.result import AggregatedResult
from src.infrastructure.vector_db.repository import VectorDBRepository
from src.application.services.query_service import QueryService


class HybridQueryRouter:
    """Hybrid query router - Smart query routing."""
    
    def __init__(
        self,
        vector_db_repository: VectorDBRepository,
        query_service: QueryService
    ):
        self.vector_db = vector_db_repository
        self.query_service = query_service
    
    async def route_query(
        self,
        user_query: str,
        database_ids: Optional[List[str]] = None
    ) -> AggregatedResult:
        """
        Smart routing: Try content vector DB first, fall back to schema + SQL.
        """
        # Analyze query type
        query_analysis = self._analyze_query(user_query)
        
        # Try content vector DB if suitable
        if query_analysis["suitable_for_content"]:
            content_result = await self._try_content_search(user_query, database_ids)
            if content_result and content_result.get("confidence", 0) > 0.8:
                # Use content result (fast path)
                return AggregatedResult(
                    results={},
                    merged_data=content_result.get("data", []),
                    aggregation_type="content_search",
                    total_rows=len(content_result.get("data", [])),
                    execution_time=content_result.get("time", 0.0),
                    databases_queried=database_ids or []
                )
        
        # Fall back to schema + SQL (slower but accurate)
        return await self.query_service.execute_query(user_query, database_ids)
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine routing strategy."""
        query_lower = query.lower()
        
        # Queries suitable for content search
        content_keywords = ["similar", "like", "find", "search", "show me"]
        needs_realtime = any(word in query_lower for word in ["current", "now", "latest", "real-time"])
        
        suitable_for_content = (
            any(keyword in query_lower for keyword in content_keywords) and
            not needs_realtime
        )
        
        return {
            "suitable_for_content": suitable_for_content,
            "needs_realtime": needs_realtime,
            "type": "semantic_search" if suitable_for_content else "analytical"
        }
    
    async def _try_content_search(
        self,
        query: str,
        database_ids: Optional[List[str]]
    ) -> Optional[Dict[str, Any]]:
        """Try to answer from content vector DB."""
        import time
        start_time = time.time()
        
        # Search content vector DB
        results = []
        if database_ids:
            for db_id in database_ids:
                content_results = await self.vector_db.search_content(
                    query=query,
                    database_id=db_id,
                    limit=10
                )
                results.extend(content_results)
        else:
            content_results = await self.vector_db.search_content(
                query=query,
                limit=20
            )
            results.extend(content_results)
        
        if results and len(results) > 0:
            # Extract data from results
            data = [r["payload"].get("data", {}) for r in results]
            confidence = results[0].get("score", 0.0)
            
            return {
                "data": data,
                "confidence": confidence,
                "time": time.time() - start_time
            }
        
        return None

