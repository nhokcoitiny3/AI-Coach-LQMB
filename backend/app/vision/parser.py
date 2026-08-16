from app.core.config import get_settings
from app.vision.gemini import GeminiVisionParser


def vision_is_configured() -> bool:
    settings = get_settings()
    return settings.vision_provider == "gemini" and bool(settings.gemini_api_key)


def get_vision_parser(hero_names: list[str]):
    if vision_is_configured():
        return GeminiVisionParser(hero_names)
    raise ValueError("Vision provider is not configured")
