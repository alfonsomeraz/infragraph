from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Resource
from app.db.session import get_session
from app.schemas.resources import ResourceListOut, ResourceOut

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("", response_model=ResourceListOut)
async def list_resources(
    resource_type: str | None = None,
    provider: str | None = None,
    source: str | None = None,
    limit: int = Query(default=50, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Resource)
    if resource_type:
        stmt = stmt.where(Resource.resource_type == resource_type)
    if provider:
        stmt = stmt.where(Resource.provider == provider)
    if source:
        stmt = stmt.where(Resource.source == source)
    stmt = stmt.offset(offset).limit(limit)

    result = await session.execute(stmt)
    resources = list(result.scalars().all())
    return ResourceListOut(count=len(resources), resources=resources)


@router.get("/{resource_id}", response_model=ResourceOut)
async def get_resource(resource_id: UUID, session: AsyncSession = Depends(get_session)):
    resource = await session.get(Resource, resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource
