"""
Live market data endpoints.

Streams real-time stock quotes and intraday data from Yahoo Finance.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

import numpy as np
import yfinance as yf
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.core.dependencies import get_current_principal

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/live", tags=["live"])


class QuoteResponse(BaseModel):
    ticker: str
    price: float
    change: float
    change_pct: float
    open: float
    high: float
    low: float
    prev_close: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    week52_high: float
    week52_low: float
    avg_volume: int
    timestamp: str


class IntradayPoint(BaseModel):
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class SessionStatus(BaseModel):
    name: str
    flag: str
    is_open: bool
    status: str
    next_event: str


class MarketStatusResponse(BaseModel):
    is_open: bool
    status: str
    next_event: str
    sessions: list[SessionStatus] = []


def _safe_float(val, default=0.0) -> float:
    if val is None:
        return default
    try:
        f = float(val)
        return default if (np.isnan(f) or np.isinf(f)) else f
    except (TypeError, ValueError):
        return default


def _safe_int(val, default=0) -> int:
    if val is None:
        return default
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


GLOBAL_SESSIONS = [
    {"name": "Tokyo",    "flag": "🇯🇵", "tz": "Asia/Tokyo",       "open": (9, 0),  "close": (15, 0),  "abbr": "JST"},
    {"name": "Shanghai", "flag": "🇨🇳", "tz": "Asia/Shanghai",    "open": (9, 30), "close": (15, 0),  "abbr": "CST"},
    {"name": "Hong Kong","flag": "🇭🇰", "tz": "Asia/Hong_Kong",   "open": (9, 30), "close": (16, 0),  "abbr": "HKT"},
    {"name": "London",   "flag": "🇬🇧", "tz": "Europe/London",    "open": (8, 0),  "close": (16, 30), "abbr": "GMT"},
    {"name": "New York", "flag": "🇺🇸", "tz": "America/New_York", "open": (9, 30), "close": (16, 0),  "abbr": "ET"},
]


def _session_status(sess: dict, now_utc) -> SessionStatus:
    from zoneinfo import ZoneInfo

    tz = ZoneInfo(sess["tz"])
    now_local = now_utc.astimezone(tz)
    weekday = now_local.weekday()
    t = now_local.hour * 60 + now_local.minute
    market_open = sess["open"][0] * 60 + sess["open"][1]
    market_close = sess["close"][0] * 60 + sess["close"][1]

    is_weekday = weekday < 5
    is_market_hours = market_open <= t < market_close
    is_open = is_weekday and is_market_hours

    open_str = f"{sess['open'][0]}:{sess['open'][1]:02d}"
    close_str = f"{sess['close'][0]}:{sess['close'][1]:02d}"
    abbr = sess["abbr"]

    if not is_weekday:
        status = "Closed"
        next_event = f"Opens Mon {open_str} {abbr}"
    elif t < market_open:
        status = "Pre-market"
        next_event = f"Opens {open_str} {abbr}"
    elif is_open:
        status = "Open"
        next_event = f"Closes {close_str} {abbr}"
    else:
        status = "Closed"
        next_event = f"Opens tomorrow {open_str} {abbr}"

    return SessionStatus(
        name=sess["name"], flag=sess["flag"],
        is_open=is_open, status=status, next_event=next_event,
    )


@router.get("/market-status", response_model=MarketStatusResponse)
async def get_market_status(_=Depends(get_current_principal)):
    now_utc = datetime.now(timezone.utc)
    sessions = [_session_status(s, now_utc) for s in GLOBAL_SESSIONS]

    us = sessions[-1]
    any_open = any(s.is_open for s in sessions)

    if us.is_open:
        status = "Open"
        next_event = us.next_event
    elif any_open:
        open_names = [s.name for s in sessions if s.is_open]
        status = "Markets active"
        next_event = f"{', '.join(open_names)} open · NY {us.next_event.lower()}"
    else:
        status = us.status
        next_event = us.next_event

    return MarketStatusResponse(
        is_open=any_open,
        status=status,
        next_event=next_event,
        sessions=sessions,
    )


@router.get("/{ticker}/quote", response_model=QuoteResponse)
async def get_live_quote(ticker: str, _=Depends(get_current_principal)):
    ticker = ticker.upper()
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or "regularMarketPrice" not in info:
            fast = stock.fast_info
            price = _safe_float(getattr(fast, "last_price", None))
            prev = _safe_float(getattr(fast, "previous_close", None), price)
            return QuoteResponse(
                ticker=ticker,
                price=price,
                change=round(price - prev, 2),
                change_pct=round(((price - prev) / prev * 100) if prev else 0, 2),
                open=_safe_float(getattr(fast, "open", None), price),
                high=_safe_float(getattr(fast, "day_high", None), price),
                low=_safe_float(getattr(fast, "day_low", None), price),
                prev_close=prev,
                volume=_safe_int(getattr(fast, "last_volume", None)),
                market_cap=_safe_float(getattr(fast, "market_cap", None)),
                pe_ratio=None,
                week52_high=_safe_float(getattr(fast, "year_high", None), price),
                week52_low=_safe_float(getattr(fast, "year_low", None), price),
                avg_volume=0,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        price = _safe_float(info.get("regularMarketPrice") or info.get("currentPrice"))
        prev = _safe_float(info.get("regularMarketPreviousClose") or info.get("previousClose"), price)
        change = price - prev
        change_pct = (change / prev * 100) if prev else 0

        return QuoteResponse(
            ticker=ticker,
            price=round(price, 2),
            change=round(change, 2),
            change_pct=round(change_pct, 2),
            open=_safe_float(info.get("regularMarketOpen") or info.get("open"), price),
            high=_safe_float(info.get("regularMarketDayHigh") or info.get("dayHigh"), price),
            low=_safe_float(info.get("regularMarketDayLow") or info.get("dayLow"), price),
            prev_close=round(prev, 2),
            volume=_safe_int(info.get("regularMarketVolume") or info.get("volume")),
            market_cap=_safe_float(info.get("marketCap")),
            pe_ratio=_safe_float(info.get("trailingPE")),
            week52_high=_safe_float(info.get("fiftyTwoWeekHigh"), price),
            week52_low=_safe_float(info.get("fiftyTwoWeekLow"), price),
            avg_volume=_safe_int(info.get("averageVolume")),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    except Exception as exc:
        logger.exception("failed to fetch quote for %s", ticker)
        raise HTTPException(status_code=502, detail=f"Could not fetch quote for {ticker}") from exc


@router.get("/{ticker}/intraday", response_model=list[IntradayPoint])
async def get_intraday(
    ticker: str,
    interval: str = Query(default="5m", regex="^(1m|2m|5m|15m|30m|1h)$"),
    _=Depends(get_current_principal),
):
    ticker = ticker.upper()
    try:
        data = yf.download(ticker, period="1d", interval=interval, progress=False, auto_adjust=True, threads=False)

        if data is None or data.empty:
            data = yf.download(ticker, period="5d", interval=interval, progress=False, auto_adjust=True, threads=False)

        if data is None or data.empty:
            return []

        if isinstance(data.columns, __import__("pandas").MultiIndex):
            data.columns = [c[0] if isinstance(c, tuple) else c for c in data.columns]

        points = []
        for idx, row in data.iterrows():
            points.append(IntradayPoint(
                time=str(idx),
                open=round(_safe_float(row.get("Open")), 2),
                high=round(_safe_float(row.get("High")), 2),
                low=round(_safe_float(row.get("Low")), 2),
                close=round(_safe_float(row.get("Close")), 2),
                volume=_safe_int(row.get("Volume")),
            ))
        return points
    except Exception as exc:
        logger.exception("failed to fetch intraday for %s", ticker)
        raise HTTPException(status_code=502, detail=f"Could not fetch intraday for {ticker}") from exc


def _aggregate_4h(data):
    """Aggregate 1h candles into 4h candles."""
    if data is None or data.empty:
        return data
    df = data.copy()
    df["group"] = (df.index.hour // 4)
    df["date"] = df.index.date
    agg = df.groupby(["date", "group"]).agg({
        "Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"
    })
    agg.index = df.groupby(["date", "group"]).apply(lambda x: x.index[0])
    return agg


@router.get("/{ticker}/chart")
async def get_chart_data(
    ticker: str,
    period: str = Query(default="6mo", regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|max)$"),
    interval: str = Query(default="1d", regex="^(1m|2m|5m|15m|30m|1h|4h|1d|1wk|1mo)$"),
    _=Depends(get_current_principal),
):
    ticker = ticker.upper()
    try:
        yf_interval = "1h" if interval == "4h" else interval
        is_intraday = yf_interval in ("1m", "2m", "5m", "15m", "30m", "1h")
        data = yf.download(ticker, period=period, interval=yf_interval, progress=False, auto_adjust=True, threads=False, prepost=is_intraday)
        if data is None or data.empty:
            return []

        if isinstance(data.columns, __import__("pandas").MultiIndex):
            data.columns = [c[0] if isinstance(c, tuple) else c for c in data.columns]

        if interval == "4h":
            data = _aggregate_4h(data)

        points = []
        for idx, row in data.iterrows():
            ts = idx
            if hasattr(ts, 'timestamp'):
                epoch = int(ts.timestamp())
            else:
                from datetime import datetime as dt
                epoch = int(dt.combine(ts, dt.min.time()).timestamp())
            points.append({
                "time": epoch,
                "open": round(_safe_float(row.get("Open")), 4),
                "high": round(_safe_float(row.get("High")), 4),
                "low": round(_safe_float(row.get("Low")), 4),
                "close": round(_safe_float(row.get("Close")), 4),
                "volume": _safe_int(row.get("Volume")),
            })
        return points
    except Exception as exc:
        logger.exception("failed to fetch chart for %s", ticker)
        raise HTTPException(status_code=502, detail=f"Could not fetch chart for {ticker}") from exc
