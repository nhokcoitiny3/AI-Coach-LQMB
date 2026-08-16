import hashlib
from pathlib import Path
from app.vision.models import ParsedMatch


class MockVisionParser:
    """Deterministic fixture parser; byte changes provide varied demo results."""
    choices = [("Aoi", "jungle"), ("Tel'Annas", "dragon"), ("Yena", "slayer"), ("Krixi", "mid"), ("Alice", "support")]

    async def parse_match_screenshot(self, image_path: Path) -> ParsedMatch:
        value = int(hashlib.sha256(image_path.read_bytes()).hexdigest()[:8], 16)
        hero, role = self.choices[value % len(self.choices)]
        return ParsedMatch(hero, role, "win" if value % 3 else "loss", value % 15, value % 9, value % 18, 0.72 if value % 5 == 0 else 0.93)
