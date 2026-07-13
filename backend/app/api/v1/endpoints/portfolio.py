import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models.portfolio import Holding
from app.db.models.user import User
from app.schemas.portfolio import HoldingCreate, HoldingUpdate, HoldingOut
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("", response_model=list[HoldingOut])
async def list_holdings(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Holding).where(Holding.user_id == user.id, Holding.closed_at.is_(None)).order_by(Holding.opened_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=HoldingOut, status_code=201)
async def add_holding(body: HoldingCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    holding = Holding(user_id=user.id, ticker=body.ticker.upper(), quantity=body.quantity, avg_cost=body.avg_cost)
    db.add(holding)
    await db.flush()
    await db.refresh(holding)
    return holding


@router.put("/{holding_id}", response_model=HoldingOut)
async def update_holding(
    holding_id: uuid.UUID,
    body: HoldingUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Holding).where(Holding.id == holding_id, Holding.user_id == user.id))
    holding = result.scalar_one_or_none()
    if holding is None:
        raise HTTPException(status_code=404, detail="Holding not found")
    if body.quantity is not None:
        holding.quantity = body.quantity
    if body.avg_cost is not None:
        holding.avg_cost = body.avg_cost
    await db.flush()
    await db.refresh(holding)
    return holding


@router.delete("/{holding_id}", status_code=204)
async def delete_holding(
    holding_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Holding).where(Holding.id == holding_id, Holding.user_id == user.id))
    holding = result.scalar_one_or_none()
    if holding is None:
        raise HTTPException(status_code=404, detail="Holding not found")
    await db.delete(holding)
