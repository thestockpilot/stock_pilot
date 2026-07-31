"""Generate StockPilot System Context PDF — a complete technical briefing
designed to be handed to another AI (or a new developer) as ground truth."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether,
)

NAVY   = HexColor("#1b2a4a")
BLUE   = HexColor("#2E5496")
ACCENT = HexColor("#b8801f")
GREEN  = HexColor("#1E7E45")
RED    = HexColor("#b03a2e")
GREY   = HexColor("#5a5a64")
LIGHTB = HexColor("#eef2f9")
LIGHTG = HexColor("#eaf6ee")
LIGHTGOLD = HexColor("#fbf6e9")
LIGHTRED  = HexColor("#fbeeec")
LIGHTGREY = HexColor("#f4f4f6")
BORDER = HexColor("#c9d3e6")
TEXT   = HexColor("#16161a")

PAGE_W, PAGE_H = A4
MARGIN = 46
CW = PAGE_W - 2 * MARGIN
OUT = os.path.join(os.path.dirname(__file__), "StockPilot_System_Context.pdf")

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                        topMargin=MARGIN, bottomMargin=MARGIN,
                        title="StockPilot - System Context Document",
                        author="Group 13 - CSE5015")

S = getSampleStyleSheet()
S.add(ParagraphStyle("T1", fontName="Helvetica-Bold", fontSize=24, leading=28,
                     textColor=NAVY, alignment=TA_LEFT, spaceAfter=4))
S.add(ParagraphStyle("T2", fontName="Helvetica-Bold", fontSize=14, leading=18,
                     textColor=ACCENT, spaceAfter=10))
S.add(ParagraphStyle("Sub", fontName="Helvetica-Oblique", fontSize=10.5, leading=15,
                     textColor=GREY, spaceAfter=14))
S.add(ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=15, leading=19,
                     textColor=NAVY, spaceBefore=18, spaceAfter=8))
S.add(ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=12, leading=16,
                     textColor=BLUE, spaceBefore=13, spaceAfter=6))
S.add(ParagraphStyle("H3", fontName="Helvetica-Bold", fontSize=10.5, leading=14,
                     textColor=HexColor("#333338"), spaceBefore=10, spaceAfter=4))
S.add(ParagraphStyle("Body", fontName="Helvetica", fontSize=9.5, leading=14,
                     textColor=TEXT, alignment=TA_JUSTIFY, spaceAfter=7))
S.add(ParagraphStyle("Bul", fontName="Helvetica", fontSize=9.5, leading=13.5,
                     textColor=TEXT, alignment=TA_JUSTIFY, spaceAfter=3,
                     leftIndent=14, bulletIndent=4))
S.add(ParagraphStyle("CodeBlock", fontName="Courier", fontSize=8, leading=11,
                     textColor=HexColor("#14141a"), backColor=LIGHTGREY,
                     borderPadding=7, spaceBefore=4, spaceAfter=8,
                     leftIndent=6, rightIndent=6))
S.add(ParagraphStyle("Cell", fontName="Helvetica", fontSize=8.2, leading=11, textColor=TEXT))
S.add(ParagraphStyle("CellB", fontName="Helvetica-Bold", fontSize=8.2, leading=11, textColor=TEXT))
S.add(ParagraphStyle("CellC", fontName="Courier", fontSize=7.6, leading=10.5, textColor=HexColor("#14141a")))
S.add(ParagraphStyle("Head", fontName="Helvetica-Bold", fontSize=8.4, leading=11, textColor=white))
S.add(ParagraphStyle("CoTitle", fontName="Helvetica-Bold", fontSize=9.5, leading=12.5, textColor=TEXT))
S.add(ParagraphStyle("CoBody", fontName="Helvetica", fontSize=9, leading=13, textColor=TEXT, alignment=TA_JUSTIFY))
S.add(ParagraphStyle("Cap", fontName="Helvetica-Oblique", fontSize=8, leading=11,
                     textColor=GREY, alignment=TA_CENTER, spaceBefore=3, spaceAfter=10))

def P(t, s="Body"): return Paragraph(t, S[s])
def _p(t): return Paragraph(str(t), S["Cell"])
def _pb(t): return Paragraph(str(t), S["CellB"])
def _pc(t): return Paragraph(str(t), S["CellC"])
def _ph(t): return Paragraph(str(t), S["Head"])
def bullet(t): return Paragraph(t, S["Bul"], bulletText="•")

def rule(color=ACCENT, w=1.1, after=10):
    t = Table([[""]], colWidths=[CW])
    t.setStyle(TableStyle([("LINEBELOW", (0,0), (-1,-1), w, color),
                           ("BOTTOMPADDING", (0,0), (-1,-1), after)]))
    return t

def callout(title, body, bg=LIGHTB, ac=BLUE):
    tp = Paragraph(f"<b>{title}</b>", S["CoTitle"])
    bp = Paragraph(body, S["CoBody"])
    t = Table([[tp], [bp]], colWidths=[CW - 14])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("LEFTPADDING", (0,0), (-1,-1), 11), ("RIGHTPADDING", (0,0), (-1,-1), 9),
        ("TOPPADDING", (0,0), (0,0), 8), ("BOTTOMPADDING", (-1,-1), (-1,-1), 9),
        ("LINEBEFORE", (0,0), (0,-1), 3, ac), ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    return t

def table(headers, rows, widths, code_cols=(), zebra=True):
    data = [[_ph(h) for h in headers]]
    for r in rows:
        row = []
        for i, c in enumerate(r):
            row.append(_pc(c) if i in code_cols else _p(c))
        data.append(row)
    t = Table(data, colWidths=widths, repeatRows=1)
    st = [
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("GRID", (0,0), (-1,-1), 0.4, BORDER),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]
    if zebra:
        st.append(("ROWBACKGROUNDS", (0,1), (-1,-1), [white, HexColor("#f7f8fb")]))
    t.setStyle(TableStyle(st))
    return t

def code(txt):
    esc = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(esc.replace("\n", "<br/>"), S["CodeBlock"])

st = []

# ───────────────── COVER ─────────────────
st.append(P("StockPilot", "T1"))
st.append(P("System Context Document &mdash; Full Technical Briefing", "T2"))
st.append(P("A complete, verified description of the StockPilot platform: architecture, database, "
            "API surface, frontend, AI/ML pipeline, and end-to-end data flows. Written to be used as "
            "ground-truth context by an AI assistant or a developer joining the project.", "Sub"))
st.append(rule())

meta = [
    ["Project", "StockPilot &mdash; AI-powered investment advisory web platform"],
    ["Course", "CSE5015 Computing Project, HND in Computing &amp; Software Engineering (ICBT), Batch 131, Group 13"],
    ["Repository", "github.com/thestockpilot/stock_pilot &mdash; two apps: <font face='Courier'>backend/</font> (FastAPI) and <font face='Courier'>Frontend/</font> (React)"],
    ["Stack", "React 18 + Vite | FastAPI (async) | PostgreSQL 16 | XGBoost, FinBERT, vectorbt | yfinance"],
    ["Scale", "12 database tables &middot; 60 REST endpoints &middot; 3 user roles &middot; 7 frontend routes"],
    ["Status", "Functional end-to-end; known design drift documented in Section 11"],
]
st.append(table(["Field", "Value"],
                [[m[0], m[1]] for m in meta],
                [1.15*inch, CW - 1.15*inch]))
st.append(Spacer(1, 10))
st.append(callout("How to use this document",
    "Sections 2&ndash;10 describe the system as it is actually implemented (verified against source code, "
    "not against the original proposal). <b>Section 11 lists known gaps where the built system differs from "
    "the written proposal</b> &mdash; read it before making claims about the system. Section 12 covers how to run it.",
    LIGHTGOLD, ACCENT))

# ───────────────── 1. WHAT IT IS ─────────────────
st.append(P("1. What StockPilot Is", "H1"))
st.append(P(
    "StockPilot is a web application that helps retail investors make evidence-based trading decisions. "
    "For any stock ticker, it produces an <b>explainable BUY / HOLD / SELL verdict</b> with a confidence score, "
    "derived from a weighted six-factor model (sentiment, momentum, valuation, volatility, volume, growth). "
    "Unlike opaque 'signal' services, every verdict exposes the contribution of each factor so the user can see "
    "<i>why</i> the recommendation was made."))
st.append(P(
    "Around that core the platform provides a portfolio tracker with live valuation, a watchlist, a trading "
    "journal that derives win rate and profit factor, and a strategy marketplace where users publish factor-weight "
    "configurations that must pass an objective backtest before an administrator lists them."))

st.append(P("1.1 User roles", "H2"))
st.append(table(["Role", "Capabilities"], [
    ["investor", "Register/login, search stocks, tune factor weights, get verdicts, run backtests, manage portfolio &amp; watchlist, log trades, browse/purchase marketplace strategies, request to publish a strategy."],
    ["analyst", "All investor capabilities. (Role exists in the schema and is enforced by RBAC, but publishing is now open to every authenticated user &mdash; see Section 11.)"],
    ["admin", "All of the above plus the Admin dashboard: approve/reject/remove listings, manage users (role, status, delete), configure marketplace thresholds, view revenue and platform statistics."],
], [0.85*inch, CW - 0.85*inch], code_cols=(0,)))

# ───────────────── 2. TECH STACK ─────────────────
st.append(P("2. Technology Stack (verified)", "H1"))
st.append(table(["Layer", "Technology", "Notes"], [
    ["Frontend", "React 18.3, Vite 7, react-router-dom 6, axios, Chart.js 4 + react-chartjs-2, lightweight-charts",
     "Plain custom CSS (single global.css, ~1570 lines). No Tailwind, no CSS framework, no Redux."],
    ["Backend", "FastAPI, Uvicorn, Pydantic, SQLAlchemy 2.0 (async), asyncpg",
     "Fully asynchronous request handling; Pydantic schemas validate all I/O."],
    ["Database", "PostgreSQL 16", "12 tables, UUID primary keys, JSONB for factor weights, native enums."],
    ["Migrations", "Alembic (+ SQLAlchemy create_all at startup)", "Hybrid: create_all runs on boot; Alembic revisions exist for later changes."],
    ["AI / ML", "XGBoost, FinBERT (HuggingFace Transformers), NumPy, Pandas, ta",
     "FinBERT classifies news headline sentiment; XGBoost powers the standalone predictor service."],
    ["Backtesting", "vectorbt 1.1", "Event-driven portfolio simulation with fees, slippage, trailing stop, take-profit."],
    ["Market data", "yfinance (Yahoo Finance)", "Live quotes, historical OHLCV, fundamentals, and news headlines."],
    ["Auth", "JWT (access + refresh), bcrypt", "Stateless; role-based access enforced by FastAPI dependencies."],
], [0.78*inch, 1.95*inch, CW - 2.73*inch]))

# ───────────────── 3. REPO MAP ─────────────────
st.append(P("3. Repository Map", "H1"))
st.append(code(
"""stock_pilot/
├── backend/
│   ├── app/
│   │   ├── main.py                 FastAPI app, CORS, lifespan (create_all), static mounts
│   │   ├── core/
│   │   │   ├── config.py           pydantic-settings; reads .env (DATABASE_URL, JWT secret)
│   │   │   ├── security.py         bcrypt hashing, JWT encode/decode
│   │   │   └── dependencies.py     get_current_user, require_role(*roles)
│   │   ├── db/
│   │   │   ├── base.py             DeclarativeBase + constraint naming convention
│   │   │   ├── session.py          async engine (pool 10/20), AsyncSessionLocal, get_db()
│   │   │   └── models/             12 ORM models (user, stock, prediction, portfolio,
│   │   │                           watchlist, trade, strategy, marketplace, notification, settings)
│   │   ├── schemas/                Pydantic request/response models
│   │   ├── services/
│   │   │   ├── market_data/fetcher.py       DataFetcher - yfinance OHLCV + CSV cache
│   │   │   ├── indicators/featureEngine.py  23 technical indicators
│   │   │   ├── sentiment/finbert.py         headline fetch + FinBERT classification
│   │   │   └── recommendation/engine.py     StockPredictor (XGBoost train/backtest/predict)
│   │   └── api/v1/
│   │       ├── router.py           mounts all endpoint routers under /api/v1
│   │       └── endpoints/          15 route modules (see Section 6)
│   ├── alembic/                    migration environment + versions
│   ├── seed.py                     drops & recreates tables, inserts demo data
│   └── pyproject.toml / uv.lock    dependencies (managed with uv)
└── Frontend/
    ├── src/
    │   ├── main.jsx / App.jsx      entry point
    │   ├── routes/AppRouter.jsx    routes + ProtectedRoute / AdminRoute / AuthRoute guards
    │   ├── context/AuthContext.jsx global auth state (user, login, logout, token persist)
    │   ├── api/client.js           axios instance + JWT interceptor + 401 refresh-and-retry
    │   ├── api/cache.js            simple client-side response cache
    │   ├── hooks/                  9 files exporting 20 data hooks (see Section 7)
    │   ├── components/             admin, advisor, auth, dashboard, journal, layout,
    │   │                           marketplace, portfolio, settings, ui
    │   └── styles/global.css       entire design system (dark 'Terminal Luxe' theme)
    └── package.json / vite.config.js"""))

# ───────────────── 4. ARCHITECTURE ─────────────────
st.append(PageBreak())
st.append(P("4. Architecture", "H1"))
st.append(P("StockPilot follows a five-layer architecture. Requests flow downward; data flows back up."))
st.append(table(["Layer", "Responsibility", "Key components"], [
    ["1. Presentation", "Renders UI, holds client state, calls the REST API with a JWT.",
     "React components (Dashboard, Advisor, Portfolio, Journal, Marketplace, Admin, Settings, Auth), custom hooks, axios client"],
    ["2. Application", "HTTP routing, authentication, authorisation, validation, orchestration, transactions.",
     "FastAPI routers, get_current_user / require_role dependencies, Pydantic schemas, get_db session"],
    ["3. AI &amp; Analytics", "Turns raw market data into scores, verdicts and backtest metrics.",
     "Six-factor scorer, FinBERT sentiment, XGBoost predictor, vectorbt backtest engine"],
    ["4. Data", "Retrieves and prepares external market data; computes indicators.",
     "DataFetcher (yfinance), FeatureEngine (23 indicators), news headline fetch"],
    ["5. Storage", "Durable persistence of users, portfolios, strategies, listings, settings.",
     "PostgreSQL via SQLAlchemy async ORM"],
], [1.0*inch, 1.9*inch, CW - 2.9*inch]))
st.append(Spacer(1, 8))
st.append(callout("Session &amp; transaction model",
    "Every request that touches the database receives an <font face='Courier'>AsyncSession</font> from "
    "<font face='Courier'>get_db()</font>. The session <b>commits on success and rolls back on any exception</b>, "
    "so a request either applies all of its changes or none of them. Connection pooling is configured at "
    "pool_size=10, max_overflow=20, with pre-ping enabled.", LIGHTG, GREEN))

# ───────────────── 5. DATABASE ─────────────────
st.append(P("5. Database Schema", "H1"))
st.append(P("PostgreSQL, 12 tables. All primary keys are UUIDs except <font face='Courier'>price_history</font> "
            "(composite ticker+date) and <font face='Courier'>platform_settings</font> (singleton integer id=1)."))

st.append(P("5.1 Tables", "H2"))
tbl_rows = [
    ["users", "id, email(uniq), password_hash, full_name, role(enum), phone, bio, avatar_url, is_active, created_at, updated_at", "Identity, authentication, RBAC"],
    ["stocks", "id, ticker(uniq), name, sector, industry, updated_at", "Reference catalogue of tradeable tickers"],
    ["price_history", "ticker+date (composite PK), open, high, low, close, volume", "Historical OHLCV cache (see Section 11)"],
    ["predictions", "id, ticker, signal(enum), confidence, probability_up, probability_down, composite_score, model_version, created_at", "Stored AI predictions for badges/history"],
    ["holdings", "id, user_id&rarr;users, ticker, quantity, avg_cost, current_price, opened_at, closed_at", "Portfolio positions"],
    ["watchlist", "id, user_id&rarr;users, ticker, added_at &mdash; UNIQUE(user_id,ticker)", "Stocks a user monitors"],
    ["trades", "id, user_id&rarr;users, ticker, side(enum), entry_price, exit_price, stop_loss, take_profit, quantity, strategy_label, opened_at, closed_at, notes, created_at", "Trading journal entries"],
    ["strategies", "id, owner_id&rarr;users (nullable), name, description, weights(JSONB), is_preset, is_published, created_at, updated_at", "Six-factor weight configurations"],
    ["marketplace_listings", "id, strategy_id&rarr;strategies (UNIQUE), price_cents, status(enum), avg_rating, rating_count, sales_count, backtest_return/sharpe/winrate/trades/max_drawdown/profit_factor, listed_at, created_at", "Published strategies + verification metrics"],
    ["marketplace_ratings", "id, listing_id&rarr;listings, user_id&rarr;users, rating, review, created_at", "User ratings/reviews"],
    ["notifications", "id, user_id&rarr;users, kind(enum), title, body, is_read, created_at", "In-app notifications"],
    ["platform_settings", "id(=1), min_trades, min_winrate, min_sharpe, max_drawdown, min_profit_factor", "Admin-configurable approval thresholds"],
]
st.append(table(["Table", "Columns", "Purpose"], tbl_rows,
                [1.15*inch, CW - 2.75*inch, 1.6*inch], code_cols=(0,)))

st.append(P("5.2 Enumerations", "H2"))
st.append(table(["Enum", "Column", "Values"], [
    ["UserRole", "users.role", "investor, analyst, admin"],
    ["SignalType", "predictions.signal", "BUY, HOLD, SELL"],
    ["TradeSide", "trades.side", "buy, sell"],
    ["ListingStatus", "marketplace_listings.status", "draft, review, verified, listed, removed"],
    ["NotificationKind", "notifications.kind", "verdict_change, price_alert, marketplace, weekly_report, security, system"],
], [1.25*inch, 1.85*inch, CW - 3.1*inch], code_cols=(0,1)))

st.append(P("5.3 Relationships and cardinality", "H2"))
st.append(table(["Parent", "Card.", "Child", "Foreign key", "On delete"], [
    ["users", "1 : N", "holdings", "holdings.user_id", "CASCADE"],
    ["users", "1 : N", "watchlist", "watchlist.user_id", "CASCADE"],
    ["users", "1 : N", "trades", "trades.user_id", "CASCADE"],
    ["users", "1 : N", "strategies", "strategies.owner_id (nullable = system preset)", "CASCADE"],
    ["users", "1 : N", "notifications", "notifications.user_id", "CASCADE"],
    ["users", "1 : N", "marketplace_ratings", "marketplace_ratings.user_id", "CASCADE"],
    ["strategies", "1 : 1", "marketplace_listings", "listings.strategy_id (UNIQUE)", "RESTRICT"],
    ["marketplace_listings", "1 : N", "marketplace_ratings", "ratings.listing_id", "CASCADE"],
], [1.25*inch, 0.5*inch, 1.35*inch, 1.85*inch, CW - 4.95*inch], code_cols=(0,2,3)))
st.append(Spacer(1, 6))
st.append(callout("Design note &mdash; why stocks/price_history/predictions have no foreign keys",
    "These three tables link to instruments by <b>ticker string</b> rather than a foreign key to "
    "<font face='Courier'>stocks.id</font>. Ticker symbols are stable, human-readable, and are the same keys used by "
    "the external Yahoo Finance API, so this avoids a join on every lookup. It is a deliberate denormalisation.",
    LIGHTB, BLUE))

# ───────────────── 6. API ─────────────────
st.append(PageBreak())
st.append(P("6. REST API Reference", "H1"))
st.append(P("All routes are mounted under <font face='Courier'>/api/v1</font>. Every endpoint except "
            "<font face='Courier'>/auth/*</font> requires a valid JWT in the <font face='Courier'>Authorization: "
            "Bearer</font> header. Admin routes additionally require role=admin."))

api_groups = [
    ("auth.py &mdash; authentication (public)", [
        ["POST", "/auth/register", "Create account (bcrypt hash), returns tokens", "users"],
        ["POST", "/auth/login", "Verify credentials, issue access + refresh JWT", "users"],
        ["POST", "/auth/refresh", "Exchange refresh token for a new access token", "users"],
    ]),
    ("users.py &mdash; profile", [
        ["GET", "/users/me", "Current user profile", "users"],
        ["PUT", "/users/me", "Update name, email, phone, bio", "users"],
        ["PUT", "/users/me/password", "Change password (verifies old)", "users"],
        ["POST", "/users/me/avatar", "Upload avatar image, store path", "users"],
        ["DELETE", "/users/me/avatar", "Remove avatar", "users"],
    ]),
    ("analysis.py &mdash; AI engine (core)", [
        ["GET", "/analysis/{ticker}/factors", "Six-factor scores + composite + verdict (live yfinance + FinBERT)", "none (live)"],
        ["GET", "/analysis/{ticker}/backtest", "vectorbt backtest; params: period, risk, horizon, w_* weights", "none (live)"],
        ["GET", "/analysis/{ticker}/bull-bear", "Generated bull case / bear case bullet points", "none (live)"],
        ["GET", "/analysis/{ticker}/fundamentals", "Fundamentals snapshot from yfinance", "none (live)"],
    ]),
    ("live.py &mdash; market data (no DB)", [
        ["GET", "/live/market-status", "Market open/closed state", "none"],
        ["GET", "/live/{ticker}/quote", "Live price, change, volume", "none"],
        ["GET", "/live/{ticker}/intraday", "Intraday series", "none"],
        ["GET", "/live/{ticker}/chart", "Chart series for a period/interval", "none"],
    ]),
    ("sentiment.py &mdash; NLP (no DB)", [
        ["GET", "/sentiment/{ticker}", "FinBERT sentiment over recent Yahoo Finance headlines", "none"],
    ]),
    ("stocks.py / predictions.py &mdash; reference data", [
        ["GET", "/stocks", "List catalogue", "stocks"],
        ["GET", "/stocks/{ticker}", "One stock", "stocks"],
        ["GET", "/stocks/{ticker}/history", "Stored OHLCV rows", "price_history"],
        ["GET", "/predictions", "All stored predictions (newest first)", "predictions"],
        ["GET", "/predictions/{ticker}", "Latest stored prediction for a ticker", "predictions"],
    ]),
    ("portfolio.py / watchlist.py / trades.py &mdash; user data", [
        ["GET/POST", "/portfolio", "List holdings (with live prices) / add holding", "holdings, stocks"],
        ["PUT/DELETE", "/portfolio/{id}", "Update quantity or cost / remove holding", "holdings"],
        ["GET/POST", "/watchlist", "List / add ticker (duplicate-checked)", "watchlist"],
        ["DELETE", "/watchlist/{ticker}", "Remove ticker", "watchlist"],
        ["GET/POST", "/trades", "List journal / log a trade", "trades"],
        ["DELETE", "/trades/{id}", "Delete journal entry", "trades"],
    ]),
    ("strategies.py &mdash; strategy CRUD + publish", [
        ["GET", "/strategies", "User's own strategies + system presets", "strategies"],
        ["POST", "/strategies", "Create strategy (weights JSONB)", "strategies"],
        ["PUT/DELETE", "/strategies/{id}", "Update / delete own strategy", "strategies"],
        ["POST", "/strategies/{id}/publish", "Validate backtest vs thresholds, create/update listing (status=review)", "strategies, listings, platform_settings"],
    ]),
    ("marketplace.py &mdash; public marketplace", [
        ["GET", "/marketplace", "All listings with eager-loaded strategy + owner", "listings, strategies, users"],
        ["GET", "/marketplace/thresholds", "Current approval thresholds (any signed-in user)", "platform_settings"],
    ]),
    ("notifications.py / dashboard.py", [
        ["GET", "/notifications", "Latest 50 notifications", "notifications"],
        ["PUT", "/notifications/{id}/read", "Mark one read", "notifications"],
        ["PUT", "/notifications/read-all", "Bulk mark all read", "notifications"],
        ["GET", "/dashboard/market-indices", "S&amp;P, Nasdaq, Dow, VIX (live)", "none"],
        ["GET", "/dashboard/sector-breakdown", "Portfolio allocation by sector", "holdings, stocks"],
        ["GET", "/dashboard/portfolio-history", "Monthly P&amp;L curve vs benchmark", "trades, holdings"],
        ["GET", "/dashboard/batch", "All three of the above in parallel (asyncio.gather)", "mixed"],
    ]),
    ("admin.py &mdash; administration (role=admin)", [
        ["GET", "/admin/stats", "User/strategy/listing counts, revenue aggregates", "users, strategies, listings"],
        ["GET", "/admin/revenue", "Revenue totals + top 10 earning strategies", "listings, strategies, users"],
        ["GET", "/admin/users", "List all users", "users"],
        ["PATCH", "/admin/users/{id}/role", "Change a user's role", "users"],
        ["PATCH", "/admin/users/{id}/status", "Activate / suspend user", "users"],
        ["DELETE", "/admin/users/{id}", "Delete user (cascades)", "users"],
        ["GET", "/admin/pending", "Listings awaiting review + full backtest report", "listings, strategies, users"],
        ["GET", "/admin/listings", "All listings", "listings"],
        ["POST", "/admin/listings/{id}/approve", "status&rarr;verified, set listed_at, strategy.is_published=true", "listings, strategies"],
        ["POST", "/admin/listings/{id}/reject", "status&rarr;removed", "listings, strategies"],
        ["POST", "/admin/listings/{id}/remove", "Delist an active listing", "listings, strategies"],
        ["DELETE", "/admin/listings/{id}", "Delete listing permanently", "listings, strategies"],
        ["GET", "/admin/strategies", "All strategies with owner", "strategies, users"],
        ["DELETE", "/admin/strategies/{id}", "Delete strategy + its listing", "strategies, listings"],
        ["GET/PUT", "/admin/thresholds", "Read / update the five approval thresholds", "platform_settings"],
    ]),
]
for title, rows in api_groups:
    st.append(P(title, "H3"))
    st.append(table(["Method", "Path", "Description", "Tables"], rows,
                    [0.68*inch, 1.95*inch, CW - 4.13*inch, 1.5*inch], code_cols=(0,1,3)))
    st.append(Spacer(1, 4))

# ───────────────── 7. FRONTEND ─────────────────
st.append(PageBreak())
st.append(P("7. Frontend Architecture", "H1"))
st.append(P("7.1 Routing and guards", "H2"))
st.append(code(
"""/auth        AuthPage        AuthRoute      - redirects to / if already signed in
/            Dashboard       ProtectedRoute - requires a valid session
/advisor     Advisor         ProtectedRoute
/marketplace Marketplace     ProtectedRoute
/portfolio   Portfolio       ProtectedRoute
/journal     Journal         ProtectedRoute
/settings    Settings        ProtectedRoute
/admin       Admin           AdminRoute     - additionally requires role === 'admin'
*            -> redirect to /"""))
st.append(P("All protected routes render inside <font face='Courier'>Layout</font>, which provides the sticky "
            "<font face='Courier'>Header</font> (brand, nav tabs, live badge, notifications dropdown, user menu)."))

st.append(P("7.2 State management", "H2"))
st.append(bullet("<b>AuthContext</b> &mdash; the only global state. Holds the user object and token; exposes login, register, logout. Tokens persist in localStorage as <font face='Courier'>sp_access_token</font> / <font face='Courier'>sp_refresh_token</font>."))
st.append(bullet("<b>Custom hooks</b> &mdash; all server state. Each hook owns its own fetch, loading flag, error and refetch function. No Redux; component state handles the rest."))
st.append(bullet("<b>api/client.js</b> &mdash; a single axios instance. A request interceptor attaches the JWT; a response interceptor catches 401, calls <font face='Courier'>/auth/refresh</font>, and transparently retries the original request. If refresh fails the user is sent to /auth."))

st.append(P("7.3 Data hooks (20 exported from 9 files)", "H2"))
st.append(table(["File", "Hooks"], [
    ["useLiveMarket.js", "useLiveQuote, useIntraday, useChartData, useMarketStatus, useFactorAnalysis, useBacktest, useBullBear, useFundamentals, useSentiment"],
    ["usePortfolio.js", "usePortfolio"],
    ["useWatchlist.js", "useWatchlist"],
    ["useTrades.js", "useTrades"],
    ["useStrategies.js", "useStrategies"],
    ["useMarketplace.js", "useMarketplace"],
    ["useNotifications.js", "useNotifications"],
    ["usePredictions.js", "usePredictions, usePrediction"],
    ["useStocks.js", "useStocks, useStockDetail, usePriceHistory"],
], [1.4*inch, CW - 1.4*inch], code_cols=(0,)))

st.append(P("7.4 Screens", "H2"))
st.append(table(["Screen", "What it shows"], [
    ["Dashboard", "Market indices strip, 5 stat cards (total value, today P/L, unrealised P/L, open positions, AI BUY count), portfolio-vs-benchmark line chart, watchlist with verdict badges, allocation doughnut, sector breakdown bars, featured strategy, recent journal activity."],
    ["Advisor", "Ticker search + chips; strategy presets or six weight sliders; risk/horizon profile; hero verdict card (BUY/HOLD/SELL + confidence bar); factor contribution bars; price &amp; MA chart; backtest panel (period tabs 6mo/1y/2y/5y, Run Backtest, Download log CSV); bull/bear cases; news sentiment; fundamentals."],
    ["Portfolio", "Stat cards (market value, cost basis, unrealised P/L, cash), holdings table with live price and verdict, allocation chart, add/edit/close position."],
    ["Marketplace", "Threshold cards (live from the API), search/sort/filter toolbar, strategy cards with weights, backtest metrics, rating and price, and the publish-request dialog (select saved strategy, run a real backtest to auto-fill metrics, threshold checklist, submit)."],
    ["Journal", "Trade entry form, journal stats (trades, win rate, net P/L, profit factor), equity curve, outcome doughnut, filterable trade history table."],
    ["Admin", "Six stat tiles; tabs for Revenue, Pending Reviews (full backtest report with per-threshold pass/fail), Listings, Strategies, Users, and Thresholds (editable approval criteria)."],
    ["Settings", "Profile, security/password, notification preferences, display preferences."],
], [0.85*inch, CW - 0.85*inch]))

# ───────────────── 8. AI PIPELINE ─────────────────
st.append(PageBreak())
st.append(P("8. AI &amp; Analytics Pipeline", "H1"))

st.append(P("8.1 Technical indicators (FeatureEngine)", "H2"))
st.append(P("<font face='Courier'>app/services/indicators/featureEngine.py</font> computes 23 columns from raw OHLCV:"))
st.append(code("RSI_14, MACD, MACD_Signal, MACD_Histogram, SMA ratios (Price_to_SMA_20, Price_to_SMA_50,\n"
               "Price_Above_SMA_20), Bollinger Bands (BB_High, BB_Mid, BB_Low, BB_Width, BB_Position),\n"
               "ATR_14, OBV, MFI_14, VWAP_20, ROC_10, Volatility_20, Volume_Ratio, Price_Position,\n"
               "Daily_Return, High_Low_Ratio, Close_Open_Ratio"))

st.append(P("8.2 The six-factor model", "H2"))
st.append(P("Each factor is normalised to 0&ndash;100, then combined using the user's weights "
            "(which must sum to 100). The composite maps to a verdict."))
st.append(table(["Factor", "Derived from"], [
    ["Momentum", "RSI_14 (40%), MACD histogram (30%), Price_Position (30%)"],
    ["Volatility", "Volatility_20 and ATR_14 as a percentage of close &mdash; lower volatility scores higher"],
    ["Volume", "Volume_Ratio (50%) and MFI_14 (50%)"],
    ["Valuation", "Inverted BB_Position and distance from SMA-20/SMA-50"],
    ["Growth", "ROC_10 plus a bonus when price is above SMA-20"],
    ["Sentiment", "<b>Live advisor:</b> FinBERT over recent Yahoo Finance headlines. <b>Backtest:</b> an OBV-trend proxy (20-day lookback), because historical daily sentiment is not stored."],
], [0.95*inch, CW - 0.95*inch]))
st.append(Spacer(1, 4))
st.append(code(
"""composite = SUM( factor_score[k] * weight[k] / SUM(weights) )   for k in six factors

