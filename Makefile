.PHONY: dev down test test-one lint format migrate migrate-new install seed logs psql clean docker-build fe-install fe-dev fe-build fe-lint

VENV   := backend/.venv
BIN    := $(VENV)/bin

# Create venv + install deps
install:
	test -d $(VENV) || python -m venv $(VENV)
	cd backend && .venv/bin/pip install -e ".[dev]"

# Start Postgres + API (detached) with hot-reload
dev:
	docker compose up -d
	@echo "Postgres + API running — http://localhost:8000"
	@echo "Logs: make logs"

# Stop everything
down:
	docker compose down

# Run all tests
test:
	cd backend && .venv/bin/python -m pytest -v

# Run a single test file or test: make test-one T=tests/test_plan_parser.py
test-one:
	cd backend && .venv/bin/python -m pytest -v $(T)

lint:
	cd backend && .venv/bin/ruff check .

format:
	cd backend && .venv/bin/ruff format .

# Run pending migrations
migrate:
	cd backend && .venv/bin/alembic upgrade head

# Create a new migration: make migrate-new MSG="add foo table"
migrate-new:
	cd backend && .venv/bin/alembic revision --autogenerate -m "$(MSG)"

# Seed the database with example Terraform files
seed:
	bash infra/scripts/seed.sh

# Tail API logs
logs:
	docker compose logs -f api

# Open psql shell in the postgres container
psql:
	docker compose exec postgres psql -U infragraph -d infragraph

# Stop everything and remove volumes
clean:
	docker compose down -v

# Build the API Docker image without starting
docker-build:
	docker compose build api

# --- Frontend ---

fe-install:
	cd frontend && npm install

fe-dev:
	cd frontend && npm run dev

fe-build:
	cd frontend && npm run build

fe-lint:
	cd frontend && npm run lint
