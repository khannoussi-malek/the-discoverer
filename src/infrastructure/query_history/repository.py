"""Query history repository."""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import deque

from src.domain.query import Query
from src.domain.result import AggregatedResult


class QueryHistoryRepository:
    """Query history repository - In-memory implementation."""
    
    def __init__(self, max_history: int = 1000):
        self.history: deque = deque(maxlen=max_history)
        self._index: Dict[str, Query] = {}  # query_id -> Query
    
    async def save(
        self,
        query: Query,
        result: Optional[AggregatedResult] = None
    ) -> None:
        """Save query to history."""
        entry = {
            "query": query,
            "result": result,
            "timestamp": datetime.now()
        }
        self.history.append(entry)
        self._index[query.id] = query
    
    async def get_by_id(self, query_id: str) -> Optional[Dict[str, Any]]:
        """Get query history by ID."""
        for entry in self.history:
            if entry["query"].id == query_id:
                return entry
        return None
    
    async def get_recent(
        self,
        limit: int = 10,
        database_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recent queries."""
        recent = list(self.history)[-limit:]
        
        if database_id:
            recent = [
                entry for entry in recent
                if entry["query"].database_id == database_id
            ]
        
        return recent[-limit:]
    
    async def search(
        self,
        query_text: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search query history by text."""
        results = []
        query_lower = query_text.lower()
        
        for entry in reversed(self.history):
            if query_lower in entry["query"].user_query.lower():
                results.append(entry)
                if len(results) >= limit:
                    break
        
        return results
    
    async def get_statistics(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get query statistics."""
        cutoff = datetime.now() - timedelta(days=days)
        recent_queries = [
            entry for entry in self.history
            if entry["timestamp"] >= cutoff
        ]
        
        if not recent_queries:
            return {
                "total_queries": 0,
                "avg_execution_time": 0,
                "databases_queried": [],
                "query_types": {}
            }
        
        execution_times = [
            entry["result"].execution_time
            for entry in recent_queries
            if entry.get("result")
        ]
        
        databases = set()
        query_types = {}
        
        for entry in recent_queries:
            if entry["result"]:
                databases.update(entry["result"].databases_queried)
            query_type = entry["query"].query_type
            query_types[query_type] = query_types.get(query_type, 0) + 1
        
        return {
            "total_queries": len(recent_queries),
            "avg_execution_time": (
                sum(execution_times) / len(execution_times)
                if execution_times else 0
            ),
            "databases_queried": list(databases),
            "query_types": query_types
        }

