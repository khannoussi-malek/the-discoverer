"""Parquet export implementation."""
from typing import List, Dict, Any, Optional
from io import BytesIO
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from src.utils.exporters.base import Exporter


class ParquetExporter(Exporter):
    """Parquet exporter implementation."""
    
    async def export(
        self,
        data: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> BytesIO:
        """Export data to Parquet format."""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Convert to PyArrow table
            table = pa.Table.from_pandas(df)
            
            # Write to Parquet
            buffer = BytesIO()
            pq.write_table(table, buffer, compression='snappy')
            buffer.seek(0)
            
            return buffer
        except Exception as e:
            raise ValueError(f"Failed to export to Parquet: {str(e)}")
    
    def get_content_type(self) -> str:
        """Get content type for Parquet."""
        return "application/octet-stream"
    
    def get_file_extension(self) -> str:
        """Get file extension."""
        return "parquet"
