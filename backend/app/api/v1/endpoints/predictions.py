from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models.prediction import Prediction
from app.schemas.prediction import PredictionOut
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("", response_model=list[PredictionOut])
async def list_predictions(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Prediction).order_by(Prediction.created_at.desc()))
    return result.scalars().all()


@router.get("/{ticker}", response_model=PredictionOut)
async def get_prediction(ticker: str, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(
        select(Prediction)
        .where(Prediction.ticker == ticker.upper())
        .order_by(Prediction.created_at.desc())
        .limit(1)
    )
    pred = result.scalar_one_or_none()
    if pred is None:
        raise HTTPException(status_code=404, detail="No prediction found for this ticker")
    return pred
