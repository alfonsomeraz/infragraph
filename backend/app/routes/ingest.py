from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import IngestionRun
from app.db.session import get_session
from app.schemas.ingest import IngestionRunOut
from app.services.ingest_service import ingest_file

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/upload", response_model=IngestionRunOut, status_code=201)
async def upload(file: UploadFile, session: AsyncSession = Depends(get_session)):
    content = await file.read()
    try:
        run = await ingest_file(file.filename or "unknown", content, session)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return run


@router.get("/{run_id}", response_model=IngestionRunOut)
async def get_run(run_id: UUID, session: AsyncSession = Depends(get_session)):
    run = await session.get(IngestionRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Ingestion run not found")
    return run
