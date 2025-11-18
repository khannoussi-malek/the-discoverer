"""CQL (Cassandra Query Language) generator."""
from typing import List, Dict, Any, Optional

from src.infrastructure.llm.generators.base import QueryGenerator
from src.infrastructure.llm.client import LLMClient
from src.domain.query import Query
from config.settings import get_settings


class CQLGenerator(QueryGenerator):
    """CQL generation strategy for Cassandra."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.settings = get_settings()
    
    async def generate(
        self,
        user_query: str,
        schema_context: List[Dict[str, Any]]
    ) -> Query:
        """Generate CQL query from natural language."""
        # Try pattern matching first
        simple_query = self._match_simple_pattern(user_query, schema_context)
        if simple_query:
            return Query(
                user_query=user_query,
                generated_query=simple_query,
                query_type="cql",
                database_id=schema_context[0]["payload"]["database_id"] if schema_context else "",
                confidence=0.9
            )
        
        # Use LLM for complex queries
        prompt = self._build_cql_prompt(user_query, schema_context)
        model = self._select_model(user_query)
        
        cql = await self.llm_client.generate(prompt, model=model)
        
        # Clean CQL
        cql = self._clean_cql(cql)
        
        return Query(
            user_query=user_query,
            generated_query=cql,
            query_type="cql",
            database_id=schema_context[0]["payload"]["database_id"] if schema_context else "",
            confidence=0.8
        )
    
    def _match_simple_pattern(
        self,
        query: str,
        schema_context: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Match common patterns without LLM."""
        query_lower = query.lower()
        
        # Extract table name
        table = self._extract_table(query, schema_context)
        if not table:
            return None
        
        keyspace = schema_context[0]["payload"].get("keyspace", "")
        table_prefix = f"{keyspace}." if keyspace else ""
        
        # Pattern: "count X"
        if query_lower.startswith("count") or "how many" in query_lower:
            return f"SELECT COUNT(*) FROM {table_prefix}{table}"
        
        # Pattern: "list/show/get X"
        if query_lower.startswith(("list", "show", "get", "select")):
            limit = self._extract_limit(query_lower) or 100
            return f"SELECT * FROM {table_prefix}{table} LIMIT {limit}"
        
        return None
    
    def _extract_table(
        self,
        query: str,
        schema_context: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Extract table name from schema context."""
        if not schema_context:
            return None
        
        for item in schema_context:
            payload = item.get("payload", {})
            if payload.get("type") == "table":
                return payload.get("table_name")
        
        return None
    
    def _extract_limit(self, query: str) -> Optional[int]:
        """Extract limit from query."""
        import re
        match = re.search(r'limit\s+(\d+)', query, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None
    
    def _build_cql_prompt(
        self,
        user_query: str,
        schema_context: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for CQL generation."""
        schema_text = self._format_schema_context(schema_context)
        
        prompt = f"""
Given the following Cassandra database schema information:

{schema_text}

User wants to: {user_query}

Generate a CQL (Cassandra Query Language) query to fulfill this request.
Return only the CQL query, no explanations.
"""
        return prompt
    
    def _select_model(self, query: str) -> str:
        """Select model based on query complexity."""
        complexity = self._estimate_complexity(query)
        if complexity == "simple":
            return self.settings.openai_model
        else:
            return self.settings.openai_model_complex
    
    def _estimate_complexity(self, query: str) -> str:
        """Estimate query complexity."""
        complex_keywords = ["join", "group by", "aggregate"]
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in complex_keywords):
            return "complex"
        return "simple"
    
    def _clean_cql(self, cql: str) -> str:
        """Clean CQL query."""
        import re
        
        # Remove markdown code blocks
        cql = re.sub(r'```cql\s*', '', cql, flags=re.IGNORECASE)
        cql = re.sub(r'```\s*', '', cql)
        cql = cql.strip()
        
        return cql


