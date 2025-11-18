"""Indexing API routes."""
from fastapi import APIRouter, HTTPException, Depends

from src.application.services.indexing_service import IndexingService


router = APIRouter(prefix="/api/indexing", tags=["indexing"])


def get_indexing_service() -> IndexingService:
    """Dependency injection for indexing service."""
    from src.api.main import app
    return app.state.indexing_service


@router.post("/databases/{db_id}/tables/{table}/index")
async def index_table_content(
    db_id: str,
    table: str,
    strategy: str = "smart",
    service: IndexingService = Depends(get_indexing_service)
):
    """Index table content to vector database."""
    try:
        await service.index_table_content(db_id, table, strategy)
        return {"status": "success", "message": f"Table {table} indexed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

