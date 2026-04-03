import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# --- Enums ---


class SourceType(enum.StrEnum):
    terraform_plan = "terraform_plan"
    terraform_state = "terraform_state"
    aws_live = "aws_live"


class RelationshipType(enum.StrEnum):
    runs_in = "runs_in"
    member_of = "member_of"
    attached_to = "attached_to"
    grants_access_to = "grants_access_to"
    routes_to = "routes_to"
    encrypted_by = "encrypted_by"
    depends_on = "depends_on"
    created_by_module = "created_by_module"


class FindingType(enum.StrEnum):
    orphan = "orphan"
    drift = "drift"
    exposure = "exposure"
    circular_dep = "circular_dep"
    critical_node = "critical_node"


class Severity(enum.StrEnum):
    info = "info"
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class IngestionStatus(enum.StrEnum):
    running = "running"
    completed = "completed"
    failed = "failed"


# --- Models ---


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String(512), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(256), nullable=False)
    name: Mapped[str | None] = mapped_column(String(512))
    provider: Mapped[str | None] = mapped_column(String(64))
    source: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    attributes: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    tags: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    region: Mapped[str | None] = mapped_column(String(64))
    account_id: Mapped[str | None] = mapped_column(String(64))
    change_action: Mapped[str | None] = mapped_column(String(32))
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    outgoing_relationships: Mapped[list["Relationship"]] = relationship(
        back_populates="from_resource", foreign_keys="Relationship.from_resource_id"
    )
    incoming_relationships: Mapped[list["Relationship"]] = relationship(
        back_populates="to_resource", foreign_keys="Relationship.to_resource_id"
    )
    findings: Mapped[list["Finding"]] = relationship(back_populates="resource")

    __table_args__ = (
        Index("ix_resources_external_id_type", "external_id", "resource_type"),
        Index("ix_resources_resource_type", "resource_type"),
        Index("ix_resources_source", "source"),
    )


class Relationship(Base):
    __tablename__ = "relationships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_resource_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False
    )
    to_resource_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False
    )
    relationship_type: Mapped[RelationshipType] = mapped_column(
        Enum(RelationshipType), nullable=False
    )
    source: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    attributes: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    from_resource: Mapped["Resource"] = relationship(
        back_populates="outgoing_relationships", foreign_keys=[from_resource_id]
    )
    to_resource: Mapped["Resource"] = relationship(
        back_populates="incoming_relationships", foreign_keys=[to_resource_id]
    )

    __table_args__ = (
        Index("ix_relationships_from", "from_resource_id"),
        Index("ix_relationships_to", "to_resource_id"),
        Index("ix_relationships_type", "relationship_type"),
    )


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    file_name: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[IngestionStatus] = mapped_column(
        Enum(IngestionStatus), default=IngestionStatus.running
    )
    resource_count: Mapped[int] = mapped_column(Integer, default=0)
    relationship_count: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False
    )
    finding_type: Mapped[FindingType] = mapped_column(Enum(FindingType), nullable=False)
    severity: Mapped[Severity] = mapped_column(Enum(Severity), nullable=False)
    category: Mapped[str | None] = mapped_column(String(128))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    resource: Mapped["Resource"] = relationship(back_populates="findings")

    __table_args__ = (
        Index("ix_findings_resource_id", "resource_id"),
        Index("ix_findings_type", "finding_type"),
        Index("ix_findings_severity", "severity"),
    )
