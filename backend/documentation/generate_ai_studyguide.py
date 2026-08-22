"""One-page beginner's visual guide to the StockPilot AI layer."""
import os
from html import escape

OUT = os.path.dirname(__file__)
FONT = "Helvetica, Arial, sans-serif"
INK = "#1F2937"
MUT = "#6B7280"


def esc(s): return escape(s, quote=False)


def box(x, y, w, h, title, lines, fill, stroke, tcol=INK):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="2"/>']
    o.append(f'<text x="{x+w/2}" y="{y+22}" font-size="14" font-weight="bold" text-anchor="middle" fill="{tcol}">{esc(title)}</text>')
    for i, ln in enumerate(lines):
        o.append(f'<text x="{x+w/2}" y="{y+42+i*15}" font-size="10.5" text-anchor="middle" fill="{tcol}">{esc(ln)}</text>')
    return o


def arrow(x1, y1, x2, y2, label=None, col="#374151"):
    o = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="2.4"/>']
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    for s in (-0.4, 0.4):
        ax = x2 - 12 * math.cos(ang - s); ay = y2 - 12 * math.sin(ang - s)
        o.append(f'<line x1="{x2}" y1="{y2}" x2="{ax}" y2="{ay}" stroke="{col}" stroke-width="2.4"/>')
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        o.append(f'<rect x="{mx-58}" y="{my-9}" width="116" height="17" rx="4" fill="white"/>')
        o.append(f'<text x="{mx}" y="{my+3.5}" font-size="9.5" text-anchor="middle" fill="{MUT}" font-style="italic">{esc(label)}</text>')
    return o


