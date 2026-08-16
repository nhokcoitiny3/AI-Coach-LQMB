from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/lien_quan"
    vision_provider: str = ""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-flash-latest"
    max_upload_size_mb: int = 10
    upload_dir: Path = Path("/app/uploads")


@lru_cache
def get_settings() -> Settings:
    return Settings()
