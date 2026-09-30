from datetime import UTC, datetime, timedelta

import jwt
import pytest
from sqlalchemy import select

from app.api.v1.auth import REFRESH_COOKIE, REFRESH_COOKIE_PATH
from app.core.config import settings
from app.models import AuthSession, User
from app.services import auth as auth_service

pytestmark = pytest.mark.anyio

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
REFRESH = "/api/v1/auth/refresh"
LOGOUT = "/api/v1/auth/logout"
ME = "/api/v1/users/me"

ALEX = {"username": "alexj", "fullName": "Alex Johnson", "email": "alex@example.com", "password": "correct-horse"}


async def register(api, **overrides):
    return await api.post(REGISTER, json={**ALEX, **overrides})


async def login(api, email=ALEX["email"], password=ALEX["password"]):
    return await api.post(LOGIN, json={"email": email, "password": password})


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def set_cookie_header(response) -> str:
    return response.headers.get("set-cookie", "")


# Registration


async def test_register_creates_account_with_hashed_password(api, session_factory):
    response = await register(api)

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"] == {"userId": 1, "isOnboarded": False}
    async with session_factory() as db:
        user = await db.scalar(select(User))
    assert user.username == "alexj"
    assert user.hashed_password.startswith("$2b$")
    assert "correct-horse" not in user.hashed_password


async def test_register_rejects_duplicate_email_case_insensitively(api):
    await register(api)

    response = await register(api, username="other", email="ALEX@Example.com")

    assert response.status_code == 409
    assert response.json()["errors"] == [{"field": "email", "message": "Email already exists."}]


async def test_register_rejects_duplicate_username(api):
    await register(api)

    response = await register(api, email="someone@example.com")

    assert response.status_code == 409
    assert [error["field"] for error in response.json()["errors"]] == ["username"]


@pytest.mark.parametrize(
    "overrides",
    [
        {"password": "short"},
        {"password": "パスワード" * 5},  # 75 bytes in UTF-8: over bcrypt's limit
        {"username": "has spaces"},
        {"email": "not-an-email"},
    ],
)
async def test_register_validates_input(api, overrides):
    response = await register(api, **overrides)

    assert response.status_code == 422


# Login


async def test_login_returns_access_token_and_sets_refresh_cookie(api, session_factory):
    await register(api)

    response = await login(api)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["userId"] == 1
    assert data["tokenType"] == "bearer"
    assert data["expiresIn"] == settings.access_token_expire_minutes * 60
    assert "refreshToken" not in data
    cookie = set_cookie_header(response).lower()
    assert f"{REFRESH_COOKIE}=" in cookie
    assert "httponly" in cookie
    assert f"path={REFRESH_COOKIE_PATH}" in cookie
    assert "samesite=lax" in cookie

    me = await api.get(ME, headers=bearer(data["accessToken"]))
    assert me.status_code == 200
    assert me.json()["email"] == ALEX["email"]
    assert me.json()["lastLoginAt"] is not None

    async with session_factory() as db:
        session = await db.scalar(select(AuthSession))
    assert session.user_id == 1
    assert session.refresh_token_hash != api.cookies[REFRESH_COOKIE]  # only the digest is stored


async def test_login_is_case_insensitive_on_email(api):
    await register(api)

    response = await login(api, email="Alex@Example.COM")

    assert response.status_code == 200


async def test_login_failures_are_indistinguishable(api):
    await register(api)

    wrong_password = await login(api, password="wrong-password")
    unknown_email = await login(api, email="nobody@example.com")

    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.headers["www-authenticate"] == "Bearer"
    strip = lambda body: {key: value for key, value in body.items() if key != "timestamp"}  # noqa: E731
    assert strip(wrong_password.json()) == strip(unknown_email.json())
    assert REFRESH_COOKIE not in api.cookies


async def test_each_login_is_a_separate_session(api, session_factory):
    await register(api)

    first = (await login(api)).json()["data"]["accessToken"]
    second = (await login(api)).json()["data"]["accessToken"]
    await api.post(LOGOUT)  # signs out the device holding the latest cookie only

    assert (await api.get(ME, headers=bearer(first))).status_code == 200
    assert (await api.get(ME, headers=bearer(second))).status_code == 401


