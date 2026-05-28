# Backend — FastAPI agent runtime

Layered FastAPI app powering Forge Agent. See the
[root README](../README.md), [`docs/architecture.md`](../docs/architecture.md),
and [`docs/tool-system.md`](../docs/tool-system.md) for the full picture.

## Local development

```bash
cp .env.example .env
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

`http://localhost:8000/docs` opens the interactive OpenAPI explorer.

## Tests

```bash
pytest -q
```

Tests use SQLite — no Postgres or API keys required.

## Folder layout

```
app/
  api/routes/      → thin HTTP adapters (workflows, health)
  core/            → config, logging, errors, security
  db/              → engine + session
  models/          → SQLAlchemy ORM
  repositories/    → data access
  schemas/         → Pydantic schemas
  services/        → business logic
  tools/           → tool base + registry + 5 registered tools
  main.py          → FastAPI app factory + lifespan
tests/             → pytest suite
```

## Adding a new tool

See [`docs/tool-system.md`](../docs/tool-system.md). TL;DR:

1. Subclass `Tool[Input, Output]` in `app/tools/<name>.py`.
2. Add `registry.register(YourTool())` in `app/tools/registry.py`.
3. Add a test in `tests/test_tools.py`.
