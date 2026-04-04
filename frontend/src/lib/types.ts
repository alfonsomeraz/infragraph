// Enum string literal types (mirrors backend StrEnums)

export type SourceType = "terraform_plan" | "terraform_state" | "aws_live";

export type RelationshipType =
  | "runs_in"
  | "member_of"
  | "attached_to"
  | "grants_access_to"
  | "routes_to"
  | "encrypted_by"
  | "depends_on"
  | "created_by_module";

export type FindingType =
  | "orphan"
  | "drift"
  | "exposure"
  | "circular_dep"
  | "critical_node";

export type Severity = "info" | "low" | "medium" | "high" | "critical";

export type IngestionStatus = "running" | "completed" | "failed";

// Resource schemas

export interface ResourceOut {
  id: string;
  external_id: string;
  resource_type: string;
  name: string | null;
  provider: string | null;
  source: SourceType;
  attributes: Record<string, unknown> | null;
  tags: Record<string, string> | null;
  change_action: string | null;
  created_at: string;
}

export interface ResourceListOut {
  count: number;
  resources: ResourceOut[];
}

// Graph schemas

export interface GraphNodeOut {
  id: string;
  external_id: string;
  resource_type: string;
  name: string | null;
  provider: string | null;
  change_action: string | null;
}

export interface GraphEdgeOut {
  id: string;
  from_resource_id: string;
  to_resource_id: string;
  relationship_type: RelationshipType;
  confidence: number;
}

export interface GraphOut {
  nodes: GraphNodeOut[];
  edges: GraphEdgeOut[];
}

export interface BlastRadiusOut extends GraphOut {
  root_resource_id: string;
  depth: number;
  impact_count: number;
}

// Findings schemas

export interface FindingOut {
  id: string;
  resource_id: string;
  finding_type: FindingType;
  severity: Severity;
  category: string | null;
  message: string;
  details: Record<string, unknown> | null;
  created_at: string;
}

export interface FindingListOut {
  count: number;
  findings: FindingOut[];
}

// Ingestion schemas

export interface IngestionRunOut {
  id: string;
  source_type: SourceType;
  file_name: string | null;
  status: IngestionStatus;
  resource_count: number;
  relationship_count: number;
  started_at: string;
  completed_at: string | null;
}
