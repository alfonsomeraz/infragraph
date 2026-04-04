"""Graph traversal and blast-radius services."""

from __future__ import annotations

from collections import deque
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import Relationship, Resource
from app.schemas.graph import BlastRadiusOut, GraphEdgeOut, GraphNodeOut, GraphOut


async def _get_resource_or_404(resource_id: UUID, session: AsyncSession) -> Resource:
    resource = await session.get(Resource, resource_id)
    if resource is None:
        raise ResourceNotFoundError(resource_id)
    return resource


class ResourceNotFoundError(Exception):
    def __init__(self, resource_id: UUID):
        self.resource_id = resource_id
        super().__init__(f"Resource {resource_id} not found")


async def get_resource_graph(
    resource_id: UUID,
    session: AsyncSession,
) -> GraphOut:
    """Return 1-hop neighborhood graph for a resource."""
    root = await _get_resource_or_404(resource_id, session)

    # Fetch all relationships where this resource is from or to.
    stmt = select(Relationship).where(
        or_(
            Relationship.from_resource_id == resource_id,
            Relationship.to_resource_id == resource_id,
        )
    )
    result = await session.execute(stmt)
    edges = list(result.scalars().all())

    # Collect IDs of neighboring resources.
    neighbor_ids: set[UUID] = set()
    for edge in edges:
        neighbor_ids.add(edge.from_resource_id)
        neighbor_ids.add(edge.to_resource_id)
    neighbor_ids.discard(resource_id)

    # Fetch neighbor resources.
    neighbors: list[Resource] = []
    if neighbor_ids:
        stmt = select(Resource).where(Resource.id.in_(neighbor_ids))
        result = await session.execute(stmt)
        neighbors = list(result.scalars().all())

    all_resources = [root, *neighbors]

    return GraphOut(
        nodes=[GraphNodeOut.model_validate(r) for r in all_resources],
        edges=[GraphEdgeOut.model_validate(e) for e in edges],
    )


async def get_blast_radius(
    resource_id: UUID,
    depth: int,
    session: AsyncSession,
) -> BlastRadiusOut:
    """BFS from resource outward through relationships up to `depth` hops."""
    depth = min(depth, settings.blast_radius_max_depth)

    await _get_resource_or_404(resource_id, session)

    visited_ids: set[UUID] = {resource_id}
    all_edges: list[Relationship] = []
    queue: deque[tuple[UUID, int]] = deque([(resource_id, 0)])

    while queue:
        current_id, current_depth = queue.popleft()
        if current_depth >= depth:
            continue

        stmt = select(Relationship).where(
            or_(
                Relationship.from_resource_id == current_id,
                Relationship.to_resource_id == current_id,
            )
        )
        result = await session.execute(stmt)
        edges = list(result.scalars().all())

        for edge in edges:
            all_edges.append(edge)
            neighbor_id = (
                edge.to_resource_id
                if edge.from_resource_id == current_id
                else edge.from_resource_id
            )
            if neighbor_id not in visited_ids:
                visited_ids.add(neighbor_id)
                queue.append((neighbor_id, current_depth + 1))

    # Fetch all visited resources.
    resources: list[Resource] = []
    if visited_ids:
        stmt = select(Resource).where(Resource.id.in_(visited_ids))
        result = await session.execute(stmt)
        resources = list(result.scalars().all())

    # Deduplicate edges by id.
    seen_edge_ids: set[UUID] = set()
    unique_edges: list[Relationship] = []
    for edge in all_edges:
        if edge.id not in seen_edge_ids:
            seen_edge_ids.add(edge.id)
            unique_edges.append(edge)

    return BlastRadiusOut(
        root_resource_id=resource_id,
        depth=depth,
        impact_count=len(visited_ids) - 1,  # Exclude root.
        nodes=[GraphNodeOut.model_validate(r) for r in resources],
        edges=[GraphEdgeOut.model_validate(e) for e in unique_edges],
    )
