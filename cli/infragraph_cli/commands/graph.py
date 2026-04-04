"""graph and blast-radius commands."""

from __future__ import annotations

import typer
from rich.console import Console

from infragraph_cli.client import InfraGraphClient
from infragraph_cli.output import blast_radius_tree, graph_tree

app = typer.Typer(help="Explore resource dependency graphs.")
console = Console()


@app.command()
def graph(
    resource_id: str = typer.Argument(..., help="Resource UUID"),
    api_url: str = typer.Option(
        None, "--api-url", envvar="INFRAGRAPH_API_URL", hidden=True
    ),
) -> None:
    """Show the dependency graph for a resource."""
    base = api_url or "http://localhost:8000"
    with InfraGraphClient(base) as client:
        data = client.get(f"/api/graph/{resource_id}")
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    console.print(f"\n[bold]Nodes:[/bold] {len(nodes)}  [bold]Edges:[/bold] {len(edges)}\n")
    console.print(graph_tree(nodes, edges, resource_id))


@app.command("blast-radius")
def blast_radius(
    resource_id: str = typer.Argument(..., help="Resource UUID"),
    depth: int = typer.Option(3, "--depth", "-d", help="Traversal depth (1–10)"),
    api_url: str = typer.Option(
        None, "--api-url", envvar="INFRAGRAPH_API_URL", hidden=True
    ),
) -> None:
    """Show the blast radius for a resource change."""
    base = api_url or "http://localhost:8000"
    with InfraGraphClient(base) as client:
        data = client.get(
            f"/api/graph/{resource_id}/blast-radius", params={"depth": depth}
        )
    affected = data.get("affected_resources", [])
    console.print(
        f"\n[bold]Root resource:[/bold] {resource_id}\n"
        f"[bold]Depth:[/bold] {depth}\n"
        f"[bold]Affected:[/bold] {len(affected)} resource(s)\n"
    )
    console.print(blast_radius_tree(data, resource_id))
