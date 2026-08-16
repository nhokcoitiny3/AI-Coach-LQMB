from app.analytics.player_stats import player_summary


async def role_distribution(session, player_id):
    return (await player_summary(session, player_id))["role_distribution"]
