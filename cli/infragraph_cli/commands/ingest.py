"""ingest and status commands."""

from __future__ import annotations

from pathlib import Path

import typer
from rich import print as rprint
from rich.console import Console

from infragraph_cli.client import InfraGraphClient
from infragraph_cli.output import ingestion_table

app = typer.Typer(help="Ingest Terraform plan/state files.")
console = Console()


@app.command("upload")
def ingest(
    file: Path = typer.Argument(..., help="Path to a Terraform plan or state JSON file"),
    api_url: str = typer.Option(
        None, "--api-url", envvar="INFRAGRAPH_API_URL", hidden=True
    ),
) -> None:
    """Upload a Terraform JSON file and ingest it into InfraGraph."""
    if not file.exists():
        rprint(f"[red]File not found: {file}[/red]")
        raise typer.Exit(1)
    base = api_url or "http://localhost:8000"
    with InfraGraphClient(base) as client:
        with file.open("rb") as fh:
            result = client.post(
                "/api/ingest/upload",
                files={"file": (file.name, fh, "application/json")},
            )
    console.print(ingestion_table(result))


@app.command()
def status(
    run_id: str = typer.Argument(..., help="Ingestion run UUID"),
    api_url: str = typer.Option(
        None, "--api-url", envvar="INFRAGRAPH_API_URL", hidden=True
    ),
) -> None:
    """Show the status of an ingestion run."""
    base = api_url or "http://localhost:8000"
    with InfraGraphClient(base) as client:
        result = client.get(f"/api/ingest/{run_id}")
    console.print(ingestion_table(result))
