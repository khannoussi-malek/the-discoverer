"""Base exporter interface."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from io import BytesIO


class Exporter(ABC):
    """Base exporter interface."""
    
    @abstractmethod
    async def export(
        self,
        data: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> BytesIO:
        """Export data to a file-like object."""
        pass
    
    @abstractmethod
    def get_content_type(self) -> str:
        """Get MIME content type."""
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Get file extension."""
        pass

