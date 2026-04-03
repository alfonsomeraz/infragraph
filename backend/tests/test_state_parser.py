"""Tests for the Terraform state parser."""

from pathlib import Path

import pytest

from app.adapters.terraform.state_parser import parse_state
from app.db.models import RelationshipType, SourceType

FIXTURE = Path(__file__).resolve().parent.parent.parent / "examples" / "terraform-state.json"


@pytest.fixture
def result():
    return parse_state(FIXTURE)


# --- Resource extraction ---


def test_resource_count(result):
    # 5 network + 3 compute + 3 data + 3 lb = 14
    assert len(result.resources) == 14


def test_source_type(result):
    assert result.source_type == SourceType.terraform_state


def test_no_change_action(result):
    for r in result.resources:
        assert r.change_action is None


def test_nested_modules_collected(result):
    modules = {r.module_path for r in result.resources}
    assert "module.network" in modules
    assert "module.compute" in modules
    assert "module.data" in modules
    assert "module.lb" in modules


def test_provider_parsed(result):
    vpc = next(r for r in result.resources if r.resource_type == "aws_vpc")
    assert vpc.provider == "aws"


def test_tags_extracted(result):
    vpc = next(r for r in result.resources if r.resource_type == "aws_vpc")
    assert vpc.tags["Name"] == "main-vpc"


# --- Relationship inference ---


def test_relationships_inferred(result):
    assert len(result.relationships) > 0
    types = {r.relationship_type for r in result.relationships}
    assert RelationshipType.runs_in in types
    assert RelationshipType.member_of in types
    assert RelationshipType.encrypted_by in types


def test_no_self_relationships(result):
    for rel in result.relationships:
        assert rel.from_address != rel.to_address


def test_all_edges_reference_known_resources(result):
    addresses = {r.external_id for r in result.resources}
    for rel in result.relationships:
        assert rel.from_address in addresses
        assert rel.to_address in addresses


# --- Error handling ---


def test_missing_values_key():
    with pytest.raises(ValueError, match="values"):
        parse_state('{"terraform_version": "1.7.0"}')


# --- Parse from different input types ---


def test_parse_from_string():
    text = FIXTURE.read_text()
    result = parse_state(text)
    assert len(result.resources) == 14


def test_parse_from_bytes():
    raw = FIXTURE.read_bytes()
    result = parse_state(raw)
    assert len(result.resources) == 14
