from datetime import datetime, timezone
from sqlalchemy import select
from app.models import Hero, Match


async def persist_match(session, job, player_id, data: dict) -> Match:
    hero = await session.scalar(select(Hero).where(Hero.name == data["hero"]))
    if not hero:
        hero = Hero(name=data["hero"], role=data["role"]); session.add(hero); await session.flush()
    match = Match(player_id=player_id, hero_id=hero.id, played_at=datetime.now(timezone.utc), role=data["role"], result=data["result"], kills=data["kills"], deaths=data["deaths"], assists=data["assists"], confidence=data.get("confidence", 1.0), source_hash=job.image.sha256)
    session.add(match); await session.flush()
    job.parsed_payload = {**data, "match_id": str(match.id)}
    return match
