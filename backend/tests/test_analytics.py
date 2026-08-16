import pytest

from app.analytics.comfort_score import comfort_score


@pytest.mark.asyncio
async def test_comfort_score_is_deterministic():
    assert await comfort_score({"games": 10, "win_rate": 0.5}) == 0.65
