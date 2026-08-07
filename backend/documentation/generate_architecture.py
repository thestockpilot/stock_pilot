"""Generate the StockPilot system architecture diagram.

Layered view of the deployed system. The AI inference layer is drawn as a
black box: its contract (inputs and outputs) is on the boundary, its internals
are deliberately not decomposed here — see the Level 2 DFD for that.

Contents are taken from the repository, not from the proposal:
    Frontend/package.json          client libraries
    backend/pyproject.toml         server libraries
    backend/app/api/v1/endpoints/  routers
    backend/app/services/          domain services
    backend/models/xgboost/        model artefact
"""
import os
from html import escape

OUT_DIR = os.path.dirname(__file__)
FONT = "Helvetica, Arial, sans-serif"

INK = "#111827"
RULE = "#111827"
MUTED = "#6B7280"
BAND = "#F3F4F6"
BLACK = "#0B0F19"


def esc(s):
    return escape(s, quote=False)


# ────────────────────────────────────────────────────────────────
# primitives
# ────────────────────────────────────────────────────────────────
def band(x, y, w, h, title, subtitle=None, fill=BAND):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" '
           f'stroke="{RULE}" stroke-width="2"/>',
           f'<text x="{x+16}" y="{y+25}" font-size="14" font-weight="bold" '
           f'fill="{INK}">{esc(title)}</text>']
    if subtitle:
        out.append(f'<text x="{x+w-16}" y="{y+25}" font-size="10.5" text-anchor="end" '
                   f'fill="{MUTED}">{esc(subtitle)}</text>')
    return out


def unit(x, y, w, h, title, lines=(), fill="white", ink=INK, fs=11, mono=False):
    """A component box inside a band."""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" '
           f'stroke="{RULE}" stroke-width="1.5"/>']
    fam = ' font-family="Consolas, monospace"' if mono else ""
    out.append(f'<text x="{x+w/2}" y="{y+19}" font-size="{fs}" font-weight="bold" '
               f'text-anchor="middle" fill="{ink}"{fam}>{esc(title)}</text>')
    for i, ln in enumerate(lines):
        out.append(f'<text x="{x+w/2}" y="{y+34+i*13}" font-size="9.5" '
                   f'text-anchor="middle" fill="{ink}" opacity="0.85">{esc(ln)}</text>')
    return out


def arrow(x1, y1, x2, y2, label=None, side="right", dashed=False, lw=2):
    dash = ' stroke-dasharray="7,5"' if dashed else ""
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{RULE}" '
           f'stroke-width="{lw}"{dash}/>']
    # head
    if abs(x2 - x1) < abs(y2 - y1):
        d = 1 if y2 > y1 else -1
        out.append(f'<polygon points="{x2},{y2} {x2-6},{y2-10*d} {x2+6},{y2-10*d}" fill="{RULE}"/>')
    else:
        d = 1 if x2 > x1 else -1
        out.append(f'<polygon points="{x2},{y2} {x2-10*d},{y2-6} {x2-10*d},{y2+6}" fill="{RULE}"/>')
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        anchor = "start" if side == "right" else "end"
        ox = 12 if side == "right" else -12
        for i, ln in enumerate(label.split("\n")):
            out.append(f'<text x="{mx+ox}" y="{my-4+i*13}" font-size="10" '
                       f'text-anchor="{anchor}" fill="{INK}">{esc(ln)}</text>')
    return out


