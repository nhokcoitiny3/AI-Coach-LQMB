import hashlib
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import select
from app.datafeed.normalizer import normalize_name
from app.db.session import SessionLocal
from app.models import Hero, Match, ParsingJob
from app.vision.parser import get_vision_parser


async def process_job(job_id) -> None:
    async with SessionLocal() as session:
        job = await session.get(ParsingJob, job_id)
        if not job:
            return
        job.status = "processing"
        await session.commit()
        try:
            heroes = list((await session.scalars(select(Hero).order_by(Hero.name))).all())
            hero_lookup = {normalize_name(alias): hero for hero in heroes for alias in [hero.name, *hero.aliases] if normalize_name(alias)}
            parsed_matches = await get_vision_parser(sorted({alias for hero in heroes for alias in [hero.name, *hero.aliases] if alias})).parse_match_screenshot(Path(job.image.stored_path))
            data = {"matches": [parsed.to_dict() for parsed in parsed_matches]}
            valid = [hero_lookup.get(normalize_name(parsed.hero)) for parsed in parsed_matches]
            if any(hero is None or parsed.confidence < 0.8 for hero, parsed in zip(valid, parsed_matches)):
                job.status = "review"
                job.parsed_payload = data
                job.error = "One or more heroes were not found in catalog" if any(hero is None for hero in valid) else None
            else:
                saved = []
                for index, parsed in enumerate(parsed_matches):
                    row = parsed.to_dict(); row["hero"] = valid[index].name
                    match = await persist_match(session, job, job.image.player_id, row, source_hash=hashlib.sha256(f"{job.image.sha256}:{index}".encode()).hexdigest())
                    saved.append({**row, "match_id": str(match.id)})
                job.parsed_payload = {"matches": saved}
                job.status = "completed"
            await session.commit()
        except Exception as exc:
            job.status = "failed"
            job.error = str(exc)[:2000]
            await session.commit()


async def persist_match(session, job, player_id, data: dict, source_hash: str | None = None) -> Match:
    hero = await session.scalar(select(Hero).where(Hero.normalized_name == normalize_name(data["hero"])))
    if not hero:
        raise ValueError("Parsed hero is absent from the versioned catalog")
    match = Match(player_id=player_id, hero_id=hero.id, played_at=datetime.now(timezone.utc), role=data["role"], result=data["result"], kills=data["kills"], deaths=data["deaths"], assists=data["assists"], confidence=data.get("confidence", 1.0), source_hash=source_hash or job.image.sha256)
    session.add(match); await session.flush()
    job.parsed_payload = {**data, "match_id": str(match.id)}
    return match
