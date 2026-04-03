"""Parser DTOs — decoupled from SQLAlchemy ORM models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.db.models import RelationshipType, SourceType


class ParsedResource(BaseModel):
    external_id: str
    resource_type: str
    name: str
    provider: str | None = None
    module_path: str | None = None
    change_action: str | None = None
    attributes: dict = Field(default_factory=dict)
    tags: dict = Field(default_factory=dict)


class ParsedRelationship(BaseModel):
    from_address: str
    to_address: str
    relationship_type: RelationshipType
    confidence: float = 1.0


class ParseResult(BaseModel):
    source_type: SourceType
    resources: list[ParsedResource] = Field(default_factory=list)
    relationships: list[ParsedRelationship] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
