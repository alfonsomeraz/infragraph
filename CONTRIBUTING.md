# Contributing to InfraGraph

Thank you for your interest in contributing! This document covers how to get your development environment set up and how to submit changes.

---

## Getting started

1. **Fork** the repo on GitHub and clone your fork:
   ```bash
   git clone https://github.com/<your-username>/infragraph.git
   cd infragraph
   ```

2. **Create a branch** for your change:
   ```bash
   git checkout -b feat/my-feature
   # or: fix/my-bug-fix
   ```

3. **Set up the dev environment:**
   ```bash
   make install      # backend venv + deps
   make fe-install   # frontend node_modules
   make cli-install  # CLI into backend venv
   docker compose up -d postgres
   make migrate
   ```

4. **Run the tests** before making changes to establish a baseline:
   ```bash
   make test
   ```

---

## Development workflow

### Backend changes

- Code lives in `backend/app/`
- All DB operations must be async (asyncpg + SQLAlchemy 2.0 async sessions)
- Enums use `StrEnum` — see existing models for the pattern
- Add tests in `backend/tests/` for any new service or route logic
- Run `make lint` and `make format` before committing

### Frontend changes

- Code lives in `frontend/src/`
- Pages go in `src/app/`, shared components in `src/components/`
- Run `make fe-lint` before committing

### CLI changes

- Code lives in `cli/infragraph_cli/`
- Commands are in `commands/` — each file is a `typer.Typer` sub-app
- Rich output helpers go in `output.py`
- Re-install after changes: `make cli-install`
- Test manually: `backend/.venv/bin/infragraph --help`

### Database migrations

If your change adds or modifies a DB model:

```bash
make migrate-new MSG="describe your change"
# review the generated file in backend/alembic/versions/
make migrate
```

---

## Submitting a pull request

1. Make sure all tests pass: `make test`
2. Make sure lint is clean: `make lint && make fe-lint`
3. Push your branch and open a PR against `main`
4. Fill in the PR template — describe *what* and *why*, not just *how*

PRs should be focused. One feature or fix per PR.

---

## Security vulnerabilities

Please **do not** open a public issue for security vulnerabilities. See [SECURITY.md](SECURITY.md) for the responsible disclosure process.

## Reporting bugs

Open a [GitHub Issue](https://github.com/alfonsomeraz/infragraph/issues) with:
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, Docker version)

---

## Code style

| Area | Tool | Config |
|------|------|--------|
| Python | ruff | `pyproject.toml` — rules E,F,I,N,W,UP, line length 100 |
| TypeScript | ESLint | `frontend/.eslintrc` / `eslint.config.mjs` |

---

## License

By contributing, you agree your contributions are licensed under the [MIT License](LICENSE).
