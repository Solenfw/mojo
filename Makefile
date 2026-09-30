# The only entry point that loads environment variables. The secrets file lives outside the repo and
# is handed to each command explicitly:
#   - Python (server/):  uv run --env-file   (parses the file the way docker compose does; make's own
#                        `include` would expand `$` and keep quotes)
#   - docker compose:    --env-file, used only to fill the POSTGRES_* values in docker-compose.yml
#   - client (Next.js):  NEXT_PUBLIC_API_URL passed on the command line
# Tests never read the secrets file.

ENV_FILE ?= $(HOME)/.config/secrets/mojo/.env
API_URL ?= http://localhost:8000
TEST_DATABASE_URL ?= postgresql://mojo:mojo@localhost:55432/mojo_test

RUN := cd server && uv run --env-file $(ENV_FILE)
COMPOSE := docker compose --env-file $(ENV_FILE)

.DEFAULT_GOAL := help
.PHONY: help check-env dev api db-up db-down migrate migration downgrade db-current \
	test-db test-db-down test lint format typecheck check hooks api-types \
	client-install client-dev client-build client-typecheck

help: ## List the available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

check-env:
	@test -f "$(ENV_FILE)" || { echo "Secrets file not found: $(ENV_FILE)"; \
		echo "Copy server/.env.example there and fill it in, or pass ENV_FILE=/path/to/file."; exit 1; }

# ── Run ───────────────────────────────────────────────────────

dev: db-up api ## Start PostgreSQL, then the API with live reload

api: check-env ## Run the API only (expects the database to be up)
	$(RUN) uvicorn app.main:app --reload

# ── Database ──────────────────────────────────────────────────

db-up: check-env ## Start PostgreSQL and wait until it is healthy
	$(COMPOSE) up -d --wait db

db-down: check-env ## Stop PostgreSQL (data is kept in the volume)
	$(COMPOSE) down

migrate: check-env ## Apply all pending migrations
	$(RUN) alembic upgrade head

migration: check-env ## Autogenerate a migration from model changes: make migration m="add foo"
	@test -n "$(m)" || { echo 'Usage: make migration m="describe the change"'; exit 1; }
	$(RUN) alembic revision --autogenerate -m "$(m)"

downgrade: check-env ## Roll back the most recent migration
	$(RUN) alembic downgrade -1

db-current: check-env ## Show the database's current migration
	$(RUN) alembic current

# ── Tests ─────────────────────────────────────────────────────

test-db: ## Start the disposable test database (tables are dropped and recreated on every run)
	docker start mojo_test_db 2>/dev/null || docker run -d --name mojo_test_db \
		-e POSTGRES_USER=mojo -e POSTGRES_PASSWORD=mojo -e POSTGRES_DB=mojo_test -p 55432:5432 postgres:17

test-db-down: ## Remove the disposable test database
	docker rm -f mojo_test_db

test: ## Run the backend test suite against the test database
	cd server && TEST_DATABASE_URL=$(TEST_DATABASE_URL) uv run pytest -q

# ── Code quality ──────────────────────────────────────────────

lint: ## Lint and check formatting (server)
	cd server && uv run ruff check . && uv run ruff format --check .

format: ## Auto-fix lint issues and format (server)
	cd server && uv run ruff check --fix . && uv run ruff format .

typecheck: ## Type-check the server (mypy) and the client (tsc)
	cd server && uv run mypy
	cd client && npm run type-check

check: lint typecheck test ## Everything CI runs on the server and client code

hooks: ## Install the git pre-commit hooks (ruff on staged server files)
	server/.venv/bin/pre-commit install

# ── API contract ──────────────────────────────────────────────

api-types: check-env ## Export the OpenAPI contract and regenerate the client's TypeScript types
	$(RUN) python -m scripts.export_openapi
	cd client && npm run gen:api

# ── Client ────────────────────────────────────────────────────

client-install: ## Install the client's dependencies
	cd client && npm install

client-dev: ## Run the Next.js dev server against API_URL
	cd client && NEXT_PUBLIC_API_URL=$(API_URL) npm run dev

client-build: ## Production build of the client against API_URL
	cd client && NEXT_PUBLIC_API_URL=$(API_URL) npm run build

client-typecheck: ## Type-check the client
	cd client && npm run type-check
