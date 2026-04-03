.PHONY: dev down test test-one lint format migrate migrate-new install

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
	@echo "Logs: docker compose logs -f api"

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
