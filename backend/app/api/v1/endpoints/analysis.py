"""
Analysis endpoints — factor scores, backtest, bull/bear cases.

Exposes the XGBoost recommendation engine through REST.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

import numpy as np
import yfinance as yf
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.core.dependencies import get_current_user
from app.services.market_data.fetcher import DataFetcher
from app.services.indicators.featureEngine import FeatureEngine
from app.services.sentiment.finbert import analyze_ticker as finbert_analyze

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analysis", tags=["analysis"])

_fetcher = DataFetcher()
_engine = FeatureEngine()


class FactorScore(BaseModel):
    key: str
    label: str
    score: float
    signal: str


class FactorAnalysisResponse(BaseModel):
    ticker: str
    factors: list[FactorScore]
    composite_score: float
    as_of: str


class BacktestMetrics(BaseModel):
    total_return_pct: float
    buy_hold_return_pct: float
    edge_vs_hold_pct: float
    win_rate: float
    sharpe: float
    max_drawdown_pct: float
    profit_factor: float
    trades: int
    equity_curve: list[float]
    dates: list[str]


class BullBearResponse(BaseModel):
    ticker: str
    bull_cases: list[str]
    bear_cases: list[str]


class FundamentalsResponse(BaseModel):
    ticker: str
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    peg_ratio: Optional[float] = None
    price_to_book: Optional[float] = None
    dividend_yield: Optional[float] = None
    beta: Optional[float] = None
    eps: Optional[float] = None
    revenue: Optional[float] = None
    profit_margin: Optional[float] = None
    roe: Optional[float] = None
    debt_to_equity: Optional[float] = None
    free_cash_flow: Optional[float] = None
    sector: Optional[str] = None
    industry: Optional[str] = None


def _safe(val, default=None):
    if val is None:
        return default
    try:
        f = float(val)
        return default if (np.isnan(f) or np.isinf(f)) else f
    except (TypeError, ValueError):
        return default


def _compute_factor_scores(ticker: str) -> dict:
    """Compute 6-factor scores from live yfinance data + technical indicators."""
    try:
        raw = _fetcher.fetch_historical(ticker, period="6mo")
        df = _engine.calculate_all_features(raw)
    except Exception as exc:
        logger.warning("factor computation failed for %s: %s", ticker, exc)
        return {}

    if df.empty:
        return {}

    latest = df.iloc[-1]
    scores = {}

    # 1. Momentum — RSI + MACD + price position
    rsi = latest.get("RSI_14", 50)
    macd_hist = latest.get("MACD_Histogram", 0)
    price_pos = latest.get("Price_Position", 0.5)
    momentum_raw = (rsi / 100) * 0.4 + (0.5 + np.clip(macd_hist / 2, -0.5, 0.5)) * 0.3 + price_pos * 0.3
    scores["momentum"] = {"score": round(np.clip(momentum_raw * 100, 0, 100), 1), "label": "Technical Momentum"}

    # 2. Volatility / Risk — inverse of volatility is "safety"
    vol20 = latest.get("Volatility_20", 0.02)
    atr14 = latest.get("ATR_14", 1)
    close = latest.get("Close", 100)
    atr_pct = atr14 / close if close > 0 else 0.02
    vol_score = 1 - np.clip((vol20 * 100) / 5, 0, 1)
    atr_score = 1 - np.clip(atr_pct / 0.05, 0, 1)
    scores["volatility"] = {"score": round(np.clip(((vol_score + atr_score) / 2) * 100, 0, 100), 1), "label": "Volatility / Risk"}

    # 3. Volume trend — volume ratio and MFI
    vol_ratio = latest.get("Volume_Ratio", 1.0)
    mfi = latest.get("MFI_14", 50)
    vol_trend = np.clip(vol_ratio / 2, 0, 1) * 0.5 + (mfi / 100) * 0.5
    scores["volume"] = {"score": round(np.clip(vol_trend * 100, 0, 100), 1), "label": "Volume Trend"}

    # 4. Valuation — Bollinger band position (proxy for mean-reversion opportunity)
    bb_pos = latest.get("BB_Position", 0.5)
    valuation_score = 1 - bb_pos
    price_sma20 = latest.get("Price_to_SMA_20", 1.0)
    price_sma50 = latest.get("Price_to_SMA_50", 1.0)
    sma_score = 1 - np.clip((price_sma20 + price_sma50 - 2) / 0.2, -1, 1) * 0.5
    scores["valuation"] = {"score": round(np.clip(((valuation_score + sma_score) / 2) * 100, 0, 100), 1), "label": "Valuation"}

    # 5. Growth / Fundamentals — ROC + trend
    roc = latest.get("ROC_10", 0)
    above_sma = latest.get("Price_Above_SMA_20", 0)
    growth_raw = np.clip(roc / 20, -1, 1) * 0.5 + 0.5 + above_sma * 0.3
    scores["growth"] = {"score": round(np.clip(growth_raw * 100 / 1.8, 0, 100), 1), "label": "Growth / Fundamentals"}

    # 6. Sentiment — FinBERT on recent news headlines, OBV trend as fallback
    try:
        finbert_result = finbert_analyze(ticker, max_headlines=10)
        if finbert_result.headline_count > 0:
            sent_score = finbert_result.overall_score
        else:
            raise ValueError("no headlines")
    except Exception:
        obv_series = df["OBV"].tail(20)
        if len(obv_series) >= 2:
            obv_trend = (obv_series.iloc[-1] - obv_series.iloc[0]) / (abs(obv_series.iloc[0]) + 1)
            sent_score = round(np.clip(0.5 + obv_trend * 5, 0, 1) * 100, 1)
        else:
            sent_score = 50.0
    scores["sentiment"] = {"score": round(np.clip(sent_score, 0, 100), 1), "label": "News Sentiment (FinBERT)"}

    return scores


def _generate_bull_bear(ticker: str, scores: dict) -> tuple[list[str], list[str]]:
    """Generate contextual bull/bear cases from factor scores and market data."""
    bull = []
    bear = []

    try:
        stock = yf.Ticker(ticker)
        info = stock.info or {}
    except Exception:
        info = {}

    # Momentum
    m = scores.get("momentum", {}).get("score", 50)
    if m > 60:
        bull.append("Strong technical momentum — price above key moving averages with positive MACD crossover")
    elif m < 40:
        bear.append("Weak momentum — price below moving averages, MACD histogram turning negative")

    # Volatility
    v = scores.get("volatility", {}).get("score", 50)
    if v > 60:
        bull.append("Low volatility regime — stable price action reduces downside risk")
    elif v < 40:
        bear.append("Elevated volatility — wide daily ranges increase the probability of sharp drawdowns")

    # Volume
    vol = scores.get("volume", {}).get("score", 50)
    if vol > 60:
        bull.append("Volume expansion confirms the current trend — institutional participation likely")
    elif vol < 40:
        bear.append("Declining volume suggests fading conviction — the current move may lack follow-through")

    # Valuation
    val = scores.get("valuation", {}).get("score", 50)
    if val > 60:
        bull.append("Price below key Bollinger mid-band — potential mean-reversion entry for value buyers")
    elif val < 40:
        bear.append("Extended valuation — trading above upper Bollinger bands suggests overextension")

    # Growth
    g = scores.get("growth", {}).get("score", 50)
    if g > 60:
        bull.append("Positive rate of change and trending above SMA-20 — fundamentals support continuation")
    elif g < 40:
        bear.append("Negative rate of change with price below SMA-20 — growth metrics deteriorating")

    # Sentiment (FinBERT)
    s = scores.get("sentiment", {}).get("score", 50)
    if s > 60:
        bull.append("FinBERT detects positive news sentiment — recent headlines signal bullish market perception")
    elif s < 40:
        bear.append("FinBERT detects negative news sentiment — recent headlines signal bearish market perception")

    # Fundamentals from yfinance
    pe = _safe(info.get("trailingPE"))
    if pe and pe < 15:
        bull.append(f"Attractive P/E ratio of {pe:.1f}x — below market average, suggesting undervaluation")
    elif pe and pe > 35:
        bear.append(f"Elevated P/E of {pe:.1f}x — priced for perfection, vulnerable to earnings misses")

    margin = _safe(info.get("profitMargins"))
    if margin and margin > 0.2:
        bull.append(f"Strong profit margins of {margin*100:.0f}% — pricing power and operational efficiency")

    debt = _safe(info.get("debtToEquity"))
    if debt and debt > 150:
        bear.append(f"High debt-to-equity of {debt:.0f}% — leveraged balance sheet increases risk in downturns")

    if not bull:
        bull.append("No strong bullish signals identified at current levels")
    if not bear:
        bear.append("No major bearish red flags detected at current levels")

    return bull, bear


@router.get("/{ticker}/factors", response_model=FactorAnalysisResponse)
async def get_factor_analysis(
    ticker: str,
    w_sentiment: float = Query(default=14),
    w_momentum: float = Query(default=22),
    w_valuation: float = Query(default=20),
    w_volatility: float = Query(default=18),
    w_volume: float = Query(default=10),
    w_growth: float = Query(default=16),
    _=Depends(get_current_user),
):
    ticker = ticker.upper()
    raw_scores = _compute_factor_scores(ticker)

    if not raw_scores:
        raise HTTPException(status_code=404, detail=f"Could not compute factors for {ticker}")

    weights = {
        "sentiment": w_sentiment,
        "momentum": w_momentum,
        "valuation": w_valuation,
        "volatility": w_volatility,
        "volume": w_volume,
        "growth": w_growth,
    }
    total_w = sum(weights.values()) or 1

    factors = []
    composite = 0
    for key, w in weights.items():
        data = raw_scores.get(key, {"score": 50, "label": key})
        score = data["score"]
        signal = "Bullish" if score > 60 else "Bearish" if score < 40 else "Neutral"
        factors.append(FactorScore(key=key, label=data["label"], score=score, signal=signal))
        composite += score * (w / total_w)

    return FactorAnalysisResponse(
        ticker=ticker,
        factors=factors,
        composite_score=round(composite, 1),
        as_of=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    )


def _compute_daily_composite(df, weights: dict) -> np.ndarray:
    """Compute a daily composite score array from indicator data and factor weights."""
    total_w = sum(weights.values()) or 1
    n = len(df)
    composite = np.zeros(n)

    close = df["Close"].values
    rsi = df["RSI_14"].values
    macd_hist = df["MACD_Histogram"].values
    pp = df["Price_Position"].values
    vol20 = df["Volatility_20"].values
    atr14 = df["ATR_14"].values
    vol_ratio = df["Volume_Ratio"].values
    mfi = df["MFI_14"].values
    bb_pos = df["BB_Position"].values
    p_sma20 = df["Price_to_SMA_20"].values
    p_sma50 = df["Price_to_SMA_50"].values
    roc = df["ROC_10"].values
    above_sma = df["Price_Above_SMA_20"].values
    obv = df["OBV"].values

    for i in range(n):
        scores = {}
        # Momentum
        m_raw = (rsi[i] / 100) * 0.4 + (0.5 + np.clip(macd_hist[i] / 2, -0.5, 0.5)) * 0.3 + pp[i] * 0.3
        scores["momentum"] = np.clip(m_raw * 100, 0, 100)

        # Volatility
        v_s = 1 - np.clip((vol20[i] * 100) / 5, 0, 1)
        atr_pct = atr14[i] / close[i] if close[i] > 0 else 0.02
        a_s = 1 - np.clip(atr_pct / 0.05, 0, 1)
        scores["volatility"] = np.clip(((v_s + a_s) / 2) * 100, 0, 100)

        # Volume
        vt = np.clip(vol_ratio[i] / 2, 0, 1) * 0.5 + (mfi[i] / 100) * 0.5
        scores["volume"] = np.clip(vt * 100, 0, 100)

        # Valuation
        val_s = 1 - bb_pos[i]
        sma_s = 1 - np.clip((p_sma20[i] + p_sma50[i] - 2) / 0.2, -1, 1) * 0.5
        scores["valuation"] = np.clip(((val_s + sma_s) / 2) * 100, 0, 100)

        # Growth
        g_raw = np.clip(roc[i] / 20, -1, 1) * 0.5 + 0.5 + above_sma[i] * 0.3
        scores["growth"] = np.clip(g_raw * 100 / 1.8, 0, 100)

        # Sentiment (OBV lookback)
        lb = max(0, i - 20)
        if i > lb and abs(obv[lb]) > 0:
            obv_trend = (obv[i] - obv[lb]) / (abs(obv[lb]) + 1)
            scores["sentiment"] = np.clip(0.5 + obv_trend * 5, 0, 1) * 100
        else:
            scores["sentiment"] = 50.0

        composite[i] = sum(scores[k] * (weights.get(k, 0) / total_w) for k in scores)

    return composite


RISK_THRESHOLDS = {
    "Conservative": {"buy": 51, "sell": 50, "trail_pct": 0.008},
    "Moderate":     {"buy": 53, "sell": 47, "trail_pct": 0.018},
    "Aggressive":   {"buy": 50, "sell": 42, "trail_pct": 0.040},
}

HORIZON_CONFIG = {
    "Short":  {"hold_min": 1, "hold_max": 5,   "cooldown": 0},
    "Medium": {"hold_min": 2, "hold_max": 15,  "cooldown": 1},
    "Long":   {"hold_min": 5, "hold_max": 40,  "cooldown": 2},
}


@router.get("/{ticker}/backtest", response_model=BacktestMetrics)
async def get_backtest(
    ticker: str,
    period: str = Query(default="1y", regex="^(6mo|1y|2y|5y)$"),
    w_sentiment: float = Query(default=14),
    w_momentum: float = Query(default=22),
    w_valuation: float = Query(default=20),
    w_volatility: float = Query(default=18),
    w_volume: float = Query(default=10),
    w_growth: float = Query(default=16),
    risk: str = Query(default="Moderate", regex="^(Conservative|Moderate|Aggressive)$"),
    horizon: str = Query(default="Medium", regex="^(Short|Medium|Long)$"),
    _=Depends(get_current_user),
):
    ticker = ticker.upper()
    weights = {
        "sentiment": w_sentiment, "momentum": w_momentum,
        "valuation": w_valuation, "volatility": w_volatility,
        "volume": w_volume, "growth": w_growth,
    }
    rt = RISK_THRESHOLDS.get(risk, RISK_THRESHOLDS["Moderate"])
    hc = HORIZON_CONFIG.get(horizon, HORIZON_CONFIG["Medium"])
    buy_thresh = rt["buy"]
    sell_thresh = rt["sell"]
    trail_pct = rt["trail_pct"]
    hold_min = hc["hold_min"]
    cooldown = hc["cooldown"]

    try:
        raw = _fetcher.fetch_historical(ticker, period=period)
        df = _engine.calculate_all_features(raw)

        if df.empty or len(df) < 60:
            raise HTTPException(status_code=400, detail="Insufficient data for backtest")

        composite = _compute_daily_composite(df, weights)
        close = df["Close"].values
        daily_ret = np.diff(close) / close[:-1]

        positions = np.zeros(len(composite), dtype=int)
        pos = 0
        hold_days = 0
        cool = 0
        entry_price = 0.0
        peak_price = 0.0

        for i in range(1, len(composite)):
            if cool > 0:
                cool -= 1
                positions[i] = 0
                continue

            if pos == 1:
                hold_days += 1
                peak_price = max(peak_price, close[i])
                trail_hit = close[i] < peak_price * (1 - trail_pct)
                signal_exit = composite[i] <= sell_thresh and hold_days >= hold_min

                if trail_hit or signal_exit:
                    pos = 0
                    cool = cooldown
                    hold_days = 0
                else:
                    positions[i] = 1
            else:
                if composite[i] >= buy_thresh:
                    pos = 1
                    entry_price = close[i]
                    peak_price = close[i]
                    hold_days = 0
                    positions[i] = 1

        strat_ret = positions[:-1] * daily_ret
        bh_ret = daily_ret

        equity = np.cumprod(1 + strat_ret)
        bh_equity = np.cumprod(1 + bh_ret)

        active_days = strat_ret[positions[:-1] == 1]
        wins = active_days[active_days > 0]
        losses = active_days[active_days < 0]
        n_trades = int(np.abs(np.diff(positions)).sum()) // 2
        win_rate = len(wins) / max(1, len(wins) + len(losses))
        total_ret = float(equity[-1] - 1) * 100
        bh_total = float(bh_equity[-1] - 1) * 100

        std = float(strat_ret.std())
        sharpe = float(np.sqrt(252) * strat_ret.mean() / std) if std > 0 else 0

        running_max = np.maximum.accumulate(equity)
        max_dd = float((1 - equity / running_max).max()) * 100

        gross_gain = float(wins.sum()) if len(wins) else 0
        gross_loss = float(-losses.sum()) if len(losses) else 1e-9
        pf = gross_gain / gross_loss

        step = max(1, len(equity) // 100)
        eq_sampled = equity[::step].tolist()
        dates = [str(df.index[i + 1]) for i in range(0, len(equity), step)]

        return BacktestMetrics(
            total_return_pct=round(total_ret, 2),
            buy_hold_return_pct=round(bh_total, 2),
            edge_vs_hold_pct=round(total_ret - bh_total, 2),
            win_rate=round(win_rate, 4),
            sharpe=round(sharpe, 3),
            max_drawdown_pct=round(max_dd, 2),
            profit_factor=round(pf, 3),
            trades=max(n_trades, 1),
            equity_curve=eq_sampled,
            dates=dates,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("backtest failed for %s", ticker)
        raise HTTPException(status_code=502, detail=f"Backtest failed for {ticker}") from exc


@router.get("/{ticker}/bull-bear", response_model=BullBearResponse)
async def get_bull_bear(ticker: str, _=Depends(get_current_user)):
    ticker = ticker.upper()
    scores = _compute_factor_scores(ticker)
    bull, bear = _generate_bull_bear(ticker, scores)
    return BullBearResponse(ticker=ticker, bull_cases=bull, bear_cases=bear)


@router.get("/{ticker}/fundamentals", response_model=FundamentalsResponse)
async def get_fundamentals(ticker: str, _=Depends(get_current_user)):
    ticker = ticker.upper()
    try:
        stock = yf.Ticker(ticker)
        info = stock.info or {}

        return FundamentalsResponse(
            ticker=ticker,
            market_cap=_safe(info.get("marketCap")),
            pe_ratio=_safe(info.get("trailingPE")),
            forward_pe=_safe(info.get("forwardPE")),
            peg_ratio=_safe(info.get("pegRatio")),
            price_to_book=_safe(info.get("priceToBook")),
            dividend_yield=_safe(info.get("dividendYield")),
            beta=_safe(info.get("beta")),
            eps=_safe(info.get("trailingEps")),
            revenue=_safe(info.get("totalRevenue")),
            profit_margin=_safe(info.get("profitMargins")),
            roe=_safe(info.get("returnOnEquity")),
            debt_to_equity=_safe(info.get("debtToEquity")),
            free_cash_flow=_safe(info.get("freeCashflow")),
            sector=info.get("sector"),
            industry=info.get("industry"),
        )
    except Exception as exc:
        logger.exception("fundamentals failed for %s", ticker)
        raise HTTPException(status_code=502, detail=f"Could not fetch fundamentals for {ticker}") from exc