verdict:  composite >= buy_threshold  -> BUY
          composite <= sell_threshold -> SELL
          otherwise                   -> HOLD
confidence = consensus strength across the six factor scores"""))

st.append(P("8.3 FinBERT sentiment", "H2"))
st.append(P("<font face='Courier'>app/services/sentiment/finbert.py</font>: fetches up to 15 recent headlines via "
            "<font face='Courier'>yfinance.Ticker(t).news</font>, classifies each with FinBERT "
            "(positive / negative / neutral probabilities), and aggregates them into a single 0&ndash;100 score "
            "(100 = all strongly positive, 50 = neutral, 0 = all strongly negative). Per-headline results are "
            "returned so the UI can list them. <b>Fetched on demand at request time &mdash; there is no RSS feed, "
            "scheduler, or stored sentiment table.</b>"))

st.append(P("8.4 XGBoost predictor", "H2"))
st.append(P("<font face='Courier'>app/services/recommendation/engine.py</font> defines <font face='Courier'>StockPredictor</font> "
            "with <font face='Courier'>prepare_data, train, walk_forward_evaluate, evaluate, backtest, predict</font>. "
            "It trains a gradient-boosted classifier on the engineered feature set to produce directional "
            "probabilities. The user-facing verdict shown in the Advisor comes from the transparent six-factor "
            "score (chosen for explainability); the XGBoost service supplies the probability model and stored "
            "<font face='Courier'>predictions</font> rows."))

st.append(P("8.5 Backtesting engine (vectorbt)", "H2"))
st.append(P("<font face='Courier'>_run_vectorbt_backtest()</font> in <font face='Courier'>analysis.py</font>. "
            "The six-factor composite generates entry/exit signals; vectorbt simulates the portfolio."))
st.append(code(
"""entries = composite >= buy_threshold
exits   = composite <= sell_threshold

