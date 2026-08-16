import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models import Hero, Match, Player

HEROES = [("Aoi", "jungle"), ("Tel'Annas", "dragon"), ("Yena", "slayer"), ("Krixi", "mid"), ("Alice", "support"), ("Nakroth", "jungle"), ("Violet", "dragon"), ("Florentino", "slayer"), ("Tulen", "mid"), ("Thane", "support")]
PLAYERS = ["Minh Quân", "Bảo Long", "Anh Khoa", "Tuấn Kiệt", "Gia Huy"]


async def seed():
    async with SessionLocal() as session:
        if await session.scalar(select(Player).limit(1)):
            print("Seed data already exists"); return
        heroes = {}
        for name, role in HEROES:
            hero = Hero(name=name, role=role); session.add(hero); heroes[name] = hero
        await session.flush()
        now = datetime.now(timezone.utc)
        for player_index, name in enumerate(PLAYERS):
            player = Player(name=name); session.add(player); await session.flush()
            for index in range(50):
                hero_name, role = HEROES[(index + player_index) % len(HEROES)]
                session.add(Match(player_id=player.id, hero_id=heroes[hero_name].id, played_at=now - timedelta(days=index), role=role, result="win" if (index + player_index) % 3 else "loss", kills=(index * 3) % 15, deaths=index % 8, assists=(index * 2) % 16, confidence=0.95))
        await session.commit(); print("Seeded 5 players and 250 matches")


if __name__ == "__main__": asyncio.run(seed())
