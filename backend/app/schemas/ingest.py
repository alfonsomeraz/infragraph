"""Pydantic response models for ingestion runs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.db.models import IngestionStatus, SourceType


class IngestionRunOut(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    source_type: SourceType
    file_name: str | None
    status: IngestionStatus
    resource_count: int
    relationship_count: int
    started_at: datetime
    completed_at: datetime | None
