"""findings list and scan commands."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

from infragraph_cli.client import InfraGraphClient
from infragraph_cli.output import finding_table

app = typer.Typer(help="View and trigger findings.")
console = Console()


@app.command("list")
def findings(
    type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by finding type"),
    severity: Optional[str] = typer.Option(
        None, "--severity", "-s", help="Filter by severity (info/low/medium/high/critical)"
    ),
    limit: int = typer.Option(50, "--limit", "-n", help="Max number of results"),
    api_url: str = typer.Option(
        None, "--api-url", envvar="INFRAGRAPH_API_URL", hidden=True
    ),
) -> None:
    """List detected findings."""
    base = api_url or "http://localhost:8000"
    params: dict = {"limit": limit}
    if type:
        params["finding_type"] = type
    if severity:
        params["severity"] = severity
    with InfraGraphClient(base) as client:
        result = client.get("/api/findings", params=params)
    items = result if isinstance(result, list) else result.get("items", [])
    console.print(finding_table(items))


@app.command()
def scan(
    api_url: str = typer.Option(
        None, "--api-url", envvar="INFRAGRAPH_API_URL", hidden=True
    ),
) -> None:
    """Run the findings scanner and display results."""
    base = api_url or "http://localhost:8000"
    with InfraGraphClient(base) as client:
        result = client.post("/api/findings/scan")
    items = result if isinstance(result, list) else result.get("items", [])
    console.print(f"\n[bold green]Scan complete.[/bold green] Found {len(items)} finding(s).\n")
    if items:
        console.print(finding_table(items))
