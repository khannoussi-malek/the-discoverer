"""Query service - Business logic for query execution."""
import time
import hashlib
from typing import List, Optional, Dict, Any

from src.domain.query import Query, QueryPlan
from src.domain.result import Result, AggregatedResult
from src.infrastructure.database.repository import DatabaseRepository
from src.infrastructure.vector_db.repository import VectorDBRepository
from src.infrastructure.llm.generators.factory import QueryGeneratorFactory
from src.infrastructure.database.adapters.factory import DatabaseAdapterFactory
from src.infrastructure.cache.repository import CacheRepository
from src.infrastructure.query_history.repository import QueryHistoryRepository
from src.utils.validators import validate_sql_query
from src.core.exceptions import QueryExecutionError


class QueryService:
    """Query service - KISS: One responsibility."""
    
    def __init__(
        self,
        db_repository: DatabaseRepository,
        vector_db_repository: VectorDBRepository,
        query_generator_factory: QueryGeneratorFactory,
        cache: CacheRepository,
        query_history: Optional[QueryHistoryRepository] = None
    ):
        self.db_repository = db_repository
        self.vector_db = vector_db_repository
        self.query_generator_factory = query_generator_factory
        self.cache = cache
        self.query_history = query_history
    
    async def execute_query(
        self,
        user_query: str,
        database_ids: Optional[List[str]] = None
    ) -> AggregatedResult:
        """
        Execute query across one or more databases.
        
        Steps:
        1. Check cache
        2. Select databases (if not specified)
        3. Search vector DB for relevant schema
        4. Generate queries per database
        5. Execute queries in parallel
        6. Aggregate results
        7. Cache result
        """
        start_time = time.time()
        
        # Check cache
        cache_key = self._generate_cache_key(user_query, database_ids)
        cached = await self.cache.get(cache_key)
        if cached:
            return AggregatedResult(**cached)
        
        # Select databases
        if not database_ids:
            database_ids = await self._select_databases(user_query)
        
        # Search vector DB for schema context
        schema_contexts = {}
        for db_id in database_ids:
            contexts = await self.vector_db.search_schema(
                query=user_query,
                database_id=db_id,
                limit=10
            )
            schema_contexts[db_id] = contexts
        
        # Generate queries
        queries = {}
        for db_id in database_ids:
            database = await self.db_repository.get_by_id(db_id)
            if not database:
                continue
            
            try:
                generator = self.query_generator_factory.create(database.type)
                query = await generator.generate(user_query, schema_contexts[db_id])
                
                # Validate SQL queries for safety
                if query.query_type == "sql":
                    validation_errors = validate_sql_query(query.generated_query)
                    if validation_errors:
                        raise QueryExecutionError(
                            f"Query validation failed: {', '.join(validation_errors)}",
                            query=query.generated_query
                        )
                
                queries[db_id] = query
            except Exception as e:
                # Log error but continue with other databases
                continue
        
        # Execute queries in parallel
        results = await self._execute_parallel(queries)
        
        # Aggregate
        aggregated = await self._aggregate_results(results, user_query)
        aggregated.execution_time = time.time() - start_time
        
        # Cache result
        await self.cache.set(
            cache_key,
            {
                "results": {k: v.__dict__ for k, v in aggregated.results.items()},
                "merged_data": aggregated.merged_data,
                "aggregation_type": aggregated.aggregation_type,
                "total_rows": aggregated.total_rows,
                "execution_time": aggregated.execution_time,
                "databases_queried": aggregated.databases_queried
            },
            ttl=600
        )
        
        # Save to history
        if self.query_history and queries:
            # Get first query for history
            first_query = list(queries.values())[0]
            await self.query_history.save(first_query, aggregated)
        
        return aggregated
    
    async def _select_databases(self, user_query: str) -> List[str]:
        """Select relevant databases based on query."""
        # Search vector DB across all databases
        results = await self.vector_db.search_schema(query=user_query, limit=50)
        
        # Group by database and calculate scores
        db_scores = {}
        for result in results:
            db_id = result["payload"].get("database_id")
            if not db_id:
                continue
            
            score = result.get("score", 0)
            if db_id not in db_scores:
                db_scores[db_id] = {"score": 0, "count": 0, "top_score": 0}
            
            db_scores[db_id]["score"] += score
            db_scores[db_id]["count"] += 1
            db_scores[db_id]["top_score"] = max(db_scores[db_id]["top_score"], score)
        
        # Calculate final scores (weighted)
        final_scores = {}
        for db_id, stats in db_scores.items():
            final_scores[db_id] = (
                stats["top_score"] * 0.7 +
                (stats["score"] / stats["count"]) * 0.3
            )
        
        # Select top databases (above threshold)
        selected = [
            db_id for db_id, score in final_scores.items()
            if score > 0.6
        ]
        
        return selected[:3]  # Limit to top 3
    
    async def _execute_parallel(
        self,
        queries: Dict[str, Query]
    ) -> Dict[str, Result]:
        """Execute queries in parallel."""
        import asyncio
        
        async def execute_single(db_id: str, query: Query) -> tuple[str, Result]:
            start_time = time.time()
            
            database = await self.db_repository.get_by_id(db_id)
            if not database:
                return db_id, Result(
                    query_id=query.id,
                    data=[],
                    metadata={"error": "Database not found"},
                    execution_time=0
                )
            
            adapter = DatabaseAdapterFactory.create(database.type, database.config)
            await adapter.connect()
            
            try:
                # Handle different query types
                if query.query_type in ["mongodb", "elasticsearch"]:
                    # NoSQL queries are JSON strings
                    import json
                    query_data = json.loads(query.generated_query)
                    data = await adapter.execute_query(query_data)
                else:
                    # SQL/CQL queries are strings
                    data = await adapter.execute_query(query.generated_query)
                
                execution_time = time.time() - start_time
                
                return db_id, Result(
                    query_id=query.id,
                    data=data,
                    metadata={
                        "row_count": len(data),
                        "database_id": db_id,
                        "query": query.generated_query
                    },
                    execution_time=execution_time
                )
            except Exception as e:
                return db_id, Result(
                    query_id=query.id,
                    data=[],
                    metadata={"error": str(e)},
                    execution_time=time.time() - start_time
                )
            finally:
                await adapter.disconnect()
        
        # Execute all queries in parallel
        tasks = [execute_single(db_id, query) for db_id, query in queries.items()]
        results_list = await asyncio.gather(*tasks)
        
        return {db_id: result for db_id, result in results_list}
    
    async def _aggregate_results(
        self,
        results: Dict[str, Result],
        user_query: str
    ) -> AggregatedResult:
        """Aggregate results from multiple databases."""
        # Determine aggregation strategy
        strategy = self._determine_strategy(user_query, results)
        
        if strategy == "merge":
            merged_data = self._merge_results(results)
        elif strategy == "join":
            merged_data = self._join_results(results)
        else:
            merged_data = self._aggregate_stats(results)
        
        total_rows = sum(
            r.metadata.get("row_count", 0) for r in results.values()
        )
        execution_time = max(r.execution_time for r in results.values())
        
        return AggregatedResult(
            results=results,
            merged_data=merged_data,
            aggregation_type=strategy,
            total_rows=total_rows,
            execution_time=execution_time,
            databases_queried=list(results.keys())
        )
    
    def _determine_strategy(
        self,
        user_query: str,
        results: Dict[str, Result]
    ) -> str:
        """Determine aggregation strategy."""
        query_lower = user_query.lower()
        
        if "join" in query_lower or "combine" in query_lower:
            return "join"
        elif any(word in query_lower for word in ["total", "sum", "average", "count"]):
            return "aggregate"
        else:
            return "merge"
    
    def _merge_results(self, results: Dict[str, Result]) -> List[Dict[str, Any]]:
        """Simple merge: Combine results from multiple DBs."""
        merged = []
        for db_id, result in results.items():
            for row in result.data:
                row_copy = dict(row)
                row_copy["_source_database"] = db_id
                merged.append(row_copy)
        return merged
    
    def _join_results(self, results: Dict[str, Result]) -> List[Dict[str, Any]]:
        """Join results across databases (simplified)."""
        # For now, just merge (proper join would need join keys)
        return self._merge_results(results)
    
    def _aggregate_stats(self, results: Dict[str, Result]) -> List[Dict[str, Any]]:
        """Aggregate statistics across databases."""
        stats = {}
        for db_id, result in results.items():
            stats[db_id] = {
                "row_count": result.metadata.get("row_count", 0),
                "execution_time": result.execution_time
            }
        
        return [{"database": db_id, **stats} for db_id, stats in stats.items()]
    
    def _generate_cache_key(
        self,
        query: str,
        db_ids: Optional[List[str]]
    ) -> str:
        """Generate consistent cache key."""
        key_parts = [query]
        if db_ids:
            key_parts.extend(sorted(db_ids))
        key_string = "|".join(key_parts)
        return f"query:{hashlib.md5(key_string.encode()).hexdigest()}"

