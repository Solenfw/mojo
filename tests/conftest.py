import sys
from pathlib import Path
import asyncio
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = ROOT / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.append(str(SERVER_DIR))

import pytest
import httpx
from server.app.main import app as fastapi_app


class SyncASGIClient:
    def __init__(self, app):
        self.app = app

    def request(self, method: str, url: str, **kwargs):
        headers = dict(kwargs.pop("headers", {}) or {})
        data = kwargs.pop("data", None)
        if isinstance(data, dict):
            kwargs["content"] = urlencode(data)
            headers.setdefault("content-type", "application/x-www-form-urlencoded")
        elif data is not None:
            kwargs["content"] = data

        async def _request():
            transport = httpx.ASGITransport(app=self.app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.request(method, url, headers=headers, **kwargs)

        return asyncio.run(_request())

    def get(self, url: str, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.request("POST", url, **kwargs)


@pytest.fixture(scope="session")
def client():
    return SyncASGIClient(fastapi_app)
