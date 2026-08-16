async def comfort_score(hero: dict) -> float:
    # Deterministic blend of familiarity and success, capped at one.
    return round(min(1.0, hero["win_rate"] * 0.7 + min(hero["games"], 10) / 10 * 0.3), 2)
