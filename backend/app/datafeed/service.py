from datetime import datetime, timezone

import httpx
from sqlalchemy import select

from app.datafeed.collectors import Collector, default_collectors
from app.datafeed.normalizer import normalize_name, normalize_role
from app.db.session import SessionLocal
from app.models import DataFeedRun, DataSource, Hero, HeroCatalogSource, HeroMetaSnapshot


async def refresh_datafeed(source_keys: set[str] | None = None) -> list[str]:
    collectors = [collector for collector in default_collectors() if source_keys is None or collector.key in source_keys]
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers={"User-Agent": "LienQuanAICoachDatafeed/0.1 (+local research; contact: admin@example.invalid)"}) as client:
        for collector in collectors:
            await _refresh_collector(collector, client)
    return [collector.key for collector in collectors]


async def _refresh_collector(collector: Collector, client: httpx.AsyncClient) -> None:
    async with SessionLocal() as session:
        source = await session.scalar(select(DataSource).where(DataSource.key == collector.key))
        if source is None:
            source = DataSource(key=collector.key, name=collector.name, base_url=collector.base_url, region=collector.region)
            session.add(source)
            await session.flush()
        run = DataFeedRun(source_id=source.id, status="running")
        session.add(run)
        await session.commit()
        try:
            records = await collector.collect(client)
            run.records_seen = len(records)
            for record in records:
                normalized = normalize_name(record.name)
                if not normalized:
                    continue
                hero = await session.scalar(select(Hero).where(Hero.normalized_name == normalized))
                if hero is None:
                    hero = Hero(name=record.name, normalized_name=normalized, role=normalize_role(record.role), region=record.region, aliases=record.aliases, source_url=record.source_url, catalog_patch=record.patch_version, last_seen_at=datetime.now(timezone.utc))
                    session.add(hero)
                    await session.flush()
                else:
                    hero.aliases = sorted(set([*hero.aliases, record.name, *record.aliases]))
                    hero.role = hero.role if hero.role != "unknown" else normalize_role(record.role)
                    hero.last_seen_at = datetime.now(timezone.utc)
                catalog_source = await session.scalar(select(HeroCatalogSource).where(HeroCatalogSource.hero_id == hero.id, HeroCatalogSource.source_id == source.id))
                if catalog_source is None:
                    catalog_source = HeroCatalogSource(hero_id=hero.id, source_id=source.id, source_name=record.name, source_role=record.role, source_url=record.source_url, region=record.region, patch_version=record.patch_version, aliases=record.aliases)
                    session.add(catalog_source)
                else:
                    catalog_source.source_name = record.name
                    catalog_source.source_role = record.role
                    catalog_source.source_url = record.source_url
                    catalog_source.region = record.region
                    catalog_source.patch_version = record.patch_version
                    catalog_source.aliases = record.aliases
                    catalog_source.fetched_at = datetime.now(timezone.utc)
                if any(value is not None for value in (record.tier, record.pick_rate, record.ban_rate, record.win_rate)):
                    session.add(HeroMetaSnapshot(hero_id=hero.id, source_id=source.id, region=record.region, patch_version=record.patch_version, tier=record.tier, pick_rate=record.pick_rate, ban_rate=record.ban_rate, win_rate=record.win_rate, sample_size=record.sample_size, source_url=record.source_url))
                run.records_written += 1
            run.status = "completed"
        except Exception as exc:
            run.status = "failed"
            run.error = str(exc)[:2000]
        run.finished_at = datetime.now(timezone.utc)
        await session.commit()


async def list_datafeed_status(session):
    sources = list((await session.scalars(select(DataSource).order_by(DataSource.key))).all())
    result = []
    for source in sources:
        latest_run = await session.scalar(select(DataFeedRun).where(DataFeedRun.source_id == source.id).order_by(DataFeedRun.started_at.desc()))
        result.append({"key": source.key, "name": source.name, "region": source.region, "base_url": source.base_url, "enabled": source.enabled, "last_run": None if latest_run is None else {"status": latest_run.status, "records_written": latest_run.records_written, "finished_at": latest_run.finished_at}})
    return result


async def catalog_heroes(session, source_key: str = "rovmeta") -> list[dict]:
    rows = (await session.execute(select(Hero, HeroMetaSnapshot, DataSource).join(HeroMetaSnapshot, HeroMetaSnapshot.hero_id == Hero.id).join(DataSource, DataSource.id == HeroMetaSnapshot.source_id).where(DataSource.key == source_key).order_by(Hero.id, HeroMetaSnapshot.captured_at.desc()))).all()
    seen: set = set()
    catalog = []
    for hero, meta, source in rows:
        if hero.id in seen:
            continue
        seen.add(hero.id)
        catalog.append({"id": str(hero.id), "name": hero.name, "role": hero.role, "aliases": hero.aliases, "tier": meta.tier, "pick_rate": meta.pick_rate, "ban_rate": meta.ban_rate, "win_rate": meta.win_rate, "patch_version": meta.patch_version, "region": meta.region, "source": source.key, "source_url": meta.source_url, "captured_at": meta.captured_at})
    return catalog


async def meta_dashboard(session) -> dict:
    heroes = await catalog_heroes(session)
    tier_counts: dict[str, int] = {}
    role_counts: dict[str, int] = {}
    for hero in heroes:
        tier_counts[hero["tier"] or "unrated"] = tier_counts.get(hero["tier"] or "unrated", 0) + 1
        role_counts[hero["role"]] = role_counts.get(hero["role"], 0) + 1
    return {"hero_count": len(heroes), "tier_distribution": tier_counts, "role_distribution": role_counts, "top_meta": sorted(heroes, key=lambda hero: ((hero["tier"] == "S"), hero["win_rate"] or 0, hero["pick_rate"] or 0), reverse=True)[:12], "sources": await list_datafeed_status(session)}
