"""Rich table/tree formatters shared across all CLI commands."""

from __future__ import annotations

from typing import Any

from rich.table import Table
from rich.tree import Tree

SEVERITY_STYLE: dict[str, str] = {
    "info": "white",
    "low": "blue",
    "medium": "yellow",
    "high": "red",
    "critical": "bold red",
}


def ingestion_table(run: dict[str, Any]) -> Table:
    table = Table(title="Ingestion Run", show_header=True, header_style="bold cyan")
    table.add_column("Field", style="dim")
    table.add_column("Value")
    rows = [
        ("ID", str(run.get("id", ""))),
        ("File", run.get("file_name") or run.get("source_file") or "—"),
        ("Status", run.get("status", "")),
        ("Source type", run.get("source_type", "")),
        ("Resources", str(run.get("resource_count", 0))),
        ("Relationships", str(run.get("relationship_count", 0))),
        ("Error", run.get("error_message") or run.get("error") or "—"),
    ]
    for field, value in rows:
        table.add_row(field, value)
    return table


def resource_table(resources: list[dict[str, Any]]) -> Table:
    table = Table(title=f"Resources ({len(resources)})", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Provider")
    table.add_column("Source")
    table.add_column("Change")
    for r in resources:
        rid = str(r.get("id", ""))[:8]
        table.add_row(
            rid,
            r.get("name") or "—",
            r.get("resource_type") or "—",
            r.get("provider") or "—",
            r.get("source_type") or "—",
            r.get("change_action") or "—",
        )
    return table


def finding_table(findings: list[dict[str, Any]]) -> Table:
    table = Table(
        title=f"Findings ({len(findings)})", show_header=True, header_style="bold cyan"
    )
    table.add_column("Severity", no_wrap=True)
    table.add_column("Type")
    table.add_column("Message")
    table.add_column("Resource ID", style="dim")
    for f in findings:
        sev = f.get("severity", "info")
        style = SEVERITY_STYLE.get(sev, "white")
        message = f.get("message", "")
        if len(message) > 60:
            message = message[:57] + "..."
        rid = str(f.get("resource_id", ""))[:8]
        table.add_row(
            f"[{style}]{sev}[/{style}]",
            f.get("finding_type") or "—",
            message,
            rid,
        )
    return table


def graph_tree(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    root_id: str,
) -> Tree:
    # Build lookup maps
    node_map = {n["id"]: n for n in nodes}

    # Gather neighbors of root
    neighbors: list[tuple[str, str]] = []  # (target_id, relationship_type)
    for edge in edges:
        src = edge.get("source_id") or edge.get("source")
        tgt = edge.get("target_id") or edge.get("target")
        rel = edge.get("relationship_type", "")
        if str(src) == str(root_id):
            neighbors.append((str(tgt), rel))
        elif str(tgt) == str(root_id):
            neighbors.append((str(src), f"{rel} (reverse)"))

    root_node = node_map.get(root_id, {})
    root_label = (
        f"[bold]{root_node.get('name') or root_id}[/bold] "
        f"[dim]({root_node.get('resource_type', '')})[/dim]"
    )
    tree = Tree(root_label)
    for neighbor_id, rel_type in neighbors:
        n = node_map.get(neighbor_id, {})
        label = (
            f"{n.get('name') or neighbor_id} "
            f"[dim]{n.get('resource_type', '')}[/dim] "
            f"[cyan]—{rel_type}→[/cyan]"
        )
        tree.add(label)
    return tree


def blast_radius_tree(
    data: dict[str, Any],
    root_id: str,
) -> Tree:
    affected = data.get("affected_resources", [])
    root_label = (
        f"[bold red]{root_id}[/bold red] "
        f"[dim](blast radius — {len(affected)} affected)[/dim]"
    )
    tree = Tree(root_label)
    for r in affected:
        label = (
            f"{r.get('name') or r.get('id', '')[:8]} "
            f"[dim]{r.get('resource_type', '')}[/dim]"
        )
        tree.add(label)
    return tree
