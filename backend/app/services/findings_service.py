"""Findings detection engine — 5 detectors for infrastructure issues."""

from __future__ import annotations

from collections import defaultdict

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Finding,
    FindingType,
    Relationship,
    Resource,
    Severity,
)

CRITICAL_NODE_THRESHOLD = 5


async def run_detection(session: AsyncSession) -> list[Finding]:
    """Run all detectors, replace existing findings, return new ones."""
    await session.execute(delete(Finding))

    findings: list[Finding] = []
    findings.extend(await _detect_orphans(session))
    findings.extend(await _detect_drift(session))
    findings.extend(await _detect_exposure(session))
    findings.extend(await _detect_circular_deps(session))
    findings.extend(await _detect_critical_nodes(session))

    session.add_all(findings)
    await session.commit()
    return findings


async def _detect_orphans(session: AsyncSession) -> list[Finding]:
    """Resources with zero outgoing AND zero incoming relationships."""
    # Subquery: resources that appear in any relationship
    from_ids = select(Relationship.from_resource_id)
    to_ids = select(Relationship.to_resource_id)

    stmt = select(Resource).where(
        Resource.id.not_in(from_ids),
        Resource.id.not_in(to_ids),
    )
    result = await session.execute(stmt)
    orphans = result.scalars().all()

    return [
        Finding(
            resource_id=r.id,
            finding_type=FindingType.orphan,
            severity=Severity.low,
            category="connectivity",
            message=f"Resource {r.external_id} has no relationships (orphan)",
            details={"external_id": r.external_id, "resource_type": r.resource_type},
        )
        for r in orphans
    ]


async def _detect_drift(session: AsyncSession) -> list[Finding]:
    """Resources whose change_action indicates plan differs from state."""
    stmt = select(Resource).where(
        Resource.change_action.in_(["delete", "update", "replace"])
    )
    result = await session.execute(stmt)
    resources = result.scalars().all()

    severity_map = {
        "delete": Severity.high,
        "update": Severity.medium,
        "replace": Severity.medium,
    }

    return [
        Finding(
            resource_id=r.id,
            finding_type=FindingType.drift,
            severity=severity_map[r.change_action],
            category="state",
            message=(
                f"Resource {r.external_id} has change_action={r.change_action}"
                " (plan differs from state)"
            ),
            details={
                "external_id": r.external_id,
                "change_action": r.change_action,
            },
        )
        for r in resources
    ]


_EXPOSURE_RULES: list[dict] = [
    {
        "resource_type": "aws_lb",
        "check": lambda attrs: attrs.get("internal") is False,
        "message": "Public load balancer (internal=false)",
        "severity": Severity.medium,
    },
    {
        "resource_type": "aws_db_instance",
        "check": lambda attrs: attrs.get("publicly_accessible") is True,
        "message": "Database is publicly accessible",
        "severity": Severity.critical,
    },
    {
        "resource_type": "aws_db_instance",
        "check": lambda attrs: not attrs.get("kms_key_id"),
        "message": "Database storage is not encrypted (missing kms_key_id)",
        "severity": Severity.high,
    },
    {
        "resource_type": "aws_lb_listener",
        "check": lambda attrs: str(attrs.get("protocol", "")).upper() == "HTTP",
        "message": "Listener uses unencrypted HTTP protocol",
        "severity": Severity.medium,
    },
]


async def _detect_exposure(session: AsyncSession) -> list[Finding]:
    """Check for known insecure patterns in resource attributes."""
    target_types = list({rule["resource_type"] for rule in _EXPOSURE_RULES})
    stmt = select(Resource).where(Resource.resource_type.in_(target_types))
    result = await session.execute(stmt)
    resources = result.scalars().all()

    findings: list[Finding] = []
    for r in resources:
        attrs = r.attributes or {}
        for rule in _EXPOSURE_RULES:
            if r.resource_type != rule["resource_type"]:
                continue
            if rule["check"](attrs):
                findings.append(
                    Finding(
                        resource_id=r.id,
                        finding_type=FindingType.exposure,
                        severity=rule["severity"],
                        category="security",
                        message=f"{r.external_id}: {rule['message']}",
                        details={
                            "external_id": r.external_id,
                            "resource_type": r.resource_type,
                            "rule": rule["message"],
                        },
                    )
                )
    return findings


async def _detect_circular_deps(session: AsyncSession) -> list[Finding]:
    """DFS cycle detection over the relationship graph."""
    stmt = select(Relationship)
    result = await session.execute(stmt)
    edges = result.scalars().all()

    adj: dict[str, list[str]] = defaultdict(list)
    for e in edges:
        adj[str(e.from_resource_id)].append(str(e.to_resource_id))

    all_nodes = set(adj.keys())
    for targets in adj.values():
        all_nodes.update(targets)

    _white, _gray, _black = 0, 1, 2
    color: dict[str, int] = {n: _white for n in all_nodes}
    cycle_members: set[str] = set()

    def dfs(node: str) -> bool:
        color[node] = _gray
        found = False
        for neighbor in adj.get(node, []):
            if color[neighbor] == _gray:
                cycle_members.add(neighbor)
                found = True
            elif color[neighbor] == _white:
                if dfs(neighbor):
                    found = True
        color[node] = _black
        return found

    for node in all_nodes:
        if color[node] == _white:
            dfs(node)

    if not cycle_members:
        return []

    # Fetch resources involved
    from uuid import UUID

    cycle_uuids = [UUID(cid) for cid in cycle_members]
    stmt = select(Resource).where(Resource.id.in_(cycle_uuids))
    result = await session.execute(stmt)
    resources = result.scalars().all()

    return [
        Finding(
            resource_id=r.id,
            finding_type=FindingType.circular_dep,
            severity=Severity.medium,
            category="architecture",
            message=f"Resource {r.external_id} is part of a dependency cycle",
            details={"external_id": r.external_id},
        )
        for r in resources
    ]


async def _detect_critical_nodes(session: AsyncSession) -> list[Finding]:
    """Resources with total relationships (in + out) >= threshold."""
    # Count outgoing
    out_counts = (
        select(
            Relationship.from_resource_id.label("resource_id"),
            func.count().label("cnt"),
        )
        .group_by(Relationship.from_resource_id)
        .subquery()
    )
    # Count incoming
    in_counts = (
        select(
            Relationship.to_resource_id.label("resource_id"),
            func.count().label("cnt"),
        )
        .group_by(Relationship.to_resource_id)
        .subquery()
    )

    # Join resource with both counts
    stmt = (
        select(
            Resource,
            (
                func.coalesce(out_counts.c.cnt, 0)
                + func.coalesce(in_counts.c.cnt, 0)
            ).label("total_edges"),
        )
        .outerjoin(out_counts, Resource.id == out_counts.c.resource_id)
        .outerjoin(in_counts, Resource.id == in_counts.c.resource_id)
        .having(
            (
                func.coalesce(out_counts.c.cnt, 0)
                + func.coalesce(in_counts.c.cnt, 0)
            )
            >= CRITICAL_NODE_THRESHOLD
        )
        .group_by(Resource.id, out_counts.c.cnt, in_counts.c.cnt)
    )
    result = await session.execute(stmt)
    rows = result.all()

    return [
        Finding(
            resource_id=r.id,
            finding_type=FindingType.critical_node,
            severity=Severity.info,
            category="architecture",
            message=f"Resource {r.external_id} is a critical node ({total} relationships)",
            details={
                "external_id": r.external_id,
                "total_edges": total,
            },
        )
        for r, total in rows
    ]