vbt.Portfolio.from_signals(
    close, entries, exits,
    sl_stop = stop_loss,  sl_trail = True,     # trailing stop-loss
    tp_stop = take_profit,                     # take-profit (re-enters after)
    upon_opposite_entry = 'close',
    fees = 0.001, slippage = 0.0005,           # realistic trading costs
    init_cash = 10_000, freq = '1D')

returns: total_return_pct, buy_hold_return_pct, edge_vs_hold_pct, win_rate,
         sharpe, max_drawdown_pct, profit_factor, trades, equity_curve[],
         dates[], trades_log[]  (per-trade ledger: entry/exit date+price, size, PnL)"""))
st.append(P("Risk tolerance and time horizon shape the simulation:"))
st.append(table(["Setting", "Effect"], [
    ["Risk: Conservative / Moderate / Aggressive", "Sets entry conviction (buy threshold 55 / 52 / 49) and scales stop &amp; take-profit width (x0.7 / x1.0 / x1.5)."],
    ["Horizon: Short / Medium / Long", "Sets exit band and trade frequency &mdash; Short: band 2, 2.5% stop, 2.5% TP (many trades); Medium: band 5, 5%, 10%; Long: band 11, 13%, no TP (few trades, rides trends)."],
], [1.9*inch, CW - 1.9*inch]))
st.append(Spacer(1, 5))
st.append(callout("Verified behaviour",
    "The engine is deterministic (identical inputs produce identical output) and its trade ledger reconciles "
    "against real historical prices &mdash; a sample trade's fill matched the actual Yahoo Finance close within the "
    "configured slippage. Trade counts scale with period: on a single ticker, roughly 24&ndash;33 trades over 1 year "
    "and 125&ndash;181 over 5 years at the Short horizon.", LIGHTG, GREEN))

# ───────────────── 9. WORKFLOWS ─────────────────
st.append(PageBreak())
st.append(P("9. End-to-End Workflows", "H1"))

flows = [
 ("9.1 Authentication",
  """1. User submits email + password on /auth (AuthPage).
