import hashlib
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.db.session import get_session
from app.models import ImportedImage, ParsingJob, Player
from app.schemas.common import JobOut, PlayerCreate, PlayerOut, ReviewUpdate
from app.services.ingestion import persist_match
from app.services.scout import scout

router = APIRouter(prefix="/api/v1")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


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
async def upload_screenshots(player_id: uuid.UUID, files: list[UploadFile] = File(...), session: AsyncSession = Depends(get_session)):
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
    return jobs


@router.put("/jobs/{job_id}/review", response_model=JobOut)
async def confirm_review(job_id: uuid.UUID, body: ReviewUpdate, session: AsyncSession = Depends(get_session)):
    job = await session.get(ParsingJob, job_id)
    if not job or job.status != "review": raise HTTPException(404, "Không tìm thấy bản cần duyệt")
    data = body.model_dump() | {"confidence": 1.0}
    await persist_match(session, job, job.image.player_id, data); job.status = "completed"; await session.commit(); await session.refresh(job); return job
