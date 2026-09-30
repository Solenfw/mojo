"""
Password hashing and token primitives. No FastAPI or database code here.

- Access tokens: short-lived JWTs carrying the user id (`sub`) and the auth session id (`sid`).
- Refresh tokens: opaque random strings; only their SHA-256 digest is stored server-side.
"""

import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import cache

import bcrypt
import jwt

from app.core.config import settings

BCRYPT_MAX_BYTES = 72
ACCESS_TOKEN_TYPE = "access"


class InvalidTokenError(Exception):
    """The access token is malformed, expired, or not an access token."""


@dataclass(frozen=True)
class AccessTokenClaims:
    user_id: int
    session_id: int


# Passwords


def get_password_hash(password: str) -> str:
    """Hash a password. Callers must reject passwords over BCRYPT_MAX_BYTES first; bcrypt raises on them."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    encoded = plain_password.encode("utf-8")
    if len(encoded) > BCRYPT_MAX_BYTES:
        return False
    return bcrypt.checkpw(encoded, hashed_password.encode("utf-8"))


@cache
def _dummy_password_hash() -> str:
    return get_password_hash(secrets.token_urlsafe(16))


def burn_password_check(plain_password: str) -> None:
    """Spend the same time as a real check, so unknown emails can't be told apart by response time."""
    verify_password(plain_password, _dummy_password_hash())


# Access tokens


def create_access_token(*, user_id: int, session_id: int) -> tuple[str, int]:
    """Return (token, lifetime in seconds)."""
    lifetime = timedelta(minutes=settings.access_token_expire_minutes)
    now = datetime.now(UTC)
    claims = {
        "sub": str(user_id),
        "sid": session_id,
        "type": ACCESS_TOKEN_TYPE,
        "iat": now,
        "exp": now + lifetime,
    }
    token = jwt.encode(claims, settings.secret_key, algorithm=settings.algorithm)
    return token, int(lifetime.total_seconds())


def decode_access_token(token: str) -> AccessTokenClaims:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={"require": ["sub", "sid", "type", "exp"]},
        )
    except jwt.PyJWTError as exc:
        raise InvalidTokenError from exc

    if payload["type"] != ACCESS_TOKEN_TYPE:
        raise InvalidTokenError
    try:
        return AccessTokenClaims(user_id=int(payload["sub"]), session_id=int(payload["sid"]))
    except (TypeError, ValueError) as exc:
        raise InvalidTokenError from exc


# Refresh tokens


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str) -> str:
    # Refresh tokens are 256-bit random values, so a fast unsalted digest is sufficient.
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
