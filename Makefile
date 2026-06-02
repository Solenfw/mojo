dev:
	docker compose -f docker-compose.dev.yml up -d --no-recreate
	PYTHONPATH=server server/.venv/bin/python -m uvicorn app.main:app --reload

test:
	PYTHONPATH=server server/.venv/bin/python -m pytest -q tests
	
migrate:
	server/.venv/bin/python -m alembic upgrade head