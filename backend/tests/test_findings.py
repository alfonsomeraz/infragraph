"""Integration tests for the findings engine and routes."""

from pathlib import Path
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

PLAN_FIXTURE = Path(__file__).resolve().parent.parent.parent / "examples" / "terraform-plan.json"


@pytest.fixture
async def ingested(db_session: AsyncSession, client: AsyncClient):
    """Ingest the plan fixture so resources + relationships exist."""
    content = PLAN_FIXTURE.read_bytes()
    resp = await client.post(
        "/api/ingest/upload",
        files={"file": ("plan.json", content, "application/json")},
    )
    assert resp.status_code == 201
    return resp.json()


async def test_scan_creates_findings(
    db_session: AsyncSession, client: AsyncClient, ingested
):
    resp = await client.post("/api/findings/scan")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] > 0
    assert len(data["findings"]) == data["count"]


async def test_drift_detection(
    db_session: AsyncSession, client: AsyncClient, ingested
):
    resp = await client.post("/api/findings/scan")
    data = resp.json()
    drift = [f for f in data["findings"] if f["finding_type"] == "drift"]
    # old_worker (replace) + deprecated (delete)
    assert len(drift) == 2

    messages = " ".join(f["message"] for f in drift)
    assert "deprecated" in messages
    assert "old_worker" in messages

    severities = {f["severity"] for f in drift}
    assert "high" in severities  # delete
    assert "medium" in severities  # replace


async def test_exposure_detection(
    db_session: AsyncSession, client: AsyncClient, ingested
):
    resp = await client.post("/api/findings/scan")
    data = resp.json()
    exposure = [f for f in data["findings"] if f["finding_type"] == "exposure"]

    messages = " ".join(f["message"] for f in exposure)
    # aws_lb.main internal=false
    assert "aws_lb.main" in messages or "Public load balancer" in messages
    # aws_lb_listener.http HTTP protocol
    assert "aws_lb_listener.http" in messages or "HTTP" in messages


async def test_critical_node_detection(
    db_session: AsyncSession, client: AsyncClient, ingested
):
    resp = await client.post("/api/findings/scan")
    data = resp.json()
    critical = [f for f in data["findings"] if f["finding_type"] == "critical_node"]
    # aws_vpc.main has many relationships
    assert len(critical) >= 1
    messages = " ".join(f["message"] for f in critical)
    assert "aws_vpc.main" in messages


async def test_list_findings(
    db_session: AsyncSession, client: AsyncClient, ingested
):
    await client.post("/api/findings/scan")
    resp = await client.get("/api/findings")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] > 0


async def test_filter_by_type(
    db_session: AsyncSession, client: AsyncClient, ingested
):
    await client.post("/api/findings/scan")
    resp = await client.get("/api/findings?finding_type=drift")
    assert resp.status_code == 200
    data = resp.json()
    assert all(f["finding_type"] == "drift" for f in data["findings"])
    assert data["count"] == 2


async def test_filter_by_severity(
    db_session: AsyncSession, client: AsyncClient, ingested
):
    await client.post("/api/findings/scan")
    resp = await client.get("/api/findings?severity=high")
    assert resp.status_code == 200
    data = resp.json()
    assert all(f["severity"] == "high" for f in data["findings"])


async def test_get_single_finding(
    db_session: AsyncSession, client: AsyncClient, ingested
):
    scan_resp = await client.post("/api/findings/scan")
    finding_id = scan_resp.json()["findings"][0]["id"]

    resp = await client.get(f"/api/findings/{finding_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == finding_id


async def test_get_finding_not_found(
    db_session: AsyncSession, client: AsyncClient, ingested
):
    resp = await client.get(f"/api/findings/{uuid4()}")
    assert resp.status_code == 404


async def test_scan_idempotent(
    db_session: AsyncSession, client: AsyncClient, ingested
):
    resp1 = await client.post("/api/findings/scan")
    count1 = resp1.json()["count"]

    resp2 = await client.post("/api/findings/scan")
    count2 = resp2.json()["count"]

    # Second scan replaces findings, count should be the same, not doubled
    assert count1 == count2

    # Verify via GET that total matches
    list_resp = await client.get("/api/findings")
    assert list_resp.json()["count"] == count1
