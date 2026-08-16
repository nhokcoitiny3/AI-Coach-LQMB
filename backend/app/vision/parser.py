from app.core.config import get_settings
from app.vision.mock import MockVisionParser


def get_vision_parser():
    if get_settings().vision_provider == "mock":
        return MockVisionParser()
    raise ValueError("Unsupported VISION_PROVIDER; use mock for this MVP")
