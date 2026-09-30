import pytest

pytestmark = pytest.mark.anyio


async def test_health_check(api):
    response = await api.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_every_api_route_requires_sign_in(app, api):
    """Guards against a new router forgetting the CurrentUser dependency."""
    public = {
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/token",
        "/api/v1/auth/refresh",
        "/api/v1/auth/logout",
    }
    for route in app.routes:
        path = getattr(route, "path", "")
        if not path.startswith("/api/v1/") or path in public:
            continue
        for method in route.methods - {"HEAD"}:
            response = await api.request(method, path.replace("{", "").replace("}", "").replace("_id", "1"))
            assert response.status_code == 401, f"{method} {path} answered {response.status_code} without a token"
