import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = ROOT / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.append(str(SERVER_DIR))

import pytest
from fastapi.testclient import TestClient
from server.app.main import app as fastapi_app


@pytest.fixture(scope="session")
def client():
    return TestClient(fastapi_app)