2. POST /api/v1/auth/login  ->  backend loads user by email, verifies bcrypt hash.
3. Backend returns access token + refresh token (JWT).
4. AuthContext stores them in localStorage and sets the user object.
5. Every later request: axios interceptor adds  Authorization: Bearer <access>.
6. On 401 the interceptor calls /auth/refresh, gets a new access token, retries once.
   If refresh fails -> logout -> redirect /auth.
NOTE: two 401s on a cold load are NORMAL - the app probes /users/me and /auth/refresh
      before any session exists."""),

 ("9.2 Generating a verdict (the core flow)",
  """1. Advisor screen: user picks a ticker and adjusts the six weight sliders.
2. useFactorAnalysis -> GET /api/v1/analysis/{ticker}/factors?w_sentiment=..&w_momentum=..
3. Backend:  DataFetcher.fetch_historical(ticker, '6mo')      [yfinance, LIVE]
             FeatureEngine.calculate_all_features(raw)        [23 indicators]
             finbert.analyze_ticker(ticker)                   [headlines -> sentiment]
             six factor scores -> weighted composite -> BUY/HOLD/SELL + confidence
4. Response: per-factor scores, composite, verdict, confidence, price context.
5. UI renders the verdict card, confidence bar and factor contribution bars.
DB involvement: none on the live path (see Section 11)."""),

 ("9.3 Running a backtest",
  """1. User selects period (6mo/1y/2y/5y) and clicks Run Backtest.
