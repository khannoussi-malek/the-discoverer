"""JSON exporter."""
from typing import List, Dict, Any, Optional
from io import BytesIO
import json

from src.utils.exporters.base import Exporter


class JSONExporter(Exporter):
    """JSON exporter."""
    
    async def export(
        self,
        data: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> BytesIO:
        """Export data to JSON."""
        json_str = json.dumps(data, indent=2, default=str)
        return BytesIO(json_str.encode('utf-8'))
    
    def get_content_type(self) -> str:
        """Get MIME content type."""
        return "application/json"
    
    def get_file_extension(self) -> str:
        """Get file extension."""
        return "json"


