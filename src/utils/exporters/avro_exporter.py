"""Avro export implementation."""
from typing import List, Dict, Any, Optional
from io import BytesIO
import json

try:
    import fastavro
    AVRO_AVAILABLE = True
except ImportError:
    AVRO_AVAILABLE = False

from src.utils.exporters.base import Exporter


class AvroExporter(Exporter):
    """Avro exporter implementation."""
    
    def __init__(self):
        if not AVRO_AVAILABLE:
            raise ImportError(
                "fastavro package not installed. Install with: pip install fastavro"
            )
    
    def _infer_schema(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Infer Avro schema from data.
        
        Args:
            data: List of dictionaries
        
        Returns:
            Avro schema dictionary
        """
        if not data:
            return {
                "type": "record",
                "name": "Record",
                "fields": []
            }
        
        # Get first record to infer types
        first_record = data[0]
        
        fields = []
        for key, value in first_record.items():
            field_type = self._infer_type(value)
            fields.append({
                "name": str(key),
                "type": field_type
            })
        
        return {
            "type": "record",
            "name": "Record",
            "fields": fields
        }
    
    def _infer_type(self, value: Any) -> Any:
        """
        Infer Avro type from Python value.
        
        Args:
            value: Python value
        
        Returns:
            Avro type
        """
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "long"  # Avro uses long for integers
        elif isinstance(value, float):
            return "double"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            if not value:
                return {"type": "array", "items": "string"}
            item_type = self._infer_type(value[0])
            return {"type": "array", "items": item_type}
        elif isinstance(value, dict):
            # Convert dict to record
            fields = [
                {
                    "name": str(k),
                    "type": self._infer_type(v)
                }
                for k, v in value.items()
            ]
            return {
                "type": "record",
                "name": "NestedRecord",
                "fields": fields
            }
        else:
            # Default to string for unknown types
            return "string"
    
    def _convert_value(self, value: Any, avro_type: Any) -> Any:
        """
        Convert Python value to Avro-compatible value.
        
        Args:
            value: Python value
            avro_type: Avro type
        
        Returns:
            Avro-compatible value
        """
        if value is None:
            return None
        
        if isinstance(avro_type, dict):
            if avro_type.get("type") == "array":
                if isinstance(value, list):
                    return [self._convert_value(v, avro_type["items"]) for v in value]
                else:
                    return [value]
            elif avro_type.get("type") == "record":
                if isinstance(value, dict):
                    result = {}
                    for field in avro_type.get("fields", []):
                        field_name = field["name"]
                        field_type = field["type"]
                        result[field_name] = self._convert_value(
                            value.get(field_name),
                            field_type
                        )
                    return result
                else:
                    return {}
        
        # Primitive types
        if avro_type == "long" and isinstance(value, float):
            return int(value)
        elif avro_type == "double" and isinstance(value, int):
            return float(value)
        elif avro_type == "string":
            return str(value)
        elif avro_type == "boolean":
            return bool(value)
        
        return value
    
    async def export(
        self,
        data: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> BytesIO:
        """Export data to Avro format."""
        if not AVRO_AVAILABLE:
            raise ImportError(
                "fastavro package not installed. Install with: pip install fastavro"
            )
        
        try:
            # Infer schema from data
            schema = self._infer_schema(data)
            
            # Parse schema
            parsed_schema = fastavro.parse_schema(schema)
            
            # Convert data to Avro-compatible format
            avro_records = []
            for record in data:
                avro_record = {}
                for field in schema["fields"]:
                    field_name = field["name"]
                    field_type = field["type"]
                    value = record.get(field_name)
                    avro_record[field_name] = self._convert_value(value, field_type)
                avro_records.append(avro_record)
            
            # Write to Avro file (with schema)
            buffer = BytesIO()
            fastavro.writer(buffer, parsed_schema, avro_records)
            buffer.seek(0)
            
            return buffer
        except Exception as e:
            raise ValueError(f"Failed to export to Avro: {str(e)}")
    
    def get_content_type(self) -> str:
        """Get content type for Avro."""
        return "application/avro"
    
    def get_file_extension(self) -> str:
        """Get file extension."""
        return "avro"

