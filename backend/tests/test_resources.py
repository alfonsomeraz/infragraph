"""Integration tests for the resources route."""

from pathlib import Path
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

PLAN_FIXTURE = Path(__file__).resolve().parent.parent.parent / "examples" / "terraform-plan.json"


async def _ingest_plan(client: AsyncClient) -> dict:
    content = PLAN_FIXTURE.read_bytes()
    resp = await client.post(
        "/api/ingest/upload",
        files={"file": ("plan.json", content, "application/json")},
    )
    return resp.json()


async def test_list_resources(db_session: AsyncSession, client: AsyncClient):
    await _ingest_plan(client)
    resp = await client.get("/api/resources")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 16
    assert len(data["resources"]) == 16


async def test_filter_by_resource_type(db_session: AsyncSession, client: AsyncClient):
    await _ingest_plan(client)
    resp = await client.get("/api/resources", params={"resource_type": "aws_vpc"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 1
    for r in data["resources"]:
        assert r["resource_type"] == "aws_vpc"


async def test_get_single_resource(db_session: AsyncSession, client: AsyncClient):
    await _ingest_plan(client)
    list_resp = await client.get("/api/resources", params={"limit": 1})
    resource_id = list_resp.json()["resources"][0]["id"]

    resp = await client.get(f"/api/resources/{resource_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == resource_id


async def test_get_resource_not_found(db_session: AsyncSession, client: AsyncClient):
    resp = await client.get(f"/api/resources/{uuid4()}")
    assert resp.status_code == 404
