from dataclasses import dataclass, field


@dataclass
class HeroRecord:
    name: str
    role: str = "unknown"
    aliases: list[str] = field(default_factory=list)
    source_url: str = ""
    image_url: str | None = None
    region: str = "global"
    patch_version: str | None = None
    tier: str | None = None
    pick_rate: float | None = None
    ban_rate: float | None = None
    win_rate: float | None = None
    sample_size: int | None = None
