"""Export template repository."""
from typing import List, Optional, Dict
from datetime import datetime

from src.domain.export_template import ExportTemplate


class ExportTemplateRepository:
    """In-memory export template repository."""
    
    def __init__(self):
        self._templates: Dict[str, ExportTemplate] = {}
    
    async def create(self, template: ExportTemplate) -> ExportTemplate:
        """Create export template."""
        self._templates[template.id] = template
        return template
    
    async def get_by_id(self, template_id: str) -> Optional[ExportTemplate]:
        """Get template by ID."""
        return self._templates.get(template_id)
    
    async def get_all(
        self,
        created_by: Optional[str] = None,
        is_public: Optional[bool] = None,
        tags: Optional[List[str]] = None
    ) -> List[ExportTemplate]:
        """Get all templates with optional filters."""
        templates = list(self._templates.values())
        
        if created_by:
            templates = [t for t in templates if t.created_by == created_by]
        
        if is_public is not None:
            templates = [t for t in templates if t.is_public == is_public]
        
        if tags:
            templates = [
                t for t in templates
                if any(tag in t.tags for tag in tags)
            ]
        
        return templates
    
    async def search(self, query: str) -> List[ExportTemplate]:
        """Search templates by name, description, or tags."""
        query_lower = query.lower()
        results = []
        
        for template in self._templates.values():
            if (
                query_lower in template.name.lower() or
                (template.description and query_lower in template.description.lower()) or
                any(query_lower in tag.lower() for tag in template.tags)
            ):
                results.append(template)
        
        return results
    
    async def update(self, template_id: str, updates: Dict[str, Any]) -> Optional[ExportTemplate]:
        """Update template."""
        template = self._templates.get(template_id)
        if not template:
            return None
        
        # Create updated template
        updated_dict = {
            "id": template.id,
            "name": updates.get("name", template.name),
            "format": updates.get("format", template.format),
            "description": updates.get("description", template.description),
            "filename_pattern": updates.get("filename_pattern", template.filename_pattern),
            "column_selection": updates.get("column_selection", template.column_selection),
            "column_mapping": updates.get("column_mapping", template.column_mapping),
            "formatting": updates.get("formatting", template.formatting),
            "compression": updates.get("compression", template.compression),
            "filters": updates.get("filters", template.filters),
            "sorting": updates.get("sorting", template.sorting),
            "created_at": template.created_at,
            "updated_at": datetime.utcnow(),
            "created_by": template.created_by,
            "tags": updates.get("tags", template.tags),
            "is_public": updates.get("is_public", template.is_public),
            "usage_count": template.usage_count
        }
        
        updated_template = ExportTemplate(**updated_dict)
        self._templates[template_id] = updated_template
        return updated_template
    
    async def delete(self, template_id: str) -> bool:
        """Delete template."""
        if template_id in self._templates:
            del self._templates[template_id]
            return True
        return False
    
    async def increment_usage(self, template_id: str) -> None:
        """Increment usage count."""
        template = self._templates.get(template_id)
        if template:
            template.usage_count += 1



