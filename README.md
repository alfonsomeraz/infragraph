# InfraGraph

Open-source cloud dependency mapper. Upload Terraform plan/state JSON, visualize a dependency graph with blast radius analysis and drift detection.

## Quick Start

```bash
# Start Postgres + API
make dev

# Run migrations
make migrate

# Run tests
make test
```

### Ingest Terraform Data

```bash
# Upload a Terraform plan
curl -X POST http://localhost:8000/api/ingest/terraform-plan \
  -H "Content-Type: application/json" \
  -d @examples/terraform-plan.json

# Upload Terraform state
curl -X POST http://localhost:8000/api/ingest/terraform-state \
  -H "Content-Type: application/json" \
  -d @examples/terraform-state.json
```

### Explore

- `GET /api/graph` — full dependency graph
- `GET /api/resources` — list resources (filterable, paginated)
- `GET /api/resources/{id}/blast-radius` — blast radius subgraph
- `GET /api/findings` — detected issues (orphans, drift, critical nodes)
- Interactive API docs at `http://localhost:8000/docs`

## Architecture

- **Backend:** Python / FastAPI with async SQLAlchemy + Postgres
- **Frontend:** Next.js + React Flow (Phase 2)
- **CLI:** Typer (Phase 3)

## License

MIT
# infragraph
