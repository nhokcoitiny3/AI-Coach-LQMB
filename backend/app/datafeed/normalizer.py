import re
import unicodedata


def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = value.lower().replace("đ", "d")
    return re.sub(r"[^a-z0-9]+", "", value)


def normalize_role(value: str) -> str:
    lowered = value.lower()
    for source_role, normalized_role in {
        "assassin": "jungle", "mage": "mid", "marksman": "dragon",
        "adc": "dragon", "warrior": "slayer", "fighter": "slayer",
    }.items():
        if source_role in lowered:
            return normalized_role
    for role, names in {
        "jungle": ("jungle", "rung", "sát thủ", "assassin"),
        "mid": ("mid", "pháp sư", "mage"),
        "dragon": ("dragon", "xạ thủ", "marksman"),
        "slayer": ("slayer", "đấu sĩ", "warrior"),
        "support": ("support", "trợ thủ", "tank"),
    }.items():
        if any(name in lowered for name in names):
            return role
    return "unknown"
