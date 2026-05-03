dev:
	PYTHONPATH=server server/.venv/bin/python -m uvicorn app.main:app --reload

test:
	PYTHONPATH=server server/.venv/bin/python -m pytest -q tests