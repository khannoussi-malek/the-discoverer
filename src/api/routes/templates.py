"""Query template API routes."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional

from src.api.models.request import QueryTemplateRequest, ExecuteTemplateRequest
from src.api.models.response import QueryTemplateResponse, QueryResponse, PaginatedResponse
from src.application.services.query_template_service import QueryTemplateService
from src.application.services.query_service import QueryService


router = APIRouter(prefix="/api/templates", tags=["templates"])


def get_template_service() -> QueryTemplateService:
    """Dependency injection for template service."""
    from src.api.main import app
    return app.state.template_service


@router.post("", response_model=QueryTemplateResponse)
async def create_template(
    request: QueryTemplateRequest,
    service: QueryTemplateService = Depends(get_template_service)
):
    """Create a new query template."""
    try:
        template = await service.create_template(
            name=request.name,
            user_query=request.user_query,
            database_ids=request.database_ids,
            description=request.description,
            parameters=request.parameters,
            tags=request.tags,
            is_public=request.is_public
        )
        return QueryTemplateResponse(**template.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=PaginatedResponse)
async def list_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tags: Optional[str] = Query(None),
    service: QueryTemplateService = Depends(get_template_service)
):
    """List query templates."""
    try:
        tag_list = tags.split(",") if tags else None
        offset = (page - 1) * page_size
        
        templates = await service.list_templates(
            tags=tag_list,
            limit=page_size,
            offset=offset
        )
        
        # Calculate total (simplified - would need count method)
        total = len(templates)  # This is approximate
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        return PaginatedResponse(
            items=[QueryTemplateResponse(**t.__dict__) for t in templates],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{template_id}", response_model=QueryTemplateResponse)
async def get_template(
    template_id: str,
    service: QueryTemplateService = Depends(get_template_service)
):
    """Get a query template by ID."""
    try:
        template = await service.template_repository.get_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return QueryTemplateResponse(**template.__dict__)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{template_id}/execute", response_model=QueryResponse)
async def execute_template(
    template_id: str,
    request: Optional[ExecuteTemplateRequest] = None,
    service: QueryTemplateService = Depends(get_template_service)
):
    """Execute a query template."""
    try:
        parameters = request.parameters if request else None
        result = await service.execute_template(template_id, parameters)
        
        query_id = list(result.results.values())[0].query_id if result.results else ""
        
        return QueryResponse(
            query_id=query_id,
            data=result.merged_data,
            total_rows=result.total_rows,
            execution_time=result.execution_time,
            databases_queried=result.databases_queried,
            cached=False
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=List[QueryTemplateResponse])
async def search_templates(
    q: str = Query(..., description="Search query"),
    service: QueryTemplateService = Depends(get_template_service)
):
    """Search query templates."""
    try:
        templates = await service.search_templates(q)
        return [QueryTemplateResponse(**t.__dict__) for t in templates]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    service: QueryTemplateService = Depends(get_template_service)
):
    """Delete a query template."""
    try:
        success = await service.delete_template(template_id)
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"message": "Template deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


