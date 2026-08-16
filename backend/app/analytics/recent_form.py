from app.analytics.player_stats import player_matches


async def recent_form(session, player_id) -> float:
    matches = (await player_matches(session, player_id))[:10]
    if not matches: return 0.0
    weighted = sum((1.2 if m.result == "win" else 0) * (len(matches) - i) for i, m in enumerate(matches))
    return round(weighted / sum(range(1, len(matches) + 1)), 2)
