from collections import Counter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Match


async def player_matches(session: AsyncSession, player_id):
    return list((await session.scalars(select(Match).where(Match.player_id == player_id).order_by(Match.played_at.desc()))).all())


async def player_summary(session: AsyncSession, player_id) -> dict:
    matches = await player_matches(session, player_id)
    wins = sum(m.result == "win" for m in matches)
    roles = Counter(m.role for m in matches)
    return {"games": len(matches), "wins": wins, "losses": len(matches) - wins, "win_rate": round(wins / len(matches), 2) if matches else 0, "main_role": roles.most_common(1)[0][0] if roles else "unknown", "role_distribution": dict(roles)}
