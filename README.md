# Liên Quân AI Coach

Docker-first MVP for importing match-result screenshots and scouting player hero pools. The host needs Docker Desktop with Docker Compose only; Python, Node.js, PostgreSQL, and npm are all contained in images.

Dockerfiles use persistent BuildKit caches for pip, npm, and Next.js build artifacts. Dependency layers are also keyed only by `requirements.txt` and `package-lock.json`, so ordinary source changes do not download libraries again. Avoid `docker builder prune` when you want to retain these caches.

## Start locally

```bash
git clone https://github.com/nhokcoitiny3/AI-Coach-LQMB.git
cd AI-Coach-LQMB
cp .env.example .env
docker compose build
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.db.seed
```

Open the frontend at http://localhost:3000, the backend at http://localhost:8000, and API documentation at http://localhost:8000/docs.

## Docker-only commands

```bash
# development logs and shutdown
docker compose logs -f
docker compose down

# database, seed, test, lint, formatting
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.db.seed
docker compose exec backend pytest
docker compose exec backend ruff check .
docker compose run --rm frontend-tools npm run lint
docker compose exec backend ruff format .
docker compose run --rm frontend-tools npm run format
```

`Makefile` provides the same shortcuts when `make` is already available, but it is never required.

## Production

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Production has no source bind mounts and uses persistent database and upload volumes. PostgreSQL is internal-only by default.

## Environment

Copy `.env.example` to `.env`. The relevant values are `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DATABASE_URL`, `NEXT_PUBLIC_API_URL`, `VISION_PROVIDER`, `VISION_API_KEY`, and `MAX_UPLOAD_SIZE_MB`. The MVP supports `VISION_PROVIDER=mock`; no external AI key is necessary.

If host port `8000` is already occupied, set `BACKEND_PORT=8001`. The frontend proxies browser API requests internally, so its public URL does not need to change.

## Current limitations

Mock Vision derives realistic deterministic results from image bytes rather than reading game UI. Background parsing is process-local, so jobs do not survive a backend restart while actively processing. Redis workers, OpenAI vision, authentication, and live AOV sources are planned follow-up work.