2. GET /api/v1/analysis/{ticker}/backtest?period=&risk=&horizon=&w_*=
3. Backend fetches OHLCV, computes indicators, derives the daily composite series,
   then runs vectorbt in a threadpool (run_in_threadpool - it is CPU-bound).
4. Returns metrics + equity curve + full per-trade ledger.
5. UI shows the stat panel and chart; 'Download log' exports summary + ledger as CSV.
NOTE: the first backtest after a server start takes ~20s while numba compiles
      vectorbt's kernels; subsequent runs are fast."""),

 ("9.4 Publishing a strategy (multi-actor)",
  """1. User creates/saves a strategy in the Advisor  -> POST /strategies.
2. Marketplace -> 'Request Publish' dialog: pick the saved strategy, optionally run a
   real backtest to auto-fill the metrics, set a price.
3. POST /strategies/{id}/publish with the six backtest metrics.
4. Backend loads thresholds from platform_settings and validates each metric.
   - any failure -> 400 with a per-metric breakdown, nothing is stored
   - all pass    -> create/update a marketplace_listing with status = 'review'
5. Admin -> Pending Reviews: sees the full backtest report with per-threshold ticks.
6. POST /admin/listings/{id}/approve
   -> status='verified', listed_at=now(), strategy.is_published=true  (now public)
   or /reject -> status='removed'."""),

 ("9.5 Portfolio valuation",
  """1. Portfolio screen -> GET /api/v1/portfolio.
2. Backend selects the user's open holdings, joins stocks for name/sector,
   and fetches the live price per ticker from yfinance.
3. Computes market value, cost basis and unrealised P/L per position and in total.
4. Dashboard uses GET /dashboard/batch, which runs market-indices, sector-breakdown
   and portfolio-history concurrently with asyncio.gather."""),

 ("9.6 Admin threshold change",
  """1. Admin -> Thresholds tab -> edits values -> PUT /admin/thresholds.
2. Backend validates bounds and updates the singleton platform_settings row.
3. Effect is immediate and global: /strategies/{id}/publish reads the row on every
   submission, and /marketplace/thresholds feeds the UI cards + publish checklist.
   No redeploy required."""),
]
for title, body in flows:
    st.append(P(title, "H2"))
    st.append(code(body))

