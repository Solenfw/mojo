# Mojo

Mojo is an AI-assisted Japanese language learning platform for learners working toward the JLPT. It has a FastAPI backend and a Next.js frontend, and uses Google Gemini for conversation practice (Kaiwa), pronunciation and handwriting feedback.

## Layout

```text
mojo/
├── client/                 # Next.js frontend (React 19, Tailwind CSS v4, npm)
│   └── openapi.json        # API contract exported from the server; source of src/types/api.generated.ts
├── server/                 # FastAPI backend (Python 3.12, uv), see server/README.md
├── .github/workflows/      # CI: lint, types, migrations, tests, client build, contract drift
├── .pre-commit-config.yaml # ruff on staged server files (`make hooks`)
├── docker-compose.yml      # Local PostgreSQL (and the API image)
└── Makefile                # The single entry point for every command
```

## Prerequisites

* [Node.js](https://nodejs.org/) 22 LTS and npm
* [uv](https://github.com/astral-sh/uv) for the Python backend
* Docker Engine (for PostgreSQL)

## Getting started

1. **Secrets.** Backend secrets live outside the repo, at `~/.config/secrets/mojo/.env` (override with `make ENV_FILE=...`). The Makefile is the only thing that loads them; it passes them to each command.
   ```bash
   mkdir -p ~/.config/secrets/mojo
   cp server/.env.example ~/.config/secrets/mojo/.env   # then fill in the values
   ```
   `SECRET_KEY` must be at least 32 characters (`openssl rand -hex 32`). `GEMINI_API_KEY` is optional; without it, AI features return canned responses.

2. **Install.**
   ```bash
   cd server && uv sync && cd ..
   make client-install
   make hooks            # optional: ruff on every commit
   ```

3. **Run.**
   ```bash
   make db-up            # PostgreSQL, waits until healthy
   make migrate          # apply migrations
   make dev              # API on http://localhost:8000 (docs at /docs)
   make client-dev       # web app on http://localhost:3000
   ```

## Everyday commands

Run `make` to list them all.

| Command | What it does |
| :--- | :--- |
| `make dev` / `make api` | Start the API (with or without starting the database first) |
| `make client-dev` | Start the Next.js dev server |
| `make migration m="..."` | Autogenerate a migration from model changes |
| `make migrate` / `make downgrade` | Apply all migrations / roll back the latest |
| `make test-db` then `make test` | Run the backend tests against a disposable database |
| `make lint` / `make format` | Check / fix server lint and formatting |
| `make typecheck` | mypy on the server, tsc on the client |
| `make check` | Lint, type checks and tests: what CI runs |
| `make api-types` | Regenerate the client's API types after changing server schemas |

CI (`.github/workflows/ci.yml`) runs the same checks, builds the client, and fails if `client/openapi.json` or the generated client types are out of date, so commit them after `make api-types`.