def build():
    W, H = 1780, 1560
    L, CW = 56, 1320                      # content left edge / width
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="{FONT}">',
         f'<rect width="{W}" height="{H}" fill="white"/>',
         f'<text x="{W/2}" y="40" font-size="22" font-weight="bold" text-anchor="middle" '
         f'fill="{INK}">StockPilot — System Architecture</text>',
         f'<text x="{W/2}" y="63" font-size="11.5" text-anchor="middle" fill="{MUTED}">'
         f'Layered architecture of the deployed system. The AI inference layer is '
         f'represented as a black box — its contract is shown, its internals are not.</text>']

    # ══ 1. PRESENTATION TIER ═════════════════════════════════════
    y = 88
    p += band(L, y, CW, 208, "1  ·  PRESENTATION TIER",
              "React 18 · Vite 7 · react-router-dom 6 · Chart.js 4 · lightweight-charts 5")
    bx, bw, gap = L + 18, 200, 15
    row = ["Role Dashboard", "Advisor", "Marketplace", "Portfolio", "Journal", "Settings"]
    subs = [["investor / analyst /", "admin, lazy-loaded"], ["six-factor verdict,", "chart, backtest"],
            ["browse, buy, rate,", "request publish"], ["holdings, watchlist,", "allocation"],
            ["trade log,", "equity curve"], ["profile, security,", "notifications"]]
    for i, (t, s) in enumerate(zip(row, subs)):
        p += unit(bx + i * (bw + gap), y + 44, bw, 62, t, s)
    p += unit(bx, y + 120, 420, 66, "Admin Console  (role: admin)",
              ["revenue · pending reviews · listings · strategies", "users · marketplace thresholds"])
    p += unit(bx + 435, y + 120, 420, 66, "Shared shell",
              ["Layout · role-aware Header · notification tray", "StatCard, MarketIndices, WatchlistPanel widgets"])
    p += unit(bx + 870, y + 120, 415, 66, "API client  (axios)",
              ["JWT Bearer interceptor · 401 refresh-and-retry",
               "with a queue so concurrent calls refresh once"], mono=False)

    # ══ 2. APPLICATION TIER ══════════════════════════════════════
    y2 = 344
    p += arrow(L + CW / 2, y + 208, L + CW / 2, y2,
               "HTTPS · JSON · REST  /api/v1", side="right")
    p += band(L, y2, CW, 232, "2  ·  APPLICATION TIER",
              "FastAPI (async) · Uvicorn ASGI · Pydantic v2")
    routers = ["auth", "users", "dashboard", "stocks", "live", "predictions", "sentiment",
               "analysis", "strategies", "marketplace", "portfolio", "watchlist",
               "trades", "notifications", "admin"]
    rw, rgap = 78, 8
    for i, r in enumerate(routers):
        rx = L + 18 + (i % 8) * (rw + rgap)
        ry = y2 + 44 + (i // 8) * 40
        p += unit(rx, ry, rw, 32, r, fs=10, mono=True)
    p += unit(L + 720, y2 + 44, 288, 72, "Security  ·  core/security.py",
              ["JWT access + refresh (python-jose)", "bcrypt password hashing (passlib)",
               "get_current_user · require_role(*roles)"])
    p += unit(L + 1020, y2 + 44, 264, 72, "Validation & contracts",
              ["Pydantic v2 request / response schemas", "CORS middleware · structured errors",
               "HTTP 400 / 401 / 403 / 404 / 503"])
    p += unit(L + 720, y2 + 128, 564, 62, "Cross-cutting: RBAC is enforced server-side on every request",
              ["Navigation hides what a role may not use, but the API is the authority — "
               "an investor calling a publish or admin route receives 403."])

    # ══ 3. DOMAIN SERVICES ═══════════════════════════════════════
    y3 = 616
    p += arrow(L + CW / 2, y2 + 232, L + CW / 2, y3, "service calls", side="right")
    p += band(L, y3, CW, 176, "3  ·  DOMAIN SERVICE LAYER", "backend/app/services/")
    svc = [
        ("market_data/fetcher.py", ["yfinance client", "OHLCV, quotes, news, fundamentals"]),
        ("indicators/featureEngine.py", ["23 technical indicators (ta)", "feature engineering"]),
        ("recommendation/engine.py", ["six-factor scoring model", "StockPredictor wrapper"]),
        ("sentiment/finbert.py", ["headline sentiment 0–100", "OBV proxy fallback"]),
        ("vectorbt backtest", ["fees 0.1% · slippage 0.05%", "risk & horizon parameters"]),
    ]
    sw = (CW - 36 - 4 * 14) / 5
    for i, (t, s) in enumerate(svc):
        p += unit(L + 18 + i * (sw + 14), y3 + 44, sw, 76, t, s, fs=10)

    # ══ 4. AI INFERENCE LAYER — BLACK BOX ════════════════════════
    y4 = 856
    BBW = CW - 210          # leaves a clear channel so the ORM path can pass by
    p += arrow(L + 170, y3 + 176, L + 170, y4,
               "feature vector,\nheadline text", side="left")
    p += arrow(L + 1000, y4, L + 1000, y3 + 176,
               "signal, confidence,\nclass probabilities,\nsentiment score", side="right")

    p.append(f'<rect x="{L}" y="{y4}" width="{BBW}" height="196" rx="6" fill="{BLACK}" '
             f'stroke="{RULE}" stroke-width="2"/>')
    p.append(f'<text x="{L+18}" y="{y4+28}" font-size="14" font-weight="bold" fill="white">'
             f'4  ·  AI INFERENCE LAYER  —  BLACK BOX</text>')
    p.append(f'<text x="{L+BBW-18}" y="{y4+28}" font-size="10.5" text-anchor="end" '
             f'fill="#9CA3AF">internals not decomposed at this level</text>')

    # contract, stated on the boundary
    p.append(f'<text x="{L+34}" y="{y4+64}" font-size="11" font-weight="bold" fill="white">'
             f'INPUT CONTRACT</text>')
    for i, ln in enumerate([
        "ticker symbol",
        "6-month OHLCV window",
        "engineered feature vector",
        "recent news headlines",
    ]):
        p.append(f'<text x="{L+34}" y="{y4+84+i*16}" font-size="10" fill="#D1D5DB">'
                 f'▸  {esc(ln)}</text>')

    p.append(f'<text x="{L+BBW-30}" y="{y4+64}" font-size="11" font-weight="bold" '
             f'text-anchor="end" fill="white">OUTPUT CONTRACT</text>')
    for i, ln in enumerate([
        "BUY / HOLD / SELL signal",
        "confidence 0–100",
        "class probability vector",
        "sentiment score 0–100",
    ]):
        p.append(f'<text x="{L+BBW-30}" y="{y4+84+i*16}" font-size="10" text-anchor="end" '
                 f'fill="#D1D5DB">{esc(ln)}  ◂</text>')

    # the two opaque components, named but not opened
    p += unit(L + 292, y4 + 62, 244, 96, "XGBoost classifier",
              ["models/xgboost/current/model.pkl", "loaded once per worker process",
               "walk-forward validated", "( internals opaque )"],
              fill=BLACK, ink="white", fs=11)
    p += unit(L + 552, y4 + 62, 244, 96, "FinBERT",
              ["transformers + torch", "financial-domain language model",
               "CPU inference", "( internals opaque )"],
              fill=BLACK, ink="white", fs=11)

    # ══ 5. PERSISTENCE ═══════════════════════════════════════════
    y5 = 1112
    # routed down the clear channel to the right of the black box: persistence is
    # reached from the service layer, never through the model
    p += arrow(L + CW - 100, y3 + 176, L + CW - 100, y5,
               "async ORM session\n(SQLAlchemy → asyncpg)", side="right", lw=2)
    p += band(L, y5, CW, 190, "5  ·  PERSISTENCE TIER",
              "PostgreSQL 16 · SQLAlchemy 2.0 async · asyncpg · Alembic")
    p += unit(L + 18, y5 + 44, 300, 128, "PostgreSQL 16",
              ["single relational database", "3NF schema, 11 tables",
               "UNIQUE, FK and CHECK constraints", "", "Alembic revision-controlled migrations"])
    tables = ["users", "holdings", "watchlist", "trades", "strategies",
              "marketplace_listings", "marketplace_ratings", "predictions",
              "notifications", "platform_settings", "stocks / price_history"]
    p.append(f'<rect x="{L+336}" y="{y5+44}" width="{CW-354}" height="128" rx="4" '
             f'fill="white" stroke="{RULE}" stroke-width="1.5"/>')
    p.append(f'<text x="{L+352}" y="{y5+64}" font-size="11" font-weight="bold" fill="{INK}">'
             f'Tables</text>')
    for i, t in enumerate(tables):
        tx = L + 352 + (i % 4) * 235
        ty = y5 + 88 + (i // 4) * 26
        p.append(f'<text x="{tx}" y="{ty}" font-size="10.5" '
                 f'font-family="Consolas, monospace" fill="{INK}">{esc(t)}</text>')

    # ══ EXTERNAL ═════════════════════════════════════════════════
    ex = L + CW + 24
    p.append(f'<rect x="{ex}" y="{y3}" width="352" height="176" rx="6" fill="white" '
             f'stroke="{RULE}" stroke-width="2" stroke-dasharray="8,5"/>')
    p.append(f'<text x="{ex+16}" y="{y3+25}" font-size="13" font-weight="bold" fill="{INK}">'
             f'EXTERNAL SERVICE</text>')
    p += unit(ex + 16, y3 + 44, 320, 76, "Yahoo Finance  (yfinance)",
              ["OHLCV history · live quotes", "news headlines · fundamentals",
               "the only third-party data source"])
    p.append(f'<text x="{ex+16}" y="{y3+146}" font-size="9.5" fill="{MUTED}">'
             f'No RSS pipeline and no paid market-data feed</text>')
    p.append(f'<text x="{ex+16}" y="{y3+161}" font-size="9.5" fill="{MUTED}">'
             f'are used, despite the proposal implying so.</text>')
    p += arrow(ex, y3 + 88, L + CW + 4, y3 + 88, None)
    p += arrow(L + CW + 4, y3 + 116, ex, y3 + 116, None)
    p.append(f'<text x="{L+CW+14}" y="{y3+82}" font-size="9.5" fill="{INK}">HTTPS</text>')

    # ══ notes + legend ═══════════════════════════════════════════
    ny = y5 + 220
    p.append(f'<text x="{L}" y="{ny}" font-size="12.5" font-weight="bold" fill="{INK}">'
             f'Why the AI layer is drawn as a black box</text>')
    for i, ln in enumerate([
        "At architecture level the rest of the system depends only on the layer's contract, not on how a verdict is produced. Any model could be",
        "swapped behind that interface — a different classifier, a hosted API, a rules engine — without a single change above it. The decomposition",
        "of what happens inside is a lower-level concern and is documented in the Level 2 DFD (processes 3.3 to 3.7).",
        "",
        "Honest limitation to state in the report: the XGBoost model is trained per instrument. Cross-ticker generalisation was tested and failed",
        "(AUC ≈ 0.42), so the black box is not a single global predictor. The six-factor scoring model, not the classifier, drives the explainable verdict.",
    ]):
        p.append(f'<text x="{L}" y="{ny+22+i*17}" font-size="10.5" fill="#333">{esc(ln)}</text>')

    ly = H - 46
    p.append(f'<rect x="{L}" y="{ly-24}" width="{CW+376}" height="40" rx="4" fill="none" '
             f'stroke="#9CA3AF" stroke-width="1"/>')
    items = [("Layer / tier", BAND), ("Component", "white"), ("Opaque (black box)", BLACK)]
    x = L + 20
    for label, fill in items:
        p.append(f'<rect x="{x}" y="{ly-12}" width="24" height="16" rx="3" fill="{fill}" '
                 f'stroke="{RULE}" stroke-width="1.4"/>')
        p.append(f'<text x="{x+33}" y="{ly}" font-size="10.5" fill="#333">{esc(label)}</text>')
        x += 60 + len(label) * 6.4
    p.append(f'<line x1="{x+10}" y1="{ly-4}" x2="{x+58}" y2="{ly-4}" stroke="{RULE}" '
             f'stroke-width="2" stroke-dasharray="7,5"/>')
    p.append(f'<text x="{x+68}" y="{ly}" font-size="10.5" fill="#333">System boundary '
             f'— everything inside the solid bands is built and deployed by the team</text>')

    p.append("</svg>")
    path = os.path.join(OUT_DIR, "StockPilot_Architecture.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(p))
    print("wrote", os.path.basename(path))
    return path


if __name__ == "__main__":
    build()
    print("done")
