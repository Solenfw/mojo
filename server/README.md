# Mojo server

FastAPI + SQLAlchemy 2 (async, asyncpg) + PostgreSQL, managed with uv. Every command runs from this directory; imports are rooted at `app`. In day-to-day use, run things through the root `Makefile`, which supplies the environment.

## Layout

```text
server/
├── app/
│   ├── main.py            # create_app(): middleware, error handlers, routers, /healthz
│   ├── api/
│   │   ├── deps.py        # DbSession, CurrentUser dependencies
│   │   ├── errors.py      # ApiError + helpers -> ErrorResponse bodies
│   │   └── v1/            # one router per domain, collected in v1/router.py
│   ├── core/              # settings (env vars only) and security primitives (hashing, tokens)
│   ├── db/                # engine, session factory, declarative Base
│   ├── models/            # SQLAlchemy models, one module per domain
│   ├── schemas/           # Pydantic request/response schemas, same domains as models/
│   ├── services/          # business logic that touches the database (auth, srs, gamification, grading)
│   └── clients/           # wrappers for outside systems (Gemini, MeCab)
├── migrations/            # Alembic; versions/ is generated, review before applying
├── scripts/               # export_openapi.py (API contract for the client)
├── tests/                 # pytest against a real PostgreSQL, schema built by the migrations
├── Dockerfile             # production image (uv build stage, slim non-root runtime)
└── pyproject.toml         # dependencies and tool config (pytest, ruff, mypy)
```

Domains share module names across layers: `api/v1/reading.py`, `models/reading.py`, `schemas/reading.py`. Import models and schemas from their packages (`from app.models import User`, `from app.schemas import LoginRequest`).

## Conventions

- **Layers.** Routers validate input, call services, and map service exceptions to `ApiError`. Services hold the rules and don't know about HTTP. Clients wrap outside APIs and are called through `anyio.to_thread` because they block.
- **Contract.** JSON is camelCase on the wire (`CamelModel`); Python stays snake_case. Enveloped responses subclass `ApiResponse[Data]`; errors are `ErrorResponse`. The acting user always comes from the access token, and scores, XP and levels are computed on the server, never taken from the client.
- **Auth.** Short-lived access JWTs name a server-side `auth_session`; the refresh token is an httpOnly cookie that rotates on use. See `services/auth.py`.
- **Configuration.** `app/core/config.py` reads environment variables only. Nothing in the code loads `.env` files.
- **Reference data** that the code depends on (e.g. `skill` codes) is seeded by migrations, not scripts.

## Commands

From the repo root (see `make help`):

```bash
make dev                    # API with live reload
make migration m="..."      # autogenerate a migration, then review it
make migrate                # apply migrations
make test-db && make test   # tests on a disposable postgres:17 (port 55432)
make lint / make format     # ruff
make typecheck              # mypy (+ client tsc)
make api-types              # regenerate client/openapi.json and the client's TS types
```

Directly, from `server/` (supply your own environment):

```bash
uv run uvicorn app.main:app --reload
uv run alembic upgrade head
TEST_DATABASE_URL=postgresql://mojo:mojo@localhost:55432/mojo_test uv run pytest
```

## Docker

```bash
docker build -t mojo-server server
docker run --rm --env-file <secrets> mojo-server alembic upgrade head
docker run -p 8000:8000 --env-file <secrets> mojo-server
```
