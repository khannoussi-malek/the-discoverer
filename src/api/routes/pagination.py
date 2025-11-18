"""Server-side pagination API routes."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from src.application.services.pagination_service import PaginationService
from src.infrastructure.database.repository import DatabaseRepository
from src.infrastructure.database.adapters.factory import DatabaseAdapterFactory


router = APIRouter(prefix="/api/pagination", tags=["pagination"])


def get_db_repository() -> DatabaseRepository:
    """Dependency injection for database repository."""
    from src.api.main import app
    return app.state.db_repository


@router.post("/query")
async def paginate_query(
    database_id: str,
    query: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=1000),
    repository: DatabaseRepository = Depends(get_db_repository)
):
    """Execute query with server-side pagination."""
    try:
        # Get database
        database = await repository.get_by_id(database_id)
        if not database:
            raise HTTPException(status_code=404, detail="Database not found")
        
        # Build paginated query
        paginated_query, offset = PaginationService.build_sql_pagination(
            query, page, page_size, database.type
        )
        
        # Build count query
        count_query = PaginationService.build_count_query(query)
        
        # Execute queries in parallel
        import asyncio
        adapter = DatabaseAdapterFactory.create(database.type, database.config)
        await adapter.connect()
        
        try:
            # Execute both queries
            data_task = adapter.execute_query(paginated_query)
            count_task = adapter.execute_query(count_query)
            
            data, count_result = await asyncio.gather(data_task, count_task)
            
            # Extract total
            total = count_result[0].get("total", 0) if count_result else 0
            
            # Calculate pagination metadata
            total_pages = (total + page_size - 1) // page_size if total > 0 else 0
            
            return {
                "items": data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        finally:
            await adapter.disconnect()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