# ───────────────── 10. SECURITY ─────────────────
st.append(P("10. Security Model", "H1"))
st.append(bullet("<b>Passwords</b> &mdash; bcrypt-hashed, never stored or logged in plain text."))
st.append(bullet("<b>Tokens</b> &mdash; JWT access + refresh, signed with a secret from <font face='Courier'>.env</font>. Stateless, so the backend can scale horizontally."))
st.append(bullet("<b>Authentication</b> &mdash; <font face='Courier'>get_current_user</font> decodes the token, loads the user, and returns 401 if invalid or the user no longer exists."))
st.append(bullet("<b>Authorisation</b> &mdash; <font face='Courier'>require_role(*roles)</font> is a dependency factory; admin routes use <font face='Courier'>require_role(UserRole.admin)</font> and return 403 otherwise."))
st.append(bullet("<b>Secrets</b> &mdash; DATABASE_URL and the JWT secret live in <font face='Courier'>backend/.env</font>, which is git-ignored and must be created per machine."))
st.append(bullet("<b>Data integrity</b> &mdash; foreign keys with cascade deletes, a unique constraint on (user_id, ticker) in watchlist, unique strategy_id on listings, and enum-constrained columns."))

# ───────────────── 11. GAPS ─────────────────
st.append(P("11. Known Gaps and Design Drift", "H1"))
st.append(callout("Read this before describing the system",
    "The written proposal describes a slightly more elaborate design than what was built. The items below are "
    "<b>the built reality</b>. Anyone (human or AI) reasoning about this project should treat this section as "
    "authoritative over the proposal document.", LIGHTRED, RED))
