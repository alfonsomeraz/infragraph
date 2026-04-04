"""Pydantic response models for relationships."""

from uuid import UUID

from pydantic import BaseModel

from app.db.models import RelationshipType


class RelationshipOut(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    from_resource_id: UUID
    to_resource_id: UUID
    relationship_type: RelationshipType
    confidence: float
