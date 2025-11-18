"""Elasticsearch query generator."""
from typing import List, Dict, Any, Optional
import json

from src.infrastructure.llm.generators.base import QueryGenerator
from src.infrastructure.llm.client import LLMClient
from src.domain.query import Query
from config.settings import get_settings


class ElasticsearchGenerator(QueryGenerator):
    """Elasticsearch query generation strategy."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.settings = get_settings()
    
    async def generate(
        self,
        user_query: str,
        schema_context: List[Dict[str, Any]]
    ) -> Query:
        """Generate Elasticsearch query from natural language."""
        # Try pattern matching first
        simple_query = self._match_simple_pattern(user_query, schema_context)
        if simple_query:
            return Query(
                user_query=user_query,
                generated_query=json.dumps(simple_query),
                query_type="elasticsearch",
                database_id=schema_context[0]["payload"]["database_id"] if schema_context else "",
                confidence=0.9
            )
        
        # Use LLM for complex queries
        prompt = self._build_elasticsearch_prompt(user_query, schema_context)
        model = self._select_model(user_query)
        
        query_json = await self.llm_client.generate(prompt, model=model)
        
        # Clean and validate JSON
        query_dict = self._clean_and_validate_json(query_json)
        
        return Query(
            user_query=user_query,
            generated_query=json.dumps(query_dict),
            query_type="elasticsearch",
            database_id=schema_context[0]["payload"]["database_id"] if schema_context else "",
            confidence=0.8
        )
    
    def _match_simple_pattern(
        self,
        query: str,
        schema_context: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Match common patterns without LLM."""
        query_lower = query.lower()
        
        # Extract index name
        index = self._extract_index(query, schema_context)
        if not index:
            return None
        
        # Pattern: "search for X" or "find X"
        if "search" in query_lower or "find" in query_lower:
            # Extract search term
            search_term = self._extract_search_term(query_lower)
            if search_term:
                return {
                    "index": index,
                    "query": {
                        "match": {
                            "_all": search_term
                        }
                    },
                    "size": 100
                }
        
        # Pattern: "list/show all X"
        if query_lower.startswith(("list", "show", "get all")):
            return {
                "index": index,
                "query": {"match_all": {}},
                "size": 100
            }
        
        return None
    
    def _extract_index(
        self,
        query: str,
        schema_context: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Extract index name from schema context."""
        if not schema_context:
            return None
        
        for item in schema_context:
            payload = item.get("payload", {})
            if payload.get("type") == "table":
                return payload.get("table_name")
        
        return None
    
    def _extract_search_term(self, query: str) -> Optional[str]:
        """Extract search term from query."""
        import re
        # Simple extraction - look for quoted strings or words after "for"
        match = re.search(r'(?:for|search|find)\s+["\']?(\w+)["\']?', query, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def _build_elasticsearch_prompt(
        self,
        user_query: str,
        schema_context: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for Elasticsearch query generation."""
        schema_text = self._format_schema_context(schema_context)
        
        prompt = f"""
Given the following Elasticsearch index schema information:

{schema_text}

User wants to: {user_query}

Generate an Elasticsearch query in JSON format with the following structure:
{{
    "index": "index_name",
    "query": {{}},
    "size": 100
}}

Return only the JSON query, no explanations.
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
        complex_keywords = ["aggregate", "aggregation", "bool", "nested"]
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in complex_keywords):
            return "complex"
        return "simple"
    
    def _clean_and_validate_json(self, json_str: str) -> Dict[str, Any]:
        """Clean and validate JSON query."""
        import re
        
        # Remove markdown code blocks
        json_str = re.sub(r'```json\s*', '', json_str, flags=re.IGNORECASE)
        json_str = re.sub(r'```\s*', '', json_str)
        json_str = json_str.strip()
        
        # Try to parse JSON
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Try to extract JSON from text
            json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            raise ValueError(f"Invalid JSON: {json_str}")


