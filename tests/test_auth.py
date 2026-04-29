import pytest
from server.app.main import app
from server.app.api.v1 import auth


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
    response = client.post("/api/v1/login/access-token", data={})
    assert response.status_code == 422


def test_login_access_token_invalid_credentials(client):
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "bad@example.com", "password": "wrong"},
    )
    assert response.status_code == 401
