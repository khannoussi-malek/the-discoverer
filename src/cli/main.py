"""CLI main entry point."""
import click
import asyncio
import json
from typing import Optional
import httpx


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """The Discoverer CLI - AI-powered database discovery and query agent."""
    pass


@cli.command()
@click.option("--host", default="http://localhost:8000", help="API host URL")
@click.option("--database-id", required=True, help="Database ID")
@click.option("--type", required=True, help="Database type (postgresql, mysql, mongodb, etc.)")
@click.option("--host-db", required=True, help="Database host")
@click.option("--port", type=int, required=True, help="Database port")
@click.option("--database", required=True, help="Database name")
@click.option("--user", help="Database user")
@click.option("--password", help="Database password")
@click.option("--name", help="Database display name")
def register(
    host: str,
    database_id: str,
    type: str,
    host_db: str,
    port: int,
    database: str,
    user: Optional[str],
    password: Optional[str],
    name: Optional[str]
):
    """Register a database."""
    config = {
        "id": database_id,
        "type": type,
        "host": host_db,
        "port": port,
        "database": database,
        "user": user,
        "password": password,
        "name": name or database_id
    }
    
    try:
        response = httpx.post(f"{host}/api/discovery/databases", json=config)
        response.raise_for_status()
        click.echo(f"✅ Database '{database_id}' registered successfully")
        click.echo(json.dumps(response.json(), indent=2))
    except httpx.HTTPError as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)


@cli.command()
@click.option("--host", default="http://localhost:8000", help="API host URL")
def list_databases(host: str):
    """List all registered databases."""
    try:
        response = httpx.get(f"{host}/api/discovery/databases")
        response.raise_for_status()
        databases = response.json()
        
        if not databases:
            click.echo("No databases registered")
            return
        
        click.echo("\n📊 Registered Databases:\n")
        for db in databases:
            status = "✅" if db.get("is_active") else "❌"
            click.echo(f"{status} {db['id']} ({db['type']}) - {db.get('name', 'N/A')}")
            click.echo(f"   Host: {db['host']}:{db['port']}")
            click.echo(f"   Database: {db['database_name']}")
            click.echo()
    except httpx.HTTPError as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)


@cli.command()
@click.option("--host", default="http://localhost:8000", help="API host URL")
@click.argument("query")
@click.option("--database-ids", multiple=True, help="Database IDs to query")
@click.option("--format", type=click.Choice(["json", "table", "csv"]), default="table", help="Output format")
@click.option("--page", type=int, help="Page number")
@click.option("--page-size", type=int, help="Page size")
def query(
    host: str,
    query: str,
    database_ids: tuple,
    format: str,
    page: Optional[int],
    page_size: Optional[int]
):
    """Execute a natural language query."""
    request_data = {
        "query": query
    }
    
    if database_ids:
        request_data["database_ids"] = list(database_ids)
    
    params = {}
    if page:
        params["page"] = page
    if page_size:
        params["page_size"] = page_size
    
    try:
        click.echo(f"🔍 Executing query: {query}\n")
        response = httpx.post(
            f"{host}/api/query/execute",
            json=request_data,
            params=params,
            timeout=60.0
        )
        response.raise_for_status()
        result = response.json()
        
        if format == "json":
            click.echo(json.dumps(result, indent=2))
        elif format == "table":
            _print_table(result)
        elif format == "csv":
            _print_csv(result)
        
        click.echo(f"\n✅ Query completed in {result.get('execution_time', 0):.2f}s")
        click.echo(f"📊 Total rows: {result.get('total_rows', 0)}")
    
    except httpx.HTTPError as e:
        click.echo(f"❌ Error: {e}", err=True)
        if hasattr(e, 'response') and e.response:
            try:
                error_detail = e.response.json()
                click.echo(f"Details: {error_detail}", err=True)
            except:
                click.echo(f"Response: {e.response.text}", err=True)
        exit(1)


def _print_table(result: dict):
    """Print result as table."""
    data = result.get("data", [])
    if not data:
        click.echo("No data returned")
        return
    
    # Get all column names
    columns = set()
    for row in data:
        columns.update(row.keys())
    columns = sorted(columns)
    
    # Print header
    header = " | ".join(columns)
    click.echo(header)
    click.echo("-" * len(header))
    
    # Print rows
    for row in data:
        values = [str(row.get(col, ""))[:30] for col in columns]
        click.echo(" | ".join(values))


def _print_csv(result: dict):
    """Print result as CSV."""
    import csv
    import sys
    
    data = result.get("data", [])
    if not data:
        return
    
    # Get all column names
    columns = set()
    for row in data:
        columns.update(row.keys())
    columns = sorted(columns)
    
    writer = csv.DictWriter(sys.stdout, fieldnames=columns)
    writer.writeheader()
    for row in data:
        writer.writerow({col: row.get(col, "") for col in columns})


@cli.command()
@click.option("--host", default="http://localhost:8000", help="API host URL")
def health(host: str):
    """Check API health."""
    try:
        response = httpx.get(f"{host}/health", timeout=5.0)
        response.raise_for_status()
        status = response.json()
        
        click.echo("🏥 Health Check:\n")
        click.echo(f"Status: {status.get('status', 'unknown')}")
        click.echo("\nServices:")
        for service, service_status in status.get("services", {}).items():
            icon = "✅" if service_status == "healthy" else "❌"
            click.echo(f"  {icon} {service}: {service_status}")
    
    except httpx.HTTPError as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)


@cli.command()
@click.option("--host", default="http://localhost:8000", help="API host URL")
@click.argument("database_id")
def sync(host: str, database_id: str):
    """Sync database schema."""
    try:
        click.echo(f"🔄 Syncing schema for database '{database_id}'...")
        response = httpx.post(f"{host}/api/discovery/databases/{database_id}/sync")
        response.raise_for_status()
        click.echo("✅ Schema synced successfully")
        click.echo(json.dumps(response.json(), indent=2))
    except httpx.HTTPError as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)


@cli.command()
@click.option("--host", default="http://localhost:8000", help="API host URL")
@click.argument("query_id")
@click.option("--format", type=click.Choice(["csv", "json", "excel"]), default="csv", help="Export format")
def export(host: str, query_id: str, format: str):
    """Export query result."""
    try:
        click.echo(f"📥 Exporting query '{query_id}' as {format}...")
        response = httpx.get(
            f"{host}/api/export/query/{query_id}",
            params={"format": format},
            timeout=60.0
        )
        response.raise_for_status()
        
        filename = f"query_{query_id}.{format if format != 'excel' else 'xlsx'}"
        with open(filename, "wb") as f:
            f.write(response.content)
        
        click.echo(f"✅ Exported to {filename}")
    
    except httpx.HTTPError as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)


if __name__ == "__main__":
    cli()


