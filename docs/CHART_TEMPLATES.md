# Chart Templates Documentation

## Overview

Chart templates allow you to save and reuse chart configurations, making it easy to create consistent visualizations across different queries.

## Features

- **Reusable Configurations**: Save chart settings for reuse
- **Public/Private Templates**: Share templates with others or keep them private
- **Tagging**: Organize templates with tags
- **Usage Tracking**: See how often templates are used
- **Search**: Find templates by name, description, or tags
- **Apply to Queries**: Quickly apply templates to any query result

## API Endpoints

### Create Template

```http
POST /api/chart-templates
Content-Type: application/json

{
  "name": "Sales Bar Chart",
  "chart_type": "bar",
  "config": {
    "x_axis": "category",
    "y_axis": "sales",
    "title": "Sales by Category",
    "colors": ["#3498db", "#2ecc71"]
  },
  "description": "Standard bar chart for sales data",
  "tags": ["sales", "bar"],
  "is_public": true
}
```

### List Templates

```http
GET /api/chart-templates?chart_type=bar&tags=sales&public_only=true
```

**Query Parameters:**
- `chart_type` (optional): Filter by chart type
- `tags` (optional): Comma-separated list of tags
- `public_only` (optional): Show only public templates

### Get Template

```http
GET /api/chart-templates/{template_id}
```

### Update Template

```http
PUT /api/chart-templates/{template_id}
Content-Type: application/json

{
  "name": "Updated Sales Chart",
  "config": {
    "title": "Updated Title"
  }
}
```

### Delete Template

```http
DELETE /api/chart-templates/{template_id}
```

### Apply Template

```http
POST /api/chart-templates/{template_id}/apply?query_id=query-123
Content-Type: application/json

{
  "overrides": {
    "title": "Custom Title"
  }
}
```

**Query Parameters:**
- `query_id` (required): Query ID to apply template to

**Body (optional):**
- `overrides`: Configuration overrides for this specific application

### Search Templates

```http
GET /api/chart-templates/search?q=sales&limit=10
```

**Query Parameters:**
- `q` (required): Search query
- `limit` (optional): Maximum results (default: 10, max: 100)

## Examples

### Create a Template

```bash
curl -X POST "http://localhost:8000/api/chart-templates" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Revenue Line Chart",
    "chart_type": "line",
    "config": {
      "x_axis": "month",
      "y_axis": "revenue",
      "title": "Monthly Revenue",
      "line_color": "#3498db"
    },
    "tags": ["revenue", "line", "monthly"],
    "is_public": true
  }'
```

### Apply Template to Query

```bash
# First execute a query
curl -X POST "http://localhost:8000/api/query/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show monthly revenue",
    "database_ids": ["db1"]
  }'

# Then apply template
curl -X POST "http://localhost:8000/api/chart-templates/template-123/apply?query_id=query-456"
```

### Search Templates

```bash
curl "http://localhost:8000/api/chart-templates/search?q=revenue&limit=5"
```

## Template Configuration

The `config` field can include any chart configuration options:

```json
{
  "x_axis": "category",
  "y_axis": "value",
  "z_axis": "segment",  // For 3D charts
  "title": "Chart Title",
  "colors": ["#3498db", "#2ecc71", "#e74c3c"],
  "width": 1200,
  "height": 800,
  "show_legend": true,
  "x_axis_title": "Categories",
  "y_axis_title": "Values"
}
```

## Use Cases

1. **Standard Reports**: Create templates for common report types
2. **Brand Consistency**: Ensure all charts follow brand guidelines
3. **Quick Visualization**: Apply templates to quickly visualize query results
4. **Team Sharing**: Share public templates with your team
5. **Best Practices**: Document and share visualization best practices

## Best Practices

1. **Naming**: Use descriptive names that indicate the chart type and use case
2. **Tags**: Use consistent tags for easy discovery
3. **Documentation**: Include descriptions explaining when to use each template
4. **Public Templates**: Mark commonly used templates as public
5. **Versioning**: Update templates when improving configurations


