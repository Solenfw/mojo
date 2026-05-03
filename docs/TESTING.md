# Testing Instructions

This document explains how to run the backend tests and verify the FastAPI docs.

## 1. Prepare the environment

From the repository root:

```bash
cd /home/solenfw/projects/LinguaSphere
```

### If you already have the backend virtual environment:

```bash
source server/.venv/bin/activate
```

### If you need to create it first:

```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
```

## 2. Create or verify the environment file

The backend code loads environment variables from `.env` in the project root.

Create or update `.env` with at least:

```env
DATABASE_URL=postgresql://user:password@localhost/linguasphere
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
```

> The tests in `tests/` patch the database dependency, so they will not require a real database connection.

## 3. Run the test suite

From the repository root:

```bash
pytest -q
```

This will run all tests in `tests/`.

## 4. Run a specific test file

To run only the auth tests:

```bash
pytest -q tests/test_auth.py
```

To run only the model tests:

```bash
pytest -q tests/test_models.py
```

## 5. Start the backend and check `/docs`

Start the FastAPI server from the `server/` directory:

```bash
cd server
source .venv/bin/activate
uvicorn app.main:app --reload
```

Then open:

- `http://localhost:8000/docs` for Swagger UI
- `http://localhost:8000/redoc` for ReDoc

## 6. Notes

- The `tests/conftest.py` file uses `TestClient` and imports `server.app.main:app`.
- If the server fails to start because of missing env variables, make sure `.env` is present and contains `SECRET_KEY`.
- If you want to run server tests against Docker, make sure the same `.env` values are available in the container.
