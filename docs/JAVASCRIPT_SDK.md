# JavaScript/TypeScript SDK Documentation

> 📖 **Navigation**: [Documentation Index](README.md) | [Getting Started](GETTING_STARTED.md) | [Examples](EXAMPLES.md) | [API Reference](API.md) | [Python SDK](SDK.md)

## Overview

The Discoverer JavaScript/TypeScript SDK provides a complete client library for interacting with The Discoverer API from both browser and Node.js environments.

## Installation

```bash
npm install @discoverer/sdk
# or
yarn add @discoverer/sdk
```

## Quick Start

### TypeScript/ES6

```typescript
import DiscovererClient from '@discoverer/sdk';

const client = new DiscovererClient({
  baseURL: 'http://localhost:8000',
  apiKey: 'your-api-key',
});

// Execute a query
const result = await client.executeQuery({
  query: 'Count all users',
  database_ids: ['db1'],
});
```

### JavaScript (CommonJS)

```javascript
const DiscovererClient = require('@discoverer/sdk').default;

const client = new DiscovererClient({
  baseURL: 'http://localhost:8000',
});
```

## Configuration

```typescript
interface DiscovererConfig {
  baseURL?: string;      // Default: 'http://localhost:8000'
  apiKey?: string;       // Optional API key
  timeout?: number;      // Default: 30000ms
}
```

## API Methods

### Discovery

```typescript
// Register a database
await client.registerDatabase({
  id: 'db1',
  type: 'postgresql',
  host: 'localhost',
  port: 5432,
  database: 'mydb',
  user: 'postgres',
  password: 'password',
});

// List databases
const databases = await client.listDatabases();

// Get database details
const db = await client.getDatabase('db1');

// Sync database schema
await client.syncDatabase('db1');
```

### Query Execution

```typescript
// Execute query
const result = await client.executeQuery({
  query: 'Show top 10 products by sales',
  database_ids: ['db1'],
  page: 1,
  page_size: 10,
});

// Analyze query without executing
const analysis = await client.analyzeQuery('Count users');
```

### Visualization

```typescript
// Generate chart
const chart = await client.generateChart({
  query_id: result.query_id,
  chart_type: 'bar',
  x_axis: 'category',
  y_axis: 'value',
  title: 'Sales by Category',
});

// Export chart
const chartBlob = await client.exportChart(
  result.query_id,
  'png',
  1920,
  1080
);
```

### Templates

```typescript
// Create template
const template = await client.createTemplate(
  'Daily Sales',
  "SELECT date, SUM(amount) FROM sales WHERE date >= '{{start_date}}'",
  ['db1'],
  'Daily sales report',
  ['sales', 'daily']
);

// Execute template
const result = await client.executeTemplate(template.id, {
  start_date: '2024-01-01',
});
```

### Export

```typescript
// Export query result
const csvBlob = await client.exportQuery(result.query_id, 'csv');
const jsonBlob = await client.exportQuery(result.query_id, 'json');
const excelBlob = await client.exportQuery(result.query_id, 'excel');
```

### Comparison

```typescript
// Compare two query results
const comparison = await client.compareQueries('query1', 'query2');
console.log(`Similarity: ${comparison.similarity_score}`);
```

### Analytics

```typescript
// Get usage analytics
const analytics = await client.getAnalytics(7); // Last 7 days

// Get top queries
const topQueries = await client.getTopQueries(10, 7);
```

## Error Handling

```typescript
try {
  const result = await client.executeQuery({ query: '...' });
} catch (error) {
  if (error.response) {
    // API error
    console.error('Status:', error.response.status);
    console.error('Data:', error.response.data);
  } else {
    // Network error
    console.error('Error:', error.message);
  }
}
```

## Browser Usage

```html
<script src="https://cdn.jsdelivr.net/npm/@discoverer/sdk/dist/index.umd.js"></script>
<script>
  const client = new DiscovererClient({
    baseURL: 'https://api.example.com',
  });
  
  client.executeQuery({ query: 'Count users' })
    .then(result => console.log(result))
    .catch(error => console.error(error));
</script>
```

## TypeScript Support

The SDK is written in TypeScript and provides complete type definitions. All methods and interfaces are fully typed for better IDE support and type safety.

## Examples

See the SDK README for complete examples and usage patterns.


