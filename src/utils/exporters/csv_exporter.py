"""CSV exporter."""
from typing import List, Dict, Any, Optional
from io import BytesIO
import csv

from src.utils.exporters.base import Exporter


class CSVExporter(Exporter):
    """CSV exporter."""
    
    async def export(
        self,
        data: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> BytesIO:
        """Export data to CSV."""
        if not data:
            return BytesIO(b"")
        
        # Get all unique keys
        fieldnames = set()
        for row in data:
            fieldnames.update(row.keys())
        fieldnames = sorted(fieldnames)
        
        # Create CSV
        output = BytesIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in data:
            # Convert all values to strings
            csv_row = {k: str(v) if v is not None else "" for k, v in row.items()}
            writer.writerow(csv_row)
        
        output.seek(0)
        return output
    
    def get_content_type(self) -> str:
        """Get MIME content type."""
        return "text/csv"
    
    def get_file_extension(self) -> str:
        """Get file extension."""
        return "csv"


