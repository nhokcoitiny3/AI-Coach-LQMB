from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.api.routes import router
from app.db.session import SessionLocal

app = FastAPI(title="Liên Quân AI Coach", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)


@app.get("/health")
async def health(): return {"status": "ok"}


@app.get("/health/database")
async def database_health():
    async with SessionLocal() as session: await session.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}
