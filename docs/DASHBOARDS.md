# Dashboards Documentation

> 📖 **Navigation**: [Documentation Index](README.md) | [Getting Started](GETTING_STARTED.md) | [Examples](EXAMPLES.md) | [Chart Templates](CHART_TEMPLATES.md)

## Overview

Dashboards allow you to create custom views with multiple widgets (charts, queries, metrics, text) arranged in a flexible layout. Perfect for creating executive dashboards, KPI views, and data monitoring screens.

## Features

- **Multiple Widgets**: Charts, queries, metrics, and text widgets
- **Flexible Layout**: Custom positioning and sizing
- **Public/Private**: Share dashboards or keep them private
- **Tagging**: Organize dashboards with tags
- **Widget Management**: Add, update, and remove widgets dynamically
- **Rendering**: Render dashboards with all widget data populated

## API Endpoints

### Create Dashboard

```http
POST /api/dashboards
Content-Type: application/json

{
  "name": "Sales Dashboard",
  "description": "Monthly sales overview",
  "widgets": [
    {
      "type": "chart",
      "title": "Sales by Month",
      "query_id": "query-123",
      "chart_template_id": "template-456",
      "position": {"x": 0, "y": 0, "width": 6, "height": 4}
    },
    {
      "type": "metric",
      "title": "Total Revenue",
      "query_id": "query-124",
      "position": {"x": 6, "y": 0, "width": 3, "height": 2}
    }
  ],
  "layout": {"grid": "12x8"},
  "tags": ["sales", "monthly"],
  "is_public": true
}
```

### List Dashboards

```http
GET /api/dashboards?public_only=true&tags=sales
```

### Get Dashboard

```http
GET /api/dashboards/{dashboard_id}
```

### Render Dashboard

```http
GET /api/dashboards/{dashboard_id}/render
```

Returns the dashboard with all widget data populated.

### Update Dashboard

```http
PUT /api/dashboards/{dashboard_id}
Content-Type: application/json

{
  "name": "Updated Dashboard",
  "widgets": [...]
}
```

### Delete Dashboard

```http
DELETE /api/dashboards/{dashboard_id}
```

### Widget Management

```http
# Add widget
POST /api/dashboards/{dashboard_id}/widgets
Content-Type: application/json

{
  "type": "chart",
  "title": "New Chart",
  "query_id": "query-125",
  "position": {"x": 0, "y": 4, "width": 6, "height": 4}
}

# Update widget
PUT /api/dashboards/{dashboard_id}/widgets/{widget_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "position": {"x": 0, "y": 0, "width": 12, "height": 6}
}

# Remove widget
DELETE /api/dashboards/{dashboard_id}/widgets/{widget_id}
```

## Widget Types

### Chart Widget

```json
{
  "type": "chart",
  "title": "Sales Chart",
  "query_id": "query-123",
  "chart_template_id": "template-456",
  "position": {"x": 0, "y": 0, "width": 6, "height": 4},
  "config": {
    "chart_type": "bar",
    "x_axis": "month",
    "y_axis": "sales"
  }
}
```

### Query Widget

```json
{
  "type": "query",
  "title": "Recent Orders",
  "query_id": "query-124",
  "position": {"x": 6, "y": 0, "width": 6, "height": 4}
}
```

### Metric Widget

```json
{
  "type": "metric",
  "title": "Total Revenue",
  "query_id": "query-125",
  "position": {"x": 0, "y": 4, "width": 3, "height": 2},
  "config": {
    "aggregation": "sum",
    "column": "revenue",
    "format": "currency"
  }
}
```

### Text Widget

```json
{
  "type": "text",
  "title": "Notes",
  "position": {"x": 3, "y": 4, "width": 9, "height": 2},
  "config": {
    "content": "Monthly sales report for Q1 2024"
  }
}
```

## Examples

### Create a Simple Dashboard

```bash
curl -X POST "http://localhost:8000/api/dashboards" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Executive Dashboard",
    "description": "Key metrics for executives",
    "widgets": [
      {
        "type": "metric",
        "title": "Total Revenue",
        "query_id": "query-123",
        "position": {"x": 0, "y": 0, "width": 4, "height": 2}
      },
      {
        "type": "chart",
        "title": "Revenue Trend",
        "query_id": "query-124",
        "position": {"x": 4, "y": 0, "width": 8, "height": 6}
      }
    ],
    "layout": {"grid": "12x8"},
    "tags": ["executive", "kpi"]
  }'
```

### Render Dashboard

```bash
curl "http://localhost:8000/api/dashboards/dashboard-123/render"
```

This returns the dashboard with all widget data populated, ready for display.

## Use Cases

1. **Executive Dashboards**: High-level KPIs and trends
2. **Operational Monitoring**: Real-time metrics and alerts
3. **Analytical Dashboards**: Deep-dive analysis with multiple charts
4. **Report Dashboards**: Scheduled reports with multiple visualizations
5. **Team Dashboards**: Shared views for team collaboration

## Best Practices

1. **Layout**: Use consistent grid systems (e.g., 12-column grid)
2. **Widget Sizing**: Balance widget sizes for optimal viewing
3. **Performance**: Limit widgets per dashboard for fast rendering
4. **Naming**: Use descriptive names and descriptions
5. **Tags**: Tag dashboards for easy discovery
6. **Public Dashboards**: Share commonly used dashboards as public


