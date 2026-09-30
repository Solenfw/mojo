"""
Request-scoped dependencies. Routes use the Annotated aliases:

    async def handler(db: DbSession, user: CurrentUser): ...
"""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.api.errors import AUTH_SESSION_INVALID, unauthorized
from app.api.v1 import API_PREFIX
from app.core.security import InvalidTokenError, decode_access_token
from app.db.database import SessionLocal
from app.services import auth as auth_service

# auto_error=False so a missing header gets the same ErrorResponse body as a bad token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{API_PREFIX}/auth/token", auto_error=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as db:
        yield db


DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: DbSession,
) -> models.User:
    if token is None:
        raise unauthorized("Not authenticated.", AUTH_SESSION_INVALID)
    try:
        claims = decode_access_token(token)
    except InvalidTokenError:
        raise unauthorized("Could not validate credentials.", AUTH_SESSION_INVALID) from None

    user = await auth_service.load_session_user(db, claims)
    if user is None:
        raise unauthorized("Session has ended. Please sign in again.", AUTH_SESSION_INVALID)
    return user


CurrentUser = Annotated[models.User, Depends(get_current_user)]
