"""Chart template service for reusable chart configurations."""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class ChartTemplate:
    """Chart template entity."""
    id: str
    name: str
    chart_type: str
    config: Dict[str, Any]
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    is_public: bool = False
    usage_count: int = 0


class ChartTemplateService:
    """Service for managing chart templates."""
    
    def __init__(self):
        self._templates: Dict[str, ChartTemplate] = {}
    
    async def create_template(
        self,
        name: str,
        chart_type: str,
        config: Dict[str, Any],
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_by: Optional[str] = None,
        is_public: bool = False
    ) -> ChartTemplate:
        """Create a new chart template."""
        template = ChartTemplate(
            id=str(uuid.uuid4()),
            name=name,
            chart_type=chart_type,
            config=config,
            description=description,
            tags=tags or [],
            created_by=created_by,
            is_public=is_public
        )
        
        self._templates[template.id] = template
        return template
    
    async def get_template(self, template_id: str) -> Optional[ChartTemplate]:
        """Get a chart template by ID."""
        return self._templates.get(template_id)
    
    async def list_templates(
        self,
        chart_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        public_only: bool = False,
        created_by: Optional[str] = None
    ) -> List[ChartTemplate]:
        """List chart templates with optional filters."""
        templates = list(self._templates.values())
        
        if chart_type:
            templates = [t for t in templates if t.chart_type == chart_type]
        
        if tags:
            templates = [
                t for t in templates
                if any(tag in t.tags for tag in tags)
            ]
        
        if public_only:
            templates = [t for t in templates if t.is_public]
        
        if created_by:
            templates = [t for t in templates if t.created_by == created_by]
        
        return templates
    
    async def update_template(
        self,
        template_id: str,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_public: Optional[bool] = None
    ) -> Optional[ChartTemplate]:
        """Update a chart template."""
        template = self._templates.get(template_id)
        if not template:
            return None
        
        if name is not None:
            template.name = name
        if config is not None:
            template.config.update(config)
        if description is not None:
            template.description = description
        if tags is not None:
            template.tags = tags
        if is_public is not None:
            template.is_public = is_public
        
        return template
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete a chart template."""
        if template_id in self._templates:
            del self._templates[template_id]
            return True
        return False
    
    async def apply_template(
        self,
        template_id: str,
        query_id: str,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Apply a chart template to a query result."""
        template = await self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Increment usage count
        template.usage_count += 1
        
        # Merge template config with overrides
        config = template.config.copy()
        if overrides:
            config.update(overrides)
        
        return {
            "template_id": template_id,
            "query_id": query_id,
            "chart_type": template.chart_type,
            "config": config
        }
    
    async def search_templates(
        self,
        query: str,
        limit: int = 10
    ) -> List[ChartTemplate]:
        """Search templates by name or description."""
        query_lower = query.lower()
        results = []
        
        for template in self._templates.values():
            if (
                query_lower in template.name.lower() or
                (template.description and query_lower in template.description.lower()) or
                any(query_lower in tag.lower() for tag in template.tags)
            ):
                results.append(template)
                if len(results) >= limit:
                    break
        
        return results


