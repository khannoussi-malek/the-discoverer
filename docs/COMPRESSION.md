# Query Result Compression Documentation

## Overview

Query result compression reduces response size and improves network transfer performance. Navo supports multiple compression algorithms with configurable compression levels.

## Features

- **Multiple Algorithms**: gzip, zlib, lzma, and brotli
- **Configurable Levels**: Compression levels from 1-9
- **Automatic Statistics**: Compression ratio and space saved metrics
- **Base64 Encoding**: Compressed data encoded for safe JSON transport
- **API Endpoints**: Standalone compression utilities

## Supported Algorithms

### GZIP
- **Best for**: General purpose, good balance of speed and compression
- **Default**: Yes
- **Speed**: Fast
- **Compression**: Good

### ZLIB
- **Best for**: Similar to gzip, slightly faster
- **Speed**: Very fast
- **Compression**: Good

### LZMA
- **Best for**: Maximum compression when size matters more than speed
- **Speed**: Slower
- **Compression**: Excellent

### Brotli
- **Best for**: Web content, excellent compression
- **Speed**: Moderate
- **Compression**: Excellent
- **Note**: Requires `brotli` package (`pip install brotli`)

## Usage

### Compress Query Results

Request compression in query execution:

```http
POST /api/query/execute
Content-Type: application/json

{
  "query": "Show me all users",
  "compress": true,
  "compression_type": "gzip"
}
```

**Response:**
```json
{
  "query_id": "query-123",
  "compressed_data": "H4sIAAAAAAAAA...",
  "compression_info": {
    "compression_type": "gzip",
    "original_size": 1024000,
    "compressed_size": 256000,
    "compression_ratio": 0.25,
    "space_saved": 768000
  },
  "total_rows": 1000,
  "execution_time": 0.5,
  "databases_queried": ["db-1"]
}
```

### Decompress Results

```python
from src.utils.compression import CompressionService

# Decompress the response
compressed_dict = {
    "compressed": True,
    "compression_type": "gzip",
    "data": "H4sIAAAAAAAAA..."
}

data = CompressionService.decompress_json(compressed_dict)
```

## API Endpoints

### Compress Data

```http
POST /api/compression/compress
Content-Type: application/json

{
  "data": {"key": "value", "array": [1, 2, 3]},
  "compression_type": "gzip",
  "level": 6
}
```

**Response:**
```json
{
  "compressed": true,
  "compression_type": "gzip",
  "data": "H4sIAAAAAAAAA...",
  "original_size": 1024,
  "compressed_size": 256,
  "compression_ratio": 0.25,
  "space_saved": 768
}
```

### Decompress Data

```http
POST /api/compression/decompress
Content-Type: application/json

{
  "compressed": true,
  "compression_type": "gzip",
  "data": "H4sIAAAAAAAAA..."
}
```

**Response:**
```json
{
  "data": {"key": "value", "array": [1, 2, 3]}
}
```

### Get Compression Statistics

```http
POST /api/compression/stats
Content-Type: application/json

{
  "data": {"large": "dataset", "with": "many", "fields": [...]},
  "compression_types": ["gzip", "zlib", "lzma"]
}
```

**Response:**
```json
{
  "stats": {
    "gzip": {
      "original_size": 1024000,
      "compressed_size": 256000,
      "compression_ratio": 0.25,
      "space_saved": 768000,
      "space_saved_percent": 75.0
    },
    "zlib": {
      "original_size": 1024000,
      "compressed_size": 270000,
      "compression_ratio": 0.26,
      "space_saved": 754000,
      "space_saved_percent": 73.6
    },
    "lzma": {
      "original_size": 1024000,
      "compressed_size": 200000,
      "compression_ratio": 0.20,
      "space_saved": 824000,
      "space_saved_percent": 80.4
    }
  }
}
```

## Compression Levels

Compression levels range from 1-9:

- **1-3**: Fast compression, larger output
- **4-6**: Balanced (default: 6)
- **7-9**: Slower compression, smaller output

## Examples

### Python SDK

```python
from src.sdk.sync_client import DiscovererClient

client = DiscovererClient("http://localhost:8000")

# Execute query with compression
response = client.execute_query(
    query="Show me all users",
    compress=True,
    compression_type="gzip"
)

# Decompress if needed
if response.compressed_data:
    from src.utils.compression import CompressionService
    data = CompressionService.decompress_from_base64(
        response.compressed_data,
        CompressionType.GZIP
    )
```

### JavaScript SDK

```javascript
const client = new DiscovererClient('http://localhost:8000');

// Execute query with compression
const response = await client.executeQuery({
  query: 'Show me all users',
  compress: true,
  compression_type: 'gzip'
});

// Decompress if needed
if (response.compressed_data) {
  // Use a compression library like pako for gzip
  const decompressed = pako.inflate(
    atob(response.compressed_data),
    { to: 'string' }
  );
  const data = JSON.parse(decompressed);
}
```

### Direct Compression

```python
from src.utils.compression import CompressionService, CompressionType

# Compress data
data = {"users": [{"id": 1, "name": "John"}, ...]}
compressed = CompressionService.compress_json(data, CompressionType.GZIP)

# Decompress
decompressed = CompressionService.decompress_json(compressed)
```

## Best Practices

1. **Use Compression for Large Results**: Enable compression for queries returning >100KB
2. **Choose Algorithm Based on Use Case**:
   - **gzip**: General purpose, good default
   - **lzma**: Maximum compression for storage
   - **brotli**: Web content, excellent compression
3. **Adjust Compression Level**: Higher levels (7-9) for storage, lower (1-3) for real-time
4. **Monitor Statistics**: Check compression ratios to optimize
5. **Client Support**: Ensure clients can decompress the chosen algorithm

## Performance Considerations

- **CPU Usage**: Compression adds CPU overhead
- **Memory**: Compressed data uses less memory
- **Network**: Significantly reduced transfer time for large results
- **Trade-off**: Compression time vs. network transfer time

## Compression Ratios

Typical compression ratios for JSON data:

- **Text-heavy data**: 70-90% reduction
- **Numeric data**: 50-70% reduction
- **Mixed data**: 60-80% reduction
- **Already compressed data**: Minimal benefit

## Error Handling

Compression failures fall back to uncompressed data:

```python
# If compression fails, query returns uncompressed data
response = client.execute_query(
    query="...",
    compress=True
)

# Check if compression was applied
if response.compression_info:
    print(f"Compressed: {response.compression_info['compression_ratio']}")
else:
    print("Compression not applied or failed")
```



