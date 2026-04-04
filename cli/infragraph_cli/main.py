"""Root Typer app — assembles all sub-commands."""

from __future__ import annotations

import os
from typing import Optional

import typer

from infragraph_cli.commands import findings, graph, ingest, resources

app = typer.Typer(
    name="infragraph",
    help="InfraGraph CLI — manage your infrastructure graph from the terminal.",
    no_args_is_help=True,
)

# ---------------------------------------------------------------------------
# Sub-apps
# ---------------------------------------------------------------------------

app.add_typer(ingest.app, name="ingest")
app.add_typer(resources.app, name="resources")
app.add_typer(graph.app, name="graph")
app.add_typer(findings.app, name="findings")

# ---------------------------------------------------------------------------
# Top-level shortcut commands (mirrors the most-used sub-commands)
# ---------------------------------------------------------------------------


@app.command()
def scan(
    api_url: str = typer.Option(
        None, "--api-url", envvar="INFRAGRAPH_API_URL", hidden=True
    ),
) -> None:
    """Run the findings scanner (shortcut for `findings scan`)."""
    findings.scan(api_url=api_url)


@app.command("blast-radius")
def blast_radius_cmd(
    resource_id: str = typer.Argument(..., help="Resource UUID"),
    depth: int = typer.Option(3, "--depth", "-d", help="Traversal depth (1–10)"),
    api_url: str = typer.Option(
        None, "--api-url", envvar="INFRAGRAPH_API_URL", hidden=True
    ),
) -> None:
    """Show blast radius for a resource (shortcut for `graph blast-radius`)."""
    graph.blast_radius(resource_id=resource_id, depth=depth, api_url=api_url)


@app.callback()
def _root_callback(
    ctx: typer.Context,
    api_url: Optional[str] = typer.Option(
        None,
        "--api-url",
        envvar="INFRAGRAPH_API_URL",
        help="Base URL of the InfraGraph API (default: http://localhost:8000)",
        is_eager=True,
    ),
) -> None:
    """InfraGraph CLI — calls the API at API_URL (env: INFRAGRAPH_API_URL)."""
    if api_url:
        os.environ["INFRAGRAPH_API_URL"] = api_url
