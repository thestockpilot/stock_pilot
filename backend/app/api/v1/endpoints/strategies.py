import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models.strategy import Strategy
from app.db.models.user import User
from app.schemas.strategy import StrategyCreate, StrategyUpdate, StrategyOut
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/strategies", tags=["strategies"])


@router.get("", response_model=list[StrategyOut])
async def list_strategies(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Strategy).where((Strategy.owner_id == user.id) | (Strategy.is_preset == True)).order_by(Strategy.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=StrategyOut, status_code=201)
async def create_strategy(body: StrategyCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    strategy = Strategy(owner_id=user.id, name=body.name, description=body.description, weights=body.weights)
    db.add(strategy)
    await db.flush()
    await db.refresh(strategy)
    return strategy


@router.put("/{strategy_id}", response_model=StrategyOut)
async def update_strategy(
    strategy_id: uuid.UUID,
    body: StrategyUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Strategy).where(Strategy.id == strategy_id, Strategy.owner_id == user.id))
    strategy = result.scalar_one_or_none()
    if strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")
    if body.name is not None:
        strategy.name = body.name
    if body.description is not None:
        strategy.description = body.description
    if body.weights is not None:
        strategy.weights = body.weights
    await db.flush()
    await db.refresh(strategy)
    return strategy


@router.delete("/{strategy_id}", status_code=204)
async def delete_strategy(
    strategy_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Strategy).where(Strategy.id == strategy_id, Strategy.owner_id == user.id))
    strategy = result.scalar_one_or_none()
    if strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")
    await db.delete(strategy)