async def test_oauth2_form_endpoint_for_swagger(api):
    await register(api)

    response = await api.post(
        "/api/v1/auth/token",
        data={"username": ALEX["email"], "password": ALEX["password"]},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert (await api.get(ME, headers=bearer(response.json()["access_token"]))).status_code == 200


# Access token checks


async def test_me_requires_a_token(api):
    response = await api.get(ME)

    assert response.status_code == 401
    assert response.json()["businessCode"] == "LMS-AUTH-SESSION-INVALID"


@pytest.mark.parametrize("token_type", ["refresh", None])
async def test_rejects_jwts_that_are_not_access_tokens(api, token_type):
    await register(api)
    await login(api)
    claims = {"sub": "1", "sid": 1, "exp": datetime.now(UTC) + timedelta(minutes=5)}
    if token_type:
        claims["type"] = token_type
    forged = jwt.encode(claims, settings.secret_key, algorithm=settings.algorithm)

    response = await api.get(ME, headers=bearer(forged))

    assert response.status_code == 401


async def test_rejects_expired_and_tampered_tokens(api):
    await register(api)
    token = (await login(api)).json()["data"]["accessToken"]
    expired = jwt.encode(
        {"sub": "1", "sid": 1, "type": "access", "exp": datetime.now(UTC) - timedelta(seconds=1)},
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    assert (await api.get(ME, headers=bearer(expired))).status_code == 401
    assert (await api.get(ME, headers=bearer(token[:-2] + "xx"))).status_code == 401


async def test_refresh_token_cannot_be_used_as_bearer(api):
    await register(api)
    await login(api)

    response = await api.get(ME, headers=bearer(api.cookies[REFRESH_COOKIE]))

    assert response.status_code == 401


# Refresh


async def test_refresh_rotates_cookie_and_issues_working_token(api):
    await register(api)
    await login(api)
    old_cookie = api.cookies[REFRESH_COOKIE]

    response = await api.post(REFRESH)

    assert response.status_code == 200
    new_cookie = api.cookies[REFRESH_COOKIE]
    assert new_cookie != old_cookie
    token = response.json()["data"]["accessToken"]
    assert (await api.get(ME, headers=bearer(token))).status_code == 200


async def test_refresh_without_cookie_is_rejected(api):
    response = await api.post(REFRESH)

    assert response.status_code == 401
    assert response.json()["businessCode"] == "LMS-AUTH-SESSION-INVALID"


async def test_concurrent_refresh_within_grace_period_succeeds_without_rotating(api):
    await register(api)
    await login(api)
    old_cookie = api.cookies[REFRESH_COOKIE]
    await api.post(REFRESH)  # first tab rotates
    newest_cookie = api.cookies[REFRESH_COOKIE]

    # Second tab's request was already in flight with the old cookie.
    api.cookies.set(REFRESH_COOKIE, old_cookie, path=REFRESH_COOKIE_PATH)
    response = await api.post(REFRESH)

    assert response.status_code == 200
    assert f"{REFRESH_COOKIE}=" not in set_cookie_header(response)
    api.cookies.set(REFRESH_COOKIE, newest_cookie, path=REFRESH_COOKIE_PATH)
    assert (await api.post(REFRESH)).status_code == 200


async def test_reusing_a_rotated_refresh_token_revokes_the_session(api, monkeypatch):
    monkeypatch.setattr(auth_service, "REFRESH_REUSE_GRACE", timedelta(0))
    await register(api)
    await login(api)
    stolen = api.cookies[REFRESH_COOKIE]
    token = (await api.post(REFRESH)).json()["data"]["accessToken"]
    legit_cookie = api.cookies[REFRESH_COOKIE]

    api.cookies.set(REFRESH_COOKIE, stolen, path=REFRESH_COOKIE_PATH)
    replay = await api.post(REFRESH)

    assert replay.status_code == 401
    assert f'{REFRESH_COOKIE}=""' in set_cookie_header(replay)  # tells the browser to drop it
    api.cookies.set(REFRESH_COOKIE, legit_cookie, path=REFRESH_COOKIE_PATH)
    assert (await api.post(REFRESH)).status_code == 401
    assert (await api.get(ME, headers=bearer(token))).status_code == 401


async def test_expired_session_cannot_refresh(api, session_factory):
    await register(api)
    await login(api)
    async with session_factory() as db:
        session = await db.scalar(select(AuthSession))
        session.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        await db.commit()

    assert (await api.post(REFRESH)).status_code == 401


# Logout


async def test_logout_ends_session_immediately(api):
    await register(api)
    token = (await login(api)).json()["data"]["accessToken"]
    refresh_cookie = api.cookies[REFRESH_COOKIE]

    response = await api.post(LOGOUT)

    assert response.status_code == 204
    assert f'{REFRESH_COOKIE}=""' in set_cookie_header(response)
    assert (await api.get(ME, headers=bearer(token))).status_code == 401
    api.cookies.set(REFRESH_COOKIE, refresh_cookie, path=REFRESH_COOKIE_PATH)
    assert (await api.post(REFRESH)).status_code == 401


async def test_logout_is_idempotent(api):
    assert (await api.post(LOGOUT)).status_code == 204
    assert (await api.post(LOGOUT)).status_code == 204
