# LinguaSphere

LinguaSphere is an AI-assisted Japanese language learning platform designed for professionals looking to build JLPT N5 proficiency. It features a FastAPI backend and a Next.js frontend, integrating Google Gemini for real-time conversation (Kaiwa) and writing feedback.

## Architecture & Layout

The project is structured as a monorepo, keeping the backend and frontend code bases isolated while sharing a unified migration and deployment workflow:

```text
LinguaSphere/
├── client/              # Next.js frontend (React 19, Tailwind CSS v4, npm)
├── server/              # FastAPI backend (Python 3.12, managed by uv)
│   └── app/
│       ├── api/         # v1 router endpoints (auth, srs, gamification, etc.)
│       ├── core/        # Configurations and security
│       ├── db/          # Database connection, schemas, and SQLAlchemy models
│       └── services/    # Engines (SRS, gamification, AI services)
├── migrations/          # Alembic schema migrations
├── tests/               # Backend tests
├── docker-compose.yml   # Local PostgreSQL service
├── alembic.ini          # Alembic database configuration
├── Makefile             # Backend dev/test shortcuts
└── README.md
```

## Prerequisites

Ensure you have the following installed locally:
*   [Node.js](https://nodejs.org/) (LTS recommended) and **npm**
*   [uv](https://github.com/astral-sh/uv) (Backend Python package manager & workflow tool)
*   [Docker Desktop](https://www.docker.com/) / Docker Engine (for PostgreSQL)

---

## Getting Started

### 1. Environment Configuration

Clone the configuration files and update them with your local credentials.

**Backend (.env at project root):**
```bash
cp .env.example .env
```
Ensure your database connection details and secret key are set:
```env
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=lingua_sphere_db
DATABASE_URL=postgresql://your_postgres_user:your_postgres_password@localhost:5432/lingua_sphere_db
SECRET_KEY=your_development_secret_key
```

**Frontend (client/.env.local):**
```bash
cp client/.env.example client/.env.local
```
Update your `client/.env.local` file with your Gemini API Key to enable AI feedback features:
```env
GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY"
NEXT_PUBLIC_API_URL="http://localhost:8000"
```

### 2. Backend & Database Setup

1.  **Sync Python dependencies:**
    Use `uv` to install the environment and packages defined in `server/pyproject.toml`:
    ```bash
    uv sync --project server
    ```

2.  **Start the Database:**
    Run the PostgreSQL container in the background:
    ```bash
    docker compose up -d 
    ```

3.  **Run Migrations:**
    Because this database uses a code-first approach managed by Alembic, apply the initial schema migration to create the tables:
    ```bash
    alembic upgrade head
    ```

### 3. Frontend Setup

1.  **Install dependencies:**
    Navigate to the `client` directory and install the Node modules:
    ```bash
    cd client
    npm install
    cd ..
    ```

2.  **Start the Next.js development server:**
    ```bash
    cd client
    npm run dev
    ```
    The web interface will be available at `http://localhost:3000`.

---

## Development & Operations

### Running the API Server

Start the FastAPI application with live-reloading enabled:
```bash
make dev
```

*   **API Base URL:** `http://localhost:8000`
*   **Interactive Documentation (Swagger):** `http://localhost:8000/docs`
*   **Health Status Endpoint:** `http://localhost:8000/healthz`

### Working with Database Migrations (Alembic)

The database schema is defined in `server/app/db/models.py`. When you modify models, always use Alembic to generate and apply migrations.

1.  **Generate a new migration script:**
    ```bash
    alembic revision --autogenerate -m "your description"
    ```
2.  **Verify the generated script:**
    Check the new Python file inside `migrations/versions/` to verify it correctly maps your changes before applying them.
3.  **Apply migrations:**
    ```bash
    alembic upgrade head
    ```

### Running Tests

Run the test suite to verify backend status, authentication logic, and model definitions:
```bash
make test
```

---

## Automation Shortcuts (Makefile)

A `Makefile` is provided for standard operations:

| Command | Action |
| :--- | :--- |
| `make dev` | Starts the PostgreSQL container and runs the FastAPI application. |
| `make test` | Runs the backend test suite via pytest. |
| `make migrate` | Applies any outstanding Alembic migrations to the database. |