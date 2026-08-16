import base64
import json
import re
from pathlib import Path

import httpx

from app.core.config import get_settings
from app.vision.models import ParsedMatch


class GeminiVisionParser:
    def __init__(self, hero_names: list[str]):
        settings = get_settings()
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required when VISION_PROVIDER=gemini")
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model
        self.hero_names = hero_names

    async def parse_match_screenshot(self, image_path: Path) -> list[ParsedMatch]:
        mime_type = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}.get(image_path.suffix.lower())
        if not mime_type:
            raise ValueError("Unsupported image type")
        prompt = (
            "Read this Garena Lien Quan Mobile match history screenshot. Return JSON only as "
            "{\"matches\":[{hero,role,result,kills,deaths,assists,confidence}]}. Extract every fully visible match row, "
            "in top-to-bottom order. role must be jungle|mid|dragon|slayer|support|unknown and result must be win|loss. "
            "Use a hero name only from this catalog: " + ", ".join(self.hero_names) + ". "
            "If a field cannot be read, use null for it and lower confidence. Never invent values."
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": mime_type, "data": base64.b64encode(image_path.read_bytes()).decode("ascii")}}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0},
        }
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(url, headers={"x-goog-api-key": self.api_key}, json=payload)
            response.raise_for_status()
        try:
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return parse_gemini_matches(text)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError("Gemini response did not contain a valid match payload") from exc


def parse_gemini_match(value: str) -> ParsedMatch:
    match = re.search(r"\{.*\}", value, re.DOTALL)
    if not match:
        raise ValueError("Gemini did not return JSON")
    data = json.loads(match.group(0))
    required = ("hero", "role", "result", "kills", "deaths", "assists", "confidence")
    if any(data.get(field) is None for field in required):
        raise ValueError("Gemini response has unreadable required fields")
    if data["result"] not in {"win", "loss"}:
        raise ValueError("Gemini result must be win or loss")
    return ParsedMatch(hero=str(data["hero"]), role=str(data["role"]), result=data["result"], kills=int(data["kills"]), deaths=int(data["deaths"]), assists=int(data["assists"]), confidence=max(0.0, min(1.0, float(data["confidence"]))))


def parse_gemini_matches(value: str) -> list[ParsedMatch]:
    match = re.search(r"\{.*\}", value, re.DOTALL)
    if not match:
        raise ValueError("Gemini did not return JSON")
    data = json.loads(match.group(0))
    rows = data.get("matches") if isinstance(data, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError("Gemini did not return any match rows")
    return [parse_gemini_match(json.dumps(row)) for row in rows]
