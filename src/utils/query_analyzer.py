"""Query analysis utilities."""
import re
from typing import Dict, Any, List


class QueryAnalyzer:
    """Analyze queries to extract information."""
    
    @staticmethod
    def analyze_query(query: str) -> Dict[str, Any]:
        """Analyze query to extract metadata."""
        query_lower = query.lower()
        
        # Detect query type
        query_type = QueryAnalyzer._detect_query_type(query_lower)
        
        # Detect complexity
        complexity = QueryAnalyzer._detect_complexity(query_lower)
        
        # Extract entities
        entities = QueryAnalyzer._extract_entities(query_lower)
        
        # Detect operations
        operations = QueryAnalyzer._detect_operations(query_lower)
        
        return {
            "type": query_type,
            "complexity": complexity,
            "entities": entities,
            "operations": operations,
            "estimated_time": QueryAnalyzer._estimate_time(complexity, operations)
        }
    
    @staticmethod
    def _detect_query_type(query: str) -> str:
        """Detect query type."""
        if any(word in query for word in ["count", "how many", "number of"]):
            return "count"
        elif any(word in query for word in ["list", "show", "get", "find", "select"]):
            return "select"
        elif any(word in query for word in ["sum", "total", "average", "avg", "max", "min"]):
            return "aggregate"
        elif any(word in query for word in ["join", "combine", "merge"]):
            return "join"
        else:
            return "general"
    
    @staticmethod
    def _detect_complexity(query: str) -> str:
        """Detect query complexity."""
        complex_keywords = [
            "join", "group by", "having", "union", "subquery",
            "aggregate", "window", "cte", "with"
        ]
        
        if any(keyword in query for keyword in complex_keywords):
            return "complex"
        elif "where" in query or "order by" in query:
            return "medium"
        else:
            return "simple"
    
    @staticmethod
    def _extract_entities(query: str) -> List[str]:
        """Extract potential entity names (tables, etc.)."""
        # Simple pattern matching - could be improved with NLP
        entities = []
        
        # Look for common patterns
        patterns = [
            r'\b(customers?|users?|orders?|products?|items?)\b',
            r'\b(table|collection|database)\s+(\w+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    entities.extend([m for m in match if m])
                else:
                    entities.append(match)
        
        return list(set(entities))
    
    @staticmethod
    def _detect_operations(query: str) -> List[str]:
        """Detect operations in query."""
        operations = []
        
        if "count" in query:
            operations.append("count")
        if "sum" in query or "total" in query:
            operations.append("sum")
        if "average" in query or "avg" in query:
            operations.append("average")
        if "join" in query:
            operations.append("join")
        if "group by" in query:
            operations.append("group")
        if "order by" in query or "sort" in query:
            operations.append("sort")
        
        return operations
    
    @staticmethod
    def _estimate_time(complexity: str, operations: List[str]) -> float:
        """Estimate query execution time in seconds."""
        base_times = {
            "simple": 0.1,
            "medium": 0.5,
            "complex": 2.0
        }
        
        base_time = base_times.get(complexity, 1.0)
        
        # Add time for operations
        operation_penalties = {
            "join": 0.3,
            "group": 0.2,
            "aggregate": 0.2
        }
        
        for op in operations:
            base_time += operation_penalties.get(op, 0.1)
        
        return base_time

