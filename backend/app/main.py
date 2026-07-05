from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.base import Base  # just to verify models are loaded
import app.db.models  # noqa: F401
from sqlalchemy import text

app = FastAPI(title="Stock Pilot Backend")

@app.get("/")
async def root():
    return {"message": "Stock Pilot API is running"}

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}