"""Parse Terraform state JSON (output of `terraform show -json terraform.tfstate`)."""

from __future__ import annotations

import json
from pathlib import Path

from app.db.models import SourceType

from .models import ParsedResource, ParseResult
from .reference_resolver import infer_relationships, normalize_address, resolve_module_relationships


def _extract_provider(provider: str) -> str:
    """Extract short provider name from fully-qualified provider string."""
    return provider.rsplit("/", 1)[-1] if provider else ""


def _collect_resources(
    module: dict,
    module_path: str | None = None,
) -> list[ParsedResource]:
    """Recursively collect resources from a module and its children."""
    resources: list[ParsedResource] = []

    for r in module.get("resources", []):
        address = normalize_address(r.get("address", ""))
        attrs = r.get("values", {})

        tags = {}
        if isinstance(attrs.get("tags"), dict):
            tags = attrs["tags"]
        elif isinstance(attrs.get("tags_all"), dict):
            tags = attrs["tags_all"]

        resources.append(
            ParsedResource(
                external_id=address,
                resource_type=r.get("type", ""),
                name=r.get("name", ""),
                provider=_extract_provider(r.get("provider_name", "")),
                module_path=module_path,
                change_action=None,
                attributes=attrs,
                tags=tags,
            )
        )

    for child in module.get("child_modules", []):
        child_path = child.get("address", module_path)
        resources.extend(_collect_resources(child, module_path=child_path))

    return resources


def parse_state(source: str | bytes | Path) -> ParseResult:
    """Parse a Terraform state JSON file into normalized resources + relationships."""
    if isinstance(source, Path):
        raw = source.read_text()
    elif isinstance(source, bytes):
        raw = source.decode()
    else:
        raw = source

    data = json.loads(raw)
    if "values" not in data:
        raise ValueError("Invalid Terraform state JSON: missing 'values' key")

    root_module = data["values"].get("root_module", {})
    resources = _collect_resources(root_module)

    known = {r.external_id for r in resources}
    relationships = []
    for r in resources:
        relationships.extend(infer_relationships(r.external_id, r.attributes, known))
    relationships.extend(resolve_module_relationships(resources))

    return ParseResult(
        source_type=SourceType.terraform_state,
        resources=resources,
        relationships=relationships,
    )
