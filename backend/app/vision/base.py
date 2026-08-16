from pathlib import Path
from typing import Protocol
from app.vision.models import ParsedMatch


class VisionParser(Protocol):
    async def parse_match_screenshot(self, image_path: Path) -> ParsedMatch: ...
