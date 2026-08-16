import pytest
from app.analytics.comfort_score import comfort_score
from app.vision.mock import MockVisionParser

@pytest.mark.asyncio
async def test_comfort_score_is_deterministic():
    assert await comfort_score({"games": 10, "win_rate": 0.5}) == 0.65

@pytest.mark.asyncio
async def test_mock_parser_is_deterministic(tmp_path):
    path = tmp_path / "screen.png"; path.write_bytes(b"fixture")
    assert (await MockVisionParser().parse_match_screenshot(path)).to_dict() == (await MockVisionParser().parse_match_screenshot(path)).to_dict()
