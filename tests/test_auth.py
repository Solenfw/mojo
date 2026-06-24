import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from server.app.main import app
from server.app.api.v1 import auth
from server.app.db.schemas import (
    CheckLoginStateRequest,
    CheckUserByEmailOrPhoneRequest,
    LoginRequest,
    MarkUserLoggedInRequest,
    UserCreate,
)


class DummyResult:
    def __init__(self, user=None):
        self._user = user

    def scalars(self):
        return self

    def first(self):
        return self._user


class DummyDB:
    async def execute(self, query):
        return DummyResult()


async def fake_get_db():
    yield DummyDB()


@pytest.fixture(autouse=True)
def override_db_dependency():
    app.dependency_overrides[auth.get_db] = fake_get_db
    yield
    app.dependency_overrides.clear()


def test_login_access_token_missing_form_data(client):
    response = client.post("/api/v1/auth/login/access-token", data={})
    assert response.status_code == 422


def test_login_access_token_invalid_credentials(client):
    form_data = OAuth2PasswordRequestForm(
        username="bad@example.com",
        password="wrong",
        scope="",
        grant_type=None,
        client_id=None,
        client_secret=None,
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(auth.login_access_token(form_data, DummyDB()))

    assert exc_info.value.status_code == 401


class DummyRegisterDB:
    def __init__(self):
        self._responses = [DummyResult(), DummyResult()]
        self.added_user = None

    async def execute(self, query):
        return self._responses.pop(0)

    def add(self, user):
        self.added_user = user

    async def commit(self):
        return None

    async def refresh(self, user):
        user.id = 1001


class DummyLoginDB:
    def __init__(self, user):
        self._responses = [DummyResult(user)]

    async def execute(self, query):
        return self._responses.pop(0)


class DummyMutableDB:
    def __init__(self, responses):
        self._responses = list(responses)
        self.committed = False
        self.refreshed = False

    async def execute(self, query):
        return self._responses.pop(0)

    async def commit(self):
        self.committed = True

    async def refresh(self, user):
        self.refreshed = True


def test_register_returns_dd_payload():
    payload = UserCreate(
        fullName="Dao Van Hung",
        email="hungdao@gmail.com",
        phone="0988888888",
        passwordHash="plain-password",
    )

    response = asyncio.run(auth.register(payload, DummyRegisterDB()))

    assert response["success"] is True
    assert response["businessCode"] == "LMS-RESP-SUCCESS"
    assert response["message"] == "Created successfully."
    assert response["data"]["userId"] == 1001
    assert response["data"]["accountStatus"] == "pending_verification"
    assert response["data"]["isLoggedIn"] is False


def test_login_returns_dd_payload(monkeypatch: pytest.MonkeyPatch):
    user = SimpleNamespace(
        id=1001,
        email="hungdao@gmail.com",
        phone="0988888888",
        session_token=None,
        is_logged_in=False,
        last_login_at=None,
        updated_at=None,
    )

    async def fake_authenticate_user(db, email_or_phone: str, password: str):
        assert email_or_phone == "hungdao@gmail.com"
        assert password == "plain-password"
        return user

    async def fake_mark_logged_in(db, user_obj, *, token: str):
        user_obj.session_token = token
        user_obj.is_logged_in = True

    monkeypatch.setattr(auth, "authenticate_user", fake_authenticate_user)
    monkeypatch.setattr(auth, "_mark_user_logged_in", fake_mark_logged_in)

    response = asyncio.run(
        auth.login(
            LoginRequest(
                emailOrPhone="hungdao@gmail.com",
                passwordHash="plain-password",
                deviceId="WEB-001",
                platform="web",
            ),
            DummyLoginDB(user),
        )
    )

    assert response["success"] is True
    assert response["businessCode"] == "LMS-AUTH-LOGIN-SUCCESS"
    assert response["message"] == "Login completed successfully."
    assert response["data"]["userId"] == 1001
    assert response["data"]["accessToken"]
    assert response["data"]["refreshToken"]


def test_check_login_state_returns_dd_payload():
    user = SimpleNamespace(id=1001, session_token="session-123", is_logged_in=True)
    response = asyncio.run(
        auth.check_login_state(
            CheckLoginStateRequest(sessionToken="session-123"),
            token="session-123",
            db=DummyMutableDB([DummyResult(user)]),
        )
    )

    assert response["businessCode"] == "LMS-RESP-SUCCESS"
    assert response["data"] == {
        "loginState": True,
        "userId": 1001,
        "redirectScreen": "HOME",
    }


def test_check_user_by_email_or_phone_returns_exists_false():
    response = asyncio.run(
        auth.check_user_by_email_or_phone(
            CheckUserByEmailOrPhoneRequest(email="newuser@example.com"),
            DummyMutableDB([DummyResult()]),
        )
    )

    assert response["success"] is True
    assert response["businessCode"] == "LMS-RESP-SUCCESS"
    assert response["data"] == {"existsFlag": False, "userId": None}


def test_mark_user_logged_in_returns_dd_payload():
    current_user = SimpleNamespace(id=1001)
    target_user = SimpleNamespace(
        id=1001,
        is_logged_in=False,
        last_login_at=None,
        updated_at=None,
    )
    db = DummyMutableDB([DummyResult(target_user)])

    response = asyncio.run(
        auth.mark_user_logged_in(
            MarkUserLoggedInRequest(userId=1001, isLoggedIn=True),
            current_user=current_user,
            db=db,
        )
    )

    assert response["success"] is True
    assert response["businessCode"] == "LMS-AUTH-LOGIN-SUCCESS"
    assert response["data"]["userId"] == 1001
    assert response["data"]["isLoggedIn"] is True
    assert response["data"]["redirectScreen"] == "HOME"
    assert response["timestamp"]
    assert db.committed is True
    assert db.refreshed is True
