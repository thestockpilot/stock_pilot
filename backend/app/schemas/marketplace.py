import uuid
from datetime import datetime
from pydantic import BaseModel


class StrategyBrief(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    weights: dict
    is_preset: bool
    owner: dict | None = None

    model_config = {"from_attributes": True}


class MarketplaceListingOut(BaseModel):
    id: uuid.UUID
    strategy_id: uuid.UUID
    price_cents: int
    status: str
    avg_rating: float | None = None
    rating_count: int
    sales_count: int
    backtest_return: float | None = None
    backtest_sharpe: float | None = None
    backtest_winrate: float | None = None
    listed_at: datetime | None = None
    strategy: StrategyBrief | None = None

    model_config = {"from_attributes": True}
