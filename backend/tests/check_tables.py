import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        tables = [r[0] for r in result.fetchall()]
        print('Tables created:', tables)

asyncio.run(check())
