# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Mojo is a Japanese (JLPT) learning platform: a FastAPI backend in `server/` and a Next.js frontend in `client/`, connected by an OpenAPI contract. Google Gemini powers Kaiwa conversation, pronunciation and handwriting feedback. `server/README.md`, `client/README.md` and `client/docs/api-layer.md` hold the detailed conventions; read the relevant one before changing that side.

## Commands

The root `Makefile` is the entry point for everything (`make help` lists targets). It is the only thing that loads backend secrets, from `~/.config/secrets/mojo/.env` (override with `ENV_FILE=...`), passing them via `uv run --env-file`. Targets that need secrets fail fast via `check-env`.

```bash
make db-up && make migrate      # PostgreSQL via docker compose, then Alembic
make dev                        # db-up + API with reload on :8000 (docs at /docs)
make client-dev                 # Next.js on :3000, NEXT_PUBLIC_API_URL from API_URL (default http://localhost:8000)
make migration m="..."          # autogenerate; review the file in server/migrations/versions/ before applying
make seed / make seed-reset     # demo data (scripts/seed_demo.py)
make lint / make format         # ruff (server only)
make typecheck                  # mypy on server + tsc on client
make check                      # lint + typecheck + test
make api-types                  # export server/openapi -> client/openapi.json -> client/src/types/api.generated.ts
```

Tests (server only; no client tests exist) run against a real PostgreSQL, not SQLite:

```bash
make test-db                    # disposable postgres:17 container on localhost:55432
make test                       # full suite
# single file / test, from server/:
TEST_DATABASE_URL=postgresql://mojo:mojo@localhost:55432/mojo_test uv run pytest tests/test_auth.py -q
TEST_DATABASE_URL=postgresql://mojo:mojo@localhost:55432/mojo_test uv run pytest tests/test_auth.py -k refresh -q
```

`tests/conftest.py` refuses to run without `TEST_DATABASE_URL`, drops and rebuilds the schema from the Alembic migrations once per session, and truncates every table except reference data (`skill`) after each test. Tests never read the secrets file.

## CI (.github/workflows/ci.yml)

Three jobs; match them locally before pushing:
- **server**: ruff check, ruff format --check, mypy, `alembic upgrade head` + `alembic check` (models and migrations must agree), pytest.
- **client**: eslint, tsc, `next build`.
- **contract**: regenerates `client/openapi.json` and `api.generated.ts` and fails on any diff. Any change to a server schema or route must be followed by `make api-types` with both generated files committed.

## Architecture

**The contract is the seam.** Server Pydantic schemas -> `scripts/export_openapi.py` -> `client/openapi.json` -> `openapi-typescript` -> `client/src/types/api.generated.ts`. The client's `api` (openapi-fetch) checks paths, params and bodies against it at compile time, so contract changes start on the server and `npm run type-check` then lists every broken call site. Never hand-edit the generated files or hand-write wire types on the client.

**Wire format.** JSON is camelCase (`CamelModel` in `server/app/schemas/base.py`); Python stays snake_case. Most responses are enveloped as `ApiResponse[Data]` (`{ success, data, ... }`), errors are `ErrorResponse` raised through `ApiError` (`server/app/api/errors.py`). A few routes are not enveloped (`/users/me`, `/speaking/pronunciation`, `/speaking/kaiwa`); client `api.ts` functions return `.data` for enveloped routes and the body otherwise.

**Server-owned rules.** The acting user always comes from the access token, never the request body. Scores, XP and levels are computed on the server; the client never sends or sums them, only displays returned values like `xpEarned`.

**Auth across both sides.** Short-lived access JWTs reference a server-side `auth_session`; the refresh token is an httpOnly cookie that rotates on use (`server/app/services/auth.py`). On the client, `client/src/lib/api-client.ts` keeps the access token in memory only, restores it from the cookie after page load, refreshes ahead of expiry, and retries once on 401. Login/register/logout in `client/src/features/auth/session.ts` deliberately use plain `fetch` (no bearer token).

**Configuration.** Server settings are env vars read by `server/app/core/config.py`. `GEMINI_API_KEY` is optional; without it AI features return canned responses. `SECRET_KEY` must be 32+ chars. Reference data the code depends on (e.g. `skill` codes) is seeded by migrations, not scripts.

Server-only and client-only guidance lives in `server/CLAUDE.md` and `client/CLAUDE.md`.

## Branches

Work on `develop`; `master` is the main branch.
