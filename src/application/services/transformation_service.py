"""Query result transformation service."""
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import re


@dataclass
class TransformationRule:
    """Transformation rule."""
    field: str
    operation: str  # rename, format, filter, aggregate, etc.
    parameters: Dict[str, Any]


class TransformationService:
    """Service for transforming query results."""
    
    @staticmethod
    def transform(
        data: List[Dict[str, Any]],
        rules: List[TransformationRule]
    ) -> List[Dict[str, Any]]:
        """Apply transformation rules to data."""
        result = data.copy()
        
        for rule in rules:
            result = TransformationService._apply_rule(result, rule)
        
        return result
    
    @staticmethod
    def _apply_rule(
        data: List[Dict[str, Any]],
        rule: TransformationRule
    ) -> List[Dict[str, Any]]:
        """Apply a single transformation rule."""
        operation = rule.operation.lower()
        
        if operation == "rename":
            return TransformationService._rename_field(data, rule.field, rule.parameters)
        elif operation == "format":
            return TransformationService._format_field(data, rule.field, rule.parameters)
        elif operation == "filter":
            return TransformationService._filter_rows(data, rule.parameters)
        elif operation == "sort":
            return TransformationService._sort_rows(data, rule.parameters)
        elif operation == "select":
            return TransformationService._select_fields(data, rule.parameters)
        elif operation == "aggregate":
            return TransformationService._aggregate(data, rule.parameters)
        else:
            return data
    
    @staticmethod
    def _rename_field(
        data: List[Dict[str, Any]],
        old_name: str,
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Rename a field."""
        new_name = params.get("new_name", old_name)
        result = []
        
        for row in data:
            new_row = row.copy()
            if old_name in new_row:
                new_row[new_name] = new_row.pop(old_name)
            result.append(new_row)
        
        return result
    
    @staticmethod
    def _format_field(
        data: List[Dict[str, Any]],
        field: str,
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Format a field value."""
        format_type = params.get("format", "string")
        result = []
        
        for row in data:
            new_row = row.copy()
            if field in new_row:
                value = new_row[field]
                
                if format_type == "currency":
                    new_row[field] = f"${value:,.2f}" if isinstance(value, (int, float)) else value
                elif format_type == "percentage":
                    new_row[field] = f"{value:.2f}%" if isinstance(value, (int, float)) else value
                elif format_type == "date":
                    # Simple date formatting
                    if hasattr(value, 'strftime'):
                        new_row[field] = value.strftime(params.get("date_format", "%Y-%m-%d"))
                elif format_type == "number":
                    new_row[field] = f"{value:,.2f}" if isinstance(value, (int, float)) else value
                elif format_type == "uppercase":
                    new_row[field] = str(value).upper()
                elif format_type == "lowercase":
                    new_row[field] = str(value).lower()
            
            result.append(new_row)
        
        return result
    
    @staticmethod
    def _filter_rows(
        data: List[Dict[str, Any]],
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter rows based on conditions."""
        field = params.get("field")
        operator = params.get("operator", "equals")
        value = params.get("value")
        
        if not field:
            return data
        
        result = []
        for row in data:
            if field not in row:
                continue
            
            row_value = row[field]
            include = False
            
            if operator == "equals":
                include = row_value == value
            elif operator == "not_equals":
                include = row_value != value
            elif operator == "greater_than":
                include = row_value > value
            elif operator == "less_than":
                include = row_value < value
            elif operator == "contains":
                include = str(value) in str(row_value)
            elif operator == "starts_with":
                include = str(row_value).startswith(str(value))
            elif operator == "ends_with":
                include = str(row_value).endswith(str(value))
            elif operator == "in":
                include = row_value in (value if isinstance(value, list) else [value])
            
            if include:
                result.append(row)
        
        return result
    
    @staticmethod
    def _sort_rows(
        data: List[Dict[str, Any]],
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Sort rows."""
        field = params.get("field")
        order = params.get("order", "asc")  # asc or desc
        
        if not field:
            return data
        
        reverse = order.lower() == "desc"
        
        # Sort by field, handling None values
        def sort_key(row):
            value = row.get(field)
            if value is None:
                return (1, None) if reverse else (0, None)
            return (0, value)
        
        return sorted(data, key=sort_key, reverse=reverse)
    
    @staticmethod
    def _select_fields(
        data: List[Dict[str, Any]],
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Select specific fields."""
        fields = params.get("fields", [])
        
        if not fields:
            return data
        
        result = []
        for row in data:
            new_row = {field: row.get(field) for field in fields if field in row}
            result.append(new_row)
        
        return result
    
    @staticmethod
    def _aggregate(
        data: List[Dict[str, Any]],
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Aggregate data."""
        group_by = params.get("group_by", [])
        aggregations = params.get("aggregations", {})  # {field: operation}
        
        if not group_by and not aggregations:
            return data
        
        # Simple aggregation - group and aggregate
        groups = {}
        
        for row in data:
            # Create group key
            if group_by:
                key = tuple(row.get(field) for field in group_by)
            else:
                key = "all"
            
            if key not in groups:
                groups[key] = {
                    "count": 0,
                    "values": []
                }
                if group_by:
                    for field in group_by:
                        groups[key][field] = row.get(field)
            
            groups[key]["count"] += 1
            groups[key]["values"].append(row)
        
        # Apply aggregations
        result = []
        for key, group_data in groups.items():
            row = {}
            
            # Add group fields
            if group_by:
                for field in group_by:
                    row[field] = group_data.get(field)
            
            # Add aggregations
            for field, operation in aggregations.items():
                values = [r.get(field) for r in group_data["values"] if field in r and r[field] is not None]
                
                if not values:
                    row[f"{field}_{operation}"] = None
                    continue
                
                if operation == "sum":
                    row[f"{field}_{operation}"] = sum(values)
                elif operation == "avg" or operation == "average":
                    row[f"{field}_{operation}"] = sum(values) / len(values)
                elif operation == "min":
                    row[f"{field}_{operation}"] = min(values)
                elif operation == "max":
                    row[f"{field}_{operation}"] = max(values)
                elif operation == "count":
                    row[f"{field}_{operation}"] = len(values)
            
            result.append(row)
        
        return result


