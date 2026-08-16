from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models import Hero, Match, ParsingJob
from app.vision.parser import get_vision_parser


async def process_job(job_id: UUID) -> None:
    async with SessionLocal() as session:
        job = await session.get(ParsingJob, job_id)
        if not job: return
        job.status = "processing"; await session.commit()
        try:
            parsed = await get_vision_parser().parse_match_screenshot(Path(job.image.stored_path))
            job.parsed_payload = parsed.to_dict()
            if parsed.confidence < 0.8:
                job.status = "review"
            else:
                await persist_match(session, job, job.image.player_id, parsed.to_dict())
                job.status = "completed"
            await session.commit()
        except Exception as exc:
            job.status = "failed"; job.error = str(exc); await session.commit()


async def persist_match(session, job, player_id, data: dict) -> Match:
    hero = await session.scalar(select(Hero).where(Hero.name == data["hero"]))
    if not hero:
        hero = Hero(name=data["hero"], role=data["role"]); session.add(hero); await session.flush()
    match = Match(player_id=player_id, hero_id=hero.id, played_at=datetime.now(timezone.utc), role=data["role"], result=data["result"], kills=data["kills"], deaths=data["deaths"], assists=data["assists"], confidence=data.get("confidence", 1.0), source_hash=job.image.sha256)
    session.add(match); await session.flush()
    job.parsed_payload = {**data, "match_id": str(match.id)}
    return match
