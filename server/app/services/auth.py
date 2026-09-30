"""
Accounts and sign-in sessions.

A session is one AuthSession row per signed-in device. Access tokens name their session (`sid`),
so revoking the row signs that device out immediately. Refresh tokens rotate on every use.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import anyio
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    AccessTokenClaims,
    burn_password_check,
    create_access_token,
    generate_refresh_token,
    get_password_hash,
    hash_refresh_token,
    verify_password,
)
from app.models import AuthSession, User

# How long a just-rotated refresh token is still accepted. Covers two tabs refreshing at once:
# the slower one gets a new access token but no new refresh token (the browser already has it).
REFRESH_REUSE_GRACE = timedelta(seconds=30)


class DuplicateAccountError(Exception):
    def __init__(self, fields: list[str]) -> None:
        super().__init__(", ".join(fields))
        self.fields = fields


class InvalidCredentialsError(Exception):
    pass


class InvalidRefreshTokenError(Exception):
    pass


@dataclass(frozen=True)
class IssuedTokens:
    user_id: int
    access_token: str
    expires_in: int
    refresh_token: str | None  # None when a concurrent refresh already rotated it
    refresh_expires_at: datetime


def _utcnow() -> datetime:
    return datetime.now(UTC)


async def register_user(
    db: AsyncSession,
    *,
    username: str,
    full_name: str,
    email: str,
    password: str,
) -> User:
    taken = (
        await db.execute(select(User.email, User.username).where(or_(User.email == email, User.username == username)))
    ).all()
    conflicts = [
        field
        for field, value in (("email", email), ("username", username))
        if any(getattr(row, field) == value for row in taken)
    ]
    if conflicts:
        raise DuplicateAccountError(conflicts)

    user = User(
        username=username,
        full_name=full_name,
        email=email,
        hashed_password=await anyio.to_thread.run_sync(get_password_hash, password),
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError as exc:  # lost a race with a concurrent registration
        await db.rollback()
        raise DuplicateAccountError(["username" if "username" in str(exc.orig) else "email"]) from exc
    await db.refresh(user)
    return user


async def authenticate(db: AsyncSession, *, email: str, password: str) -> User:
    user = await db.scalar(select(User).where(User.email == email))
    if user is None:
        await anyio.to_thread.run_sync(burn_password_check, password)
        raise InvalidCredentialsError
    if not await anyio.to_thread.run_sync(verify_password, password, user.hashed_password):
        raise InvalidCredentialsError
    return user


async def start_session(db: AsyncSession, user: User, *, user_agent: str | None) -> IssuedTokens:
    now = _utcnow()
    refresh_token = generate_refresh_token()
    session = AuthSession(
        user_id=user.id,
        refresh_token_hash=hash_refresh_token(refresh_token),
        user_agent=user_agent[:255] if user_agent else None,
        last_used_at=now,
        expires_at=now + timedelta(days=settings.refresh_token_expire_days),
    )
    db.add(session)
    user.last_login_at = now
    await db.flush()

    access_token, expires_in = create_access_token(user_id=user.id, session_id=session.id)
    await db.commit()
    return IssuedTokens(user.id, access_token, expires_in, refresh_token, session.expires_at)


async def refresh_session(db: AsyncSession, refresh_token: str) -> IssuedTokens:
    """Rotate the refresh token and issue a new access token. Replaying an old token revokes the session."""
    digest = hash_refresh_token(refresh_token)
    # Row lock: concurrent refreshes of one session run one after another, so the second sees the rotation.
    session = await db.scalar(
        select(AuthSession)
        .where(or_(AuthSession.refresh_token_hash == digest, AuthSession.previous_token_hash == digest))
        .with_for_update()
    )
    now = _utcnow()
    if session is None or session.revoked_at is not None or session.expires_at <= now:
        raise InvalidRefreshTokenError

    session.last_used_at = now
    if session.refresh_token_hash != digest:
        if session.rotated_at is None or now - session.rotated_at > REFRESH_REUSE_GRACE:
            session.revoked_at = now
            await db.commit()
            raise InvalidRefreshTokenError
        new_refresh_token = None
    else:
        new_refresh_token = generate_refresh_token()
        session.previous_token_hash = digest
        session.refresh_token_hash = hash_refresh_token(new_refresh_token)
        session.rotated_at = now
        session.expires_at = now + timedelta(days=settings.refresh_token_expire_days)

    access_token, expires_in = create_access_token(user_id=session.user_id, session_id=session.id)
    await db.commit()
    return IssuedTokens(session.user_id, access_token, expires_in, new_refresh_token, session.expires_at)


async def revoke_session(db: AsyncSession, refresh_token: str) -> None:
    digest = hash_refresh_token(refresh_token)
    session = await db.scalar(
        select(AuthSession).where(
            or_(AuthSession.refresh_token_hash == digest, AuthSession.previous_token_hash == digest),
            AuthSession.revoked_at.is_(None),
        )
    )
    if session is not None:
        session.revoked_at = _utcnow()
        await db.commit()


async def load_session_user(db: AsyncSession, claims: AccessTokenClaims) -> User | None:
    """The token's user, provided its session is still active."""
    return await db.scalar(
        select(User)
        .join(AuthSession, AuthSession.user_id == User.id)
        .where(
            User.id == claims.user_id,
            AuthSession.id == claims.session_id,
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > func.now(),
        )
    )
