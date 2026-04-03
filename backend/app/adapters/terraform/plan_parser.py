"""Parse Terraform plan JSON (output of `terraform show -json <planfile>`)."""

from __future__ import annotations

import json
from pathlib import Path

from app.db.models import SourceType

from .models import ParsedResource, ParseResult
from .reference_resolver import infer_relationships, normalize_address, resolve_module_relationships

# Map multi-element action lists to a single canonical action.
_ACTION_MAP: dict[tuple[str, ...], str] = {
    ("create",): "create",
    ("delete",): "delete",
    ("update",): "update",
    ("delete", "create"): "replace",
    ("create", "delete"): "replace",
    ("read",): "read",
    ("no-op",): "no-op",
}


def _normalize_action(actions: list[str]) -> str:
    return _ACTION_MAP.get(tuple(actions), ",".join(actions))


def _extract_provider(provider_name: str) -> str:
    """Extract short provider name from fully-qualified provider string.

    e.g. 'registry.terraform.io/hashicorp/aws' -> 'aws'
    """
    return provider_name.rsplit("/", 1)[-1] if provider_name else ""


def parse_plan(source: str | bytes | Path) -> ParseResult:
    """Parse a Terraform plan JSON file into normalized resources + relationships."""
    if isinstance(source, Path):
        raw = source.read_text()
    elif isinstance(source, bytes):
        raw = source.decode()
    else:
        raw = source

    data = json.loads(raw)
    if "resource_changes" not in data:
        raise ValueError("Invalid Terraform plan JSON: missing 'resource_changes' key")

    resources: list[ParsedResource] = []
    warnings: list[str] = []

    for rc in data["resource_changes"]:
        address = normalize_address(rc.get("address", ""))
        change = rc.get("change", {})
        actions = change.get("actions", [])
        action = _normalize_action(actions)

        # Prefer after (the planned state); fall back to before (for deletes).
        attrs = change.get("after") or change.get("before") or {}

        # Extract tags from attributes if present.
        tags = {}
        if isinstance(attrs.get("tags"), dict):
            tags = attrs["tags"]
        elif isinstance(attrs.get("tags_all"), dict):
            tags = attrs["tags_all"]

        resource = ParsedResource(
            external_id=address,
            resource_type=rc.get("type", ""),
            name=rc.get("name", ""),
            provider=_extract_provider(rc.get("provider_name", "")),
            module_path=rc.get("module_address"),
            change_action=action,
            attributes=attrs,
            tags=tags,
        )
        resources.append(resource)

    # Build known address set for relationship inference.
    known = {r.external_id for r in resources}

    relationships = []
    for r in resources:
        relationships.extend(infer_relationships(r.external_id, r.attributes, known))
    relationships.extend(resolve_module_relationships(resources))

    return ParseResult(
        source_type=SourceType.terraform_plan,
        resources=resources,
        relationships=relationships,
        warnings=warnings,
    )
