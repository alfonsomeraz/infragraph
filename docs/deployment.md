# Deployment Guide

## Prerequisites

- Docker 24+ and Docker Compose v2
- A PostgreSQL 16 database (or use the bundled Compose service)
- (Optional) A reverse proxy (nginx, Caddy, Traefik) for TLS termination

---

## Quick start with Docker Compose

The fastest way to run InfraGraph end-to-end:

```bash
git clone https://github.com/alfonsomeraz/infragraph.git
cd infragraph

# Copy and edit environment variables
cp .env.example .env
# edit .env — set POSTGRES_PASSWORD and any other values

# Start everything
docker compose up --build -d

# Run DB migrations (one-time or after updates)
docker compose run --rm migrate

# Verify
curl http://localhost:8000/api/health   # {"status":"ok"}
open http://localhost:3000             # Frontend
```

### Services started by Compose

| Service | Port | Description |
|---------|------|-------------|
| `postgres` | 5432 | PostgreSQL 16 database |
| `api` | 8000 | FastAPI backend |
| `frontend` | 3000 | Next.js frontend |
| `migrate` | — | One-shot Alembic migration runner (profile: tools) |

---

## Environment variables

Copy `.env.example` to `.env` and fill in:

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `infragraph` | DB username |
| `POSTGRES_PASSWORD` | `infragraph` | DB password — **change in production** |
| `POSTGRES_DB` | `infragraph` | Database name |
| `INFRAGRAPH_DATABASE_URL` | `postgresql+asyncpg://infragraph:infragraph@postgres:5432/infragraph` | Full async DB URL for the API |
| `NEXT_PUBLIC_API_URL` | _(empty, uses rewrite proxy)_ | Set only if frontend and API run on different origins |
| `INFRAGRAPH_API_URL` | `http://localhost:8000` | Used by the CLI to locate the API |

---

## Production considerations

### Authentication

InfraGraph v0.1.0 has no built-in authentication. Before exposing the API publicly:

- Place a reverse proxy in front with basic auth or OAuth2 (nginx, Caddy, Traefik + forward auth)
- Restrict PostgreSQL to the API container's network only

### TLS

Use a reverse proxy to terminate TLS. Example with Caddy:

```
# Caddyfile
infragraph.example.com {
    reverse_proxy /api/* api:8000
    reverse_proxy /* frontend:3000
}
```

### Scaling

The API is stateless — you can run multiple replicas behind a load balancer:

```yaml
# docker-compose.override.yml (example)
services:
  api:
    deploy:
      replicas: 3
```

The frontend is also stateless (SSR/SSG). Scale similarly.

### Database

For production, use a managed PostgreSQL service (RDS, Cloud SQL, Supabase, etc.) and set `INFRAGRAPH_DATABASE_URL` accordingly. Run migrations on deploy:

```bash
docker compose run --rm migrate
```

---

## Running locally without Docker

### Backend

```bash
# 1. Create venv and install deps
make install

# 2. Start Postgres only
docker compose up -d postgres

# 3. Run migrations
make migrate

# 4. Start API
make dev   # hot-reload on :8000
```

### Frontend

```bash
# Install deps
make fe-install

# Start dev server on :3000
make fe-dev
```

### CLI

```bash
# Install into backend venv
make cli-install

# Use it (with API running)
backend/.venv/bin/infragraph --help
```

---

## Kubernetes (Helm — coming soon)

A Helm chart is planned for v0.2.0. Until then, adapt the Docker Compose manifest to Kubernetes Deployments and a Service/Ingress directly.

---

## Upgrading

1. Pull the latest code: `git pull`
2. Rebuild images: `docker compose build`
3. Run migrations: `docker compose run --rm migrate`
4. Restart services: `docker compose up -d`

Check [CHANGELOG.md](../CHANGELOG.md) for breaking changes between versions.
