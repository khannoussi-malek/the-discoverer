"""Analytics and usage tracking utilities."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class UsageStats:
    """Usage statistics."""
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    total_execution_time: float = 0.0
    avg_execution_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    database_usage: Dict[str, int] = field(default_factory=dict)
    query_types: Dict[str, int] = field(default_factory=dict)
    time_period: Optional[str] = None


class AnalyticsCollector:
    """Analytics data collector."""
    
    def __init__(self):
        self.query_log: List[Dict[str, Any]] = []
        self.max_log_size = 10000
    
    def record_query(
        self,
        query: str,
        database_ids: List[str],
        execution_time: float,
        success: bool,
        cached: bool = False,
        query_type: Optional[str] = None
    ):
        """Record a query execution."""
        entry = {
            "timestamp": datetime.utcnow(),
            "query": query[:200],  # Truncate long queries
            "database_ids": database_ids,
            "execution_time": execution_time,
            "success": success,
            "cached": cached,
            "query_type": query_type
        }
        
        self.query_log.append(entry)
        
        # Trim log if too large
        if len(self.query_log) > self.max_log_size:
            self.query_log = self.query_log[-self.max_log_size:]
    
    def get_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> UsageStats:
        """Get usage statistics for a time period."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=7)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Filter logs by date
        filtered_logs = [
            log for log in self.query_log
            if start_date <= log["timestamp"] <= end_date
        ]
        
        if not filtered_logs:
            return UsageStats()
        
        stats = UsageStats()
        stats.total_queries = len(filtered_logs)
        stats.successful_queries = sum(1 for log in filtered_logs if log["success"])
        stats.failed_queries = stats.total_queries - stats.successful_queries
        
        execution_times = [log["execution_time"] for log in filtered_logs]
        stats.total_execution_time = sum(execution_times)
        stats.avg_execution_time = stats.total_execution_time / len(execution_times) if execution_times else 0.0
        
        stats.cache_hits = sum(1 for log in filtered_logs if log.get("cached", False))
        stats.cache_misses = stats.total_queries - stats.cache_hits
        
        # Database usage
        for log in filtered_logs:
            for db_id in log.get("database_ids", []):
                stats.database_usage[db_id] = stats.database_usage.get(db_id, 0) + 1
        
        # Query types
        for log in filtered_logs:
            query_type = log.get("query_type", "unknown")
            stats.query_types[query_type] = stats.query_types.get(query_type, 0) + 1
        
        return stats
    
    def get_top_queries(
        self,
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get most frequently executed queries."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=7)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Filter and count
        filtered_logs = [
            log for log in self.query_log
            if start_date <= log["timestamp"] <= end_date
        ]
        
        query_counts = defaultdict(int)
        query_times = defaultdict(list)
        
        for log in filtered_logs:
            query = log["query"]
            query_counts[query] += 1
            query_times[query].append(log["execution_time"])
        
        # Sort by count
        top_queries = sorted(
            query_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        result = []
        for query, count in top_queries:
            times = query_times[query]
            result.append({
                "query": query,
                "execution_count": count,
                "avg_execution_time": sum(times) / len(times) if times else 0.0,
                "total_execution_time": sum(times)
            })
        
        return result
    
    def get_database_stats(
        self,
        database_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get statistics for a specific database."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=7)
        if not end_date:
            end_date = datetime.utcnow()
        
        filtered_logs = [
            log for log in self.query_log
            if start_date <= log["timestamp"] <= end_date
            and database_id in log.get("database_ids", [])
        ]
        
        if not filtered_logs:
            return {
                "database_id": database_id,
                "total_queries": 0,
                "successful_queries": 0,
                "failed_queries": 0,
                "avg_execution_time": 0.0
            }
        
        return {
            "database_id": database_id,
            "total_queries": len(filtered_logs),
            "successful_queries": sum(1 for log in filtered_logs if log["success"]),
            "failed_queries": sum(1 for log in filtered_logs if not log["success"]),
            "avg_execution_time": sum(log["execution_time"] for log in filtered_logs) / len(filtered_logs),
            "cache_hit_rate": sum(1 for log in filtered_logs if log.get("cached", False)) / len(filtered_logs) if filtered_logs else 0.0
        }


# Global analytics collector
analytics_collector = AnalyticsCollector()


