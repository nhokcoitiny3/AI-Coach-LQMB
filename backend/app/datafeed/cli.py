import asyncio

from app.datafeed.service import refresh_datafeed


if __name__ == "__main__":
    asyncio.run(refresh_datafeed())
