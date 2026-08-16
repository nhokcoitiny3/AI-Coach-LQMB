from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class PlayerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)


class PlayerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    created_at: datetime


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    status: str
    parsed_payload: dict | None = None
    error: str | None = None
    image_id: UUID


class ReviewUpdate(BaseModel):
    hero: str
    role: str
    result: str
    kills: int = Field(ge=0, le=99)
    deaths: int = Field(ge=0, le=99)
    assists: int = Field(ge=0, le=99)
