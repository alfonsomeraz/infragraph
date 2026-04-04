from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.graph import BlastRadiusOut, GraphOut
from app.services.graph_service import ResourceNotFoundError, get_blast_radius, get_resource_graph

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/{resource_id}", response_model=GraphOut)
async def graph(resource_id: UUID, session: AsyncSession = Depends(get_session)):
    try:
        return await get_resource_graph(resource_id, session)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{resource_id}/blast-radius", response_model=BlastRadiusOut)
async def blast_radius(
    resource_id: UUID,
    depth: int = Query(default=3, ge=1, le=10),
    session: AsyncSession = Depends(get_session),
):
    try:
        return await get_blast_radius(resource_id, depth, session)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
