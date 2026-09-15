import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.db.models.marketplace import MarketplaceListing, ListingStatus
from app.db.models.strategy import Strategy
from app.db.models.purchase import Purchase
from app.db.models.notification import NotificationKind
from app.db.models.settings import get_settings, thresholds_dict
from app.core.dependencies import get_current_principal, get_current_user, is_admin
from app.core.notify import notify

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


class PurchaseRequest(BaseModel):
    # Cosmetic only — a label like "Visa ****4242" for the mock/demo payment.
    payment_method: str | None = None


@router.get("/thresholds")
async def marketplace_thresholds(db: AsyncSession = Depends(get_db), _=Depends(get_current_principal)):
    """Current backtest approval thresholds, readable by any signed-in user so the
    marketplace and publish dialog stay in sync with what admins have configured."""
    settings = await get_settings(db)
    return thresholds_dict(settings)


@router.get("")
async def list_marketplace(db: AsyncSession = Depends(get_db), principal=Depends(get_current_principal)):
    result = await db.execute(
        select(MarketplaceListing)
        .options(selectinload(MarketplaceListing.strategy).selectinload(Strategy.owner))
        .order_by(MarketplaceListing.created_at.desc())
    )
    listings = result.scalars().all()

    # Which listings the signed-in user has already bought (admins own none).
    owned_ids: set = set()
    if not is_admin(principal):
        rows = await db.execute(
            select(Purchase.listing_id).where(Purchase.user_id == principal.id)
        )
        owned_ids = {r for r in rows.scalars().all()}

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
        is_owner = (not is_admin(principal)) and strategy is not None and strategy.owner_id == principal.id
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
            "owned": listing.id in owned_ids,
            "is_owner": is_owner,
            "strategy": strat_data,
        })
    return out


@router.get("/purchases")
async def my_purchases(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    rows = await db.execute(
        select(Purchase.listing_id).where(Purchase.user_id == user.id)
    )
    return {"listing_ids": [str(x) for x in rows.scalars().all()]}


@router.post("/{listing_id}/purchase")
async def purchase_listing(
    listing_id: uuid.UUID,
    body: PurchaseRequest | None = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Mock/demo payment: records the purchase and increments the sales count.
    No real money changes hands — this is an educational simulation."""
    result = await db.execute(
        select(MarketplaceListing)
        .where(MarketplaceListing.id == listing_id)
        .options(selectinload(MarketplaceListing.strategy))
    )
    listing = result.scalar_one_or_none()
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.status not in (ListingStatus.verified, ListingStatus.listed):
        raise HTTPException(status_code=400, detail="This strategy is not available for purchase")
    if listing.strategy and listing.strategy.owner_id == user.id:
        raise HTTPException(status_code=400, detail="You cannot purchase your own strategy")

    existing = await db.execute(
        select(Purchase).where(Purchase.user_id == user.id, Purchase.listing_id == listing.id)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="You already own this strategy")

    method = (body.payment_method if body else None) or "Demo card"
    db.add(Purchase(
        user_id=user.id,
        listing_id=listing.id,
        price_cents=listing.price_cents,
        payment_method=method[:60],
    ))
    listing.sales_count = (listing.sales_count or 0) + 1

    # Let the strategy author know they made a sale.
    if listing.strategy and listing.strategy.owner_id:
        amount = f"${listing.price_cents / 100:.2f}" if listing.price_cents else "free"
        await notify(
            db, listing.strategy.owner_id, NotificationKind.marketplace,
            "Strategy sold",
            f"Your strategy “{listing.strategy.name}” was purchased ({amount}).",
        )

    await db.flush()
    return {
        "status": "success",
        "listing_id": str(listing.id),
        "price_cents": listing.price_cents,
        "sales_count": listing.sales_count,
    }
