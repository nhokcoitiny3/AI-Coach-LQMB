import asyncio
import re
from abc import ABC, abstractmethod
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.datafeed.models import HeroRecord


class Collector(ABC):
    key: str
    name: str
    base_url: str
    region: str

    @abstractmethod
    async def collect(self, client: httpx.AsyncClient) -> list[HeroRecord]: ...


class LienQuanMobiCollector(Collector):
    key = "lienquanmobi"
    name = "LienQuanMobi community catalog"
    base_url = "https://lienquanmobi.vn/"
    region = "vn"

    async def collect(self, client: httpx.AsyncClient) -> list[HeroRecord]:
        response = await client.get(self.base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        hero_urls: dict[str, str] = {}
        for link in soup.select("a[href]"):
            name = link.get_text(" ", strip=True)
            href = link.get("href", "")
            if not name or name.lower() == "xem thêm" or len(name) > 50 or "/hoc-vien/tuong-skin/d/" not in href.lower():
                continue
            hero_urls.setdefault(name, urljoin(self.base_url, href))
        records: list[HeroRecord] = []
        for name, hero_url in hero_urls.items():
            await asyncio.sleep(0.15)
            detail = await client.get(hero_url)
            role = "unknown"
            if detail.status_code == 200:
                role = _lq_role(BeautifulSoup(detail.text, "html.parser"))
            records.append(HeroRecord(name=name, role=role, region=self.region, source_url=hero_url))
        return records


class FandomVietnamCollector(Collector):
    key = "aov_fandom_vi"
    name = "Arena of Valor Fandom Vietnam"
    base_url = "https://arenaofvalor.fandom.com/vi/wiki/Thể_loại:Tướng"
    region = "vn"

    async def collect(self, client: httpx.AsyncClient) -> list[HeroRecord]:
        response = await client.get(self.base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        records: dict[str, HeroRecord] = {}
        for link in soup.select("a[href*='/vi/wiki/']"):
            name = link.get_text(" ", strip=True)
            href = link.get("href", "")
            if not name or len(name) > 50 or name.lower() in {"tướng", "trang chủ", "thể loại"}:
                continue
            records.setdefault(name, HeroRecord(name=name, region=self.region, source_url=urljoin(self.base_url, href)))
        return list(records.values())


class RovMetaCollector(Collector):
    key = "rovmeta"
    name = "ROV/AOV Meta"
    base_url = "https://www.rovmeta.com/heroes"
    region = "th"

    async def collect(self, client: httpx.AsyncClient) -> list[HeroRecord]:
        response = await client.get(self.base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        patch = _first_group(r"Patch\s*([0-9.]+)", soup.get_text(" ", strip=True))
        hero_urls = {urljoin(self.base_url, link["href"]) for link in soup.select("a[href^='/heroes/']") if link["href"] != "/heroes"}
        records: list[HeroRecord] = []
        for hero_url in sorted(hero_urls):
            await asyncio.sleep(0.2)
            detail = await client.get(hero_url)
            if detail.status_code != 200:
                continue
            page = BeautifulSoup(detail.text, "html.parser")
            name = page.select_one("h1")
            if not name:
                continue
            text = page.get_text(" ", strip=True).replace("\\n", " ")
            tier = _first_group(r"\b([SABCDF])\s+TIER\b", text)
            tier = tier.upper() if tier else None
            records.append(HeroRecord(name=name.get_text(" ", strip=True), role=_rov_role(page), region=self.region, source_url=hero_url, image_url=_rov_image(page), patch_version=patch, tier=tier))
        return records


class LiquipediaAplCollector(Collector):
    key = "liquipedia_apl"
    name = "Liquipedia APL professional statistics"
    base_url = "https://liquipedia.net/honorofkings/Arena_of_Valor_Premier_League/2026/Statistics"
    region = "global"

    async def collect(self, client: httpx.AsyncClient) -> list[HeroRecord]:
        response = await client.get(self.base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        records: list[HeroRecord] = []
        for row in soup.select("table tr"):
            cells = [cell.get_text(" ", strip=True) for cell in row.select("th,td")]
            if len(cells) < 2 or cells[0].lower() in {"hero", "heroes"}:
                continue
            percentages = [_to_percent(value) for value in cells]
            numeric = [value for value in percentages if value is not None]
            if not numeric or len(cells[0]) > 50:
                continue
            records.append(HeroRecord(name=cells[0], region=self.region, source_url=self.base_url, pick_rate=numeric[0], ban_rate=numeric[1] if len(numeric) > 1 else None, win_rate=numeric[2] if len(numeric) > 2 else None))
        return records


def _first_group(pattern: str, value: str) -> str | None:
    match = re.search(pattern, value, re.IGNORECASE)
    return match.group(1) if match else None


def _to_percent(value: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)%", value)
    return float(match.group(1)) / 100 if match else None


def _lq_role(soup: BeautifulSoup) -> str:
    lines = [line.strip() for line in soup.get_text("\n", strip=True).splitlines()]
    for index, line in enumerate(lines):
        if line.startswith("Vị trí:"):
            return line.removeprefix("Vị trí:").strip() or (lines[index + 1] if index + 1 < len(lines) else "unknown")
    return "unknown"


def _rov_role(soup: BeautifulSoup) -> str:
    text = soup.get_text(" ", strip=True).replace("\\n", " ")
    match = re.search(r"\bTIER\b\s+\w+\s+(Jungle|Mid|Dragon(?: Lane)?|Slayer|Support)\b", text, re.IGNORECASE)
    if match:
        return match.group(1)
    # Some ROVMeta pages expose a class (for example, "S TIER marksman")
    # instead of a lane. Preserve it for normalize_role below.
    match = re.search(r"\bTIER\b\s+(assassin|mage|marksman|adc|warrior|fighter|tank|support)\b", text, re.IGNORECASE)
    return match.group(1) if match else "unknown"


def _rov_image(soup: BeautifulSoup) -> str | None:
    for image in soup.select("img[src]"):
        if "portrait" in (image.get("alt") or "").lower():
            return urljoin("https://www.rovmeta.com", image["src"])
    return None


def default_collectors() -> list[Collector]:
    return [LienQuanMobiCollector(), FandomVietnamCollector(), RovMetaCollector(), LiquipediaAplCollector()]
