# Database

PostgreSQL holds players, heroes, normalized matches, match-player links, imported images, and parsing jobs. All identifiers are UUIDs. `imported_images.sha256` and `matches.source_hash` prevent duplicate imports; parsing jobs retain the original parsed payload for review.

Run migrations only through Docker Compose: `docker compose exec backend alembic upgrade head`.
