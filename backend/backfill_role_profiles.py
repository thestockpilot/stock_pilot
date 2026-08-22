"""One-off backfill: give every existing user a role subtype row.

Run once after adding the investors/analysts/admins tables (Option A). Safe to
re-run — users that already have a profile row are skipped.
"""
import asyncio
from sqlalchemy import select
from app.db.session import engine, AsyncSessionLocal
from app.db.base import Base
import app.db.models  # noqa: F401  registers every model
from app.db.models.user import User
from app.db.models.role_profiles import PROFILE_BY_ROLE, profile_for


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # create the new tables
    async with AsyncSessionLocal() as db:
        users = (await db.execute(select(User))).scalars().all()
        created = 0
        for u in users:
            model = PROFILE_BY_ROLE[u.role]
            if await db.get(model, u.id) is None:
                db.add(profile_for(u.role, u.id))
                created += 1
        await db.commit()
        print(f"backfilled {created} profile row(s) across {len(users)} user(s)")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
