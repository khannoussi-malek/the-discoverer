"""Query result comparison service."""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from src.domain.result import AggregatedResult


@dataclass
class ComparisonResult:
    """Query result comparison."""
    query1_id: str
    query2_id: str
    compared_at: datetime
    differences: Dict[str, Any]
    similarity_score: float
    row_count_diff: int
    column_differences: List[Dict[str, Any]]
    value_differences: List[Dict[str, Any]]


class QueryComparisonService:
    """Service for comparing query results."""
    
    async def compare_results(
        self,
        result1: AggregatedResult,
        result2: AggregatedResult,
        query1_id: str = "",
        query2_id: str = ""
    ) -> ComparisonResult:
        """Compare two query results."""
        data1 = result1.merged_data
        data2 = result2.merged_data
        
        # Calculate differences
        row_count_diff = len(data1) - len(data2)
        
        # Column differences
        columns1 = set(data1[0].keys()) if data1 else set()
        columns2 = set(data2[0].keys()) if data2 else set()
        
        added_columns = columns2 - columns1
        removed_columns = columns1 - columns2
        common_columns = columns1 & columns2
        
        column_differences = []
        if added_columns:
            column_differences.append({
                "type": "added",
                "columns": list(added_columns)
            })
        if removed_columns:
            column_differences.append({
                "type": "removed",
                "columns": list(removed_columns)
            })
        
        # Value differences (compare common columns)
        value_differences = []
        if data1 and data2 and common_columns:
            min_len = min(len(data1), len(data2))
            
            for i in range(min_len):
                row_diffs = []
                for col in common_columns:
                    val1 = data1[i].get(col)
                    val2 = data2[i].get(col)
                    
                    if val1 != val2:
                        row_diffs.append({
                            "column": col,
                            "value1": val1,
                            "value2": val2
                        })
                
                if row_diffs:
                    value_differences.append({
                        "row_index": i,
                        "differences": row_diffs
                    })
        
        # Calculate similarity score
        similarity_score = self._calculate_similarity(
            data1, data2, common_columns
        )
        
        return ComparisonResult(
            query1_id=query1_id,
            query2_id=query2_id,
            compared_at=datetime.utcnow(),
            differences={
                "row_count_diff": row_count_diff,
                "added_columns": list(added_columns),
                "removed_columns": list(removed_columns),
                "common_columns": list(common_columns)
            },
            similarity_score=similarity_score,
            row_count_diff=row_count_diff,
            column_differences=column_differences,
            value_differences=value_differences
        )
    
    def _calculate_similarity(
        self,
        data1: List[Dict[str, Any]],
        data2: List[Dict[str, Any]],
        common_columns: set
    ) -> float:
        """Calculate similarity score between two datasets."""
        if not data1 or not data2:
            return 0.0
        
        if not common_columns:
            return 0.0
        
        # Compare row counts
        row_count_similarity = 1.0 - abs(len(data1) - len(data2)) / max(len(data1), len(data2), 1)
        
        # Compare values in common columns
        min_len = min(len(data1), len(data2))
        if min_len == 0:
            return 0.0
        
        matching_values = 0
        total_values = 0
        
        for i in range(min_len):
            for col in common_columns:
                total_values += 1
                if data1[i].get(col) == data2[i].get(col):
                    matching_values += 1
        
        value_similarity = matching_values / total_values if total_values > 0 else 0.0
        
        # Weighted average
        similarity = (row_count_similarity * 0.3) + (value_similarity * 0.7)
        
        return round(similarity, 4)
    
    async def compare_by_query_ids(
        self,
        query1_id: str,
        query2_id: str
    ) -> ComparisonResult:
        """Compare results by query IDs from history."""
        from src.api.main import app
        history_repo = app.state.query_history_repository
        
        history1 = await history_repo.get_by_id(query1_id)
        history2 = await history_repo.get_by_id(query2_id)
        
        if not history1 or not history2:
            raise ValueError("One or both queries not found in history")
        
        result1 = history1.get("result")
        result2 = history2.get("result")
        
        if not result1 or not result2:
            raise ValueError("One or both queries have no results")
        
        # Create AggregatedResult objects
        from src.domain.result import AggregatedResult
        agg_result1 = AggregatedResult(
            results={},
            merged_data=result1.get("merged_data", []),
            aggregation_type=result1.get("aggregation_type", "merge"),
            total_rows=result1.get("total_rows", 0),
            execution_time=result1.get("execution_time", 0.0),
            databases_queried=result1.get("databases_queried", [])
        )
        
        agg_result2 = AggregatedResult(
            results={},
            merged_data=result2.get("merged_data", []),
            aggregation_type=result2.get("aggregation_type", "merge"),
            total_rows=result2.get("total_rows", 0),
            execution_time=result2.get("execution_time", 0.0),
            databases_queried=result2.get("databases_queried", [])
        )
        
        return await self.compare_results(
            agg_result1,
            agg_result2,
            query1_id,
            query2_id
        )


