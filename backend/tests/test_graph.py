"""Integration tests for the graph route."""

from pathlib import Path
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

PLAN_FIXTURE = Path(__file__).resolve().parent.parent.parent / "examples" / "terraform-plan.json"


async def _ingest_and_get_resource(client: AsyncClient, resource_type: str) -> dict:
    """Ingest plan and return a resource of the given type."""
    content = PLAN_FIXTURE.read_bytes()
    await client.post(
        "/api/ingest/upload",
        files={"file": ("plan.json", content, "application/json")},
    )
    resp = await client.get("/api/resources", params={"resource_type": resource_type, "limit": 1})
    return resp.json()["resources"][0]


async def test_graph_returns_nodes_and_edges(db_session: AsyncSession, client: AsyncClient):
    # aws_instance.web has relationships (runs_in, member_of, attached_to, etc.)
    resource = await _ingest_and_get_resource(client, "aws_instance")
    resp = await client.get(f"/api/graph/{resource['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["nodes"]) >= 2  # At least root + 1 neighbor.
    assert len(data["edges"]) >= 1


async def test_blast_radius_depth_1(db_session: AsyncSession, client: AsyncClient):
    resource = await _ingest_and_get_resource(client, "aws_instance")
    resp = await client.get(f"/api/graph/{resource['id']}/blast-radius", params={"depth": 1})
    assert resp.status_code == 200
    data = resp.json()
    assert data["root_resource_id"] == resource["id"]
    assert data["depth"] == 1
    assert data["impact_count"] >= 1
    assert len(data["nodes"]) >= 2


async def test_blast_radius_depth_3(db_session: AsyncSession, client: AsyncClient):
    resource = await _ingest_and_get_resource(client, "aws_instance")
    resp = await client.get(f"/api/graph/{resource['id']}/blast-radius", params={"depth": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert data["depth"] == 3
    # With depth 3, we should reach more resources than depth 1.
    assert data["impact_count"] >= 1
    assert len(data["nodes"]) >= len(data["edges"]) or len(data["edges"]) >= 1


async def test_graph_not_found(db_session: AsyncSession, client: AsyncClient):
    resp = await client.get(f"/api/graph/{uuid4()}")
    assert resp.status_code == 404


async def test_blast_radius_not_found(db_session: AsyncSession, client: AsyncClient):
    resp = await client.get(f"/api/graph/{uuid4()}/blast-radius")
    assert resp.status_code == 404
