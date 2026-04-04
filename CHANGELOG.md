# Changelog

All notable changes to InfraGraph are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
InfraGraph uses [semantic versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.1.0] — 2026-04-04

### Added

**Backend**
- FastAPI application with async SQLAlchemy 2.0 + asyncpg + PostgreSQL 16
- Terraform plan JSON parser (`terraform show -json` output)
- Terraform state JSON parser (`terraform state pull` output)
- Reference resolver: infers relationships from resource attributes (`subnet_id`, `vpc_id`, `security_groups`, etc.)
- `POST /api/ingest/upload` — upload and parse a Terraform JSON file
- `GET /api/ingest/{run_id}` — fetch ingestion run status
- `GET /api/resources` — list resources with filters (type, provider, source, limit/offset)
- `GET /api/resources/{resource_id}` — fetch a single resource
- `GET /api/graph/{resource_id}` — 1-hop dependency graph
- `GET /api/graph/{resource_id}/blast-radius` — BFS blast radius subgraph (depth 1–10)
- `GET /api/findings` — list findings with filters (type, severity, limit/offset)
- `GET /api/findings/{finding_id}` — fetch a single finding
- `POST /api/findings/scan` — run all finding detectors
- `GET /api/health` — liveness probe
- Findings engine: orphan detection, drift detection, security exposure detection, circular dependency detection, critical node detection
- Alembic migrations for all four core tables
- pytest-asyncio test suite (plan parser, state parser, ingest, resources, graph, findings, health)

**Frontend**
- Next.js 16 (App Router) with React Flow v12 for graph visualization
- Dashboard — summary statistics + recent findings
- Upload page — drag-and-drop Terraform JSON file upload
- Resources page — filterable/paginated resource list
- Graph page — interactive dependency graph with dagre layout
- Blast Radius page — BFS impact visualization
- Findings page — filterable findings list with severity badges
- Tailwind CSS v4, TypeScript strict mode
- Next.js rewrite proxy for `/api/*` → backend

**CLI**
- Typer-based `infragraph` CLI calling the API over HTTP
- `infragraph ingest upload <file>` — upload a Terraform JSON file
- `infragraph ingest status <run_id>` — check ingestion run status
- `infragraph resources list [--type] [--provider] [--source] [--limit]`
- `infragraph graph graph <resource_id>` — print dependency tree
- `infragraph graph blast-radius <resource_id> [--depth]` — print impact tree
- `infragraph findings list [--type] [--severity] [--limit]`
- `infragraph findings scan` — trigger scanner + display results
- Top-level shortcuts: `infragraph scan`, `infragraph blast-radius`
- `--api-url` flag and `INFRAGRAPH_API_URL` env var for remote API support
- Rich tables and trees for all output

**Infrastructure**
- Multi-service Docker Compose: postgres, api, migrate, frontend
- Multi-stage Dockerfiles for API and frontend
- GitHub Actions CI: lint (ruff), migrations, pytest, frontend build + lint
- `make` targets: `install`, `dev`, `down`, `test`, `lint`, `format`, `migrate`, `seed`, `logs`, `psql`, `clean`, `docker-build`, `fe-install`, `fe-dev`, `fe-build`, `fe-lint`, `cli-install`, `cli-run`
- Seed script (`infra/scripts/seed.sh`) for example data
- Example Terraform plan + state files

[Unreleased]: https://github.com/alfonsomeraz/infragraph/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/alfonsomeraz/infragraph/releases/tag/v0.1.0
