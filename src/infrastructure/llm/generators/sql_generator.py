"""SQL query generator with pattern matching."""
import re
from typing import List, Dict, Any, Optional

from src.infrastructure.llm.generators.base import QueryGenerator
from src.infrastructure.llm.client import LLMClient
from src.domain.query import Query
from config.settings import get_settings


class SQLGenerator(QueryGenerator):
    """SQL generation strategy with pattern matching."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.settings = get_settings()
        self.simple_patterns = self._load_patterns()
    
    async def generate(
        self,
        user_query: str,
        schema_context: List[Dict[str, Any]]
    ) -> Query:
        """Generate SQL query with pattern matching fallback."""
        # Try pattern matching first (instant, no LLM call)
        simple_query = self._match_simple_pattern(user_query, schema_context)
        if simple_query:
            return Query(
                user_query=user_query,
                generated_query=simple_query["sql"],
                query_type="sql",
                database_id=schema_context[0]["payload"]["database_id"] if schema_context else "",
                confidence=0.9
            )
        
        # Use LLM for complex queries
        prompt = self._build_prompt(user_query, schema_context)
        
        # Select model based on complexity
        model = self._select_model(user_query)
        
        sql = await self.llm_client.generate(prompt, model=model)
        
        # Clean SQL (remove markdown code blocks if present)
        sql = self._clean_sql(sql)
        
        return Query(
            user_query=user_query,
            generated_query=sql,
            query_type="sql",
            database_id=schema_context[0]["payload"]["database_id"] if schema_context else "",
            confidence=0.8
        )
    
    def _match_simple_pattern(
        self,
        query: str,
        schema_context: List[Dict[str, Any]]
    ) -> Optional[Dict[str, str]]:
        """Match common patterns without LLM (instant)."""
        query_lower = query.lower()
        
        # Extract table name from schema context
        table = self._extract_table(query, schema_context)
        if not table:
            return None
        
        # Pattern: "count X" or "how many X"
        if query_lower.startswith("count") or "how many" in query_lower:
            return {"sql": f'SELECT COUNT(*) FROM "{table}"'}
        
        # Pattern: "list/show/get X"
        if query_lower.startswith(("list", "show", "get", "select")):
            limit = self._extract_limit(query_lower) or 100
            return {"sql": f'SELECT * FROM "{table}" LIMIT {limit}'}
        
        # Pattern: "find X where Y"
        if "where" in query_lower:
            where_clause = self._extract_where_clause(query_lower)
            if where_clause:
                return {"sql": f'SELECT * FROM "{table}" WHERE {where_clause} LIMIT 100'}
        
        return None
    
    def _extract_table(
        self,
        query: str,
        schema_context: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Extract table name from schema context."""
        if not schema_context:
            return None
        
        # Get first table from context
        for item in schema_context:
            payload = item.get("payload", {})
            if payload.get("type") == "table":
                return payload.get("table_name")
        
        return None
    
    def _extract_limit(self, query: str) -> Optional[int]:
        """Extract limit from query."""
        match = re.search(r'limit\s+(\d+)', query, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None
    
    def _extract_where_clause(self, query: str) -> Optional[str]:
        """Extract WHERE clause from query (simplified)."""
        # This is a simplified extraction - could be more sophisticated
        match = re.search(r'where\s+(.+?)(?:\s+limit|\s*$)', query, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
    
    def _select_model(self, query: str) -> str:
        """Select model based on query complexity."""
        complexity = self._estimate_complexity(query)
        if complexity == "simple":
            return self.settings.openai_model  # GPT-3.5-turbo (faster, cheaper)
        else:
            return self.settings.openai_model_complex  # GPT-4 (better for complex)
    
    def _estimate_complexity(self, query: str) -> str:
        """Estimate query complexity."""
        complex_keywords = ["join", "group by", "having", "union", "subquery", "aggregate"]
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in complex_keywords):
            return "complex"
        return "simple"
    
    def _clean_sql(self, sql: str) -> str:
        """Clean SQL (remove markdown, extra whitespace)."""
        # Remove markdown code blocks
        sql = re.sub(r'```sql\s*', '', sql, flags=re.IGNORECASE)
        sql = re.sub(r'```\s*', '', sql)
        
        # Remove leading/trailing whitespace
        sql = sql.strip()
        
        return sql
    
    def _load_patterns(self) -> Dict[str, str]:
        """Load SQL template patterns."""
        return {
            "count": "SELECT COUNT(*) FROM {table}",
            "list": "SELECT * FROM {table} LIMIT {limit}",
            "find": "SELECT * FROM {table} WHERE {condition} LIMIT {limit}",
        }

