from dataclasses import asdict, dataclass


@dataclass
class ParsedMatch:
    hero: str
    role: str
    result: str
    kills: int
    deaths: int
    assists: int
    confidence: float

    def to_dict(self) -> dict:
        return asdict(self)
