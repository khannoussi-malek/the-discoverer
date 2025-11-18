"""Query template repository."""
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from src.domain.query_template import QueryTemplate


class QueryTemplateRepository:
    """Repository for query templates - in-memory implementation."""
    
    def __init__(self):
        self._templates: Dict[str, QueryTemplate] = {}
    
    async def save(self, template: QueryTemplate) -> QueryTemplate:
        """Save a query template."""
        if not template.id:
            template.id = str(uuid.uuid4())
        
        template.updated_at = datetime.utcnow()
        self._templates[template.id] = template
        return template
    
    async def get_by_id(self, template_id: str) -> Optional[QueryTemplate]:
        """Get template by ID."""
        return self._templates.get(template_id)
    
    async def list(
        self,
        user_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[QueryTemplate]:
        """List templates with filters."""
        templates = list(self._templates.values())
        
        # Filter by user
        if user_id:
            templates = [t for t in templates if t.created_by == user_id or t.is_public]
        
        # Filter by tags
        if tags:
            templates = [
                t for t in templates
                if t.tags and any(tag in t.tags for tag in tags)
            ]
        
        # Sort by updated_at descending
        templates.sort(key=lambda t: t.updated_at, reverse=True)
        
        # Paginate
        return templates[offset:offset + limit]
    
    async def search(self, query: str) -> List[QueryTemplate]:
        """Search templates by name or description."""
        query_lower = query.lower()
        results = []
        
        for template in self._templates.values():
            if (
                query_lower in template.name.lower() or
                (template.description and query_lower in template.description.lower()) or
                query_lower in template.user_query.lower()
            ):
                results.append(template)
        
        return results
    
    async def delete(self, template_id: str) -> bool:
        """Delete a template."""
        if template_id in self._templates:
            del self._templates[template_id]
            return True
        return False
    
    async def update(self, template_id: str, updates: Dict[str, Any]) -> Optional[QueryTemplate]:
        """Update a template."""
        template = self._templates.get(template_id)
        if not template:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(template, key):
                setattr(template, key, value)
        
        template.updated_at = datetime.utcnow()
        return template


