"""Shared relationship-inference logic for Terraform parsers."""

from __future__ import annotations

import re

from app.db.models import RelationshipType

from .models import ParsedRelationship, ParsedResource

# Maps attribute keys to (RelationshipType, confidence).
ATTR_RELATIONSHIP_MAP: dict[str, tuple[RelationshipType, float]] = {
    "subnet_id": (RelationshipType.runs_in, 1.0),
    "vpc_id": (RelationshipType.member_of, 1.0),
    "security_groups": (RelationshipType.attached_to, 0.9),
    "vpc_security_group_ids": (RelationshipType.attached_to, 0.9),
    "iam_instance_profile": (RelationshipType.grants_access_to, 0.9),
    "role": (RelationshipType.grants_access_to, 0.8),
    "execution_role_arn": (RelationshipType.grants_access_to, 0.9),
    "target_group_arn": (RelationshipType.routes_to, 1.0),
    "target_group_arns": (RelationshipType.routes_to, 1.0),
    "kms_key_id": (RelationshipType.encrypted_by, 1.0),
    "kms_master_key_id": (RelationshipType.encrypted_by, 1.0),
    "key_arn": (RelationshipType.encrypted_by, 1.0),
}


def normalize_address(address: str) -> str:
    """Canonicalize a Terraform resource address (strip index brackets)."""
    return re.sub(r'\["[^"]*"\]|\[\d+\]', "", address)


def infer_relationships(
    from_address: str,
    attributes: dict,
    known_addresses: set[str],
) -> list[ParsedRelationship]:
    """Scan attributes for references to known resources."""
    relationships: list[ParsedRelationship] = []
    for attr_key, (rel_type, confidence) in ATTR_RELATIONSHIP_MAP.items():
        value = attributes.get(attr_key)
        if value is None:
            continue
        targets = value if isinstance(value, list) else [value]
        for target in targets:
            if not isinstance(target, str):
                continue
            target_norm = normalize_address(target)
            if target_norm in known_addresses and target_norm != from_address:
                relationships.append(
                    ParsedRelationship(
                        from_address=from_address,
                        to_address=target_norm,
                        relationship_type=rel_type,
                        confidence=confidence,
                    )
                )
    return relationships


def resolve_module_relationships(
    resources: list[ParsedResource],
) -> list[ParsedRelationship]:
    """Emit created_by_module edges for resources that have a module_path."""
    relationships: list[ParsedRelationship] = []
    addresses = {r.external_id for r in resources}
    for resource in resources:
        if not resource.module_path:
            continue
        # Find the parent module resource (the module call itself) — we represent
        # this as an edge from the resource to the module namespace.
        # If no explicit module resource exists we skip.
        parent = resource.module_path
        if parent in addresses and parent != resource.external_id:
            relationships.append(
                ParsedRelationship(
                    from_address=resource.external_id,
                    to_address=parent,
                    relationship_type=RelationshipType.created_by_module,
                    confidence=1.0,
                )
            )
    return relationships
