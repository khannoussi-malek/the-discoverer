"""Export template service."""
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import re

from src.domain.export_template import ExportTemplate
from src.infrastructure.export_template.repository import ExportTemplateRepository
from src.utils.exporters.factory import ExporterFactory


class ExportTemplateService:
    """Service for managing export templates."""
    
    def __init__(self, repository: ExportTemplateRepository):
        self.repository = repository
    
    async def create_template(
        self,
        name: str,
        format: str,
        description: Optional[str] = None,
        filename_pattern: Optional[str] = None,
        column_selection: Optional[List[str]] = None,
        column_mapping: Optional[Dict[str, str]] = None,
        formatting: Optional[Dict[str, Any]] = None,
        compression: Optional[Dict[str, Any]] = None,
        filters: Optional[Dict[str, Any]] = None,
        sorting: Optional[List[Dict[str, str]]] = None,
        created_by: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_public: bool = False
    ) -> ExportTemplate:
        """Create export template."""
        # Validate format
        if format.lower() not in ExporterFactory.get_supported_formats():
            raise ValueError(f"Unsupported export format: {format}")
        
        template = ExportTemplate(
            id=str(uuid.uuid4()),
            name=name,
            format=format.lower(),
            description=description,
            filename_pattern=filename_pattern,
            column_selection=column_selection,
            column_mapping=column_mapping,
            formatting=formatting,
            compression=compression,
            filters=filters,
            sorting=sorting,
            created_by=created_by,
            tags=tags or [],
            is_public=is_public
        )
        
        return await self.repository.create(template)
    
    async def get_template(self, template_id: str) -> Optional[ExportTemplate]:
        """Get template by ID."""
        return await self.repository.get_by_id(template_id)
    
    async def list_templates(
        self,
        created_by: Optional[str] = None,
        is_public: Optional[bool] = None,
        tags: Optional[List[str]] = None
    ) -> List[ExportTemplate]:
        """List templates."""
        return await self.repository.get_all(created_by, is_public, tags)
    
    async def search_templates(self, query: str) -> List[ExportTemplate]:
        """Search templates."""
        return await self.repository.search(query)
    
    async def update_template(
        self,
        template_id: str,
        updates: Dict[str, Any]
    ) -> Optional[ExportTemplate]:
        """Update template."""
        # Validate format if provided
        if "format" in updates:
            format_value = updates["format"]
            if format_value.lower() not in ExporterFactory.get_supported_formats():
                raise ValueError(f"Unsupported export format: {format_value}")
            updates["format"] = format_value.lower()
        
        return await self.repository.update(template_id, updates)
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete template."""
        return await self.repository.delete(template_id)
    
    def apply_template(
        self,
        template: ExportTemplate,
        data: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> tuple[List[Dict[str, Any]], str]:
        """
        Apply template to data.
        
        Args:
            template: Export template
            data: Data to export
            context: Optional context for filename pattern (e.g., query_id, date)
        
        Returns:
            Tuple of (processed_data, filename)
        """
        processed_data = data.copy()
        
        # Apply filters
        if template.filters:
            processed_data = self._apply_filters(processed_data, template.filters)
        
        # Apply column selection
        if template.column_selection:
            processed_data = [
                {k: row.get(k) for k in template.column_selection if k in row}
                for row in processed_data
            ]
        
        # Apply column mapping (rename)
        if template.column_mapping:
            processed_data = [
                {
                    template.column_mapping.get(k, k): v
                    for k, v in row.items()
                }
                for row in processed_data
            ]
        
        # Apply sorting
        if template.sorting:
            processed_data = self._apply_sorting(processed_data, template.sorting)
        
        # Apply formatting
        if template.formatting:
            processed_data = self._apply_formatting(processed_data, template.formatting)
        
        # Generate filename
        filename = self._generate_filename(template, context)
        
        return processed_data, filename
    
    def _apply_filters(
        self,
        data: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply filters to data."""
        filtered = data
        
        for field, condition in filters.items():
            if isinstance(condition, dict):
                # Complex filter
                if "eq" in condition:
                    filtered = [r for r in filtered if r.get(field) == condition["eq"]]
                elif "ne" in condition:
                    filtered = [r for r in filtered if r.get(field) != condition["ne"]]
                elif "gt" in condition:
                    filtered = [r for r in filtered if r.get(field, 0) > condition["gt"]]
                elif "lt" in condition:
                    filtered = [r for r in filtered if r.get(field, 0) < condition["lt"]]
                elif "in" in condition:
                    filtered = [r for r in filtered if r.get(field) in condition["in"]]
                elif "contains" in condition:
                    filtered = [
                        r for r in filtered
                        if condition["contains"].lower() in str(r.get(field, "")).lower()
                    ]
            else:
                # Simple equality filter
                filtered = [r for r in filtered if r.get(field) == condition]
        
        return filtered
    
    def _apply_sorting(
        self,
        data: List[Dict[str, Any]],
        sorting: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """Apply sorting to data."""
        def sort_key(row):
            key_parts = []
            for sort_config in sorting:
                field = sort_config.get("field")
                order = sort_config.get("order", "asc").lower()
                value = row.get(field)
                
                # Handle None values
                if value is None:
                    key_parts.append((0 if order == "asc" else 1, None))
                else:
                    key_parts.append((0 if order == "asc" else 1, value))
            
            return key_parts
        
        return sorted(data, key=sort_key)
    
    def _apply_formatting(
        self,
        data: List[Dict[str, Any]],
        formatting: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply formatting to data."""
        formatted = []
        
        for row in data:
            formatted_row = row.copy()
            
            for field, format_config in formatting.items():
                if field in formatted_row:
                    value = formatted_row[field]
                    
                    if isinstance(format_config, dict):
                        format_type = format_config.get("type")
                        
                        if format_type == "date":
                            # Date formatting would go here
                            pass
                        elif format_type == "number":
                            decimals = format_config.get("decimals", 2)
                            if isinstance(value, (int, float)):
                                formatted_row[field] = round(value, decimals)
                        elif format_type == "currency":
                            symbol = format_config.get("symbol", "$")
                            decimals = format_config.get("decimals", 2)
                            if isinstance(value, (int, float)):
                                formatted_row[field] = f"{symbol}{value:.{decimals}f}"
                        elif format_type == "percentage":
                            if isinstance(value, (int, float)):
                                formatted_row[field] = f"{value * 100:.2f}%"
            
            formatted.append(formatted_row)
        
        return formatted
    
    def _generate_filename(
        self,
        template: ExportTemplate,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate filename from pattern."""
        if not template.filename_pattern:
            # Default filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            return f"export_{timestamp}.{template.format}"
        
        # Replace placeholders
        filename = template.filename_pattern
        context = context or {}
        
        # Standard placeholders
        filename = filename.replace("{date}", datetime.utcnow().strftime("%Y%m%d"))
        filename = filename.replace("{datetime}", datetime.utcnow().strftime("%Y%m%d_%H%M%S"))
        filename = filename.replace("{timestamp}", str(int(datetime.utcnow().timestamp())))
        filename = filename.replace("{format}", template.format)
        
        # Context placeholders
        for key, value in context.items():
            filename = filename.replace(f"{{{key}}}", str(value))
        
        # Ensure extension matches format
        if not filename.endswith(f".{template.format}"):
            filename = f"{filename}.{template.format}"
        
        return filename



