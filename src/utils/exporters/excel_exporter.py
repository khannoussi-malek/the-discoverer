"""Excel exporter."""
from typing import List, Dict, Any, Optional
from io import BytesIO
import pandas as pd

from src.utils.exporters.base import Exporter


class ExcelExporter(Exporter):
    """Excel exporter."""
    
    async def export(
        self,
        data: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> BytesIO:
        """Export data to Excel."""
        if not data:
            # Create empty DataFrame
            df = pd.DataFrame()
        else:
            df = pd.DataFrame(data)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        
        output.seek(0)
        return output
    
    def get_content_type(self) -> str:
        """Get MIME content type."""
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    def get_file_extension(self) -> str:
        """Get file extension."""
        return "xlsx"


