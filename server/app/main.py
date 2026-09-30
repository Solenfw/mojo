from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_exception_handlers
from app.api.v1 import API_PREFIX
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.database import engine


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="mojo API",
        version="0.1.0",
        description="Backend API for mojo: Japanese learning with SRS, AI-rated practice and gamification.",
        lifespan=lifespan,
    )
    # Credentialed CORS (the refresh cookie) requires an explicit origin list, never a wildcard.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.frontend_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(api_router, prefix=API_PREFIX)

    @app.get("/healthz", tags=["health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
