"""Pydantic response models for findings."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.db.models import FindingType, Severity


class FindingOut(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    resource_id: UUID
    finding_type: FindingType
    severity: Severity
    category: str | None
    message: str
    details: dict | None
    created_at: datetime


class FindingListOut(BaseModel):
    count: int
    findings: list[FindingOut]
