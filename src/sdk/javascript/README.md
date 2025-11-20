# Navo JavaScript/TypeScript SDK

Official JavaScript and TypeScript SDK for Navo API.

## Installation

```bash
npm install navo-sdk
# or
yarn add navo-sdk
```

## Quick Start

### TypeScript/ES6

```typescript
import NavoClient from 'navo-sdk';

const client = new NavoClient({
  baseURL: 'http://localhost:8000',
  apiKey: 'your-api-key', // Optional
});

// Register a database
const db = await client.registerDatabase({
  id: 'db1',
  type: 'postgresql',
  host: 'localhost',
  port: 5432,
  database: 'mydb',
  user: 'postgres',
  password: 'password',
});

// Execute a query
const result = await client.executeQuery({
  query: 'Count all users',
  database_ids: ['db1'],
});

console.log(`Found ${result.total_rows} rows`);

// Generate a chart
const chart = await client.generateChart({
  query_id: result.query_id,
  chart_type: 'bar',
  x_axis: 'category',
  y_axis: 'value',
});

// Export chart
const chartBlob = await client.exportChart(result.query_id, 'png', 1920, 1080);
```

### JavaScript (CommonJS)

```javascript
const NavoClient = require('navo-sdk').default;

const client = new NavoClient({
  baseURL: 'http://localhost:8000',
});

// Use the client...
```

## API Reference

### Constructor

```typescript
new NavoClient(config?: NavoConfig)
```

**Config options:**
- `baseURL` (string): API base URL (default: `http://localhost:8000`)
- `apiKey` (string): API key for authentication (optional)
- `timeout` (number): Request timeout in ms (default: 30000)

### Methods

#### Discovery
- `registerDatabase(config: DatabaseConfig): Promise<any>`
- `listDatabases(): Promise<any[]>`
- `getDatabase(databaseId: string): Promise<any>`
- `syncDatabase(databaseId: string): Promise<any>`

#### Query
- `executeQuery(request: QueryRequest): Promise<QueryResponse>`
- `analyzeQuery(query: string): Promise<any>`

#### Visualization
- `generateChart(request: VisualizationRequest): Promise<any>`
- `exportChart(queryId: string, format: 'png' | 'pdf' | 'html' | 'svg', width?: number, height?: number): Promise<Blob>`

#### Templates
- `createTemplate(name: string, query: string, databaseIds?: string[], description?: string, tags?: string[]): Promise<any>`
- `listTemplates(page?: number, pageSize?: number, tags?: string[]): Promise<any>`
- `executeTemplate(templateId: string, parameters?: Record<string, any>): Promise<any>`

#### Export
- `exportQuery(queryId: string, format: 'csv' | 'json' | 'excel'): Promise<Blob>`

#### Analytics
- `getAnalytics(days?: number): Promise<any>`
- `getTopQueries(limit?: number, days?: number): Promise<any>`

#### Comparison
- `compareQueries(query1Id: string, query2Id: string): Promise<any>`

#### Health
- `healthCheck(): Promise<any>`

## Examples

### Complete Workflow

```typescript
import NavoClient from 'navo-sdk';

const client = new NavoClient({
  baseURL: 'https://api.example.com',
  apiKey: 'your-api-key',
});

async function main() {
  // 1. Register database
  const db = await client.registerDatabase({
    id: 'analytics_db',
    type: 'postgresql',
    host: 'db.example.com',
    port: 5432,
    database: 'analytics',
    user: 'analyst',
    password: 'secret',
  });

  // 2. Sync schema
  await client.syncDatabase('analytics_db');

  // 3. Execute query
  const result = await client.executeQuery({
    query: 'Show monthly revenue trends',
    database_ids: ['analytics_db'],
    page: 1,
    page_size: 100,
  });

  // 4. Generate visualization
  const chart = await client.generateChart({
    query_id: result.query_id,
    chart_type: 'line',
    x_axis: 'month',
    y_axis: 'revenue',
    title: 'Monthly Revenue Trends',
  });

  // 5. Export data
  const csvBlob = await client.exportQuery(result.query_id, 'csv');
  
  // Save to file (Node.js)
  const fs = require('fs');
  fs.writeFileSync('revenue.csv', csvBlob);
}

main().catch(console.error);
```

### Using Templates

```typescript
// Create template
const template = await client.createTemplate(
  'Daily Sales Report',
  "SELECT date, SUM(amount) as total FROM sales WHERE date >= '{{start_date}}' GROUP BY date",
  ['analytics_db'],
  'Daily sales aggregation',
  ['sales', 'daily']
);

// Execute with parameters
const result = await client.executeTemplate(template.id, {
  start_date: '2024-01-01',
});
```

### Error Handling

```typescript
try {
  const result = await client.executeQuery({ query: 'Invalid query' });
} catch (error) {
  if (error.response) {
    console.error('API Error:', error.response.status, error.response.data);
  } else {
    console.error('Network Error:', error.message);
  }
}
```

## Browser Usage

```html
<script src="https://cdn.jsdelivr.net/npm/navo-sdk/dist/index.umd.js"></script>
<script>
  const client = new NavoClient({
    baseURL: 'https://api.example.com',
    apiKey: 'your-api-key',
  });

  client.executeQuery({ query: 'Count users' })
    .then(result => console.log(result))
    .catch(error => console.error(error));
</script>
```

## TypeScript Support

Full TypeScript definitions are included. The SDK is written in TypeScript and provides complete type safety.

## License

MIT


