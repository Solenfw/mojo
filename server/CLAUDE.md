# Server

**Layering** (`server/app/`): `api/v1/<domain>.py` routers (collected in `api/v1/router.py`) validate input, call `services/`, and map service exceptions to `ApiError`. Services hold business rules (auth, SRS, gamification, practice) and know nothing about HTTP. `clients/` wrap blocking outside systems (Gemini in `audio.py`/`vision.py`, MeCab) and are called via `anyio.to_thread`. Domains share module names across `api/v1`, `models`, `schemas`. Import from packages: `from app.models import User`.

`scripts/seeder.py` is excluded from ruff pending rework.
