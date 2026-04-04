"""Pydantic response models for graph and blast-radius queries."""

from uuid import UUID

from pydantic import BaseModel

from app.db.models import RelationshipType


class GraphNodeOut(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    external_id: str
    resource_type: str
    name: str | None
    provider: str | None
    change_action: str | None


class GraphEdgeOut(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    from_resource_id: UUID
    to_resource_id: UUID
    relationship_type: RelationshipType
    confidence: float


class GraphOut(BaseModel):
    nodes: list[GraphNodeOut]
    edges: list[GraphEdgeOut]


class BlastRadiusOut(GraphOut):
    root_resource_id: UUID
    depth: int
    impact_count: int
