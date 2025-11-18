"""Query optimization utilities."""
from typing import Dict, Any, List, Optional
import re


class QueryOptimizer:
    """Query optimization analyzer."""
    
    @staticmethod
    def analyze_sql(query: str) -> Dict[str, Any]:
        """Analyze SQL query for optimization opportunities."""
        query_upper = query.upper()
        suggestions = []
        warnings = []
        score = 100  # Start with perfect score
        
        # Check for SELECT *
        if re.search(r'SELECT\s+\*', query_upper):
            suggestions.append({
                "type": "warning",
                "message": "Avoid SELECT * - specify columns explicitly",
                "impact": "medium",
                "fix": "List specific columns instead of *"
            })
            score -= 10
        
        # Check for missing WHERE clause on large tables
        if "SELECT" in query_upper and "WHERE" not in query_upper:
            suggestions.append({
                "type": "warning",
                "message": "Consider adding WHERE clause to filter results",
                "impact": "high",
                "fix": "Add WHERE conditions to limit rows"
            })
            score -= 15
        
        # Check for missing LIMIT
        if "SELECT" in query_upper and "LIMIT" not in query_upper and "WHERE" not in query_upper:
            suggestions.append({
                "type": "warning",
                "message": "Add LIMIT clause to prevent large result sets",
                "impact": "medium",
                "fix": "Add LIMIT N to restrict result size"
            })
            score -= 10
        
        # Check for LIKE without index hint
        if "LIKE" in query_upper and "%" in query:
            if query.count("%") == 1 and query.find("%") == 0:
                suggestions.append({
                    "type": "info",
                    "message": "Leading wildcard in LIKE may prevent index usage",
                    "impact": "medium",
                    "fix": "Consider full-text search or inverted index"
                })
                score -= 5
        
        # Check for multiple JOINs
        join_count = query_upper.count("JOIN")
        if join_count > 5:
            suggestions.append({
                "type": "warning",
                "message": f"Query has {join_count} JOINs - consider query structure",
                "impact": "medium",
                "fix": "Review join order and indexes"
            })
            score -= 5
        
        # Check for subqueries that could be JOINs
        if re.search(r'WHERE\s+.*\s+IN\s*\(.*SELECT', query_upper, re.DOTALL):
            suggestions.append({
                "type": "info",
                "message": "Consider converting IN (SELECT...) to JOIN",
                "impact": "low",
                "fix": "Use JOIN instead of subquery in WHERE clause"
            })
            score -= 3
        
        # Check for ORDER BY without LIMIT
        if "ORDER BY" in query_upper and "LIMIT" not in query_upper:
            suggestions.append({
                "type": "info",
                "message": "ORDER BY without LIMIT may be expensive",
                "impact": "low",
                "fix": "Add LIMIT if full sort is not needed"
            })
            score -= 3
        
        return {
            "score": max(0, score),
            "suggestions": suggestions,
            "warnings": warnings,
            "optimized": score >= 80
        }
    
    @staticmethod
    def suggest_indexes(query: str, schema: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Suggest indexes based on query."""
        suggestions = []
        query_upper = query.upper()
        
        # Extract WHERE conditions
        where_match = re.search(r'WHERE\s+(.+?)(?:\s+GROUP|\s+ORDER|\s+LIMIT|$)', query_upper, re.DOTALL)
        if where_match:
            conditions = where_match.group(1)
            
            # Find column names in WHERE
            column_pattern = r'(\w+)\s*[=<>!]'
            columns = re.findall(column_pattern, conditions)
            
            for column in set(columns):
                suggestions.append({
                    "type": "index",
                    "column": column,
                    "reason": "Used in WHERE clause",
                    "priority": "medium"
                })
        
        # Extract JOIN conditions
        join_matches = re.findall(r'JOIN\s+\w+\s+ON\s+(\w+\.\w+)\s*=\s*(\w+\.\w+)', query_upper)
        for left, right in join_matches:
            left_col = left.split('.')[-1]
            right_col = right.split('.')[-1]
            suggestions.append({
                "type": "index",
                "column": left_col,
                "reason": "Used in JOIN condition",
                "priority": "high"
            })
            suggestions.append({
                "type": "index",
                "column": right_col,
                "reason": "Used in JOIN condition",
                "priority": "high"
            })
        
        return suggestions
    
    @staticmethod
    def estimate_complexity(query: str) -> Dict[str, Any]:
        """Estimate query complexity."""
        query_upper = query.upper()
        
        complexity_score = 0
        factors = []
        
        # Count operations
        if "SELECT" in query_upper:
            complexity_score += 1
        if "JOIN" in query_upper:
            join_count = query_upper.count("JOIN")
            complexity_score += join_count * 2
            factors.append(f"{join_count} JOIN(s)")
        if "GROUP BY" in query_upper:
            complexity_score += 3
            factors.append("GROUP BY")
        if "ORDER BY" in query_upper:
            complexity_score += 2
            factors.append("ORDER BY")
        if "HAVING" in query_upper:
            complexity_score += 2
            factors.append("HAVING")
        if "UNION" in query_upper:
            complexity_score += 5
            factors.append("UNION")
        if "DISTINCT" in query_upper:
            complexity_score += 2
            factors.append("DISTINCT")
        
        # Subquery detection
        subquery_count = query_upper.count("SELECT") - 1
        if subquery_count > 0:
            complexity_score += subquery_count * 3
            factors.append(f"{subquery_count} subquery(ies)")
        
        # Determine level
        if complexity_score <= 3:
            level = "simple"
        elif complexity_score <= 8:
            level = "medium"
        elif complexity_score <= 15:
            level = "complex"
        else:
            level = "very_complex"
        
        return {
            "score": complexity_score,
            "level": level,
            "factors": factors
        }


