"""Base query generator - Strategy pattern."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from src.domain.query import Query
from src.domain.schema import Schema


class QueryGenerator(ABC):
    """Strategy interface - KISS: Simple contract."""
    
    @abstractmethod
    async def generate(
        self,
        user_query: str,
        schema_context: List[Dict[str, Any]]
    ) -> Query:
        """Generate query from natural language."""
        pass
    
    def _build_prompt(
        self,
        user_query: str,
        schema_context: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for LLM."""
        # Extract relevant schema information
        schema_text = self._format_schema_context(schema_context)
        
        prompt = f"""
Given the following database schema information:

{schema_text}

User wants to: {user_query}

Generate a SQL query to fulfill this request. Return only the SQL query, no explanations.
"""
        return prompt
    
    def _format_schema_context(self, schema_context: List[Dict[str, Any]]) -> str:
        """Format schema context for prompt."""
        parts = []
        for item in schema_context:
            payload = item.get("payload", {})
            if payload.get("type") == "table":
                parts.append(
                    f"Table: {payload.get('table_name')} "
                    f"({', '.join(payload.get('columns', []))})"
                )
            elif payload.get("type") == "column":
                parts.append(
                    f"Column: {payload.get('table_name')}.{payload.get('column_name')} "
                    f"({payload.get('data_type')})"
                )
        return "\n".join(parts)

