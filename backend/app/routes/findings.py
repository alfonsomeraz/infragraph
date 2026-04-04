from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Finding, FindingType, Severity
from app.db.session import get_session
from app.schemas.findings import FindingListOut, FindingOut
from app.services import findings_service

router = APIRouter(prefix="/findings", tags=["findings"])


@router.post("/scan", response_model=FindingListOut, status_code=200)
async def scan(session: AsyncSession = Depends(get_session)):
    results = await findings_service.run_detection(session)
    return FindingListOut(
        count=len(results),
        findings=[FindingOut.model_validate(f) for f in results],
    )


@router.get("", response_model=FindingListOut)
async def list_findings(
    finding_type: FindingType | None = None,
    severity: Severity | None = None,
    resource_id: UUID | None = None,
    limit: int = Query(default=50, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Finding)
    if finding_type:
        stmt = stmt.where(Finding.finding_type == finding_type)
    if severity:
        stmt = stmt.where(Finding.severity == severity)
    if resource_id:
        stmt = stmt.where(Finding.resource_id == resource_id)
    stmt = stmt.offset(offset).limit(limit)

    result = await session.execute(stmt)
    findings = list(result.scalars().all())
    return FindingListOut(count=len(findings), findings=findings)


@router.get("/{finding_id}", response_model=FindingOut)
async def get_finding(finding_id: UUID, session: AsyncSession = Depends(get_session)):
    finding = await session.get(Finding, finding_id)
    if finding is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding
