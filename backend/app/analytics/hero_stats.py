from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Hero, Match


async def hero_stats(session: AsyncSession, player_id) -> list[dict]:
    rows = (await session.execute(select(Match, Hero).join(Hero).where(Match.player_id == player_id))).all()
    stats = defaultdict(lambda: {"games": 0, "wins": 0})
    for match, hero in rows:
        item = stats[hero.name]; item["hero"] = hero.name; item["games"] += 1; item["wins"] += match.result == "win"
    return [{**x, "win_rate": round(x["wins"] / x["games"], 2)} for x in sorted(stats.values(), key=lambda x: x["games"], reverse=True)]
