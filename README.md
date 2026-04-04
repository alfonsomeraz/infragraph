# InfraGraph

**Open-source cloud dependency mapper.** Upload Terraform plan or state JSON files and get an interactive graph of your infrastructure — with blast radius analysis, drift detection, and security findings.

[![CI](https://github.com/alfonsomeraz/infragraph/actions/workflows/ci.yml/badge.svg)](https://github.com/alfonsomeraz/infragraph/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

![InfraGraph screenshot placeholder](docs/screenshot.png)

---

## Features

- **Graph visualization** — interactive React Flow canvas showing resource dependencies
- **Blast radius** — select any resource and see what would be affected by a change
- **Findings engine** — auto-detect orphaned resources, security exposures, circular dependencies, and critical nodes
- **Drift detection** — surface resources with uncommitted changes from Terraform plans
- **Multi-source** — supports Terraform plan JSON, Terraform state JSON

---

## Quick start

**Requirements:** Docker + Docker Compose (or Python 3.11+ and Node 20+ for local dev)

```bash
# Clone
git clone https://github.com/alfonsomeraz/infragraph.git
cd infragraph

# Start everything (Postgres + API + Frontend)
docker compose up --build

# In a second terminal, run migrations
docker compose run --rm migrate
```

Then open **http://localhost:3000** and upload one of the example files from `examples/`.

---

## Development setup

### Backend (Python / FastAPI)

```bash
# Create venv and install all deps (including dev/test)
make install

# Start Postgres
docker compose up -d postgres

# Run migrations
make migrate

# Start API with hot-reload on :8000
make dev

# Run all tests
make test

# Lint / format
make lint
make format
```

### Frontend (Next.js)

```bash
# Install deps
make fe-install

# Start dev server on :3000 (requires API running)
make fe-dev

# Production build
make fe-build
```

### Seed with example data

```bash
make seed
```

This uploads the Terraform files in `examples/` and runs the findings scanner.

---

## API reference

Interactive docs are available at **http://localhost:8000/docs** when the API is running.

| Endpoint | Description |
|----------|-------------|
| `POST /api/ingest/upload` | Upload a Terraform plan or state JSON file |
| `GET /api/resources` | List resources (filter by type, provider, source) |
| `GET /api/graph/{resource_id}` | Full dependency graph for a resource |
| `GET /api/graph/{resource_id}/blast-radius` | Blast radius subgraph (depth 1–10) |
| `GET /api/findings` | List findings (filter by type, severity) |
| `POST /api/findings/scan` | Run the findings detector |

---

## Project structure

```
infragraph/
├── backend/                 # Python / FastAPI
│   ├── app/
│   │   ├── adapters/terraform/  # Plan + state parsers, reference resolver
│   │   ├── db/              # SQLAlchemy models, session
│   │   ├── routes/          # FastAPI routers
│   │   ├── schemas/         # Pydantic request/response models
│   │   └── services/        # Business logic (ingest, graph, findings)
│   └── tests/
├── frontend/                # Next.js 16 + React Flow
│   └── src/
│       ├── app/             # Pages (dashboard, graph, blast-radius, findings, upload)
│       ├── components/      # Shared UI + graph components
│       └── lib/             # API client, types, constants
├── infra/
│   ├── docker/              # Dockerfiles
│   └── scripts/             # seed.sh
├── examples/                # Sample Terraform plan + state JSON files
└── docs/
```

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), asyncpg |
| Database | PostgreSQL 16 |
| Frontend | Next.js 16, React Flow v12, Tailwind CSS |
| Migrations | Alembic |
| Testing | pytest, pytest-asyncio |
| Lint | ruff (backend), ESLint (frontend) |
| CI | GitHub Actions |

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Good first issues** are tagged [`good first issue`](https://github.com/alfonsomeraz/infragraph/issues?q=is%3Aopen+label%3A%22good+first+issue%22) on GitHub.

---

## License

[MIT](LICENSE) — © 2026 InfraGraph Contributors