st.append(Spacer(1, 6))
st.append(table(["Area", "Proposal said", "Actually implemented"], [
    ["News sentiment", "Scheduled RSS &rarr; FinBERT &rarr; daily-sentiment ingestion pipeline with a stored daily_sentiment table and pipeline logs.",
     "Headlines are fetched <b>on demand from Yahoo Finance via yfinance</b> and classified by FinBERT at request time. No RSS, no scheduler, no daily_sentiment table."],
    ["Backtest sentiment", "Backtest reads historical daily sentiment rows.",
     "The backtest uses an <b>OBV-trend proxy</b> for the sentiment factor, because historical per-day sentiment is not persisted. FinBERT is used only in the live advisor."],
    ["Backtest scope", "Backtest runs across multiple tickers.",
     "The backtest is <b>single-ticker</b> (vectorbt) over the selected period."],
    ["Storage tables", "purchases, daily_sentiment, admin_logs, personal_strategies tables.",
     "None of these exist. Purchases are tracked by <font face='Courier'>sales_count</font> on the listing; ratings live in marketplace_ratings; there is no admin audit-log table."],
    ["Publishing", "Analyst-only publishing workflow.",
     "Publishing is open to <b>any authenticated user</b>; quality is still gated by the threshold check plus admin approval."],
], [0.95*inch, 2.1*inch, CW - 3.05*inch]))

