import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TimestampedUUID(Base):
    __abstract__ = True
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Player(TimestampedUUID):
    __tablename__ = "players"
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    matches: Mapped[list["Match"]] = relationship(back_populates="player", cascade="all, delete-orphan")


class Hero(TimestampedUUID):
    __tablename__ = "heroes"
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(30))
    normalized_name: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True, index=True)
    aliases: Mapped[list] = mapped_column(JSON, default=list)
    region: Mapped[str] = mapped_column(String(30), default="unknown")
    catalog_patch: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DataSource(TimestampedUUID):
    __tablename__ = "data_sources"
    key: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    base_url: Mapped[str] = mapped_column(String(500))
    region: Mapped[str] = mapped_column(String(30))
    enabled: Mapped[bool] = mapped_column(default=True)


class DataFeedRun(TimestampedUUID):
    __tablename__ = "data_feed_runs"
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("data_sources.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(20), index=True)
    records_seen: Mapped[int] = mapped_column(Integer, default=0)
    records_written: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source: Mapped[DataSource] = relationship()


class HeroMetaSnapshot(TimestampedUUID):
    __tablename__ = "hero_meta_snapshots"
    hero_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("heroes.id", ondelete="CASCADE"), index=True)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("data_sources.id", ondelete="CASCADE"), index=True)
    region: Mapped[str] = mapped_column(String(30))
    patch_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tier: Mapped[str | None] = mapped_column(String(10), nullable=True)
    pick_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    ban_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    win_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    sample_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_url: Mapped[str] = mapped_column(String(500))
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    hero: Mapped[Hero] = relationship()
    source: Mapped[DataSource] = relationship()
    __table_args__ = (Index("ix_meta_source_hero_capture", "source_id", "hero_id", "captured_at"),)


class HeroCatalogSource(TimestampedUUID):
    __tablename__ = "hero_catalog_sources"
    hero_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("heroes.id", ondelete="CASCADE"), index=True)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("data_sources.id", ondelete="CASCADE"), index=True)
    source_name: Mapped[str] = mapped_column(String(100))
    source_role: Mapped[str] = mapped_column(String(100), default="unknown")
    source_url: Mapped[str] = mapped_column(String(500))
    region: Mapped[str] = mapped_column(String(30))
    patch_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    aliases: Mapped[list] = mapped_column(JSON, default=list)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    hero: Mapped[Hero] = relationship()
    source: Mapped[DataSource] = relationship()
    __table_args__ = (UniqueConstraint("hero_id", "source_id", name="uq_hero_catalog_source"),)


class HeroCounter(TimestampedUUID):
    __tablename__ = "hero_counters"
    hero_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("heroes.id", ondelete="CASCADE"), index=True)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("data_sources.id", ondelete="CASCADE"), index=True)
    counter_name: Mapped[str] = mapped_column(String(100))
    normalized_counter_name: Mapped[str] = mapped_column(String(100), index=True)
    source_url: Mapped[str] = mapped_column(String(500))
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    hero: Mapped[Hero] = relationship()
    source: Mapped[DataSource] = relationship()
    __table_args__ = (Index("ix_counter_source_hero", "source_id", "hero_id"),)


class Match(TimestampedUUID):
    __tablename__ = "matches"
    player_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), index=True)
    hero_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("heroes.id"), index=True)
    played_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    role: Mapped[str] = mapped_column(String(30))
    result: Mapped[str] = mapped_column(String(10))
    kills: Mapped[int] = mapped_column(Integer, default=0)
    deaths: Mapped[int] = mapped_column(Integer, default=0)
    assists: Mapped[int] = mapped_column(Integer, default=0)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    source_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)
    player: Mapped[Player] = relationship(back_populates="matches")
    hero: Mapped[Hero] = relationship()


class MatchPlayer(TimestampedUUID):
    __tablename__ = "match_players"
    match_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), index=True)
    player_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), index=True)
    __table_args__ = (UniqueConstraint("match_id", "player_id", name="uq_match_players"),)


class ImportedImage(TimestampedUUID):
    __tablename__ = "imported_images"
    player_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), index=True)
    original_name: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(String(500), unique=True)
    sha256: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    media_type: Mapped[str] = mapped_column(String(50))
    size_bytes: Mapped[int] = mapped_column(Integer)


class ParsingJob(TimestampedUUID):
    __tablename__ = "parsing_jobs"
    image_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("imported_images.id", ondelete="CASCADE"), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    parsed_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    image: Mapped[ImportedImage] = relationship(lazy="selectin")
    __table_args__ = (Index("ix_jobs_status_created", "status", "created_at"),)
