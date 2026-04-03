"""Tests for the Terraform plan parser."""

from pathlib import Path

import pytest

from app.adapters.terraform.plan_parser import parse_plan
from app.db.models import RelationshipType, SourceType

FIXTURE = Path(__file__).resolve().parent.parent.parent / "examples" / "terraform-plan.json"


@pytest.fixture
def result():
    return parse_plan(FIXTURE)


# --- Resource extraction ---


def test_resource_count(result):
    assert len(result.resources) == 16


def test_source_type(result):
    assert result.source_type == SourceType.terraform_plan


def test_resource_types_extracted(result):
    types = {r.resource_type for r in result.resources}
    assert "aws_vpc" in types
    assert "aws_instance" in types
    assert "aws_db_instance" in types


def test_provider_parsed(result):
    vpc = next(r for r in result.resources if r.resource_type == "aws_vpc")
    assert vpc.provider == "aws"


def test_module_paths(result):
    vpc = next(r for r in result.resources if r.name == "main" and r.resource_type == "aws_vpc")
    assert vpc.module_path == "module.network"
    web = next(
        r for r in result.resources if r.name == "web" and r.resource_type == "aws_instance"
    )
    assert web.module_path == "module.compute"


def test_action_create(result):
    vpc = next(r for r in result.resources if r.resource_type == "aws_vpc")
    assert vpc.change_action == "create"


def test_action_replace(result):
    worker = next(r for r in result.resources if r.name == "old_worker")
    assert worker.change_action == "replace"


def test_action_delete(result):
    dep = next(r for r in result.resources if r.name == "deprecated")
    assert dep.change_action == "delete"


def test_delete_uses_before_attrs(result):
    dep = next(r for r in result.resources if r.name == "deprecated")
    assert dep.attributes["ami"] == "ami-old"


def test_tags_extracted(result):
    vpc = next(r for r in result.resources if r.resource_type == "aws_vpc")
    assert vpc.tags["Name"] == "main-vpc"


# --- Relationship inference ---


def test_runs_in_relationship(result):
    rels = [
        r
        for r in result.relationships
        if r.relationship_type == RelationshipType.runs_in
        and r.from_address == "module.compute.aws_instance.web"
    ]
    assert any(r.to_address == "module.network.aws_subnet.private" for r in rels)


def test_member_of_relationship(result):
    rels = [
        r
        for r in result.relationships
        if r.relationship_type == RelationshipType.member_of
        and r.from_address == "module.network.aws_subnet.private"
    ]
    assert any(r.to_address == "module.network.aws_vpc.main" for r in rels)


def test_attached_to_relationship(result):
    rels = [
        r
        for r in result.relationships
        if r.relationship_type == RelationshipType.attached_to
        and r.from_address == "module.compute.aws_instance.web"
    ]
    assert any(r.to_address == "module.network.aws_security_group.web" for r in rels)


def test_grants_access_to_relationship(result):
    rels = [
        r
        for r in result.relationships
        if r.relationship_type == RelationshipType.grants_access_to
        and r.from_address == "module.compute.aws_instance.web"
    ]
    assert any(
        r.to_address == "module.compute.aws_iam_instance_profile.web" for r in rels
    )


def test_routes_to_relationship(result):
    rels = [
        r
        for r in result.relationships
        if r.relationship_type == RelationshipType.routes_to
        and r.from_address == "module.lb.aws_lb_listener.http"
    ]
    assert any(r.to_address == "module.lb.aws_lb_target_group.web" for r in rels)


def test_encrypted_by_relationship(result):
    rels = [
        r
        for r in result.relationships
        if r.relationship_type == RelationshipType.encrypted_by
        and r.from_address == "module.data.aws_db_instance.postgres"
    ]
    assert any(r.to_address == "module.data.aws_kms_key.db_key" for r in rels)


def test_no_self_relationships(result):
    for rel in result.relationships:
        assert rel.from_address != rel.to_address


def test_all_edges_reference_known_resources(result):
    addresses = {r.external_id for r in result.resources}
    for rel in result.relationships:
        assert rel.from_address in addresses, f"from_address {rel.from_address} not in resources"
        assert rel.to_address in addresses, f"to_address {rel.to_address} not in resources"


# --- Parse from different input types ---


def test_parse_from_string():
    text = FIXTURE.read_text()
    result = parse_plan(text)
    assert len(result.resources) == 16


def test_parse_from_bytes():
    raw = FIXTURE.read_bytes()
    result = parse_plan(raw)
    assert len(result.resources) == 16


# --- Error handling ---


def test_missing_resource_changes_key():
    with pytest.raises(ValueError, match="resource_changes"):
        parse_plan('{"terraform_version": "1.7.0"}')
