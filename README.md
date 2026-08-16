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
```

Open the frontend at http://localhost:3000, the backend at http://localhost:8000, and API documentation at http://localhost:8000/docs.

## Docker-only commands

```bash
# development logs and shutdown
docker compose logs -f
docker compose down

# database, test, lint, formatting
docker compose exec backend alembic upgrade head
docker compose exec backend pytest
docker compose exec backend ruff check .
docker compose run --rm frontend-tools npm run lint
docker compose exec backend ruff format .
docker compose run --rm frontend-tools npm run format

# Crawl the configured public catalog/meta sources (rate-limited, with provenance)
docker compose exec backend python -m app.datafeed.cli
```

`Makefile` provides the same shortcuts when `make` is already available, but it is never required.

## Production

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Production has no source bind mounts and uses persistent database and upload volumes. PostgreSQL is internal-only by default.

## Environment

Copy `.env.example` to `.env`. The relevant values are `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DATABASE_URL`, `NEXT_PUBLIC_API_URL`, `VISION_PROVIDER`, `GEMINI_API_KEY`, `GEMINI_MODEL`, and `MAX_UPLOAD_SIZE_MB`. Leave `VISION_PROVIDER` empty until the real datafeed and vision provider are configured. Set `VISION_PROVIDER=gemini` only with `GEMINI_API_KEY` supplied through the ignored `.env` file or deployment secret.

If host port `8000` is already occupied, set `BACKEND_PORT=8001`. The frontend proxies browser API requests internally, so its public URL does not need to change.

## Current limitations

The project deliberately includes no synthetic hero, match, or vision data. Uploads remain pending until the versioned official hero catalog and a real vision provider are configured. Redis workers, OpenAI vision, authentication, and live AOV sources are planned follow-up work.

## Multi-source datafeed

`python -m app.datafeed.cli` runs the community-source collectors and writes only normalized records with source URL, region, patch, and collection time. Current collectors: LienQuanMobi, Arena of Valor Fandom Vietnam, ROVMeta, and Liquipedia APL. Sources may disagree or refer to different regions; analytics must query by `region` and `patch_version` rather than treating them as one global meta.