st.append(P("11.1 Tables not on the live compute path", "H2"))
st.append(P("<font face='Courier'>price_history</font> and <font face='Courier'>predictions</font> exist and are "
            "queried by <font face='Courier'>/stocks/{t}/history</font> and <font face='Courier'>/predictions</font>, "
            "and are populated by <font face='Courier'>seed.py</font> &mdash; but the live Advisor <b>bypasses them</b>, "
            "fetching fresh data from yfinance and returning the verdict without persisting it. They were designed as "
            "a cache/reference layer (fast watchlist badges, fewer yfinance calls) and that loop was never closed. "
            "<font face='Courier'>stocks</font> <i>is</i> used live (names, sectors) by the dashboard and portfolio."))

st.append(P("11.2 Other known issues", "H2"))
st.append(bullet("<b>Schema drift risk</b> &mdash; the app uses <font face='Courier'>create_all</font> at startup, which creates missing tables but never alters existing ones. Three backtest columns were once present in the model but absent from the live database, producing a 500 on /marketplace until they were added. Standardising fully on Alembic is the fix."))
st.append(bullet("<b>Threshold realism</b> &mdash; the default 100-trade minimum is hard to reach on a single ticker over one year (typically 24&ndash;33 trades). Options: use a 5-year period, aggregate across multiple tickers, or lower the threshold (it is admin-configurable)."))
st.append(bullet("<b>Cold-start latency</b> &mdash; the first backtest after each server start spends ~20s compiling vectorbt/numba kernels."))
st.append(bullet("<b>Marketplace payments are simulated</b> &mdash; no real payment processor is integrated."))
st.append(bullet("<b>Free data source</b> &mdash; yfinance has no SLA and is rate-limited; a licensed feed would be required for production."))

# ───────────────── 12. RUNNING ─────────────────
st.append(P("12. Running the System", "H1"))
st.append(code(
"""PREREQUISITES: Git, Node.js (LTS), PostgreSQL 16, uv (Python package manager)

1. Clone and enter the repo
   git clone https://github.com/thestockpilot/stock_pilot.git && cd stock_pilot

2. Create the database
   psql -U postgres -c "CREATE DATABASE stockpilot;"

3. Backend  (cd backend)
   echo DATABASE_URL=postgresql+asyncpg://postgres:<password>@localhost:5432/stockpilot > .env
   uv sync                      # install dependencies
   uv run python seed.py        # create tables + demo data  (WARNING: drops existing data)
   uv run uvicorn app.main:app --reload --port 8000

4. Frontend (cd Frontend)
   npm install
   npm run dev                  # http://localhost:5173

DEMO ACCOUNTS
   demo@stockpilot.io    / demo1234      (investor, fully populated)
   admin@stockpilot.io   / admin1234     (admin)
   analyst1@stockpilot.io/ analyst1234   (analyst)

NOTES
   .env is git-ignored - create it per machine.
   Use `uv run alembic upgrade head` for schema updates instead of re-seeding
   (seed.py drops all data)."""))

st.append(P("13. Quick Reference", "H1"))
st.append(table(["Question", "Answer"], [
    ["Where is the verdict computed?", "backend/app/api/v1/endpoints/analysis.py &mdash; _compute_daily_composite() and the /factors route"],
    ["Where is the backtest?", "analysis.py &mdash; _run_vectorbt_backtest(), called via run_in_threadpool"],
    ["Where are the thresholds enforced?", "strategies.py &mdash; /strategies/{id}/publish, reading platform_settings"],
    ["Where is auth enforced?", "core/dependencies.py &mdash; get_current_user, require_role"],
    ["Where does the frontend attach the JWT?", "Frontend/src/api/client.js &mdash; axios request interceptor"],
    ["Where is the design system?", "Frontend/src/styles/global.css &mdash; single file, CSS custom properties"],
    ["How do I add an endpoint?", "Create the route in app/api/v1/endpoints/, then include its router in api/v1/router.py"],
    ["How do I add a table?", "Add the model under app/db/models/, export it in models/__init__.py, then create an Alembic revision"],
], [1.95*inch, CW - 1.95*inch]))

def footer(canvas, d):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GREY)
    canvas.drawCentredString(PAGE_W/2, 26,
        f"StockPilot - System Context Document  |  Group 13, CSE5015  |  Page {d.page}")
    canvas.restoreState()

doc.build(st, onFirstPage=footer, onLaterPages=footer)
print("Generated:", OUT)
