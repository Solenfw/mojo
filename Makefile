dev:
	uv run uvicorn server.app.main:app --reload

test:
	PYTHONPATH=server server/.venv/bin/python -m pytest -q tests