"""Query template service."""
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from src.domain.query_template import QueryTemplate
from src.infrastructure.query_templates.repository import QueryTemplateRepository
from src.application.services.query_service import QueryService
from src.domain.result import AggregatedResult


class QueryTemplateService:
    """Service for managing query templates."""
    
    def __init__(
        self,
        template_repository: QueryTemplateRepository,
        query_service: QueryService
    ):
        self.template_repository = template_repository
        self.query_service = query_service
    
    async def create_template(
        self,
        name: str,
        user_query: str,
        database_ids: Optional[List[str]] = None,
        description: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        is_public: bool = False,
        created_by: Optional[str] = None
    ) -> QueryTemplate:
        """Create a new query template."""
        template = QueryTemplate(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            user_query=user_query,
            database_ids=database_ids,
            parameters=parameters,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=created_by,
            tags=tags or [],
            is_public=is_public
        )
        
        return await self.template_repository.save(template)
    
    async def execute_template(
        self,
        template_id: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> AggregatedResult:
        """Execute a saved query template."""
        template = await self.template_repository.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Substitute parameters in query
        query = template.user_query
        if parameters:
            for key, value in parameters.items():
                query = query.replace(f"{{{{{key}}}}}", str(value))
        
        # Execute query
        return await self.query_service.execute_query(
            user_query=query,
            database_ids=template.database_ids
        )
    
    async def list_templates(
        self,
        user_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[QueryTemplate]:
        """List query templates."""
        return await self.template_repository.list(
            user_id=user_id,
            tags=tags,
            limit=limit,
            offset=offset
        )
    
    async def search_templates(self, query: str) -> List[QueryTemplate]:
        """Search templates."""
        return await self.template_repository.search(query)
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        return await self.template_repository.delete(template_id)
    
    async def update_template(
        self,
        template_id: str,
        updates: Dict[str, Any]
    ) -> Optional[QueryTemplate]:
        """Update a template."""
        return await self.template_repository.update(template_id, updates)


