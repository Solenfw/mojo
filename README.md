# Linguasphere

**Advanced Japanese Learning Platform** - Think Duolingo for serious learners with deep Gamification, SRS (Spaced Repetition System), and NLP capabilities.

> **⚠️ Development Stage**: This project is still very much in development. Features are incomplete, and the codebase is evolving rapidly. Use at your own risk!

## Overview

Linguasphere is a modern web application for learning Japanese, featuring:

- **Gamification**: XP, streaks, hearts, leagues, daily quests
- **SRS**: SuperMemo-2 algorithm for vocabulary retention
- **NLP**: MeCab tokenization and OpenAI-powered grammar explanations
- **Social**: Leaderboards and community features
- **Admin**: B2B dashboard for user management

Built with:
- **Backend**: FastAPI (Python), SQLAlchemy 2.0 (async), PostgreSQL
- **Frontend**: Vue 3, Pinia, Vite
- **Deployment**: Docker, Alembic migrations

## Project Structure

```
LinguaSphere/
├── client/          # Vue 3 frontend
├── server/          # FastAPI backend
├── migrations/      # Alembic database migrations
├── docker-compose.yml
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+ (or Bun)
- PostgreSQL (or use Docker)
- Git
- [uv](https://github.com/astral-sh/uv) (fast Python package installer)
- [Bun](https://bun.sh/) (optional, fast JavaScript runtime)

### Backend Setup (server/)

1. **Navigate to server directory**:
   ```bash
   cd server
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create `.env` file in `server/`:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/linguasphere
   SECRET_KEY=your-secret-key-here
   OPENAI_API_KEY=your-openai-key
   ```

5. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

6. **Start the server**:
   ```bash
   uv uvicorn server.app.main:app --reload (or "make dev" if using Makefile)
   ```
   API will be available at `http://localhost:8000`

### Frontend Setup (client/)

1. **Navigate to client directory**:
   ```bash
   cd client
   ```

2. **Install dependencies**:
   ```bash
   bun install
   ```

3. **Set up environment variables**:
   Create `.env` file in `client/`:
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```

4. **Start development server**:
   ```bash
   bun run dev
   ```
   Frontend will be available at `http://localhost:5173`

### Docker Setup (Alternative)

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

## API Documentation

Once the server is running, visit `http://localhost:8000/docs` for interactive API docs (Swagger UI).

## Development Notes

- **Database**: Uses async SQLAlchemy with PostgreSQL. Models are in `server/app/db/models.py`.
- **Auth**: JWT-based authentication with OAuth2.
- **Testing**: No tests implemented yet.
- **Deployment**: Not configured yet.

## Contributing

This is a solo project for now. Feel free to open issues or PRs!

## License

MIT License
