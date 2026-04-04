"""resources list command."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

from infragraph_cli.client import InfraGraphClient
from infragraph_cli.output import resource_table

app = typer.Typer(help="Browse ingested resources.")
console = Console()


@app.command("list")
def resources(
    type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by resource type"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Filter by provider"),
    source: Optional[str] = typer.Option(None, "--source", "-s", help="Filter by source type"),
    limit: int = typer.Option(50, "--limit", "-n", help="Max number of results"),
    api_url: str = typer.Option(
        None, "--api-url", envvar="INFRAGRAPH_API_URL", hidden=True
    ),
) -> None:
    """List ingested resources with optional filters."""
    base = api_url or "http://localhost:8000"
    params: dict = {"limit": limit}
    if type:
        params["resource_type"] = type
    if provider:
        params["provider"] = provider
    if source:
        params["source_type"] = source
    with InfraGraphClient(base) as client:
        result = client.get("/api/resources", params=params)
    items = result if isinstance(result, list) else result.get("items", [])
    console.print(resource_table(items))
