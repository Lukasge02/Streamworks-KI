# Repository Guidelines

## Project Structure & Module Organization
- `backend/` houses the FastAPI service: `routers/` expose endpoints, `services/` contain the RAG workflow, `models/` and `database/` manage persistence, and Alembic scripts live in `migrations/`.
- `frontend/` is the Next.js 15 app under `src/` (`app/` routes, `components/`, `stores/`, `hooks/`, `utils/`); static assets belong in `public/`, while large ingest payloads stay under `storage/`.
- Runbooks and deployment blueprints sit in `docs/`, `infra/`, `k8s/`, and `docker-compose*.yml`; automation is kept in `scripts/`. Regression helpers like `test_api_fixes.py` sit at the repo root—co-locate new suites with related services.

## Build, Test, and Development Commands
- `make setup` installs Python and Node dependencies and copies `.env.example` for local configuration.
- `make dev` boots uvicorn and Next.js dev servers inside tmux (stop with `make stop`); `cd frontend && npm run dev` and `cd backend && python -m uvicorn main:app --reload --port 8000` run services individually.
- `make test` currently executes backend `pytest tests/ -v`; wire up a frontend `npm test` script before enabling it in CI.

## Coding Style & Naming Conventions
- Backend Python adheres to Ruff (88-char lines, spaces, double quotes). Use `snake_case` for modules/functions and `PascalCase` for classes, adding type hints on service boundaries.
- Frontend TypeScript keeps 2-space indents, `PascalCase` components, `camelCase` hooks/utilities, and SCREAMING_CASE constants. Run `npm run lint` and `npm run type-check` before commits.
- Prefer descriptive module names (`document_ingest.py`, `ragWorkflowStore.ts`) and consolidate shared logic in `core/` or `frontend/src/lib/`.

## Testing Guidelines
- Store backend tests in `tests/` or next to features as `test_<feature>.py`; rely on pytest fixtures to prepare Postgres/Qdrant state.
- Capture integration flows in scripts like `test_api_fixes.py` and keep them idempotent so `make test` can run locally and in CI.

## Commit & Pull Request Guidelines
- Match existing history: emoji prefix + concise subject (`🚀 Backend v0.07 - Phase 2 RAG Pipeline Implementation`). Separate concerns per commit and include migration or config updates with the feature that needs them.
- Pull requests should summarize impact, link Streamworks tickets, call out new env vars or migrations, and attach UI screenshots or API samples when behaviour changes.

## Environment & Secrets
- Start from `.env.example`, copy to `.env`, and fill Supabase, OpenAI, and Qdrant credentials. Never commit populated env files.
- Use `docker-compose.qdrant.yml` or manifests in `supabase/` and `infra/` for reproducible services; document schema changes inside the PR.
