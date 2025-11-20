# Chart Export Documentation

## Overview

Navo supports exporting charts to various formats for sharing, reporting, and integration with other tools.

## Supported Formats

- **PNG** - Raster image format (default)
- **PDF** - Portable Document Format
- **HTML** - Interactive HTML with embedded Plotly.js
- **SVG** - Scalable Vector Graphics

## API Endpoint

### Export Chart

```http
GET /api/visualization/export/{query_id}?format=png&width=1200&height=800&chart_type=bar
```

**Parameters:**
- `query_id` (path) - ID of the query result to export
- `format` (query) - Export format: `png`, `pdf`, `html`, `svg` (default: `png`)
- `chart_type` (query) - Chart type to generate (optional, defaults to `bar`)
- `width` (query) - Image width in pixels (default: 1200, range: 100-4000)
- `height` (query) - Image height in pixels (default: 800, range: 100-4000)

**Response:**
- Content-Type varies by format:
  - PNG: `image/png`
  - PDF: `application/pdf`
  - HTML: `text/html`
  - SVG: `image/svg+xml`
- File download with appropriate filename

## Examples

### Export to PNG

```bash
curl -X GET "http://localhost:8000/api/visualization/export/query-123?format=png&width=1920&height=1080" \
  --output chart.png
```

### Export to PDF

```bash
curl -X GET "http://localhost:8000/api/visualization/export/query-123?format=pdf" \
  --output chart.pdf
```

### Export to HTML (Interactive)

```bash
curl -X GET "http://localhost:8000/api/visualization/export/query-123?format=html" \
  --output chart.html
```

### Export to SVG

```bash
curl -X GET "http://localhost:8000/api/visualization/export/query-123?format=svg" \
  --output chart.svg
```

## Python SDK Usage

```python
from src.sdk.sync_client import DiscovererSyncClient, DiscovererConfig

with DiscovererSyncClient(DiscovererConfig()) as client:
    # Execute query
    result = client.execute_query("Show sales by month")
    
    # Export chart
    png_data = client.client.get(
        f"/api/visualization/export/{result['query_id']}",
        params={"format": "png", "width": 1920, "height": 1080}
    ).content
    
    with open("sales_chart.png", "wb") as f:
        f.write(png_data)
```

## Requirements

For PNG, PDF, and SVG export, the `kaleido` package is required:

```bash
pip install kaleido
```

This is already included in `requirements.txt`.

## Chart Types

All chart types are supported for export:
- Basic: bar, line, pie, scatter, table
- Advanced: heatmap, box, violin, scatter3d, surface, sunburst, treemap, funnel, gauge, waterfall

## Use Cases

1. **Reports**: Export charts to PDF for inclusion in reports
2. **Presentations**: Export to PNG for slides
3. **Web Integration**: Export to HTML for embedding in web pages
4. **Print**: Export to SVG for high-quality printing
5. **Sharing**: Download charts for sharing via email or other channels

## Notes

- PNG and PDF exports require the `kaleido` package
- HTML exports are interactive and include Plotly.js
- SVG exports are vector-based and scale without quality loss
- Large charts may take longer to export
- Recommended dimensions: 1200x800 for standard use, 1920x1080 for high-resolution


