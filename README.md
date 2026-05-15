# LinguaSphere

AI-assisted Japanese learning platform with a FastAPI backend and a Next.js frontend.

> Development status: this project is still evolving. Some routes and features are prototype-level and may change quickly.

## Stack

- Frontend: Next.js 16, React 19, TypeScript, Tailwind CSS
- Frontend package manager/runtime: Bun
- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL
- Backend package manager/runtime: uv
- AI: Google Gemini integration in the client

## Repository Layout

```text
LinguaSphere/
├── client/              # Next.js frontend
├── server/              # FastAPI backend project managed by uv
├── migrations/          # Alembic migrations
├── tests/               # Backend tests
├── docker-compose.yml   # Local PostgreSQL service
├── alembic.ini          # Alembic config
├── Makefile             # Backend dev/test shortcuts
└── README.md
```

## Prerequisites

- Bun
- uv
- Python 3.12+
- PostgreSQL, or Docker for the included PostgreSQL service

## Environment

Create the root environment file:

```bash
cp .env.example .env
```

The root `.env` is used by Docker Compose, Alembic, and backend commands run from the repository root.

Required backend values:

```env
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_db
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/your_db
SECRET_KEY=your-secret-key
```

Create the frontend environment file:

```bash
cp client/.env.example client/.env.local
```

Set `GEMINI_API_KEY` in `client/.env.local` if you are using Gemini-backed conversation or feedback features.

## Backend Setup

Install backend dependencies with uv:

```bash
uv sync --project server
```

Start PostgreSQL:

```bash
docker compose up -d db
```

Run migrations from the repository root:

```bash
PYTHONPATH=server uv run --project server alembic upgrade head
```

Start the API:

```bash
PYTHONPATH=server uv run --project server uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`.

Useful backend endpoints:

- Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/healthz`

## Frontend Setup

Install frontend dependencies with Bun:

```bash
cd client
bun install
```

Start the frontend:

```bash
bun run dev
```

The Next.js dev server runs at `http://localhost:3000` by default.

## Common Commands

From the repository root:

```bash
# Backend
uv sync --project server
PYTHONPATH=server uv run --project server uvicorn app.main:app --reload
PYTHONPATH=server uv run --project server pytest -q tests
PYTHONPATH=server uv run --project server alembic upgrade head

# Database
docker compose up -d db
docker compose down

# Frontend
cd client
bun install
bun run dev
bun run type-check
bun run build
```

The `Makefile` also provides backend shortcuts that use the uv-created virtual environment:

```bash
make dev
make test
```

## Notes

- The backend package is in `server/`, but commands that need `alembic.ini`, `migrations/`, or the root `.env` should be run from the repository root.
- The frontend is a Next.js App Router app under `client/src/app`.
- Docker Compose currently provisions PostgreSQL only; the frontend and backend are run locally with Bun and uv.

## License

MIT. See [LICENSE](LICENSE) if present in your checkout.
