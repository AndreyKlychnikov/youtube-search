.ONESHELL: all

install:
	@poetry install --no-root

compose:
	@docker-compose up -d

run-services:
	@docker-compose up -d db elasticsearch kibana redis
	@cp compose.env .env
	@poetry run alembic upgrade head
	@poetry run python app/prerun.py

run-local-app:
	@poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-local-celery:
	@poetry run celery -A app.tasks.main worker --loglevel=DEBUG

migrate:
	@poetry run alembic upgrade head
