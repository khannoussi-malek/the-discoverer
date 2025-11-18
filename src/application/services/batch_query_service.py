"""Batch query execution service."""
from typing import List, Dict, Any, Optional
import asyncio
import time

from src.application.services.query_service import QueryService
from src.domain.result import AggregatedResult


class BatchQueryRequest:
    """Batch query request."""
    def __init__(
        self,
        query: str,
        database_ids: Optional[List[str]] = None,
        priority: int = 0  # Higher = more priority
    ):
        self.query = query
        self.database_ids = database_ids
        self.priority = priority


class BatchQueryResult:
    """Batch query result."""
    def __init__(
        self,
        request: BatchQueryRequest,
        result: Optional[AggregatedResult] = None,
        error: Optional[str] = None,
        execution_time: float = 0.0
    ):
        self.request = request
        self.result = result
        self.error = error
        self.execution_time = execution_time
        self.success = result is not None


class BatchQueryService:
    """Service for executing multiple queries in batch."""
    
    def __init__(self, query_service: QueryService):
        self.query_service = query_service
    
    async def execute_batch(
        self,
        requests: List[BatchQueryRequest],
        max_concurrent: int = 5,
        stop_on_error: bool = False
    ) -> List[BatchQueryResult]:
        """Execute multiple queries in batch."""
        # Sort by priority (higher first)
        sorted_requests = sorted(requests, key=lambda r: r.priority, reverse=True)
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_single(request: BatchQueryRequest) -> BatchQueryResult:
            """Execute a single query with semaphore."""
            async with semaphore:
                start_time = time.time()
                try:
                    result = await self.query_service.execute_query(
                        user_query=request.query,
                        database_ids=request.database_ids
                    )
                    execution_time = time.time() - start_time
                    return BatchQueryResult(request, result, execution_time=execution_time)
                except Exception as e:
                    execution_time = time.time() - start_time
                    if stop_on_error:
                        raise
                    return BatchQueryResult(
                        request,
                        error=str(e),
                        execution_time=execution_time
                    )
        
        # Execute all queries
        if stop_on_error:
            tasks = [execute_single(req) for req in sorted_requests]
            results = await asyncio.gather(*tasks)
        else:
            tasks = [execute_single(req) for req in sorted_requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Convert exceptions to error results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append(BatchQueryResult(
                        sorted_requests[i],
                        error=str(result),
                        execution_time=0.0
                    ))
                else:
                    processed_results.append(result)
            results = processed_results
        
        return results
    
    async def execute_sequential(
        self,
        requests: List[BatchQueryRequest],
        stop_on_error: bool = False
    ) -> List[BatchQueryResult]:
        """Execute queries sequentially."""
        results = []
        
        for request in requests:
            start_time = time.time()
            try:
                result = await self.query_service.execute_query(
                    user_query=request.query,
                    database_ids=request.database_ids
                )
                execution_time = time.time() - start_time
                results.append(BatchQueryResult(
                    request,
                    result,
                    execution_time=execution_time
                ))
            except Exception as e:
                execution_time = time.time() - start_time
                if stop_on_error:
                    raise
                results.append(BatchQueryResult(
                    request,
                    error=str(e),
                    execution_time=execution_time
                ))
        
        return results


