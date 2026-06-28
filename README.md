# product_lm_comparator

Поиск и сравнение поставщиков продуктов питания с LLM-ассистентом.

## Архитектура

Двухпроцессное приложение: **FastAPI backend** (REST API) + **Streamlit frontend** (UI).  
Фронтенд обращается к бекенду по HTTP. Локальная LLM (Ollama) используется для чата-сравнения и парсинга сайтов поставщиков.

| Компонент | Технология | Порт |
|---|---|---|
| Backend | FastAPI + SQLAlchemy ORM | `8000` |
| Frontend | Streamlit | `8501` |
| Database | PostgreSQL 16 | `5432` |
| LLM | Ollama (например, `llama3.2:3b`) | `11434` |

## Функциональность

- Каталог поставщиков продуктов питания с фильтрацией по категориям, городу, рейтингу
- Управление контактами, сертификатами, условиями заказа, заметками
- Сравнение поставщиков в диалоге с LLM-ассистентом
- Парсинг сайта поставщика с автоматическим извлечением данных через LLM
- REST API с документацией Swagger (`/docs`)
- 7 ресурсных эндпоинтов: `/suppliers`, `/categories`, `/contacts`, `/order_conditions`, `/certificates`, `/user_notes`, `/comparison`

## Быстрый старт (локально)

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

## Переменные окружения

| Переменная | Значение по умолчанию | Описание |
|---|---|---|
| `DB_HOST` | `localhost` | Хост PostgreSQL |
| `DB_PORT` | `5432` | Порт PostgreSQL |
| `DB_NAME` | `supplier_db` | Название базы данных |
| `DB_USER` | `postgres` | Пользователь БД |
| `DB_PASSWORD` | `password` | Пароль БД |
| `BASE_URL` | `http://localhost:8000/` | URL бекенда (для фронтенда) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Адрес Ollama |
| `LLM_MODEL` | `llama3.2:3b` | Модель по умолчанию |
| `LLM_TIMEOUT` | `300` | Таймаут запроса к LLM (сек) |

## Структура проекта

```
app/
  backend/           — FastAPI приложение и REST эндпоинты
    endpoints/       —  7 роутеров
    services/        —  url_parser.py, llm_client.py
  frontend/          — Streamlit приложение (main.py, api_requests/)
  db/                — SQLAlchemy модели, CRUD, seed_data.py
  schemas/           — Pydantic модели запросов/ответов
  tests/             — 45 pytest-тестов
```

## Тестирование

```sh
python -m pytest app/tests/ -v
```

## Лицензия

MIT
