"""Chart export utilities for PNG and PDF."""
from typing import Dict, Any, Optional
from io import BytesIO
import base64

try:
    import plotly.graph_objects as go
    from plotly.io import to_image, write_image
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class ChartExporter:
    """Export charts to various formats."""
    
    @staticmethod
    async def export_to_png(
        chart_data: Dict[str, Any],
        width: int = 1200,
        height: int = 800,
        scale: float = 2.0
    ) -> BytesIO:
        """Export chart to PNG."""
        if not PLOTLY_AVAILABLE:
            raise ValueError("Plotly is required for PNG export. Install kaleido: pip install kaleido")
        
        try:
            # Reconstruct figure from chart data
            fig = go.Figure(chart_data)
            
            # Export to PNG
            img_bytes = to_image(
                fig,
                format="png",
                width=width,
                height=height,
                scale=scale
            )
            
            return BytesIO(img_bytes)
        except Exception as e:
            raise ValueError(f"Failed to export chart to PNG: {str(e)}")
    
    @staticmethod
    async def export_to_pdf(
        chart_data: Dict[str, Any],
        width: int = 1200,
        height: int = 800
    ) -> BytesIO:
        """Export chart to PDF."""
        if not PLOTLY_AVAILABLE:
            raise ValueError("Plotly is required for PDF export. Install kaleido: pip install kaleido")
        
        try:
            # Reconstruct figure from chart data
            fig = go.Figure(chart_data)
            
            # Export to PDF
            pdf_bytes = to_image(
                fig,
                format="pdf",
                width=width,
                height=height
            )
            
            return BytesIO(pdf_bytes)
        except Exception as e:
            raise ValueError(f"Failed to export chart to PDF: {str(e)}")
    
    @staticmethod
    async def export_to_html(
        chart_data: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """Export chart to HTML."""
        if not PLOTLY_AVAILABLE:
            raise ValueError("Plotly is required for HTML export")
        
        try:
            fig = go.Figure(chart_data)
            html_str = fig.to_html(include_plotlyjs='cdn')
            return html_str
        except Exception as e:
            raise ValueError(f"Failed to export chart to HTML: {str(e)}")
    
    @staticmethod
    async def export_to_svg(
        chart_data: Dict[str, Any],
        width: int = 1200,
        height: int = 800
    ) -> str:
        """Export chart to SVG."""
        if not PLOTLY_AVAILABLE:
            raise ValueError("Plotly is required for SVG export. Install kaleido: pip install kaleido")
        
        try:
            fig = go.Figure(chart_data)
            svg_str = to_image(
                fig,
                format="svg",
                width=width,
                height=height
            )
            return svg_str.decode('utf-8') if isinstance(svg_str, bytes) else svg_str
        except Exception as e:
            raise ValueError(f"Failed to export chart to SVG: {str(e)}")


