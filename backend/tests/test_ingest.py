"""Integration tests for the ingest route."""

import json
from pathlib import Path
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

PLAN_FIXTURE = Path(__file__).resolve().parent.parent.parent / "examples" / "terraform-plan.json"
STATE_FIXTURE = Path(__file__).resolve().parent.parent.parent / "examples" / "terraform-state.json"


async def test_upload_plan(db_session: AsyncSession, client: AsyncClient):
    content = PLAN_FIXTURE.read_bytes()
    resp = await client.post(
        "/api/ingest/upload",
        files={"file": ("plan.json", content, "application/json")},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "completed"
    assert data["source_type"] == "terraform_plan"
    assert data["resource_count"] == 16
    assert data["relationship_count"] == 16
    assert data["file_name"] == "plan.json"


async def test_upload_state(db_session: AsyncSession, client: AsyncClient):
    content = STATE_FIXTURE.read_bytes()
    resp = await client.post(
        "/api/ingest/upload",
        files={"file": ("state.json", content, "application/json")},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "completed"
    assert data["source_type"] == "terraform_state"
    assert data["resource_count"] == 14
    assert data["relationship_count"] == 14


async def test_upload_invalid_json(db_session: AsyncSession, client: AsyncClient):
    resp = await client.post(
        "/api/ingest/upload",
        files={"file": ("bad.json", b"not json", "application/json")},
    )
    assert resp.status_code == 400


async def test_upload_missing_keys(db_session: AsyncSession, client: AsyncClient):
    content = json.dumps({"terraform_version": "1.7.0"}).encode()
    resp = await client.post(
        "/api/ingest/upload",
        files={"file": ("empty.json", content, "application/json")},
    )
    assert resp.status_code == 400


async def test_get_run(db_session: AsyncSession, client: AsyncClient):
    content = PLAN_FIXTURE.read_bytes()
    upload_resp = await client.post(
        "/api/ingest/upload",
        files={"file": ("plan.json", content, "application/json")},
    )
    run_id = upload_resp.json()["id"]

    resp = await client.get(f"/api/ingest/{run_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == run_id
    assert resp.json()["status"] == "completed"


async def test_get_run_not_found(db_session: AsyncSession, client: AsyncClient):
    resp = await client.get(f"/api/ingest/{uuid4()}")
    assert resp.status_code == 404
