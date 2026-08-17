import asyncio
import re
from abc import ABC, abstractmethod
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.datafeed.models import CounterRecord, HeroRecord


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
            image_url = None
            if detail.status_code == 200:
                page = BeautifulSoup(detail.text, "html.parser")
                role = _lq_role(page)
                image_url = _lq_image(page, hero_url)
            records.append(HeroRecord(name=name, role=role, region=self.region, source_url=hero_url, image_url=image_url))
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


def _lq_image(soup: BeautifulSoup, page_url: str) -> str | None:
    """Use the current Vietnamese hero-page social/portrait image when available."""
    for selector, attribute in (("meta[property='og:image']", "content"), ("meta[name='twitter:image']", "content")):
        image = soup.select_one(selector)
        if image and image.get(attribute):
            return urljoin(page_url, image[attribute])
    for image in soup.select("img[src]"):
        source = image.get("src", "")
        if any(token in source.lower() for token in ("tuong", "hero", "character")):
            return urljoin(page_url, source)
    return None


def default_collectors() -> list[Collector]:
    return [LienQuanMobiCollector(), FandomVietnamCollector(), RovMetaCollector(), LiquipediaAplCollector()]


class AovBuildsCounterCollector:
    key = "aov_builds_counters"
    name = "AOV Builds counter picks"
    base_url = "https://aov-builds.com/khac-che/"
    region = "vn"

    async def collect(self, client: httpx.AsyncClient) -> list[CounterRecord]:
        response = await client.get(self.base_url)
        response.raise_for_status()
        index = BeautifulSoup(response.text, "html.parser")
        urls = {urljoin(self.base_url, link["href"]) for link in index.select("a[href]") if "/khac-che/" in link["href"] and link["href"].rstrip("/") != self.base_url.rstrip("/")}
        records: list[CounterRecord] = []
        for source_url in sorted(urls):
            await asyncio.sleep(0.2)
            page_response = await client.get(source_url)
            if page_response.status_code != 200:
                continue
            page = BeautifulSoup(page_response.text, "html.parser")
            heading = page.select_one("h2")
            text = page.get_text(" ", strip=True)
            listed = re.search(r"Tướng khắc chế\s+.+?\s+gồm:\s*(.+?)(?:\.\s|\. Đây)", text, re.IGNORECASE)
            if not heading or not listed:
                continue
            names = [re.split(r"\s+(?:là|gồm|bao gồm)\s+", name, maxsplit=1, flags=re.IGNORECASE)[0].strip().removeprefix("và ").strip() for name in listed.group(1).split(",")]
            names = [name for name in names if name and len(name) <= 80]
            if names:
                records.append(CounterRecord(hero_name=heading.get_text(" ", strip=True), counter_names=names, source_url=source_url))
        return records


def default_counter_collectors() -> list[AovBuildsCounterCollector]:
    return [AovBuildsCounterCollector()]
