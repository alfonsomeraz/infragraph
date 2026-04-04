"""Ingestion orchestration — parse Terraform JSON and persist to DB."""

from __future__ import annotations

import json

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.terraform.plan_parser import parse_plan
from app.adapters.terraform.state_parser import parse_state
from app.db.models import IngestionRun, IngestionStatus, Relationship, Resource, SourceType


def _detect_source_type(data: dict) -> SourceType:
    """Auto-detect whether the JSON is a Terraform plan or state."""
    if "resource_changes" in data:
        return SourceType.terraform_plan
    if "values" in data:
        return SourceType.terraform_state
    raise ValueError(
        "Unrecognized Terraform JSON: must contain 'resource_changes' (plan) or 'values' (state)"
    )


async def ingest_file(
    file_name: str,
    content: bytes,
    session: AsyncSession,
) -> IngestionRun:
    """Parse a Terraform JSON file and persist resources + relationships."""
    # Validate JSON first.
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc

    source_type = _detect_source_type(data)

    run = IngestionRun(
        source_type=source_type,
        file_name=file_name,
        status=IngestionStatus.running,
    )
    session.add(run)
    await session.flush()

    try:
        if source_type == SourceType.terraform_plan:
            result = parse_plan(content)
        else:
            result = parse_state(content)

        # Build Resource ORM objects and track address → UUID mapping.
        address_to_resource: dict[str, Resource] = {}
        resources = []
        for pr in result.resources:
            resource = Resource(
                external_id=pr.external_id,
                resource_type=pr.resource_type,
                name=pr.name,
                provider=pr.provider,
                source=source_type,
                attributes=pr.attributes,
                tags=pr.tags,
                change_action=pr.change_action,
            )
            resources.append(resource)
            address_to_resource[pr.external_id] = resource

        session.add_all(resources)
        await session.flush()  # Generates UUIDs for resources.

        # Build Relationship ORM objects, resolving addresses to DB UUIDs.
        relationships = []
        for pr in result.relationships:
            from_res = address_to_resource.get(pr.from_address)
            to_res = address_to_resource.get(pr.to_address)
            if from_res is None or to_res is None:
                continue  # Skip unresolvable edges.
            relationships.append(
                Relationship(
                    from_resource_id=from_res.id,
                    to_resource_id=to_res.id,
                    relationship_type=pr.relationship_type,
                    source=source_type,
                    confidence=pr.confidence,
                )
            )

        session.add_all(relationships)
        await session.flush()

        run.resource_count = len(resources)
        run.relationship_count = len(relationships)
        run.status = IngestionStatus.completed
        run.completed_at = func.now()
        await session.commit()
        await session.refresh(run)

    except Exception:
        run.status = IngestionStatus.failed
        run.completed_at = func.now()
        await session.commit()
        await session.refresh(run)
        raise

    return run
