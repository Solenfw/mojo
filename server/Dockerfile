# syntax=docker/dockerfile:1
#
# API image. Build context is server/:  docker build -t mojo-server server
# Configuration (DATABASE_URL, SECRET_KEY, ...) comes from the environment at run time; nothing is baked in.
#   run the API:     docker run -p 8000:8000 --env-file <secrets> mojo-server
#   run migrations:  docker run --rm --env-file <secrets> mojo-server alembic upgrade head

# ── build: resolve locked dependencies into /app/.venv ────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Only the lockfile and project metadata feed this layer, so code changes reuse the cached dependencies.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-install-project

# ── runtime: the same Python base, with just the venv and the code ──
FROM python:3.12-slim-bookworm

RUN groupadd --system app && useradd --system --gid app --no-create-home --home-dir /app app

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app alembic.ini ./
COPY --chown=app:app migrations ./migrations
COPY --chown=app:app app ./app

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
