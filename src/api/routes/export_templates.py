"""Export template API routes."""
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Optional, Dict, Any
from fastapi.responses import StreamingResponse

from src.application.services.export_template_service import ExportTemplateService
from src.api.models.request import ExportTemplateCreateRequest, ExportTemplateUpdateRequest
from src.utils.exporters.factory import ExporterFactory


router = APIRouter(prefix="/api/export-templates", tags=["export-templates"])


def get_export_template_service() -> ExportTemplateService:
    """Dependency injection for export template service."""
    from src.api.main import app
    if not hasattr(app.state, 'export_template_service'):
        from src.infrastructure.export_template.repository import ExportTemplateRepository
        from src.application.services.export_template_service import ExportTemplateService
        repository = ExportTemplateRepository()
        app.state.export_template_service = ExportTemplateService(repository)
    return app.state.export_template_service


@router.post("")
async def create_template(
    request: ExportTemplateCreateRequest,
    service: ExportTemplateService = Depends(get_export_template_service)
):
    """Create export template."""
    try:
        template = await service.create_template(
            name=request.name,
            format=request.format,
            description=request.description,
            filename_pattern=request.filename_pattern,
            column_selection=request.column_selection,
            column_mapping=request.column_mapping,
            formatting=request.formatting,
            compression=request.compression,
            filters=request.filters,
            sorting=request.sorting,
            tags=request.tags,
            is_public=request.is_public
        )
        
        return {
            "id": template.id,
            "name": template.name,
            "format": template.format,
            "description": template.description,
            "created_at": template.created_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_templates(
    created_by: Optional[str] = Query(None),
    is_public: Optional[bool] = Query(None),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    service: ExportTemplateService = Depends(get_export_template_service)
):
    """List export templates."""
    try:
        tag_list = tags.split(",") if tags else None
        templates = await service.list_templates(
            created_by=created_by,
            is_public=is_public,
            tags=tag_list
        )
        
        return {
            "templates": [
                {
                    "id": t.id,
                    "name": t.name,
                    "format": t.format,
                    "description": t.description,
                    "tags": t.tags,
                    "is_public": t.is_public,
                    "usage_count": t.usage_count,
                    "created_at": t.created_at.isoformat()
                }
                for t in templates
            ],
            "total": len(templates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{template_id}")
async def get_template(
    template_id: str,
    service: ExportTemplateService = Depends(get_export_template_service)
):
    """Get export template."""
    try:
        template = await service.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "id": template.id,
            "name": template.name,
            "format": template.format,
            "description": template.description,
            "filename_pattern": template.filename_pattern,
            "column_selection": template.column_selection,
            "column_mapping": template.column_mapping,
            "formatting": template.formatting,
            "compression": template.compression,
            "filters": template.filters,
            "sorting": template.sorting,
            "tags": template.tags,
            "is_public": template.is_public,
            "usage_count": template.usage_count,
            "created_at": template.created_at.isoformat(),
            "updated_at": template.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{template_id}")
async def update_template(
    template_id: str,
    request: ExportTemplateUpdateRequest,
    service: ExportTemplateService = Depends(get_export_template_service)
):
    """Update export template."""
    try:
        updates = request.dict(exclude_unset=True)
        template = await service.update_template(template_id, updates)
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "id": template.id,
            "name": template.name,
            "format": template.format,
            "updated_at": template.updated_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    service: ExportTemplateService = Depends(get_export_template_service)
):
    """Delete export template."""
    try:
        success = await service.delete_template(template_id)
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {"message": "Template deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_templates(
    q: str = Query(..., description="Search query"),
    service: ExportTemplateService = Depends(get_export_template_service)
):
    """Search export templates."""
    try:
        templates = await service.search_templates(q)
        
        return {
            "templates": [
                {
                    "id": t.id,
                    "name": t.name,
                    "format": t.format,
                    "description": t.description,
                    "tags": t.tags,
                    "usage_count": t.usage_count
                }
                for t in templates
            ],
            "total": len(templates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{template_id}/apply")
async def apply_template(
    template_id: str,
    data: List[Dict[str, Any]] = Body(...),
    context: Optional[Dict[str, Any]] = Body(None),
    service: ExportTemplateService = Depends(get_export_template_service)
):
    """Apply export template to data and return export."""
    try:
        template = await service.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Apply template
        processed_data, filename = service.apply_template(template, data, context)
        
        # Create exporter
        exporter = ExporterFactory.create(template.format)
        
        # Export
        file_data = await exporter.export(processed_data)
        
        # Increment usage
        await service.repository.increment_usage(template_id)
        
        return StreamingResponse(
            file_data,
            media_type=exporter.get_content_type(),
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



