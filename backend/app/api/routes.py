import hashlib
import uuid
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.db.session import get_session
from app.models import ImportedImage, ParsingJob, Player
from app.datafeed.service import catalog_hero, catalog_heroes, hero_counters, list_datafeed_status, meta_dashboard, refresh_datafeed
from app.schemas.common import DataFeedRefresh, JobOut, PlayerCreate, PlayerOut, ReviewUpdate
from app.services.ingestion import persist_match, process_job
from app.services.scout import scout
from app.vision.parser import vision_is_configured

router = APIRouter(prefix="/api/v1")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.get("/datafeed/sources")
async def datafeed_sources(session: AsyncSession = Depends(get_session)):
    return await list_datafeed_status(session)


@router.get("/catalog/heroes")
async def heroes_catalog(session: AsyncSession = Depends(get_session)):
    return await catalog_heroes(session)


@router.get("/catalog/heroes/{hero_id}")
async def hero_catalog_detail(hero_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    hero = await catalog_hero(session, str(hero_id))
    if hero is None:
        raise HTTPException(404, "Không tìm thấy tướng trong datafeed")
    return hero


@router.get("/catalog/heroes/{hero_id}/counters")
async def hero_counter_catalog(hero_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    return await hero_counters(session, str(hero_id))


@router.get("/meta/dashboard")
async def dashboard_meta(session: AsyncSession = Depends(get_session)):
    return await meta_dashboard(session)


@router.post("/datafeed/refresh", status_code=status.HTTP_202_ACCEPTED)
async def refresh_sources(body: DataFeedRefresh, background: BackgroundTasks):
    source_keys = set(body.sources) if body.sources else None
    background.add_task(refresh_datafeed, source_keys)
    return {"status": "scheduled", "sources": body.sources or "all"}


@router.get("/players", response_model=list[PlayerOut])
async def list_players(session: AsyncSession = Depends(get_session)):
    return list((await session.scalars(select(Player).order_by(Player.name))).all())

@router.post("/players", response_model=PlayerOut, status_code=status.HTTP_201_CREATED)
async def create_player(body: PlayerCreate, session: AsyncSession = Depends(get_session)):
    if await session.scalar(select(Player).where(Player.name == body.name)):
        raise HTTPException(409, "Tên người chơi đã tồn tại")
    player = Player(name=body.name); session.add(player); await session.commit(); await session.refresh(player); return player


async def get_player(player_id: uuid.UUID, session: AsyncSession) -> Player:
    player = await session.get(Player, player_id)
    if not player: raise HTTPException(404, "Không tìm thấy người chơi")
    return player


@router.get("/players/{player_id}", response_model=PlayerOut)
async def player_detail(player_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    return await get_player(player_id, session)


@router.get("/players/{player_id}/scout")
async def player_scout(player_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    return await scout(session, await get_player(player_id, session))


@router.get("/players/{player_id}/jobs", response_model=list[JobOut])
async def jobs(player_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    await get_player(player_id, session)
    return list((await session.scalars(select(ParsingJob).join(ImportedImage).where(ImportedImage.player_id == player_id).order_by(ParsingJob.created_at.desc()))).all())


@router.post("/players/{player_id}/screenshots", response_model=list[JobOut], status_code=status.HTTP_202_ACCEPTED)
async def upload_screenshots(player_id: uuid.UUID, background: BackgroundTasks, files: list[UploadFile] = File(...), session: AsyncSession = Depends(get_session)):
    await get_player(player_id, session)
    settings = get_settings(); settings.upload_dir.mkdir(parents=True, exist_ok=True); jobs = []
    for file in files:
        if file.content_type not in ALLOWED_TYPES: raise HTTPException(415, "Chỉ nhận jpg, png hoặc webp")
        content = await file.read()
        if len(content) > settings.max_upload_size_mb * 1024 * 1024: raise HTTPException(413, "Ảnh quá lớn")
        digest = hashlib.sha256(content).hexdigest()
        if await session.scalar(select(ImportedImage).where(ImportedImage.sha256 == digest)): raise HTTPException(409, "Ảnh đã được nhập")
        suffix = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}[file.content_type]
        path = settings.upload_dir / f"{uuid.uuid4()}{suffix}"; path.write_bytes(content)
        image = ImportedImage(player_id=player_id, original_name=Path(file.filename or "upload").name, stored_path=str(path), sha256=digest, media_type=file.content_type, size_bytes=len(content))
        session.add(image); await session.flush()
        job = ParsingJob(image_id=image.id, status="pending"); session.add(job); await session.flush(); jobs.append(job)
    await session.commit()
    if vision_is_configured():
        for job in jobs:
            background.add_task(process_job, job.id)
    return jobs


@router.put("/jobs/{job_id}/review", response_model=JobOut)
async def confirm_review(job_id: uuid.UUID, body: ReviewUpdate, session: AsyncSession = Depends(get_session)):
    job = await session.get(ParsingJob, job_id)
    if not job or job.status != "review": raise HTTPException(404, "Không tìm thấy bản cần duyệt")
    data = body.model_dump() | {"confidence": 1.0}
    await persist_match(session, job, job.image.player_id, data); job.status = "completed"; await session.commit(); await session.refresh(job); return job
