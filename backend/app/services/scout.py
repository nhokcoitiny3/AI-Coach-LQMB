from app.analytics.comfort_score import comfort_score
from app.analytics.hero_stats import hero_stats
from app.analytics.player_stats import player_summary
from app.analytics.recent_form import recent_form
from app.datafeed.service import catalog_heroes


async def scout(session, player):
    summary = await player_summary(session, player.id)
    heroes = await hero_stats(session, player.id)
    for hero in heroes: hero["comfort_score"] = await comfort_score(hero)
    bans = [item["hero"] for item in sorted(heroes, key=lambda x: x["comfort_score"], reverse=True)[:3]]
    catalog = await catalog_heroes(session)
    picks = [hero for hero in catalog if hero["role"] == summary["main_role"] and hero["tier"] == "S"][:3]
    weak = sorted((hero for hero in heroes if hero["games"] >= 2), key=lambda hero: hero["win_rate"])[:2]
    return {"player": {"id": str(player.id), "name": player.name}, "main_role": summary["main_role"], "hero_pool": heroes, "recent_form": await recent_form(session, player.id), "role_distribution": summary["role_distribution"], "recommended_bans": bans, "recommended_picks": picks, "review_heroes": weak, **summary}
