"""
Tests run against a real PostgreSQL database named by TEST_DATABASE_URL. Its schema is rebuilt
with the Alembic migrations at the start of each run. From the repo root:

    make test-db   # disposable postgres:17 on localhost:55432
    make test      # sets TEST_DATABASE_URL to it
"""

import os
from pathlib import Path

import pytest

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    raise pytest.UsageError("Set TEST_DATABASE_URL to a disposable PostgreSQL database (see tests/conftest.py).")

# Settings are read at import time, so point them at the test database before importing the app.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-characters")

import httpx  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402
from sqlalchemy.pool import NullPool  # noqa: E402

from app.api.deps import get_db  # noqa: E402
from app.db.database import Base  # noqa: E402
from app.main import create_app  # noqa: E402

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"
REFERENCE_TABLES = {"skill"}  # seeded by migrations, kept between tests


def _sync_url(url: str) -> str:
    return url.replace("postgresql+asyncpg://", "postgresql://", 1)


def _async_url(url: str) -> str:
    return url.replace("postgresql://", "postgresql+asyncpg://", 1)


@pytest.fixture(scope="session", autouse=True)
def _schema():
    engine = create_engine(_sync_url(TEST_DATABASE_URL))
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
    command.upgrade(Config(str(ALEMBIC_INI)), "head")
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def _clean_tables(_schema):
    yield
    tables = ", ".join(f'"{table.name}"' for table in Base.metadata.sorted_tables if table.name not in REFERENCE_TABLES)
    with _schema.begin() as conn:
        conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def session_factory():
    # NullPool: each test runs in its own event loop, so connections must not outlive it.
    engine = create_async_engine(_async_url(TEST_DATABASE_URL), poolclass=NullPool)
    yield async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    await engine.dispose()


@pytest.fixture
def app(session_factory) -> FastAPI:
    app = create_app()

    async def _get_db():
        async with session_factory() as db:
            yield db

    app.dependency_overrides[get_db] = _get_db
    return app


@pytest.fixture
async def api(app):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
