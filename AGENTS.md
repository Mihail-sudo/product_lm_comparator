# product_lm_comparator — agent guide

## Architecture

Two-process app: **FastAPI backend** + **Streamlit frontend**.  
Both must run simultaneously. Frontend polls the backend via HTTP (`requests`).

- Backend: `app.backend.main:app` — FastAPI, SQLAlchemy ORM, PostgreSQL
- Frontend: `app.frontend.main` — Streamlit (the current version at `app/frontend/main.py`)
- Root files `b.py` and `n.py` are older prototypes — do not edit them.
- Backend routes: `/suppliers`, `/categories`, `/contacts`, `/order_conditions`, `/certificates`, `/user_notes`, `/comparison`
- CORS wide open (`allow_origins=["*"]`) for Streamlit access.
- App is in Russian (UI labels, comments, data).

## Startup

```sh
# Terminal 1 — backend
uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — frontend
streamlit run app/frontend/main.py
```

## Database

- **PostgreSQL** required. Connection from `app/db/db_config.py` via env vars:
  `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` (defaults: localhost, 5432, supplier_db, postgres, password).
- `.env` file loaded via `python-dotenv` — create one if missing.
- Seed data: `python -m app.db.seed_data` — reads `app/db/data.json`, creates tables, imports categories + suppliers.
- Schema defined in `app/db/models.py` with SQLAlchemy declarative models.

## Package management

No `pyproject.toml`, `setup.py`, or `requirements.txt`.  
Dependencies live only in `.venv/` (Python 3, pip-installed manually).  
Key packages: fastapi, uvicorn, sqlalchemy, streamlit, pydantic, requests, python-dotenv, psycopg2 (implied by postgresql://).

## Project structure

```
app/
  backend/       — FastAPI app + REST endpoints
  frontend/      — Streamlit app (main.py entrypoint, api_requests/ for HTTP calls)
  db/            — SQLAlchemy models, DB config, CRUD layer, seed script, data.json
  schemas/       — Pydantic models for request/response validation
```

## No tests, no CI, no linter/typecheck

None configured. No verification commands to run.

## LLM (comparison dialog)

- The comparison chat in `app/frontend/main.py` calls a local Ollama instance via `app/frontend/llm_service.py`.
- Configured via env vars: `OLLAMA_BASE_URL` (default `http://localhost:11434`), `LLM_MODEL` (default `llama3.2`).
- Model can also be set in the sidebar text input at runtime.
- Falls back to an error message if Ollama is unreachable.

## Style notes

- `serializer.py` contains manual dict serialization from SQLAlchemy objects to Pydantic-compatible dicts.
- Streamlit frontend uses `api_requests/` module with `requests` library (synchronous calls inside async wrappers).
