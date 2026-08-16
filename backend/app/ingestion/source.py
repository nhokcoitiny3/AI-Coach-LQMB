from typing import Protocol
from app.vision.models import ParsedMatch


class MatchDataSource(Protocol):
    async def fetch_matches(self, *args, **kwargs) -> list[ParsedMatch]: ...


class ScreenshotDataSource:
    def __init__(self, parser): self.parser = parser
    async def fetch_matches(self, image_path, **kwargs) -> list[ParsedMatch]:
        return [await self.parser.parse_match_screenshot(image_path)]
