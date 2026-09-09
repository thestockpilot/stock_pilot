from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.db.models.marketplace import MarketplaceListing
from app.db.models.strategy import Strategy
from app.db.models.settings import get_settings, thresholds_dict
from app.core.dependencies import get_current_principal

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


@router.get("/thresholds")
async def marketplace_thresholds(db: AsyncSession = Depends(get_db), _=Depends(get_current_principal)):
    """Current backtest approval thresholds, readable by any signed-in user so the
    marketplace and publish dialog stay in sync with what admins have configured."""
    settings = await get_settings(db)
    return thresholds_dict(settings)


@router.get("")
async def list_marketplace(db: AsyncSession = Depends(get_db), _=Depends(get_current_principal)):
    result = await db.execute(
        select(MarketplaceListing)
        .options(selectinload(MarketplaceListing.strategy).selectinload(Strategy.owner))
        .order_by(MarketplaceListing.created_at.desc())
    )
    listings = result.scalars().all()
    out = []
    for listing in listings:
        strategy = listing.strategy
        owner_data = None
        if strategy and strategy.owner:
            owner_data = {"full_name": strategy.owner.full_name}
        strat_data = None
        if strategy:
            strat_data = {
                "id": str(strategy.id),
                "name": strategy.name,
                "description": strategy.description,
                "weights": strategy.weights,
                "is_preset": strategy.is_preset,
                "owner": owner_data,
            }
        out.append({
            "id": str(listing.id),
            "strategy_id": str(listing.strategy_id),
            "price_cents": listing.price_cents,
            "status": listing.status.value if listing.status else "draft",
            "avg_rating": float(listing.avg_rating) if listing.avg_rating else None,
            "rating_count": listing.rating_count,
            "sales_count": listing.sales_count,
            "backtest_return": float(listing.backtest_return) if listing.backtest_return is not None else None,
            "backtest_sharpe": float(listing.backtest_sharpe) if listing.backtest_sharpe is not None else None,
            "backtest_winrate": float(listing.backtest_winrate) if listing.backtest_winrate is not None else None,
            "backtest_trades": listing.backtest_trades,
            "backtest_max_drawdown": float(listing.backtest_max_drawdown) if listing.backtest_max_drawdown is not None else None,
            "backtest_profit_factor": float(listing.backtest_profit_factor) if listing.backtest_profit_factor is not None else None,
            "listed_at": listing.listed_at.isoformat() if listing.listed_at else None,
            "strategy": strat_data,
        })
    return out
