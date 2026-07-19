import uuid
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models.strategy import Strategy
from app.db.models.marketplace import MarketplaceListing, ListingStatus
from app.db.models.user import User, UserRole
from app.schemas.strategy import StrategyCreate, StrategyUpdate, StrategyOut
from app.core.dependencies import get_current_user, require_role

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


@router.post("/{strategy_id}/publish")
async def request_publish(
    strategy_id: uuid.UUID,
    price_cents: int = Body(default=0, embed=True),
    backtest_trades: int = Body(default=0, embed=True),
    backtest_winrate: float = Body(default=0.0, embed=True),
    backtest_sharpe: float = Body(default=0.0, embed=True),
    backtest_max_drawdown: float = Body(default=1.0, embed=True),
    backtest_profit_factor: float = Body(default=0.0, embed=True),
    backtest_return: float = Body(default=0.0, embed=True),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.analyst, UserRole.admin)),
):
    result = await db.execute(
        select(Strategy).where(Strategy.id == strategy_id, Strategy.owner_id == user.id)
    )
    strategy = result.scalar_one_or_none()
    if strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")

    failures = []
    if backtest_trades < 100:
        failures.append(f"Min trades: {backtest_trades}/100")
    if backtest_winrate < 0.65:
        failures.append(f"Win rate: {backtest_winrate*100:.0f}%/65%")
    if backtest_sharpe < 1.0:
        failures.append(f"Sharpe: {backtest_sharpe:.2f}/1.0")
    if backtest_max_drawdown > 0.15:
        failures.append(f"Max drawdown: {backtest_max_drawdown*100:.0f}%/15%")
    if backtest_profit_factor < 1.5:
        failures.append(f"Profit factor: {backtest_profit_factor:.2f}/1.5")
    if failures:
        raise HTTPException(status_code=400, detail="Backtest thresholds not met: " + "; ".join(failures))

    existing = await db.execute(
        select(MarketplaceListing).where(MarketplaceListing.strategy_id == strategy_id)
    )
    listing = existing.scalar_one_or_none()
    if listing:
        if listing.status == ListingStatus.review:
            raise HTTPException(status_code=400, detail="Already pending review")
        if listing.status == ListingStatus.verified:
            raise HTTPException(status_code=400, detail="Already published")
        listing.status = ListingStatus.review
        listing.price_cents = price_cents
        listing.backtest_return = backtest_return
        listing.backtest_sharpe = backtest_sharpe
        listing.backtest_winrate = backtest_winrate
        listing.backtest_trades = backtest_trades
        listing.backtest_max_drawdown = backtest_max_drawdown
        listing.backtest_profit_factor = backtest_profit_factor
    else:
        listing = MarketplaceListing(
            strategy_id=strategy_id,
            price_cents=price_cents,
            status=ListingStatus.review,
            backtest_return=backtest_return,
            backtest_sharpe=backtest_sharpe,
            backtest_winrate=backtest_winrate,
            backtest_trades=backtest_trades,
            backtest_max_drawdown=backtest_max_drawdown,
            backtest_profit_factor=backtest_profit_factor,
        )
        db.add(listing)

    await db.flush()
    return {"status": "review", "listing_id": str(listing.id)}
