"""Exporter factory."""
from typing import Dict, Type, List
from src.utils.exporters.base import Exporter
from src.utils.exporters.csv_exporter import CSVExporter
from src.utils.exporters.json_exporter import JSONExporter
from src.utils.exporters.excel_exporter import ExcelExporter
from src.utils.exporters.parquet_exporter import ParquetExporter
from src.utils.exporters.avro_exporter import AvroExporter


class ExporterFactory:
    """Factory for exporters."""
    
    _exporters: Dict[str, Type[Exporter]] = {
        "csv": CSVExporter,
        "json": JSONExporter,
        "excel": ExcelExporter,
        "xlsx": ExcelExporter,
        "parquet": ParquetExporter,
        "avro": AvroExporter,
    }
    
    @classmethod
    def create(cls, format: str) -> Exporter:
        """Create exporter by format."""
        exporter_class = cls._exporters.get(format.lower())
        if not exporter_class:
            raise ValueError(f"Unsupported export format: {format}")
        return exporter_class()
    
    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """Get supported export formats."""
        return list(cls._exporters.keys())
