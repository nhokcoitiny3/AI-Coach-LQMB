.PHONY: up down build logs backend-shell frontend-shell db-shell migrate migration test lint format clean
up:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
down:
	docker compose down
build:
	docker compose build
logs:
	docker compose logs -f
backend-shell:
	docker compose exec backend sh
frontend-shell:
	docker compose exec frontend sh
db-shell:
	docker compose exec postgres psql -U $${POSTGRES_USER:-postgres} -d $${POSTGRES_DB:-lien_quan}
migrate:
	docker compose exec backend alembic upgrade head
migration:
	docker compose exec backend alembic revision --autogenerate -m "$(MESSAGE)"
test:
	docker compose exec backend pytest
lint:
	docker compose exec backend ruff check . && docker compose run --rm frontend-tools npm run lint
format:
	docker compose exec backend ruff format . && docker compose run --rm frontend-tools npm run format
clean:
	docker compose down -v --remove-orphans
