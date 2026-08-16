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
            parsed = await get_vision_parser([hero.name for hero in heroes]).parse_match_screenshot(Path(job.image.stored_path))
            data = parsed.to_dict()
            hero = await session.scalar(select(Hero).where(Hero.normalized_name == normalize_name(parsed.hero)))
            if hero is None or parsed.confidence < 0.8:
                job.status = "review"
                job.parsed_payload = data
                job.error = "Hero not found in catalog" if hero is None else None
            else:
                data["hero"] = hero.name
                await persist_match(session, job, job.image.player_id, data)
                job.status = "completed"
            await session.commit()
        except Exception as exc:
            job.status = "failed"
            job.error = str(exc)[:2000]
            await session.commit()


async def persist_match(session, job, player_id, data: dict) -> Match:
    hero = await session.scalar(select(Hero).where(Hero.normalized_name == normalize_name(data["hero"])))
    if not hero:
        raise ValueError("Parsed hero is absent from the versioned catalog")
    match = Match(player_id=player_id, hero_id=hero.id, played_at=datetime.now(timezone.utc), role=data["role"], result=data["result"], kills=data["kills"], deaths=data["deaths"], assists=data["assists"], confidence=data.get("confidence", 1.0), source_hash=job.image.sha256)
    session.add(match); await session.flush()
    job.parsed_payload = {**data, "match_id": str(match.id)}
    return match
