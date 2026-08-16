# Architecture

The browser reaches Next.js on port 3000. Client requests use `NEXT_PUBLIC_API_URL`; server-rendered frontend code reaches FastAPI through Docker DNS at `backend:8000`. FastAPI uses async SQLAlchemy against `postgres:5432` and writes screenshots to the `backend_uploads` volume.

Ingestion is deliberately split into upload, image record, parsing job, parser, normalization/persistence, and analytics. The MVP uses in-process FastAPI background tasks, but a future Redis worker can consume the same parsing-job service without changing upload APIs or normalized match storage.
