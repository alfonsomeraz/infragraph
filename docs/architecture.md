# Architecture

## Overview

InfraGraph is a three-tier application:

```
┌──────────────────────────────────────────────────────────────┐
│                         Clients                              │
│   Browser (Next.js)          Terminal (infragraph CLI)       │
└──────────────┬───────────────────────┬───────────────────────┘
               │ HTTP                  │ HTTP
               ▼                       ▼
┌──────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (:8000)                    │
│                                                              │
│   /api/ingest     /api/resources   /api/graph  /api/findings │
│        │                │               │            │       │
│        └────────────────┴───────────────┴────────────┘       │
│                          Services                            │
│          ingest_service  graph_service  findings_service      │
│                │                                             │
│          Adapters (Terraform plan/state parsers)             │
└──────────────────────────────┬───────────────────────────────┘
                               │ asyncpg
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                    PostgreSQL 16 (:5432)                      │
│   resources  relationships  ingestion_runs  findings         │
└──────────────────────────────────────────────────────────────┘
```

---

## Backend

### Entry point

`backend/app/main.py` creates the FastAPI app and mounts all routers under `/api`.

### Routers (`app/routes/`)

| Router | Prefix | Responsibility |
|--------|--------|----------------|
| `ingest` | `/api/ingest` | File upload, run status |
| `resources` | `/api/resources` | Resource list + detail |
| `graph` | `/api/graph` | Dependency graph + blast radius |
| `findings` | `/api/findings` | Finding list, detail, scan trigger |

### Services (`app/services/`)

**`ingest_service.py`**
Orchestrates the full parse-and-store flow:
1. Detect source type (plan vs state) from the JSON structure
2. Delegate to the appropriate adapter parser
3. Resolve cross-resource references via `reference_resolver`
4. Persist `Resource` rows, `Relationship` edges, and the `IngestionRun` record in a single transaction

**`graph_service.py`**
- `get_graph(resource_id)` — fetches the resource and all 1-hop neighbors (resources connected by any edge)
- `get_blast_radius(resource_id, depth)` — BFS traversal up to `depth` hops; returns all reachable nodes and the edges that connect them

**`findings_service.py`**
Runs five independent detectors in sequence:

| Detector | Finding type | Logic |
|----------|-------------|-------|
| Orphan | `orphan` | Resources with no relationships |
| Drift | `drift` | Resources with `change_action` not `no-op` or `null` |
| Exposure | `exposure` | Resources whose `attributes` contain insecure flags (`encrypted=false`, open CIDR `0.0.0.0/0`) |
| Circular dep | `circular_dep` | DFS cycle detection over the full relationship graph |
| Critical node | `critical_node` | Resources with degree ≥ threshold (default: 5 edges) |

### Adapters (`app/adapters/terraform/`)

**`plan_parser.py`**
Parses `terraform show -json` output. Iterates `planned_values.root_module.resources` and `resource_changes` to capture change actions.

**`state_parser.py`**
Parses `terraform state pull` output. Iterates `values.root_module.resources`.

**`reference_resolver.py`**
Scans each resource's attributes for known reference fields (`subnet_id`, `vpc_id`, `security_group_ids`, `security_groups`, `load_balancer_arn`, `target_group_arns`, `instance_id`, `role_arn`, `bucket_name`, etc.) and creates typed `Relationship` rows linking source → target by `external_id`.

### Data model

```
resources
  id UUID PK
  external_id TEXT          -- Terraform address (e.g. aws_instance.web)
  name TEXT
  resource_type TEXT        -- e.g. aws_instance
  provider TEXT             -- e.g. aws
  source_type SourceType    -- plan | state
  change_action TEXT        -- create | update | delete | no-op
  attributes JSONB
  tags JSONB
  ingestion_run_id UUID FK

relationships
  id UUID PK
  source_id UUID FK → resources
  target_id UUID FK → resources
  relationship_type RelationshipType
  confidence FLOAT
  ingestion_run_id UUID FK

ingestion_runs
  id UUID PK
  source_file TEXT
  source_type SourceType
  status IngestionStatus    -- pending | processing | complete | failed
  resource_count INT
  relationship_count INT
  error_message TEXT
  created_at TIMESTAMPTZ
  completed_at TIMESTAMPTZ

findings
  id UUID PK
  resource_id UUID FK → resources
  finding_type FindingType
  severity Severity
  message TEXT
  details JSONB
  created_at TIMESTAMPTZ
```

---

## Frontend

Built with Next.js 16 App Router. All pages are in `frontend/src/app/`.

```
src/
├── app/
│   ├── page.tsx              # Dashboard
│   ├── upload/page.tsx       # File upload
│   ├── resources/page.tsx    # Resource browser
│   ├── graph/page.tsx        # Dependency graph
│   ├── blast-radius/page.tsx # Blast radius
│   └── findings/page.tsx     # Findings list
├── components/
│   ├── AppShell.tsx          # Layout wrapper + sidebar
│   ├── graph/                # React Flow nodes/edges/canvas
│   └── ui/                   # Badge, Spinner, EmptyState, Pagination
└── lib/
    ├── api.ts                # fetch wrapper (all API calls)
    ├── types.ts              # TypeScript types matching backend schemas
    └── constants.ts          # Severity colors, labels, limits
```

API calls from the browser go through Next.js rewrites (`/api/*` → `http://api:8000`) so no CORS configuration is needed in development.

---

## CLI

The `infragraph` CLI (`cli/`) is a standalone Typer app that calls the API over HTTP. It does not import or depend on the backend Python package.

```
infragraph_cli/
├── main.py      # Root Typer app + global --api-url callback
├── client.py    # httpx.Client wrapper with unified error handling
├── output.py    # Rich table/tree formatters
└── commands/
    ├── ingest.py     # upload, status
    ├── resources.py  # list
    ├── graph.py      # graph, blast-radius
    └── findings.py   # list, scan
```

The CLI reads `INFRAGRAPH_API_URL` from the environment (default: `http://localhost:8000`) and can target any InfraGraph deployment.

---

## Data flow

```
User uploads file
       │
       ▼
POST /api/ingest/upload
       │
       ▼
ingest_service.ingest_file()
  ├─ detect_source_type()
  ├─ plan_parser / state_parser → [ParsedResource]
  ├─ reference_resolver → [Relationship]
  └─ persist to DB (transaction)
       │
       ▼
IngestionRun returned (id, status, counts)
       │
       ▼
POST /api/findings/scan (optional, can be called separately)
  └─ findings_service.run_all_detectors()
       ├─ detect_orphans()
       ├─ detect_drift()
       ├─ detect_exposures()
       ├─ detect_circular_deps()
       └─ detect_critical_nodes()
```
