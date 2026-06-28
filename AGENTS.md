# product_lm_comparator — agent guide

## Architecture

Two-process app: **FastAPI backend** + **Streamlit frontend**.  
Both must run simultaneously. Frontend polls the backend via HTTP (`requests`).

- Backend: `app.backend.main:app` — FastAPI, SQLAlchemy ORM, PostgreSQL
- Frontend: `app.frontend.main` — Streamlit
- Root files `b.py` and `n.py` are older prototypes — do not edit them.
- Backend routes: `/suppliers`, `/categories`, `/contacts`, `/order_conditions`, `/certificates`, `/user_notes`, `/comparison`
- CORS wide open (`allow_origins=["*"]`) for Streamlit access.
- App is in Russian (UI labels, comments, data).

## Quick start (local)

```sh
# 1. Установка зависимостей
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 2. Настройка окружения
cp .env.example .env   # отредактировать при необходимости

# 3. База данных (PostgreSQL должен быть запущен)
python -m app.db.seed_data

# 4. Запуск
# Терминал 1 — бекенд
uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000

# Терминал 2 — фронтенд
streamlit run app/frontend/main.py
```

## Docker

```sh
docker compose up --build
```

PostgreSQL + backend (8000) + frontend (8501) поднимутся автоматически.  
Ollama должна быть запущена отдельно на хосте.

## Testing

```sh
python -m pytest app/tests/ -v
```

## Environment

| Variable | Default | Description |
|---|---|---|
| `DB_HOST` | localhost | PostgreSQL host |
| `DB_PORT` | 5432 | PostgreSQL port |
| `DB_NAME` | supplier_db | Database name |
| `DB_USER` | postgres | Database user |
| `DB_PASSWORD` | password | Database password |
| `BASE_URL` | http://localhost:8000/ | Backend API URL (for frontend) |
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama endpoint |
| `LLM_MODEL` | llama3.2:3b | Default model name |
| `LLM_TIMEOUT` | 300 | LLM request timeout (seconds) |

## Package management

`pyproject.toml` — main dependencies in `[project]`, dev-only in `[project.optional-dependencies] dev`.

## Project structure

```
app/
  backend/       — FastAPI app + REST endpoints
  frontend/      — Streamlit app (main.py, api_requests/, llm_common.py)
  db/            — SQLAlchemy models, DB config, CRUD layer, seed script
  schemas/       — Pydantic models for request/response validation
  tests/         — pytest tests (45 tests)
Dockerfile           — Backend container
Dockerfile.frontend  — Frontend container
docker-compose.yml   — PostgreSQL + backend + frontend
pyproject.toml       — Dependencies and project metadata
.env.example         — Environment template
```

## LLM (comparison dialog)

- The comparison chat in `app/frontend/main.py` calls a local Ollama instance via `app/frontend/llm_service.py`.
- Configured via env vars: `OLLAMA_BASE_URL`, `LLM_MODEL`, `LLM_TIMEOUT`.
- Model can also be set in the sidebar text input at runtime.
- Falls back to an error message if Ollama is unreachable.

## URL parsing service

- `app/backend/services/url_parser.py` — fetches a supplier's website, extracts text via BeautifulSoup, sends it to the LLM, and parses the JSON response into structured supplier data.
- `app/backend/services/llm_client.py` — backend-side Ollama client (re-exports from `app.frontend.llm_common`).
- Endpoint: `POST /suppliers/parse-from-url` with body `{"url": "...", "model": "..."}`.
- The LLM extracts name, description, city, region, address, foundation_year, categories, contacts, and certificates.
- Categories not found in the DB are auto-created. Contacts and certificates are linked to the new supplier.
- Ollama must be running locally.
