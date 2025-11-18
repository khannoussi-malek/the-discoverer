"""Query result transformation API routes."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from src.application.services.transformation_service import TransformationService, TransformationRule
from src.infrastructure.query_history.repository import QueryHistoryRepository


router = APIRouter(prefix="/api/transformation", tags=["transformation"])


class TransformationRuleModel(BaseModel):
    """Transformation rule model."""
    field: str
    operation: str
    parameters: Dict[str, Any]


class TransformRequest(BaseModel):
    """Transform request."""
    query_id: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None
    rules: List[TransformationRuleModel]


def get_history_repository() -> QueryHistoryRepository:
    """Dependency injection for history repository."""
    from src.api.main import app
    return app.state.query_history_repository


@router.post("/transform")
async def transform_data(
    request: TransformRequest,
    repository: QueryHistoryRepository = Depends(get_history_repository)
):
    """Transform query result data."""
    try:
        # Get data from query history or use provided data
        if request.query_id:
            query_history = await repository.get_by_id(request.query_id)
            if not query_history:
                raise HTTPException(status_code=404, detail="Query not found")
            data = query_history.result.get("merged_data", [])
        elif request.data:
            data = request.data
        else:
            raise HTTPException(status_code=400, detail="Either query_id or data must be provided")
        
        # Convert rules
        rules = [
            TransformationRule(
                field=rule.field,
                operation=rule.operation,
                parameters=rule.parameters
            )
            for rule in request.rules
        ]
        
        # Apply transformations
        transformed = TransformationService.transform(data, rules)
        
        return {
            "original_count": len(data),
            "transformed_count": len(transformed),
            "data": transformed
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preview")
async def preview_transformation(
    request: TransformRequest
):
    """Preview transformation on sample data."""
    try:
        if not request.data:
            raise HTTPException(status_code=400, detail="Data must be provided for preview")
        
        # Use first 10 rows for preview
        sample_data = request.data[:10]
        
        # Convert rules
        rules = [
            TransformationRule(
                field=rule.field,
                operation=rule.operation,
                parameters=rule.parameters
            )
            for rule in request.rules
        ]
        
        # Apply transformations
        transformed = TransformationService.transform(sample_data, rules)
        
        return {
            "sample_count": len(sample_data),
            "transformed_count": len(transformed),
            "original_sample": sample_data,
            "transformed_sample": transformed
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

