# CLI Tool Documentation

## Installation

Install the CLI tool by installing the package:

```bash
pip install -e .
```

Or use directly:

```bash
python -m src.cli.main
```

## Commands

### Register Database

Register a new database:

```bash
navo register \
  --database-id db1 \
  --type postgresql \
  --host-db localhost \
  --port 5432 \
  --database mydb \
  --user postgres \
  --password mypassword \
  --name "My Database"
```

**Options:**
- `--host` - API host URL (default: http://localhost:8000)
- `--database-id` - Unique database identifier (required)
- `--type` - Database type: postgresql, mysql, mongodb, sqlite, cassandra, elasticsearch (required)
- `--host-db` - Database host (required)
- `--port` - Database port (required)
- `--database` - Database name (required)
- `--user` - Database user (optional)
- `--password` - Database password (optional)
- `--name` - Display name (optional)

### List Databases

List all registered databases:

```bash
navo list-databases [--host http://localhost:8000]
```

### Execute Query

Execute a natural language query:

```bash
navo query "Count all users" \
  --database-ids db1 db2 \
  --format table \
  --page 1 \
  --page-size 20
```

**Options:**
- `--host` - API host URL (default: http://localhost:8000)
- `--database-ids` - Database IDs to query (can specify multiple)
- `--format` - Output format: json, table, csv (default: table)
- `--page` - Page number for pagination
- `--page-size` - Page size for pagination

**Output Formats:**
- `json` - JSON output
- `table` - Formatted table
- `csv` - CSV format

### Health Check

Check API health:

```bash
navo health [--host http://localhost:8000]
```

### Sync Schema

Sync database schema:

```bash
navo sync db1 [--host http://localhost:8000]
```

### Export Query Result

Export a query result to a file:

```bash
navo export query_id \
  --format csv \
  [--host http://localhost:8000]
```

**Options:**
- `--format` - Export format: csv, json, excel (default: csv)

## Examples

### Complete Workflow

```bash
# 1. Register a database
navo register \
  --database-id production_db \
  --type postgresql \
  --host-db db.example.com \
  --port 5432 \
  --database analytics \
  --user analyst \
  --password secret

# 2. Check health
navo health

# 3. Sync schema
navo sync production_db

# 4. Execute a query
navo query "Show top 10 customers by revenue" \
  --database-ids production_db \
  --format table

# 5. Export result (using query_id from previous step)
navo export abc123 --format excel
```

### Using Different Hosts

```bash
# Connect to remote API
navo query "Count users" \
  --host https://api.example.com \
  --format json
```

### Batch Operations

```bash
# List all databases
navo list-databases

# Sync all databases (using shell loop)
for db in db1 db2 db3; do
  navo sync $db
done
```

## Authentication

If the API requires authentication, you can set the token as an environment variable:

```bash
export DISCOVERER_TOKEN="your-jwt-token"
```

(Note: CLI authentication support can be added in future versions)

## Error Handling

The CLI provides clear error messages:

- ❌ Red X for errors
- ✅ Green checkmark for success
- Detailed error information when available

## Tips

1. **Use aliases**: Create shell aliases for common commands
   ```bash
   alias dq='navo query'
   alias dl='navo list-databases'
   ```

2. **Output redirection**: Save query results to files
   ```bash
   navo query "SELECT * FROM users" --format json > results.json
   ```

3. **Scripting**: Use in shell scripts for automation
   ```bash
   #!/bin/bash
   navo health || exit 1
   navo query "Daily report" --format csv > daily_report.csv
   ```


