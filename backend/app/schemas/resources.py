"""Pydantic response models for resources."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.db.models import SourceType


class ResourceOut(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    external_id: str
    resource_type: str
    name: str | None
    provider: str | None
    source: SourceType
    attributes: dict | None
    tags: dict | None
    change_action: str | None
    created_at: datetime


class ResourceListOut(BaseModel):
    count: int
    resources: list[ResourceOut]