def build():
    W, H = 1320, 1330
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">',
         f'<rect width="{W}" height="{H}" fill="white"/>',
         f'<text x="{W/2}" y="46" font-size="24" font-weight="bold" text-anchor="middle" fill="{INK}">StockPilot AI Layer &mdash; How It Works</text>',
         f'<text x="{W/2}" y="72" font-size="13" text-anchor="middle" fill="{MUT}">A beginner\'s map: from a stock symbol to a BUY / HOLD / SELL recommendation</text>']
    cx = W / 2

    BLUE, BLUEB = "#EFF6FF", "#3B82F6"
    GREEN, GREENB = "#ECFDF5", "#10B981"
    PURP, PURPB = "#F5F3FF", "#8B5CF6"
    AMB, AMBB = "#FFFBEB", "#F59E0B"
    GREY, GREYB = "#F3F4F6", "#9CA3AF"

    # INPUT
    p += box(cx - 120, 96, 240, 50, "INPUT: a stock symbol", ['e.g. "AAPL"'], "#111827", "#111827", "white")
    p += arrow(cx, 146, cx, 178)

    # 1 DataFetcher
    p += box(cx - 230, 178, 460, 66, "1.  DataFetcher  —  get the data", [
        "Downloads price history from Yahoo Finance.",
        "OHLCV = Open, High, Low, Close, Volume (per day)"], BLUE, BLUEB)
    p += arrow(cx, 244, cx, 276, "raw prices")

    # 2 FeatureEngine
    p += box(cx - 230, 288, 460, 66, "2.  FeatureEngine  —  make clues", [
        "Turns raw prices into 23 technical indicators.",
        'RSI, MACD, moving averages…  (called "features")'], BLUE, BLUEB)
    p += arrow(cx, 354, cx, 386, "features")

    # 3 FinBERT
    p += box(cx - 230, 398, 460, 66, "3.  FinBERT  —  read the news mood", [
        "Reads headlines, scores sentiment 0–100.",
        "No news? falls back to a volume (OBV) proxy."], BLUE, BLUEB)

    # split to two brains
    p += arrow(cx, 464, cx - 300, 512)
    p += arrow(cx, 464, cx + 300, 512)
    p.append(f'<text x="{cx}" y="492" font-size="12" font-weight="bold" text-anchor="middle" fill="{MUT}">TWO INDEPENDENT BRAINS</text>')

    # LEFT brain: six-factor
    lx = cx - 560
    p += box(lx, 512, 470, 250, "BRAIN A  —  Six-Factor Engine", [], GREEN, GREENB)
    p.append(f'<text x="{lx+235}" y="556" font-size="11.5" text-anchor="middle" fill="#047857" font-style="italic">The EXPLAINABLE brain — it shows its reasoning</text>')
    factors = ["1. Sentiment  (news mood)", "2. Momentum  (trending up?)",
               "3. Valuation  (cheap or dear?)", "4. Volatility  (how jumpy?)",
               "5. Volume  (activity confirms?)", "6. Growth  (company growing?)"]
    for i, f in enumerate(factors):
        yy = 578 + i * 22
        p.append(f'<text x="{lx+30}" y="{yy}" font-size="11" fill="{INK}">•  {esc(f)}</text>')
    p.append(f'<text x="{lx+235}" y="748" font-size="10.5" text-anchor="middle" fill="{MUT}">Scores 6 factors, applies your weights → verdict</text>')

    # RIGHT brain: xgboost
    rx = cx + 90
    p += box(rx, 512, 470, 250, "BRAIN B  —  XGBoost Model", [], PURP, PURPB)
    p.append(f'<text x="{rx+235}" y="556" font-size="11.5" text-anchor="middle" fill="#6D28D9" font-style="italic">The LEARNED brain — finds patterns by itself</text>')
    steps = ["TRAIN:  study thousands of past days —",
             "        “these indicators → price went UP/DOWN”",
             "PREDICT:  feed today’s indicators →",
             "        outputs a probability (e.g. 62% DOWN)",
             "It is a team of small decision trees, each",
             "one fixing the previous one’s mistakes."]
    for i, sfx in enumerate(steps):
        yy = 582 + i * 24
        col = "#6D28D9" if sfx.startswith(("TRAIN", "PREDICT")) else INK
        p.append(f'<text x="{rx+28}" y="{yy}" font-size="10.5" fill="{col}">{esc(sfx)}</text>')

    # merge to output
    p += arrow(lx + 235, 762, cx - 4, 812)
    p += arrow(rx + 235, 762, cx + 4, 812)
    p += box(cx - 220, 820, 440, 60, "OUTPUT: the recommendation", [
        "BUY  /  HOLD  /  SELL   +   confidence 0–100%"], "#111827", "#111827", "white")
    p += arrow(cx, 880, cx, 912)

    # backtest
    p += box(cx - 300, 912, 600, 74, "SAFETY CHECK  —  Backtest", [
        "“If I had followed these signals over the last 5 years,",
        "would I have made money?”  Simulates trades with real",
        "costs (fees, slippage). Reports return, win rate, Sharpe."], AMB, AMBB)

    # glossary
    gy = 1020
    p.append(f'<rect x="60" y="{gy}" width="{W-120}" height="270" rx="10" fill="{GREY}" stroke="{GREYB}" stroke-width="1.4"/>')
    p.append(f'<text x="86" y="{gy+30}" font-size="15" font-weight="bold" fill="{INK}">Beginner glossary &mdash; the words that trip people up</text>')
    gloss = [
        ("Feature", "a clue/input the model uses (an indicator like RSI)."),
        ("Label / target", "the answer we want (did the price go UP or DOWN?)."),
        ("Training", "the model learning patterns from past examples."),
        ("Prediction (inference)", "using the trained model on new, unseen data."),
        ("Probability", "the model’s confidence, 0–100%."),
        ("Accuracy", "how often the model is right."),
        ("Walk-forward validation", "fair testing: train on the past, test on the future (no peeking)."),
        ("Backtest", "simulating the strategy on historical data to see if it works."),
        ("OHLCV", "Open, High, Low, Close, Volume — a stock’s daily data."),
    ]
    for i, (term, meaning) in enumerate(gloss):
        yy = gy + 58 + i * 24
        p.append(f'<text x="86" y="{yy}" font-size="11" font-weight="bold" fill="#111827">{esc(term)}</text>')
        p.append(f'<text x="290" y="{yy}" font-size="11" fill="{INK}">{esc(meaning)}</text>')

    p.append(f'<text x="{W/2}" y="{H-14}" font-size="11" text-anchor="middle" fill="{MUT}" font-style="italic">'
             f'Remember: TWO brains — Six-Factor (explains why) + XGBoost (learned from history). A backtest checks it would have worked.</text>')

    p.append("</svg>")
    path = os.path.join(OUT, "StockPilot_AI_StudyGuide.svg")
    open(path, "w", encoding="utf-8").write("\n".join(p))
    print("wrote", os.path.basename(path))
    return path


if __name__ == "__main__":
    build()
