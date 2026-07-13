"""Seed the database with stocks, price history, predictions, and a demo user."""
import asyncio
import random
from datetime import date, datetime, timedelta, timezone
from app.db.session import AsyncSessionLocal, engine
from app.db.base import Base
import app.db.models  # noqa
from app.db.models.stock import Stock, PriceHistory
from app.db.models.prediction import Prediction, SignalType
from app.db.models.user import User
from app.db.models.notification import Notification, NotificationKind
from app.core.security import hash_password

STOCKS = [
    ("AAPL", "Apple Inc.", "Technology", "Consumer Electronics"),
    ("MSFT", "Microsoft Corporation", "Technology", "Software"),
    ("GOOGL", "Alphabet Inc.", "Technology", "Internet Services"),
    ("AMZN", "Amazon.com Inc.", "Consumer Cyclical", "Internet Retail"),
    ("NVDA", "NVIDIA Corporation", "Technology", "Semiconductors"),
    ("TSLA", "Tesla Inc.", "Consumer Cyclical", "Auto Manufacturers"),
    ("META", "Meta Platforms Inc.", "Technology", "Internet Services"),
    ("JPM", "JPMorgan Chase & Co.", "Financial Services", "Banks"),
    ("V", "Visa Inc.", "Financial Services", "Credit Services"),
    ("JNJ", "Johnson & Johnson", "Healthcare", "Drug Manufacturers"),
]

BASE_PRICES = {
    "AAPL": 195.0, "MSFT": 420.0, "GOOGL": 175.0, "AMZN": 185.0, "NVDA": 130.0,
    "TSLA": 245.0, "META": 500.0, "JPM": 195.0, "V": 280.0, "JNJ": 155.0,
}


def generate_price_history(ticker: str, days: int = 180) -> list[PriceHistory]:
    rows = []
    price = BASE_PRICES[ticker]
    today = date.today()
    for i in range(days, 0, -1):
        d = today - timedelta(days=i)
        if d.weekday() >= 5:
            continue
        change_pct = random.gauss(0.0005, 0.018)
        price = max(price * (1 + change_pct), 1.0)
        high = price * (1 + abs(random.gauss(0, 0.008)))
        low = price * (1 - abs(random.gauss(0, 0.008)))
        op = low + random.random() * (high - low)
        vol = int(random.gauss(40_000_000, 15_000_000))
        if vol < 1_000_000:
            vol = 1_000_000
        rows.append(PriceHistory(
            ticker=ticker, date=d,
            open=round(op, 4), high=round(high, 4),
            low=round(low, 4), close=round(price, 4),
            volume=vol,
        ))
    return rows


def generate_prediction(ticker: str) -> Prediction:
    signal = random.choice([SignalType.BUY, SignalType.HOLD, SignalType.SELL])
    confidence = round(random.uniform(55, 95), 2)
    if signal == SignalType.BUY:
        prob_up = round(random.uniform(55, 85), 2)
    elif signal == SignalType.SELL:
        prob_up = round(random.uniform(15, 45), 2)
    else:
        prob_up = round(random.uniform(40, 60), 2)
    prob_down = round(100 - prob_up, 2)
    return Prediction(
        ticker=ticker, signal=signal, confidence=confidence,
        probability_up=prob_up, probability_down=prob_down,
        model_version="xgboost_v1",
    )


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        from sqlalchemy import select, func

        count = (await session.execute(select(func.count()).select_from(Stock))).scalar()
        if count and count > 0:
            print(f"Database already has {count} stocks. Skipping seed.")
            return

        # Demo user
        demo = User(
            email="demo@stockpilot.io",
            password_hash=hash_password("demo1234"),
            full_name="Demo Trader",
        )
        session.add(demo)
        await session.flush()

        # Stocks + price history + predictions
        for ticker, name, sector, industry in STOCKS:
            stock = Stock(ticker=ticker, name=name, sector=sector, industry=industry)
            session.add(stock)
            for ph in generate_price_history(ticker):
                session.add(ph)
            session.add(generate_prediction(ticker))

        # Welcome notification
        session.add(Notification(
            user_id=demo.id,
            kind=NotificationKind.system,
            title="Welcome to StockPilot",
            body="Your AI-powered investment advisor is ready. Explore the dashboard to get started.",
        ))

        await session.commit()
        print(f"Seeded {len(STOCKS)} stocks with price history, predictions, and demo user (demo@stockpilot.io / demo1234)")


if __name__ == "__main__":
    asyncio.run(seed())
