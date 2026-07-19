"""
Generate a comprehensive 100+ page PDF documenting the StockPilot backend system.

Organised into three main sections:
  1. Backend  — FastAPI, endpoints, authentication, schemas, configuration
  2. AI / ML  — XGBoost predictor, FinBERT sentiment, feature engineering, backtesting
  3. DB Management — SQLAlchemy models, session management, relationships, seeding

Run:  python generate_docs.py
Output: StockPilot_Backend_Documentation.pdf
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
    Preformatted,
)
from reportlab.platypus.xpreformatted import XPreformatted
from reportlab.lib import colors

# ── Colour palette ──────────────────────────────────────────────
GOLD = HexColor("#d4a853")
DARK_BG = HexColor("#18181b")
DARK_SURFACE = HexColor("#27272a")
MUTED = HexColor("#71717a")
CODE_BG = HexColor("#f5f5f0")
LIGHT_GOLD_BG = HexColor("#fdf8ed")
SECTION_BG = HexColor("#1a1a2e")
BLUE = HexColor("#1a5276")
DARK_TEXT = HexColor("#2d2d2d")
GRAY_TEXT = HexColor("#555555")
LIGHT_GRAY = HexColor("#f8f8f8")

W, H = A4

styles = getSampleStyleSheet()

# ── Custom paragraph styles ─────────────────────────────────────
styles.add(ParagraphStyle(
    "CoverTitle", parent=styles["Title"],
    fontSize=36, leading=44, textColor=GOLD, alignment=TA_CENTER,
    spaceAfter=10,
))
styles.add(ParagraphStyle(
    "CoverSub", parent=styles["Normal"],
    fontSize=14, leading=18, textColor=HexColor("#666666"), alignment=TA_CENTER,
    spaceAfter=6,
))
styles.add(ParagraphStyle(
    "PartTitle", parent=styles["Heading1"],
    fontSize=28, leading=36, textColor=GOLD, alignment=TA_CENTER,
    spaceBefore=40, spaceAfter=20,
))
styles.add(ParagraphStyle(
    "SectionHead", parent=styles["Heading1"],
    fontSize=20, leading=26, textColor=GOLD, spaceBefore=22, spaceAfter=10,
    borderWidth=1, borderColor=GOLD, borderPadding=6,
))
styles.add(ParagraphStyle(
    "SubSection", parent=styles["Heading2"],
    fontSize=15, leading=20, textColor=BLUE, spaceBefore=16, spaceAfter=6,
))
styles.add(ParagraphStyle(
    "FileHead", parent=styles["Heading2"],
    fontSize=14, leading=18, textColor=HexColor("#2c3e50"), spaceBefore=14, spaceAfter=6,
))
styles.add(ParagraphStyle(
    "FuncName", parent=styles["Heading3"],
    fontSize=12, leading=16, textColor=BLUE, spaceBefore=10, spaceAfter=4,
    leftIndent=12,
))
styles.add(ParagraphStyle(
    "Body", parent=styles["Normal"],
    fontSize=10, leading=14, textColor=HexColor("#333333"),
    spaceAfter=6, alignment=TA_JUSTIFY,
))
styles.add(ParagraphStyle(
    "BodyIndent", parent=styles["Normal"],
    fontSize=10, leading=14, textColor=HexColor("#333333"), leftIndent=12,
    spaceAfter=6, alignment=TA_JUSTIFY,
))
styles.add(ParagraphStyle(
    "CodeBlock", parent=styles["Normal"],
    fontSize=8, leading=11, fontName="Courier", textColor=DARK_TEXT,
    leftIndent=10, rightIndent=10, backColor=CODE_BG, borderPadding=6,
    spaceAfter=8, spaceBefore=4,
))
styles.add(ParagraphStyle(
    "Param", parent=styles["Normal"],
    fontSize=9, leading=12, textColor=GRAY_TEXT, leftIndent=24,
    spaceAfter=2,
))
styles.add(ParagraphStyle(
    "TOCSection", parent=styles["Normal"],
    fontSize=13, leading=18, textColor=GOLD, spaceBefore=8, spaceAfter=2,
    fontName="Helvetica-Bold",
))
styles.add(ParagraphStyle(
    "TOCEntry", parent=styles["Normal"],
    fontSize=11, leading=16, leftIndent=12, spaceAfter=2,
))
styles.add(ParagraphStyle(
    "WhyBox", parent=styles["Normal"],
    fontSize=10, leading=14, textColor=HexColor("#333333"),
    leftIndent=14, rightIndent=14, backColor=LIGHT_GOLD_BG, borderPadding=8,
    spaceAfter=10, spaceBefore=6,
    borderWidth=1, borderColor=GOLD,
))
styles.add(ParagraphStyle(
    "BulletItem", parent=styles["Normal"],
    fontSize=10, leading=14, textColor=HexColor("#333333"),
    leftIndent=24, bulletIndent=12, spaceAfter=3,
))


# ── Helper functions ────────────────────────────────────────────

def hr():
    return HRFlowable(width="100%", thickness=1, color=HexColor("#cccccc"), spaceAfter=8, spaceBefore=4)


def gold_hr():
    return HRFlowable(width="40%", thickness=2, color=GOLD, spaceAfter=12, spaceBefore=12)


def body(text):
    return Paragraph(text, styles["Body"])


def body_i(text):
    return Paragraph(text, styles["BodyIndent"])


def why_box(text):
    return Paragraph(text, styles["WhyBox"])


def bullet(text):
    return Paragraph(f"&bull; {text}", styles["BulletItem"])


def code_block(text):
    escaped = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return XPreformatted(escaped, styles["CodeBlock"])


def func_block(name, signature, description, params=None, returns=None):
    elems = []
    elems.append(Paragraph(
        f"<b>{name}</b>(<font face='Courier' size='9'>{signature}</font>)",
        styles["FuncName"],
    ))
    if description:
        elems.append(Paragraph(description, styles["BodyIndent"]))
    if params:
        for p_name, p_desc in params:
            elems.append(Paragraph(f"<b>{p_name}</b> — {p_desc}", styles["Param"]))
    if returns:
        elems.append(Paragraph(f"<b>Returns:</b> {returns}", styles["Param"]))
    elems.append(Spacer(1, 4))
    return KeepTogether(elems)


def read_source(rel_path: str, start: int | None = None, end: int | None = None) -> str:
    base = Path(__file__).resolve().parent
    fp = base / rel_path
    if not fp.exists():
        return f"# File not found: {rel_path}"
    lines = fp.read_text(encoding="utf-8", errors="replace").splitlines()
    if start is not None and end is not None:
        lines = lines[start - 1 : end]
    text = "\n".join(lines)
    return text


def source_block(rel_path: str, start: int | None = None, end: int | None = None, caption: str | None = None):
    elems = []
    if caption:
        elems.append(Paragraph(
            f"<b>{caption}</b>  "
            f"<font face='Courier' size='8' color='#888888'>{rel_path}"
            + (f" (lines {start}-{end})" if start else "")
            + "</font>",
            styles["BodyIndent"],
        ))
    src = read_source(rel_path, start, end)
    elems.append(code_block(src))
    return elems


# ══════════════════════════════════════════════════════════════════
# PDF BUILDER
# ══════════════════════════════════════════════════════════════════

def build_pdf():
    doc = SimpleDocTemplate(
        "StockPilot_Backend_Documentation.pdf",
        pagesize=A4,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
    )

    story = []

    # ══════════════════════════════════════════════════════════════
    # COVER PAGE
    # ══════════════════════════════════════════════════════════════
    story.append(Spacer(1, 2 * inch))
    story.append(Paragraph("STOCK PILOT", styles["CoverTitle"]))
    story.append(Paragraph("Backend System Documentation", styles["CoverSub"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(gold_hr())
    story.append(Paragraph("Complete Technical Reference", styles["CoverSub"]))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles["CoverSub"]))
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph("FastAPI  |  PostgreSQL  |  SQLAlchemy 2.0  |  XGBoost  |  FinBERT", styles["CoverSub"]))
    story.append(Paragraph("JWT Authentication  |  Async Architecture  |  Real-time Market Data", styles["CoverSub"]))
    story.append(Spacer(1, 1 * inch))
    story.append(Paragraph("Three Main Sections", styles["CoverSub"]))
    story.append(Spacer(1, 0.15 * inch))

    parts_table = Table(
        [
            ["PART 1", "Backend", "FastAPI, endpoints, auth, schemas, configuration"],
            ["PART 2", "AI / ML", "XGBoost, FinBERT, feature engineering, backtesting"],
            ["PART 3", "DB Management", "SQLAlchemy models, sessions, relationships, seeding"],
        ],
        colWidths=[1 * inch, 1.4 * inch, 3.6 * inch],
    )
    parts_table.setStyle(TableStyle([
        ("TEXTCOLOR", (0, 0), (0, -1), GOLD),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
    ]))
    story.append(parts_table)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Table of Contents", styles["SectionHead"]))
    story.append(Spacer(1, 8))

    toc = [
        ("PART 1 — BACKEND", [
            ("1.1", "Technology Stack and Rationale"),
            ("1.2", "Application Entry Point (main.py)"),
            ("1.3", "Core Configuration (config.py)"),
            ("1.4", "Security Module (security.py)"),
            ("1.5", "Authentication Dependencies (dependencies.py)"),
            ("1.6", "API Router Architecture (router.py)"),
            ("1.7", "Authentication Endpoints (auth.py)"),
            ("1.8", "User Management Endpoints (users.py)"),
            ("1.9", "Stock and Prediction Endpoints"),
            ("1.10", "Portfolio Endpoints (portfolio.py)"),
            ("1.11", "Watchlist and Trade Endpoints"),
            ("1.12", "Strategy and Marketplace Endpoints"),
            ("1.13", "Notification Endpoints"),
            ("1.14", "Dashboard Endpoints (dashboard.py)"),
            ("1.15", "Live Market Data Endpoints (live.py)"),
            ("1.16", "Analysis Endpoints (analysis.py)"),
            ("1.17", "Sentiment Endpoints (sentiment.py)"),
            ("1.18", "Pydantic Schemas — Complete Reference"),
        ]),
        ("PART 2 — AI / ML", [
            ("2.1", "Machine Learning Architecture Overview"),
            ("2.2", "Data Acquisition — DataFetcher"),
            ("2.3", "Feature Engineering — FeatureEngine"),
            ("2.4", "XGBoost Prediction Model — StockPredictor"),
            ("2.5", "FinBERT Sentiment Analysis"),
            ("2.6", "Six-Factor Composite Scoring System"),
            ("2.7", "Backtest Simulation Engine"),
            ("2.8", "How XGBoost Training Works Step by Step"),
            ("2.9", "How FinBERT Inference Works Step by Step"),
        ]),
        ("PART 3 — DB MANAGEMENT", [
            ("3.1", "Database Architecture Overview"),
            ("3.2", "SQLAlchemy Base and Naming Conventions"),
            ("3.3", "Async Engine and Session Management"),
            ("3.4", "User Model and Role System"),
            ("3.5", "Stock and Price History Models"),
            ("3.6", "Prediction Model"),
            ("3.7", "Portfolio (Holding) Model"),
            ("3.8", "Watchlist Model"),
            ("3.9", "Trade Journal Model"),
            ("3.10", "Strategy Model with JSONB Weights"),
            ("3.11", "Marketplace and Rating Models"),
            ("3.12", "Notification Model"),
            ("3.13", "Entity Relationship Diagram"),
            ("3.14", "Database Seeder (seed.py)"),
            ("3.15", "Default Strategy Configurations (Research-Backed)"),
        ]),
        ("APPENDICES", [
            ("A", "Python Dependencies"),
            ("B", "Complete API Endpoint Reference"),
            ("C", "Technical Indicators Reference"),
            ("D", "Authentication and Request Flow"),
            ("E", "XGBoost Model Architecture Details"),
            ("F", "FinBERT Architecture Details"),
            ("G", "Database Operations Guide"),
            ("H", "Error Handling Patterns"),
            ("I", "CORS and Security Configuration"),
            ("J", "Backtesting Metrics Explained"),
            ("K", "System Data Flow Diagrams"),
            ("L", "Schema Field Reference Tables"),
            ("M", "Project Setup and Running Guide"),
            ("N", "Glossary of Technical Terms"),
            ("O", "Live Market Data Implementation"),
            ("P", "Analysis Endpoint Implementation"),
            ("Q", "Complete Database Column Reference"),
            ("R", "Async Patterns and Concurrency"),
            ("S", "Testing and Debugging Guide"),
            ("T", "Design Decisions and Trade-offs"),
            ("U", "Production Deployment Checklist"),
            ("V", "Frontend-Backend Integration"),
            ("W", "Walk-Forward Validation Deep Dive"),
            ("X", "Request/Response Examples"),
            ("Y", "Complete Feature Column Reference"),
        ]),
    ]

    for part_title, entries in toc:
        story.append(Paragraph(part_title, styles["TOCSection"]))
        for num, title in entries:
            story.append(Paragraph(f"  <b>{num}</b>  {title}", styles["TOCEntry"]))
    story.append(PageBreak())

    # ╔════════════════════════════════════════════════════════════╗
    # ║                    PART 1 — BACKEND                       ║
    # ╚════════════════════════════════════════════════════════════╝

    story.append(Spacer(1, 1.5 * inch))
    story.append(Paragraph("PART 1", styles["CoverTitle"]))
    story.append(Paragraph("Backend", styles["PartTitle"]))
    story.append(gold_hr())
    story.append(Paragraph(
        "FastAPI application architecture, API endpoints, authentication system, "
        "request/response schemas, and configuration management.",
        styles["CoverSub"],
    ))
    story.append(PageBreak())

    # ── 1.1 Technology Stack ────────────────────────────────────
    story.append(Paragraph("1.1  Technology Stack and Rationale", styles["SectionHead"]))
    story.append(body(
        "This section explains <b>why</b> each core technology was chosen, the problems it solves, "
        "and how all pieces fit together into a cohesive system."
    ))
    story.append(hr())

    # FastAPI
    story.append(Paragraph("FastAPI — Web Framework", styles["SubSection"]))
    story.append(why_box(
        "<b>Why not Flask or Django?</b> StockPilot fetches live stock prices from Yahoo Finance on almost every "
        "request. These external HTTP calls take 200-800 ms each. In a synchronous framework like Flask, the server "
        "thread blocks while waiting for Yahoo's response — meaning it cannot serve any other user during that time. "
        "FastAPI is built on Python's <font face='Courier'>async/await</font> (via Starlette and uvicorn), so while "
        "one request waits for Yahoo Finance data, the server can handle dozens of other requests concurrently on "
        "the same thread."
    ))
    story.append(body(
        "<b>Additional benefits:</b> FastAPI auto-generates OpenAPI/Swagger documentation at "
        "<font face='Courier'>/docs</font>, making it easy for the frontend team to explore and test endpoints. "
        "Its dependency injection system (used for <font face='Courier'>get_db</font> and "
        "<font face='Courier'>get_current_user</font>) cleanly separates authentication and database concerns "
        "from business logic. Pydantic integration means request/response validation happens automatically — "
        "invalid data never reaches the endpoint function."
    ))
    story.append(Spacer(1, 8))

    # PostgreSQL
    story.append(Paragraph("PostgreSQL — Database", styles["SubSection"]))
    story.append(why_box(
        "<b>Why not SQLite or MySQL?</b> PostgreSQL was chosen for three specific reasons: "
        "(1) <b>JSONB columns</b> — strategy weights are stored as flexible JSON objects "
        "(<font face='Courier'>{\"momentum\": 30, \"value\": 25, ...}</font>) that can vary per strategy. "
        "PostgreSQL's native JSONB type stores and indexes these efficiently. "
        "(2) <b>UUID primary keys</b> — every model uses UUIDs instead of auto-incrementing integers, "
        "preventing ID enumeration attacks and enabling client-side ID generation. "
        "(3) <b>Concurrent connections</b> — PostgreSQL handles many simultaneous connections gracefully "
        "via connection pooling, critical for the async server."
    ))
    story.append(Spacer(1, 8))

    # asyncpg
    story.append(Paragraph("asyncpg — Database Driver", styles["SubSection"]))
    story.append(why_box(
        "<b>Why not psycopg2?</b> Since FastAPI is async, the database driver must also be async — otherwise "
        "every SQL query would block the event loop and negate FastAPI's concurrency advantages. "
        "<font face='Courier'>asyncpg</font> is a pure-async PostgreSQL driver written in Cython, making it "
        "the fastest Python PostgreSQL driver available (3-5x faster than psycopg2 in benchmarks). It integrates "
        "with SQLAlchemy's async engine via <font face='Courier'>postgresql+asyncpg://</font>."
    ))
    story.append(Spacer(1, 8))

    # SQLAlchemy
    story.append(Paragraph("SQLAlchemy 2.0 — ORM", styles["SubSection"]))
    story.append(body(
        "StockPilot has 9 interrelated database models with foreign keys, relationships, and complex queries. "
        "SQLAlchemy provides: (1) DeclarativeBase models — Python classes that map to tables, (2) Relationship "
        "loading — <font face='Courier'>selectinload</font> fetches related records in optimised queries, "
        "(3) Async session management with automatic commit/rollback, (4) Auto-migration via "
        "<font face='Courier'>Base.metadata.create_all</font>."
    ))
    story.append(why_box(
        "<b>Why version 2.0?</b> SQLAlchemy 2.0 introduced native async support "
        "(<font face='Courier'>AsyncSession</font>, <font face='Courier'>create_async_engine</font>) and the new "
        "<font face='Courier'>DeclarativeBase</font> class with better type hints. Earlier versions required "
        "third-party wrappers for async."
    ))
    story.append(Spacer(1, 8))

    # JWT
    story.append(Paragraph("JWT — Authentication", styles["SubSection"]))
    story.append(body(
        "StockPilot's frontend is a React SPA on port 5173 communicating with the API on port 8000 — a "
        "cross-origin setup. JWT tokens are sent via the <font face='Courier'>Authorization: Bearer</font> header, "
        "which works seamlessly across origins. The system uses HS256 (symmetric HMAC-SHA256) — appropriate for "
        "a single-server application."
    ))
    story.append(why_box(
        "<b>Why two tokens (access + refresh)?</b> Access tokens expire in 120 minutes for security — if one "
        "is stolen, the window of exploitation is limited. Refresh tokens last 7 days and are used to silently "
        "obtain new access tokens without forcing the user to re-login."
    ))
    story.append(Spacer(1, 8))

    # bcrypt
    story.append(Paragraph("bcrypt — Password Hashing", styles["SubSection"]))
    story.append(why_box(
        "<b>Why bcrypt instead of SHA-256 or MD5?</b> General-purpose hash functions are designed to be fast — "
        "an attacker with a GPU can try billions of SHA-256 hashes per second. bcrypt is intentionally slow "
        "(cost factor makes each hash take ~100 ms) and includes automatic salting. This makes brute-force and "
        "rainbow table attacks impractical. bcrypt is the industry standard recommended by OWASP."
    ))
    story.append(Spacer(1, 8))

    # Pydantic
    story.append(Paragraph("Pydantic v2 — Data Validation", styles["SubSection"]))
    story.append(body(
        "Every API endpoint validates incoming data and serialises outgoing data. Pydantic handles both: "
        "(1) Request validation — <font face='Courier'>HoldingCreate(ticker, quantity=Field(gt=0))</font> "
        "rejects invalid data with a clear 422 error. "
        "(2) Response serialisation — <font face='Courier'>ConfigDict(from_attributes=True)</font> reads from "
        "ORM objects directly. "
        "(3) v2 is rewritten in Rust (via pydantic-core), 5-50x faster than v1."
    ))
    story.append(Spacer(1, 8))

    # yfinance
    story.append(Paragraph("yfinance — Market Data", styles["SubSection"]))
    story.append(body(
        "Professional market data APIs cost $100-$2000+/month. yfinance provides free access to Yahoo Finance "
        "data including real-time quotes, historical OHLCV, fundamentals, and intraday data. The trade-off is "
        "rate limiting, handled with retry logic and safe type conversion."
    ))
    story.append(why_box(
        "<b>The async bridge pattern:</b> yfinance is synchronous. To avoid blocking the event loop, the codebase "
        "uses <font face='Courier'>ThreadPoolExecutor</font> + <font face='Courier'>asyncio.run_in_executor()</font>. "
        "Multiple tickers are fetched in parallel via <font face='Courier'>asyncio.gather()</font>."
    ))
    story.append(Spacer(1, 8))

    # Architecture patterns
    story.append(Paragraph("Architecture Patterns", styles["SubSection"]))
    story.append(body(
        "<b>UUID primary keys:</b> Security (unguessable IDs), distributed creation (frontend can pre-generate), "
        "merge safety (no collisions)."
    ))
    story.append(body(
        "<b>/api/v1 prefix:</b> API versioning allows breaking changes in v2 without disrupting existing clients."
    ))
    story.append(body(
        "<b>Dependency injection (get_db, get_current_user):</b> Auth logic written once, database lifecycle "
        "handled in one place, endpoints easy to test with mock dependencies."
    ))
    story.append(body(
        "<b>Async session commit-after-yield:</b> If any part of an endpoint fails, no partial data is committed. "
        "This is the unit-of-work pattern providing transactional safety."
    ))
    story.append(PageBreak())

    # ── 1.2 Application Entry Point ─────────────────────────────
    story.append(Paragraph("1.2  Application Entry Point", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/main.py</font>", styles["Body"]))
    story.append(hr())
    story.append(body(
        "The central FastAPI application file. It creates the app instance, configures CORS, mounts the router "
        "and static files, and defines the lifespan that initialises the database on startup."
    ))
    story.append(code_block(textwrap.dedent("""\
        UPLOADS_DIR = Path(__file__).resolve().parent.parent / "uploads"
        UPLOADS_DIR.mkdir(exist_ok=True)
    """)))
    story.append(body(
        "<font face='Courier'>UPLOADS_DIR</font> is created at import time if it does not exist. This directory "
        "stores user avatar images uploaded via the <font face='Courier'>/api/v1/users/me/avatar</font> endpoint."
    ))
    story.append(Paragraph("<b>Lifespan context manager</b>", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            yield
    """)))
    story.append(body(
        "The <font face='Courier'>lifespan</font> async context manager runs during app startup/shutdown. On startup, "
        "it creates all SQLAlchemy tables via <font face='Courier'>Base.metadata.create_all</font>. This ensures "
        "the database schema is up to date every time the server starts — no separate migration step needed."
    ))
    story.append(Paragraph("<b>App initialisation, CORS, and static files</b>", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        app = FastAPI(title="StockPilot API", lifespan=lifespan)

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        app.include_router(api_router, prefix="/api/v1")
        app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
    """)))
    story.append(body(
        "<b>CORS middleware:</b> Allows all origins (<font face='Courier'>allow_origins=['*']</font>) because "
        "the React frontend runs on a different port (5173) than the API (8000). In production this should be "
        "restricted to the actual frontend domain."
    ))
    story.append(body(
        "<b>Static file mount:</b> <font face='Courier'>/uploads</font> serves user-uploaded files (avatars) "
        "directly from the filesystem."
    ))
    story.append(Paragraph("<b>Health check endpoint</b>", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        @app.get("/health")
        async def health(db: AsyncSession = Depends(get_db)):
            try:
                await db.execute(text("SELECT 1"))
                return {"status": "healthy", "database": "connected"}
            except Exception as e:
                return {"status": "unhealthy", "database": str(e)}
    """)))
    story.append(body(
        "The health check endpoint executes <font face='Courier'>SELECT 1</font> against PostgreSQL to verify "
        "database connectivity. It returns <font face='Courier'>healthy/connected</font> on success or the error "
        "message on failure — useful for container orchestration health probes."
    ))
    story.append(PageBreak())

    # ── 1.3 Configuration ───────────────────────────────────────
    story.append(Paragraph("1.3  Core Configuration", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/core/config.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        class Settings(BaseSettings):
            DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/stockpilot"
            SECRET_KEY: str = "change-me-in-production"
            ALGORITHM: str = "HS256"
            ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
            REFRESH_TOKEN_EXPIRE_DAYS: int = 7

            model_config = SettingsConfigDict(env_file=".env")

        settings = Settings()
    """)))
    story.append(body(
        "Pydantic Settings class that loads configuration from environment variables or a "
        "<font face='Courier'>.env</font> file. Key fields:"
    ))
    story.append(bullet("<b>DATABASE_URL</b> — PostgreSQL connection string using asyncpg driver"))
    story.append(bullet("<b>SECRET_KEY</b> — JWT signing key (must be changed in production)"))
    story.append(bullet("<b>ALGORITHM</b> — JWT algorithm (HS256)"))
    story.append(bullet("<b>ACCESS_TOKEN_EXPIRE_MINUTES</b> — Access token TTL (120 minutes)"))
    story.append(bullet("<b>REFRESH_TOKEN_EXPIRE_DAYS</b> — Refresh token TTL (7 days)"))
    story.append(why_box(
        "<b>Why Pydantic Settings?</b> It validates environment variables at startup — a typo in "
        "<font face='Courier'>DATABASE_URL</font> is caught immediately rather than causing a cryptic error "
        "minutes later when the first database query runs."
    ))
    story.append(PageBreak())

    # ── 1.4 Security Module ─────────────────────────────────────
    story.append(Paragraph("1.4  Security Module", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/core/security.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        def hash_password(password: str) -> str:
            return pwd_context.hash(password)

        def verify_password(plain: str, hashed: str) -> bool:
            return pwd_context.verify(plain, hashed)

        def create_access_token(data: dict) -> str:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            return jwt.encode({**data, "exp": expire, "type": "access"}, settings.SECRET_KEY)
    """)))
    story.append(Spacer(1, 8))
    story.append(body("<b>Function-by-function explanation:</b>"))
    story.append(func_block(
        "hash_password", "password: str",
        "Hashes a plain-text password using bcrypt with automatic salt generation. The bcrypt context "
        "uses the default cost factor (12 rounds = 2<super>12</super> = 4,096 iterations), making each hash "
        "take ~100ms. Returns the full bcrypt hash string including salt and cost factor.",
        returns="str — bcrypt hash",
    ))
    story.append(func_block(
        "verify_password", "plain: str, hashed: str",
        "Compares a plain-text password against a stored bcrypt hash. Internally, bcrypt extracts the salt "
        "from the stored hash, re-hashes the plain-text input with that salt, and compares the results. "
        "This is constant-time comparison to prevent timing attacks.",
        returns="bool",
    ))
    story.append(func_block(
        "create_access_token", "data: dict",
        "Creates a short-lived JWT. Encodes the data dict with an <font face='Courier'>exp</font> timestamp "
        "(current time + 120 minutes) and a <font face='Courier'>type: access</font> field. Uses HS256 with the "
        "SECRET_KEY from settings.",
        returns="str — encoded JWT",
    ))
    story.append(func_block(
        "create_refresh_token", "data: dict",
        "Creates a long-lived JWT with <font face='Courier'>type: refresh</font> and 7-day expiry. "
        "Used only for obtaining new access tokens, never for API authentication.",
        returns="str — encoded JWT",
    ))
    story.append(func_block(
        "decode_token", "token: str",
        "Decodes and validates a JWT. Returns the payload dict on success, None if expired or invalid.",
        returns="dict | None",
    ))
    story.append(PageBreak())

    # ── 1.5 Auth Dependencies ───────────────────────────────────
    story.append(Paragraph("1.5  Authentication Dependencies", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/core/dependencies.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        async def get_current_user(
            token: str = Depends(oauth2_scheme),
            db: AsyncSession = Depends(get_db),
        ) -> User:
            payload = decode_token(token)
            if payload is None or payload.get("type") != "access":
                raise HTTPException(401, "Invalid or expired token")
            user_id = payload.get("sub")
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(401, "User not found")
            return user
    """)))
    story.append(Spacer(1, 8))
    story.append(body(
        "This is the cornerstone of authentication in StockPilot. "
        "<font face='Courier'>get_current_user</font> is a FastAPI dependency that:"
    ))
    story.append(bullet("Extracts the JWT from the <font face='Courier'>Authorization: Bearer &lt;token&gt;</font> header"))
    story.append(bullet("Decodes and validates the token using <font face='Courier'>decode_token()</font>"))
    story.append(bullet("Extracts the user ID from the <font face='Courier'>sub</font> claim"))
    story.append(bullet("Looks up the User record in PostgreSQL by UUID"))
    story.append(bullet("Returns the User ORM instance or raises HTTP 401"))
    story.append(Spacer(1, 4))
    story.append(why_box(
        "<b>Why dependency injection?</b> Any endpoint that needs authentication simply adds "
        "<font face='Courier'>user: User = Depends(get_current_user)</font> to its parameters. FastAPI "
        "calls the dependency automatically before the endpoint function runs. The auth logic is written "
        "once, tested once, and reused across all 40+ protected endpoints."
    ))
    story.append(PageBreak())

    # ── 1.6 API Router ──────────────────────────────────────────
    story.append(Paragraph("1.6  API Router Architecture", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/api/v1/router.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        api_router = APIRouter()
        api_router.include_router(auth.router,    prefix="/auth",    tags=["Authentication"])
        api_router.include_router(users.router,   prefix="/users",   tags=["Users"])
        api_router.include_router(stocks.router,  prefix="/stocks",  tags=["Stocks"])
        api_router.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])
        # ... 10 more routers for watchlist, trades, strategies, etc.
    """)))
    story.append(Spacer(1, 8))
    story.append(body(
        "Aggregates all 14 endpoint routers under the <font face='Courier'>/api/v1</font> prefix. "
        "Each sub-router adds its own prefix (e.g. <font face='Courier'>/auth</font>, "
        "<font face='Courier'>/portfolio</font>)."
    ))

    routes_data = [
        ["/api/v1/auth", "Authentication", "Login, register, refresh"],
        ["/api/v1/users", "Users", "Profile, password, avatar"],
        ["/api/v1/stocks", "Stocks", "Stock listing, price history"],
        ["/api/v1/predictions", "Predictions", "AI predictions"],
        ["/api/v1/portfolio", "Portfolio", "Holdings CRUD"],
        ["/api/v1/watchlist", "Watchlist", "Watch/unwatch tickers"],
        ["/api/v1/trades", "Trades", "Trade journal"],
        ["/api/v1/strategies", "Strategies", "Strategy CRUD"],
        ["/api/v1/notifications", "Notifications", "Notification management"],
        ["/api/v1/marketplace", "Marketplace", "Strategy marketplace"],
        ["/api/v1/live", "Live Data", "Real-time quotes"],
        ["/api/v1/analysis", "Analysis", "Factor analysis, backtest"],
        ["/api/v1/dashboard", "Dashboard", "Overview data"],
        ["/api/v1/sentiment", "Sentiment", "FinBERT news analysis"],
    ]
    t = Table(
        [["Route Prefix", "Tag", "Description"]] + routes_data,
        colWidths=[2.2 * inch, 1.3 * inch, 2.5 * inch],
    )
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 1), (0, -1), "Courier"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(PageBreak())

    # ── 1.7 Auth Endpoints ──────────────────────────────────────
    story.append(Paragraph("1.7  Authentication Endpoints", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/api/v1/endpoints/auth.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        @router.post("/login")
        async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User).where(User.email == body.email))
            user = result.scalar_one_or_none()
            if not user or not verify_password(body.password, user.password_hash):
                raise HTTPException(401, "Invalid email or password")
            return {
                "access_token": create_access_token({"sub": str(user.id)}),
                "refresh_token": create_refresh_token({"sub": str(user.id)}),
                "token_type": "bearer",
            }
    """)))
    story.append(Spacer(1, 8))
    story.append(func_block(
        "login", "body: LoginRequest, db: AsyncSession",
        "POST <font face='Courier'>/api/v1/auth/login</font> — Looks up user by email, verifies bcrypt hash, "
        "returns access + refresh tokens. The JWT <font face='Courier'>sub</font> claim contains the user UUID.",
        returns="TokenResponse",
    ))
    story.append(func_block(
        "register", "body: RegisterRequest, db: AsyncSession",
        "POST <font face='Courier'>/api/v1/auth/register</font> — Checks for duplicate email, hashes password, "
        "creates User record, returns tokens for auto-login.",
        returns="TokenResponse",
    ))
    story.append(func_block(
        "refresh_token", "body: RefreshRequest, db: AsyncSession",
        "POST <font face='Courier'>/api/v1/auth/refresh</font> — Validates the refresh token type, looks up user, "
        "issues new token pair. This allows the frontend to silently renew access tokens.",
        returns="TokenResponse",
    ))
    story.append(PageBreak())

    # ── 1.8 User Endpoints ──────────────────────────────────────
    story.append(Paragraph("1.8  User Management Endpoints", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/api/v1/endpoints/users.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        @router.get("/me", response_model=UserOut)
        async def get_me(user: User = Depends(get_current_user)):
            return user

        @router.post("/me/avatar", response_model=UserOut)
        async def upload_avatar(file: UploadFile, user = Depends(get_current_user), db = Depends(get_db)):
            if file.content_type not in ALLOWED_TYPES:
                raise HTTPException(400, "Only JPEG, PNG, WEBP images allowed")
            data = await file.read()
            if len(data) > MAX_SIZE:
                raise HTTPException(400, "File exceeds 2 MB limit")
            ext = file.content_type.split("/")[-1]
            path = UPLOADS_DIR / f"{user.id}.{ext}"
            path.write_bytes(data)
            user.avatar_url = f"/uploads/{path.name}"
            return user
    """)))
    story.append(Spacer(1, 8))
    story.append(body(
        "Manages user profiles, password changes, and avatar uploads. Constants: "
        "<font face='Courier'>ALLOWED_TYPES</font> (jpeg, png, webp), "
        "<font face='Courier'>MAX_SIZE</font> (2 MB)."
    ))
    story.append(func_block("get_me", "user: User",
        "GET <font face='Courier'>/api/v1/users/me</font> — Returns the authenticated user's profile."))
    story.append(func_block("update_me", "body: UserUpdate, user: User, db",
        "PUT <font face='Courier'>/api/v1/users/me</font> — Updates profile fields. Only non-None fields are applied."))
    story.append(func_block("update_password", "body: PasswordUpdate, user: User, db",
        "PUT <font face='Courier'>/api/v1/users/me/password</font> — Verifies current password, enforces min 8 chars."))
    story.append(func_block("upload_avatar", "file: UploadFile, user: User, db",
        "POST <font face='Courier'>/api/v1/users/me/avatar</font> — Validates content type and size, saves as "
        "<font face='Courier'>{user_id}.{ext}</font>, updates <font face='Courier'>avatar_url</font>."))
    story.append(func_block("remove_avatar", "user: User, db",
        "DELETE <font face='Courier'>/api/v1/users/me/avatar</font> — Deletes file, sets avatar_url to None."))
    story.append(PageBreak())

    # ── 1.9 Stock & Prediction ──────────────────────────────────
    story.append(Paragraph("1.9  Stock and Prediction Endpoints", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/api/v1/endpoints/stocks.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        @router.get("/", response_model=list[StockOut])
        async def list_stocks(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Stock).order_by(Stock.ticker))
            return result.scalars().all()

        @router.get("/{ticker}", response_model=StockOut)
        async def get_stock(ticker: str, db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Stock).where(Stock.ticker == ticker.upper()))
            stock = result.scalar_one_or_none()
            if not stock:
                raise HTTPException(404, "Stock not found")
            return stock
    """)))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/api/v1/endpoints/predictions.py</font>", styles["Body"]))
    story.append(hr())
    story.append(func_block("list_predictions", "db", "GET <font face='Courier'>/api/v1/predictions</font> — All predictions ordered by created_at desc."))
    story.append(func_block("get_prediction", "ticker: str, db", "GET <font face='Courier'>/api/v1/predictions/{ticker}</font> — Latest prediction for a ticker."))
    story.append(PageBreak())

    # ── 1.10 Portfolio ──────────────────────────────────────────
    story.append(Paragraph("1.10  Portfolio Endpoints", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/api/v1/endpoints/portfolio.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        _executor = ThreadPoolExecutor(max_workers=4)

        def _fetch_price(ticker: str) -> tuple[str, float | None]:
            try:
                info = yf.Ticker(ticker).fast_info
                price = getattr(info, "last_price", None) or getattr(info, "previous_close", None)
                return ticker, float(price) if price else None
            except Exception:
                return ticker, None

        async def _fetch_live_prices(tickers: list[str]) -> dict[str, float | None]:
            loop = asyncio.get_event_loop()
            tasks = [loop.run_in_executor(_executor, _fetch_price, t) for t in tickers]
            results = await asyncio.gather(*tasks)
            return dict(results)
    """)))
    story.append(Spacer(1, 8))
    story.append(body(
        "Manages user holdings with <b>live price fetching</b> via yfinance. Uses a "
        "<font face='Courier'>ThreadPoolExecutor</font> (4 workers) to parallelise Yahoo Finance API calls."
    ))
    story.append(func_block("_fetch_price", "ticker: str",
        "Synchronous helper: fetches latest price from <font face='Courier'>yf.Ticker.fast_info</font>. "
        "Falls back to <font face='Courier'>previous_close</font> if <font face='Courier'>last_price</font> unavailable."))
    story.append(func_block("_fetch_live_prices", "tickers: list[str]",
        "Async wrapper: runs _fetch_price in parallel via <font face='Courier'>run_in_executor()</font> + "
        "<font face='Courier'>asyncio.gather()</font>.",
        returns="dict[str, float]"))
    story.append(func_block("list_holdings", "db, user",
        "GET <font face='Courier'>/api/v1/portfolio</font> — Lists active holdings with live prices."))
    story.append(func_block("add_holding", "body: HoldingCreate, db, user",
        "POST <font face='Courier'>/api/v1/portfolio</font> — Creates holding, fetches live price at creation."))
    story.append(func_block("update_holding", "holding_id: UUID, body, db, user",
        "PUT <font face='Courier'>/api/v1/portfolio/{id}</font> — Updates quantity/avg_cost. Scoped to owner."))
    story.append(func_block("delete_holding", "holding_id: UUID, db, user",
        "DELETE <font face='Courier'>/api/v1/portfolio/{id}</font> — Removes holding. Returns 204."))
    story.append(PageBreak())

    # ── 1.11 Watchlist & Trades ─────────────────────────────────
    story.append(Paragraph("1.11  Watchlist and Trade Endpoints", styles["SectionHead"]))

    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/api/v1/endpoints/watchlist.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        @router.post("/", response_model=WatchlistOut, status_code=201)
        async def add_to_watchlist(body: WatchlistAdd, db = Depends(get_db), user = Depends(get_current_user)):
            item = Watchlist(user_id=user.id, ticker=body.ticker.upper())
            db.add(item)
            return item  # DB unique constraint prevents duplicates
    """)))
    story.append(Spacer(1, 8))
    story.append(func_block("list_watchlist", "db, user", "GET — Returns all watchlist items ordered by added_at desc."))
    story.append(func_block("add_to_watchlist", "body: WatchlistAdd, db, user", "POST — Adds ticker. DB unique constraint prevents duplicates."))
    story.append(func_block("remove_from_watchlist", "ticker: str, db, user", "DELETE — Removes ticker from watchlist."))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/api/v1/endpoints/trades.py</font>", styles["Body"]))
    story.append(hr())
    story.append(func_block("list_trades", "db, user", "GET — All trades ordered by opened_at desc."))
    story.append(func_block("create_trade", "body: TradeCreate, db, user", "POST — Records new trade. Converts ticker to uppercase."))
    story.append(func_block("delete_trade", "trade_id: UUID, db, user", "DELETE — Removes trade from journal."))
    story.append(PageBreak())

    # ── 1.12 Strategy & Marketplace ─────────────────────────────
    story.append(Paragraph("1.12  Strategy and Marketplace Endpoints", styles["SectionHead"]))

    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/api/v1/endpoints/strategies.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        @router.post("/", response_model=StrategyOut, status_code=201)
        async def create_strategy(body: StrategyCreate, db = Depends(get_db), user = Depends(get_current_user)):
            strategy = Strategy(owner_id=user.id, name=body.name,
                                description=body.description, weights=body.weights)
            db.add(strategy)
            return strategy
    """)))
    story.append(Spacer(1, 8))
    story.append(func_block("list_strategies", "db, user", "GET — User's strategies plus system presets."))
    story.append(func_block("create_strategy", "body, db, user", "POST — Creates strategy with JSONB weights."))
    story.append(func_block("update_strategy", "id, body, db, user", "PUT — Updates non-None fields. Owner-scoped."))
    story.append(func_block("delete_strategy", "id, db, user", "DELETE — Returns 204."))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/api/v1/endpoints/marketplace.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        @router.get("/", response_model=list[MarketplaceListingOut])
        async def list_marketplace(db: AsyncSession = Depends(get_db)):
            result = await db.execute(
                select(MarketplaceListing)
                .options(selectinload(MarketplaceListing.strategy)
                         .selectinload(Strategy.owner))
                .order_by(MarketplaceListing.created_at.desc())
            )
            return result.scalars().all()
    """)))
    story.append(Spacer(1, 8))
    story.append(func_block("list_marketplace", "db",
        "GET — Lists marketplace listings. Uses <font face='Courier'>selectinload</font> to eagerly load "
        "strategy + owner in a single query, avoiding N+1 queries."))
    story.append(PageBreak())

    # ── 1.13 Notifications ──────────────────────────────────────
    story.append(Paragraph("1.13  Notification Endpoints", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/api/v1/endpoints/notifications.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        @router.put("/read-all")
        async def mark_all_read(db = Depends(get_db), user = Depends(get_current_user)):
            await db.execute(
                update(Notification)
                .where(Notification.user_id == user.id, Notification.is_read == False)
                .values(is_read=True)
            )
            return {"message": "All notifications marked as read"}
    """)))
    story.append(Spacer(1, 8))
    story.append(func_block("list_notifications", "db, user", "GET — All notifications ordered by created_at desc."))
    story.append(func_block("mark_read", "notification_id, db, user", "PUT /{id}/read — Marks single notification as read."))
    story.append(func_block("mark_all_read", "db, user", "PUT /read-all — Bulk update all unread to read."))
    story.append(PageBreak())

    # ── 1.14 Dashboard ──────────────────────────────────────────
    story.append(Paragraph("1.14  Dashboard Endpoints", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/api/v1/endpoints/dashboard.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        @router.get("/indices")
        async def get_market_indices():
            indices = {"^GSPC": "S&P 500", "^IXIC": "NASDAQ", "^DJI": "Dow Jones", "^VIX": "VIX"}
            loop = asyncio.get_event_loop()
            tasks = [loop.run_in_executor(_executor, _fetch_index, sym, name)
                     for sym, name in indices.items()]
            results = await asyncio.gather(*tasks)
            return [r for r in results if r]
    """)))
    story.append(Spacer(1, 8))
    story.append(func_block("get_market_indices", "",
        "GET /indices — Fetches S&amp;P 500, NASDAQ, Dow Jones, VIX via parallel yfinance calls."))
    story.append(func_block("get_sector_breakdown", "db, user",
        "GET /sectors — Portfolio allocation by sector. Joins holdings with Stock table."))
    story.append(func_block("get_portfolio_history", "db, user",
        "GET /history — 30-day portfolio value history using yfinance 1-month data per holding."))
    story.append(PageBreak())

    # ── 1.15 Live Market Data ───────────────────────────────────
    story.append(Paragraph("1.15  Live Market Data Endpoints", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/api/v1/endpoints/live.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        @router.get("/quote/{ticker}", response_model=QuoteResponse)
        async def get_live_quote(ticker: str):
            t = yf.Ticker(ticker)
            info = t.info
            fi = t.fast_info
            return QuoteResponse(
                ticker=ticker.upper(),
                price=_safe_float(getattr(fi, "last_price", None)),
                change=_safe_float(info.get("regularMarketChange")),
                change_percent=_safe_float(info.get("regularMarketChangePercent")),
                volume=_safe_int(info.get("regularMarketVolume")),
                market_cap=_safe_int(info.get("marketCap")),
                pe_ratio=_safe_float(info.get("trailingPE")),
                week_52_high=_safe_float(getattr(fi, "fifty_two_week_high", None)),
                week_52_low=_safe_float(getattr(fi, "fifty_two_week_low", None)),
            )
    """)))
    story.append(Spacer(1, 8))
    story.append(body(
        "Real-time market data using yfinance. Defines inline Pydantic models: "
        "<font face='Courier'>QuoteResponse</font>, <font face='Courier'>IntradayPoint</font>, "
        "<font face='Courier'>SessionStatus</font>, <font face='Courier'>MarketStatusResponse</font>."
    ))
    story.append(func_block("get_market_status", "",
        "GET /market-status — Open/closed state of US (NYSE), Europe (LSE), Asia (TSE) sessions."))
    story.append(func_block("get_live_quote", "ticker: str",
        "GET /quote/{ticker} — Full quote: price, change, OHLC, volume, market cap, P/E, 52-week range."))
    story.append(func_block("get_intraday", "ticker: str, interval: str",
        "GET /intraday/{ticker} — Intraday OHLCV at specified interval (1m/5m/15m/30m/60m/90m)."))
    story.append(func_block("get_chart_data", "ticker: str, period: str, interval: str",
        "GET /chart/{ticker} — Historical data. For '4h' interval, aggregates from 1h data via pandas resample."))
    story.append(PageBreak())

    # ── 1.16 Analysis ───────────────────────────────────────────
    story.append(Paragraph("1.16  Analysis Endpoints", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/api/v1/endpoints/analysis.py</font>", styles["Body"]))
    story.append(hr())
    story.append(body(
        "The most computationally intensive endpoint file. Provides AI-driven stock analysis using "
        "6-factor scoring, backtesting, bull/bear cases, and fundamental data."
    ))
    story.append(code_block(textwrap.dedent("""\
        @router.get("/factors/{ticker}")
        async def get_factor_analysis(
            ticker: str,
            sentiment: int = 14, momentum: int = 22, valuation: int = 20,
            volatility: int = 18, volume: int = 10, growth: int = 16,
        ):
            weights = {"sentiment": sentiment, "momentum": momentum,
                       "valuation": valuation, "volatility": volatility,
                       "volume": volume, "growth": growth}
            # Fetch data, compute 6 factor scores, apply weights, generate signal
            composite = sum(scores[f] * weights[f] for f in weights) / sum(weights.values())
            signal = "BUY" if composite >= 62 else "SELL" if composite <= 38 else "HOLD"
            ...
    """)))
    story.append(Spacer(1, 8))
    story.append(func_block("get_factor_analysis", "ticker, weights (query params)",
        "GET /factors/{ticker} — 6-factor analysis with custom weights. Returns individual scores, composite, signal, confidence."))
    story.append(func_block("get_backtest", "ticker, period, risk, horizon",
        "GET /backtest/{ticker} — Simulates trading strategy with configurable risk profiles and holding periods."))
    story.append(func_block("get_bull_bear", "ticker",
        "GET /bull-bear/{ticker} — Data-driven bull and bear case arguments."))
    story.append(func_block("get_fundamentals", "ticker",
        "GET /fundamentals/{ticker} — 20+ fundamental metrics from yfinance."))
    story.append(PageBreak())

    # ── 1.17 Sentiment ──────────────────────────────────────────
    story.append(Paragraph("1.17  Sentiment Endpoints (FinBERT)", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/api/v1/endpoints/sentiment.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        @router.get("/{ticker}", response_model=SentimentResponse)
        async def get_sentiment(ticker: str):
            analyzer = SentimentAnalyzer()
            result = await asyncio.get_event_loop().run_in_executor(
                _executor, analyzer.analyze_ticker, ticker
            )
            return result
    """)))
    story.append(Spacer(1, 8))
    story.append(func_block("get_sentiment", "ticker: str",
        "GET /sentiment/{ticker} — Full FinBERT pipeline: fetches headlines from Yahoo Finance, classifies each "
        "through the ProsusAI/finbert transformer, aggregates into overall score (0-100). Returns per-headline "
        "breakdown with positive/negative/neutral probabilities.",
        returns="SentimentResponse"))
    story.append(PageBreak())

    # ── 1.18 Schemas ────────────────────────────────────────────
    story.append(Paragraph("1.18  Pydantic Schemas — Complete Reference", styles["SectionHead"]))
    story.append(body(
        "All schemas use Pydantic v2 with <font face='Courier'>model_config = ConfigDict(from_attributes=True)</font>."
    ))
    story.append(hr())

    story.append(Paragraph("Schema Pattern Example", styles["SubSection"]))
    story.append(body(
        "All 10 schema files follow the same Pydantic v2 pattern. Here is a representative example "
        "showing the HoldingCreate (input) and HoldingOut (output) schemas:"
    ))
    story.append(code_block(textwrap.dedent("""\
        from pydantic import BaseModel, ConfigDict
        from uuid import UUID
        from datetime import datetime

        class HoldingCreate(BaseModel):
            ticker: str
            quantity: float
            avg_cost: float

        class HoldingOut(BaseModel):
            model_config = ConfigDict(from_attributes=True)

            id: UUID
            user_id: UUID
            ticker: str
            quantity: float
            avg_cost: float
            current_price: float | None = None
            opened_at: datetime
    """)))
    story.append(Spacer(1, 8))
    story.append(body(
        "<b>Key pattern:</b> <font face='Courier'>ConfigDict(from_attributes=True)</font> tells Pydantic to read "
        "attributes from SQLAlchemy ORM objects (e.g., <font face='Courier'>holding.ticker</font>) rather than "
        "requiring dict keys. This enables <font face='Courier'>return holding</font> in endpoints without "
        "manual serialisation."
    ))
    story.append(Spacer(1, 6))
    story.append(body(
        "The 10 schema files are: <font face='Courier'>auth.py</font>, <font face='Courier'>user.py</font>, "
        "<font face='Courier'>stock.py</font>, <font face='Courier'>prediction.py</font>, "
        "<font face='Courier'>portfolio.py</font>, <font face='Courier'>watchlist.py</font>, "
        "<font face='Courier'>trade.py</font>, <font face='Courier'>strategy.py</font>, "
        "<font face='Courier'>notification.py</font>, <font face='Courier'>marketplace.py</font>. "
        "For complete field-by-field reference, see <b>Appendix L</b>."
    ))
    story.append(PageBreak())

    # ╔════════════════════════════════════════════════════════════╗
    # ║                    PART 2 — AI / ML                       ║
    # ╚════════════════════════════════════════════════════════════╝

    story.append(Spacer(1, 1.5 * inch))
    story.append(Paragraph("PART 2", styles["CoverTitle"]))
    story.append(Paragraph("AI / ML", styles["PartTitle"]))
    story.append(gold_hr())
    story.append(Paragraph(
        "XGBoost stock prediction, FinBERT sentiment analysis, feature engineering, "
        "backtesting engine, and the six-factor composite scoring system.",
        styles["CoverSub"],
    ))
    story.append(PageBreak())

    # ── 2.1 ML Architecture ────────────────────────────────────
    story.append(Paragraph("2.1  Machine Learning Architecture Overview", styles["SectionHead"]))
    story.append(hr())
    story.append(body(
        "StockPilot's ML pipeline consists of four interconnected services located under "
        "<font face='Courier'>backend/app/services/</font>:"
    ))
    story.append(Spacer(1, 4))

    ml_arch = Table(
        [
            ["Service", "File", "Purpose"],
            ["DataFetcher", "market_data/fetcher.py", "Downloads and caches OHLCV data from Yahoo Finance"],
            ["FeatureEngine", "indicators/featureEngine.py", "Computes 30+ technical indicators from OHLCV data"],
            ["StockPredictor", "recommendation/engine.py", "XGBoost classifier for next-day direction prediction"],
            ["FinBERT", "sentiment/finbert.py", "Transformer-based news sentiment analysis"],
        ],
        colWidths=[1.3 * inch, 2 * inch, 3 * inch],
    )
    ml_arch.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (1, 1), (1, -1), "Courier"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(ml_arch)
    story.append(Spacer(1, 12))
    story.append(body(
        "<b>Data flow:</b> DataFetcher downloads raw OHLCV from Yahoo Finance. FeatureEngine transforms it into "
        "30+ technical indicators. StockPredictor trains an XGBoost model on these features to predict next-day "
        "price direction. FinBERT analyses news headlines independently. The 6-factor analysis system "
        "(in analysis.py) combines both technical indicators and FinBERT sentiment into a composite score."
    ))
    story.append(PageBreak())

    # ── 2.2 DataFetcher ─────────────────────────────────────────
    story.append(Paragraph("2.2  Data Acquisition — DataFetcher", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/services/market_data/fetcher.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        class DataFetcher:
            def __init__(self, data_path="data_storage/historical/", default_period="6mo",
                         default_interval="1d", max_retries=3, retry_backoff=1.0):
                self.data_path = Path(data_path)
                self.data_path.mkdir(parents=True, exist_ok=True)
                ...

            def fetch_historical(self, ticker, period=None, interval=None, start=None, end=None):
                for attempt in range(self.max_retries):
                    try:
                        df = yf.download(ticker, period=period, interval=interval)
                        if df.empty:
                            raise ValueError(f"No data for {ticker}")
                        df = self._flatten_columns(df)
                        df = self._standardize_ohlcv(df)
                        return df
                    except Exception as e:
                        if attempt == self.max_retries - 1:
                            raise
                        time.sleep(self.retry_backoff * (2 ** attempt))
    """)))
    story.append(Spacer(1, 8))
    story.append(body("<b>Class: DataFetcher</b> — Downloads and caches historical OHLCV data."))
    story.append(func_block("__init__", "data_path, default_period, default_interval, max_retries, retry_backoff",
        "Configuration: data storage path (default: data_storage/historical/), download period (6mo), "
        "interval (1d), retry attempts (3), backoff multiplier (1.0 seconds, doubling each retry)."))
    story.append(func_block("_flatten_columns", "df",
        "Flattens MultiIndex column names that yfinance returns for single-ticker downloads. "
        "Handles the inconsistency where yfinance sometimes returns ('Close', 'AAPL') instead of just 'Close'."))
    story.append(func_block("_standardize_ohlcv", "df",
        "Ensures canonical OHLCV column names. Handles suffix/prefix variations like Close_AAPL or AAPL_Close."))
    story.append(func_block("fetch_historical", "ticker, period, interval, start, end",
        "Downloads OHLCV with retry logic (3 attempts, exponential backoff). Flattens columns, standardises names, "
        "attaches ticker as Categorical column. Raises ValueError on invalid ticker or empty response."))
    story.append(func_block("save_to_csv / load_from_csv", "data, ticker, period, interval",
        "Persist/load data as CSV. Pattern: <font face='Courier'>{TICKER}_{period}_{interval}.csv</font>."))
    story.append(why_box(
        "<b>Why retry logic?</b> Yahoo Finance is a free API with rate limits. It occasionally returns empty "
        "responses or times out under load. The exponential backoff (1s, 2s, 4s) gives the API time to recover "
        "between attempts without hammering it."
    ))
    story.append(PageBreak())

    # ── 2.3 Feature Engineering ─────────────────────────────────
    story.append(Paragraph("2.3  Feature Engineering — FeatureEngine", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/services/indicators/featureEngine.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        class FeatureEngine:
            def calculate_all_features(self, data: pd.DataFrame) -> pd.DataFrame:
                df = data.copy()
                df = self.calculate_moving_averages(df)     # SMA/EMA 5,10,20,50
                df = self.calculate_rsi(df)                 # RSI-14
                df = self.calculate_macd(df)                # MACD, Signal, Histogram
                df = self.calculate_bollinger_bands(df)     # BB Width, Position
                df = self.calculate_volume_indicators(df)   # VWAP, OBV, MFI, Volume Ratio
                df = self.calculate_volatility(df)          # ATR-14, Volatility-20
                df = self.calculate_price_position(df)      # Position, ROC-10, Price/SMA
                df = self.handle_nan_values(df)             # Trim warmup rows
                return df

            def calculate_rsi(self, df):
                df["RSI_14"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()
                return df
    """)))
    story.append(Spacer(1, 8))

    story.append(body(
        "<b>Class: FeatureEngine</b> — Computes 30+ technical indicators from raw OHLCV data. "
        "Key design: validates input returns a copy (never mutates), NaN handling drops warmup rows "
        "instead of back-filling (back-fill is look-ahead bias)."
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Indicator Methods (each returns a new DataFrame):", styles["SubSection"]))

    indicators_detail = [
        ("calculate_moving_averages()", "SMA and EMA for periods 5, 10, 20, 50. "
         "Simple Moving Average gives equal weight to all days; Exponential Moving Average weights recent days "
         "more heavily. Short-term MA crossing above long-term MA (golden cross) is a classic bullish signal."),
        ("calculate_rsi()", "14-period RSI (Relative Strength Index) using the ta library. "
         "Measures speed and magnitude of price changes on a 0-100 scale. RSI > 70 = overbought, RSI < 30 = oversold."),
        ("calculate_macd()", "MACD line (12-day EMA - 26-day EMA), signal line (9-day EMA of MACD), "
         "histogram (MACD - signal). Positive histogram = strengthening uptrend."),
        ("calculate_bollinger_bands()", "20-period, 2-sigma bands. BB_Width measures volatility. "
         "BB_Position shows where price sits within the bands (0 = lower, 1 = upper)."),
        ("calculate_volume_indicators()", "Rolling 20-day VWAP, OBV (On-Balance Volume), "
         "volume ratio (current vs 20-day average), 14-period MFI (Money Flow Index)."),
        ("calculate_volatility()", "ATR-14 (Average True Range), daily return, 20-day volatility, "
         "high/low ratio, close/open ratio."),
        ("calculate_price_position()", "20-day price position (0-1), 10-day ROC (Rate of Change), "
         "price/SMA ratios, above/below SMA flags."),
    ]
    for title, desc in indicators_detail:
        story.append(Paragraph(f"<b>{title}</b>", styles["BodyIndent"]))
        story.append(body_i(desc))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 6))
    story.append(func_block("handle_nan_values", "df: DataFrame",
        "Finds the first row where all indicators are finite and drops everything before it. "
        "Uses forward-fill for single-day gaps but never back-fill (look-ahead bias)."))
    story.append(func_block("calculate_all_features", "data: DataFrame",
        "Top-level pipeline: validate, compute all indicators, trim warmup, cache result."))
    story.append(why_box(
        "<b>Why trim warmup rows instead of filling with zeros?</b> The 50-day SMA needs 50 days of data "
        "before producing a meaningful value. Filling the first 50 rows with zero would teach the model that "
        "zero SMA is normal, producing garbage predictions. Trimming is honest about data availability."
    ))
    story.append(PageBreak())

    # ── 2.4 XGBoost Predictor ───────────────────────────────────
    story.append(Paragraph("2.4  XGBoost Prediction Model — StockPredictor", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/services/recommendation/engine.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        @dataclass
        class PredictorConfig:
            target_horizon: int = 1           # Predict 1-day forward return
            target_deadband: float = 0.003    # Ignore moves < 0.3% (noise)
            training_period: str = "5y"
            max_estimators: int = 300
            early_stopping_rounds: int = 100
            max_depth: int = 4
            learning_rate: float = 0.01
            hold_lower: float = 0.43          # HOLD zone boundaries
            hold_upper: float = 0.57

        class StockPredictor:
            def predict(self, ticker):
                proba = self.model.predict_proba(features)[:, 1][0]
                if proba >= self.config.hold_upper:
                    return "BUY", proba
                elif proba <= self.config.hold_lower:
                    return "SELL", 1 - proba
                else:
                    return "HOLD", max(proba, 1 - proba)
    """)))
    story.append(Spacer(1, 8))

    story.append(why_box(
        "<b>Why XGBoost instead of a neural network (LSTM/Transformer)?</b> "
        "(1) Stock features are tabular data — XGBoost outperforms deep learning on tabular datasets (NeurIPS 2022). "
        "(2) XGBoost provides feature importance scores for explainability. "
        "(3) Trains on 5 years of daily data in seconds, not hours. "
        "(4) Only ~1,250 rows — neural networks need millions to generalise."
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("PredictorConfig — Configuration Dataclass", styles["SubSection"]))
    story.append(body("Key parameters that control the model's behaviour:"))
    config_params = [
        ("target_horizon = 1", "Predict the sign of the 1-day forward return"),
        ("target_deadband = 0.003", "Moves smaller than 0.3% are treated as noise and dropped"),
        ("training_period = '5y'", "5 years of daily data (~1,250 rows)"),
        ("max_estimators = 300", "Maximum decision trees (ceiling, not target)"),
        ("early_stopping_rounds = 100", "Stop if validation loss hasn't improved in 100 trees"),
        ("max_depth = 4", "Each tree has at most 4 levels — prevents overfitting"),
        ("learning_rate = 0.01", "Small step size for gradual convergence"),
        ("subsample = 0.8", "Each tree sees 80% of rows (stochastic regularisation)"),
        ("colsample_bytree = 0.8", "Each tree sees 80% of features"),
        ("hold_lower = 0.43, hold_upper = 0.57", "Probabilities in this range produce HOLD signal"),
    ]
    for param, desc in config_params:
        story.append(Paragraph(
            f"<font face='Courier'>{param}</font> — {desc}", styles["BodyIndent"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Key Methods", styles["SubSection"]))
    story.append(func_block("prepare_data", "ticker, period",
        "Fetches OHLCV, engineers features, builds labelled dataset. Target: 1 if forward return > +0.3%, "
        "0 if < -0.3%, neutral rows dropped. Close column dropped from features (leakage-adjacent)."))
    story.append(func_block("train", "ticker, period, test_size, save",
        "Splits data chronologically: 64% train, 16% validation (early stopping), 20% test. "
        "Sets scale_pos_weight for class balance. Evaluates on held-out test set."))
    story.append(func_block("walk_forward_evaluate", "ticker, n_splits, period",
        "TimeSeriesSplit cross-validation. Each fold's test period is strictly after training. "
        "The honest accuracy estimate."))
    story.append(func_block("predict", "ticker",
        "Live signal: BUY if P(UP) >= 0.57, SELL if <= 0.43, HOLD otherwise. "
        "Hard errors on missing features (never fills with zero)."))
    story.append(func_block("backtest", "ticker, period, test_size, cost_bps",
        "Simulates signal-following strategy. Long-only. 5 bps transaction cost per flip. "
        "Reports: equity curve, Sharpe, max drawdown, profit factor, edge vs buy-and-hold."))
    story.append(func_block("save_model / load_model", "",
        "Version-safe joblib persistence. Bundle: model + features + config + library versions. "
        "Warns on version drift (xgboost, sklearn)."))
    story.append(func_block("feature_importance", "top_k=15",
        "Top features by XGBoost gain. Maps internal f0/f1 names back to human-readable names."))
    story.append(PageBreak())

    # ── 2.5 FinBERT ─────────────────────────────────────────────
    story.append(Paragraph("2.5  FinBERT Sentiment Analysis", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/services/sentiment/finbert.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        class SentimentAnalyzer:
            def analyze_headline(self, text: str) -> dict:
                pipe = self._get_pipeline()
                result = pipe(text)[0]
                scores = {r["label"]: r["score"] for r in result}
                score = scores.get("positive", 0) * 100 + scores.get("neutral", 0) * 50
                label = "positive" if score >= 62 else "negative" if score <= 38 else "neutral"
                return {"text": text, "score": score, "label": label, **scores}

            def analyze_ticker(self, ticker: str, max_headlines=15) -> dict:
                headlines = self.fetch_news_headlines(ticker, max_headlines)
                results = [self.analyze_headline(h) for h in headlines]
                avg = sum(r["score"] for r in results) / len(results) if results else 50
                return {"ticker": ticker, "score": avg, "headlines": results}
    """)))
    story.append(Spacer(1, 8))

    story.append(why_box(
        "<b>What is FinBERT?</b> A BERT model fine-tuned on 50,000+ financial texts. Unlike general sentiment "
        "tools, it understands financial context: 'beat expectations' is positive, 'guidance raised' is positive, "
        "'margin compression' is negative. Standard sentiment tools would miss these nuances."
    ))
    story.append(why_box(
        "<b>Why not keyword scoring?</b> Keyword-based sentiment fails on financial text: "
        "'Short squeeze' contains 'short' (negative word) but is bullish. "
        "'Despite missing revenue, guidance was raised' is net positive but has more negative keywords. "
        "'The stock is not expected to decline' — negation flips meaning."
    ))
    story.append(Spacer(1, 6))
    story.append(func_block("_get_pipeline", "",
        "Lazy-loads the FinBERT HuggingFace pipeline (~420 MB) on first call. Cached in memory. "
        "Uses truncation with max_length=512 and top_k=None for all three class probabilities."))
    story.append(func_block("fetch_news_headlines", "ticker, max_headlines=15",
        "Fetches headlines via yfinance. Handles both nested and flat response formats."))
    story.append(func_block("analyze_headline", "text",
        "Runs single headline through FinBERT. Score: P(positive) x 100 + P(neutral) x 50. "
        "Maps to 0-100 scale."))
    story.append(func_block("analyze_ticker", "ticker, max_headlines=15",
        "Full pipeline: fetch headlines, classify each, aggregate. Overall label based on average score: "
        ">= 62 positive, <= 38 negative, else neutral. Returns score=50 if no headlines available."))
    story.append(PageBreak())

    # ── 2.6 Six-Factor Scoring ──────────────────────────────────
    story.append(Paragraph("2.6  Six-Factor Composite Scoring System", styles["SectionHead"]))
    story.append(hr())
    story.append(body(
        "The Advisor page's verdict (BUY/HOLD/SELL) is driven by a weighted composite of 6 factors. "
        "Each factor produces a score from 0 (most bearish) to 100 (most bullish). The factors and their "
        "default weights are:"
    ))
    story.append(Spacer(1, 6))

    factors = [
        ("1. Sentiment (FinBERT)", "18%",
         "News headlines through FinBERT transformer. Falls back to OBV trend when no headlines available."),
        ("2. Momentum", "24%",
         "RSI-14 (40%), MACD histogram direction (30%), 20-day price position (30%)."),
        ("3. Valuation", "20%",
         "Bollinger Band position + price/SMA ratios. Trading below mid-Bollinger = potential undervaluation."),
        ("4. Volatility", "16%",
         "Inverse scoring: low volatility = high score. 20-day return std + ATR-14 as % of price."),
        ("5. Volume", "10%",
         "Volume ratio (current vs 20-day avg) + MFI-14. High volume + positive flow = institutional buying."),
        ("6. Growth", "12%",
         "ROC-10 + trend positioning (above/below SMA-20). Positive acceleration = high growth score."),
    ]
    for name, weight, desc in factors:
        story.append(Paragraph(f"<b>{name} — default weight {weight}</b>", styles["BodyIndent"]))
        story.append(body_i(desc))
    story.append(Spacer(1, 8))
    story.append(body(
        "<b>Composite calculation:</b> composite = sum(score_i x weight_i) / sum(weight_i). "
        "Users can adjust weights through the Advisor UI."
    ))
    story.append(PageBreak())

    # ── 2.7 Backtest Engine ─────────────────────────────────────
    story.append(Paragraph("2.7  Backtest Simulation Engine", styles["SectionHead"]))
    story.append(hr())
    story.append(body(
        "The backtester simulates a trading strategy over historical data using daily 6-factor composite scores."
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Risk Profiles", styles["SubSection"]))
    risk_table = Table([
        ["Profile", "Buy Threshold", "Sell Threshold", "Trailing Stop"],
        ["Conservative", "> 51", "<= 50", "0.8%"],
        ["Moderate", "> 53", "<= 47", "1.8%"],
        ["Aggressive", "> 50", "<= 42", "4.0%"],
    ], colWidths=[1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
    risk_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Holding Periods", styles["SubSection"]))
    hold_table = Table([
        ["Horizon", "Min Hold", "Max Hold", "Cooldown"],
        ["Short", "1 day", "5 days", "0 days"],
        ["Medium", "2 days", "15 days", "1 day"],
        ["Long", "5 days", "40 days", "2 days"],
    ], colWidths=[1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
    hold_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))
    story.append(hold_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Simulation Loop (daily)", styles["SubSection"]))
    story.append(bullet("If not in position and composite > buy_threshold: ENTER long, record entry price"))
    story.append(bullet("If in position: track peak price for trailing stop"))
    story.append(bullet("If trailing stop hit OR sell signal AND min hold met: EXIT"))
    story.append(bullet("After exit: wait cooldown days before next entry"))
    story.append(Spacer(1, 4))
    story.append(body(
        "<b>Metrics computed:</b> total return, buy-and-hold return, edge vs hold, win rate, "
        "Sharpe ratio (annualised, 252 trading days), max drawdown, profit factor, trade count, equity curve."
    ))
    story.append(PageBreak())

    # ── 2.8 XGBoost Step by Step ────────────────────────────────
    story.append(Paragraph("2.8  How XGBoost Training Works — Step by Step", styles["SectionHead"]))
    story.append(hr())

    steps = [
        ("Step 1 — Data Acquisition",
         "DataFetcher downloads 5 years of daily OHLCV (~1,250 rows) from Yahoo Finance with retry logic "
         "(3 attempts, exponential backoff). Column names are standardised."),
        ("Step 2 — Feature Engineering (30+ indicators)",
         "FeatureEngine computes: SMA/EMA (5/10/20/50), RSI-14, MACD/Signal/Histogram, Bollinger Bands "
         "(width + position), VWAP-20, OBV, Volume Ratio, MFI-14, ATR-14, Volatility-20, Price Position, "
         "ROC-10, Price/SMA ratios, above/below SMA flags."),
        ("Step 3 — NaN Handling (Warmup Trimming)",
         "Drops rows where indicators haven't warmed up (first ~50 rows). Never back-fills — that would be "
         "look-ahead bias (leaking future information into past rows)."),
        ("Step 4 — Target Label Construction",
         "Forward return = (tomorrow_close - today_close) / today_close. If > +0.3%: label = 1 (UP). "
         "If < -0.3%: label = 0 (DOWN). Between: row dropped (noise). Close column dropped from features."),
        ("Step 5 — Chronological Split",
         "First 64% = training, next 16% = validation (early stopping), last 20% = test. Never random splits "
         "(leaks future data). scale_pos_weight = count_neg / count_pos for class balance."),
        ("Step 6 — Training with Early Stopping",
         "XGBoost builds up to 300 trees sequentially. Each tree corrects prior errors. After each tree, "
         "checks validation logloss. If no improvement for 100 trees, stops. Typical: 80-150 trees used."),
        ("Step 7 — HOLD Zone Prediction",
         "Output: P(UP) in [0, 1]. If >= 0.57: BUY. If <= 0.43: SELL. Between: HOLD (uncertain). "
         "Confidence = probability of predicted class."),
        ("Step 8 — Walk-Forward Validation",
         "TimeSeriesSplit(n=5): 5 expanding-window folds where every test period is strictly after training. "
         "Reports mean accuracy and standard deviation — the honest performance estimate."),
    ]
    for title, desc in steps:
        story.append(Paragraph(f"<b>{title}</b>", styles["SubSection"]))
        story.append(body(desc))
        story.append(Spacer(1, 4))
    story.append(PageBreak())

    # ── 2.9 FinBERT Step by Step ────────────────────────────────
    story.append(Paragraph("2.9  How FinBERT Inference Works — Step by Step", styles["SectionHead"]))
    story.append(hr())

    finbert_steps = [
        ("Step 1 — Headline Collection",
         "<font face='Courier'>yf.Ticker(ticker).news</font> returns up to 15 recent articles. "
         "Only headline text is extracted."),
        ("Step 2 — Tokenisation",
         "Each headline is split into WordPiece subword tokens. Example: 'Apple beats Q3 earnings' becomes "
         "['apple', 'beats', 'q', '##3', 'earnings']. Truncated to 512 tokens max."),
        ("Step 3 — Transformer Inference",
         "Tokens pass through 12 transformer layers. Each layer has self-attention (captures word relationships — "
         "'beats' + 'expectations' = positive in finance) and feed-forward networks. The [CLS] token's "
         "768-dimensional output captures overall semantic meaning."),
        ("Step 4 — Classification",
         "[CLS] vector passes through linear layer + softmax: P(positive) + P(negative) + P(neutral) = 1.0. "
         "Example: 'Apple reports record revenue' -> positive: 0.92, negative: 0.02, neutral: 0.06."),
        ("Step 5 — Score Computation",
         "Score = P(positive) x 100 + P(neutral) x 50. Maps positive headlines near 100, neutral near 50, "
         "negative near 0."),
        ("Step 6 — Aggregation",
         "Overall score = average of all headline scores. Label: >= 62 positive, <= 38 negative, else neutral."),
        ("Step 7 — Integration with 6-Factor System",
         "The aggregated score becomes the Sentiment factor (default weight 18%). Falls back to OBV trend "
         "if no headlines available."),
    ]
    for title, desc in finbert_steps:
        story.append(Paragraph(f"<b>{title}</b>", styles["SubSection"]))
        story.append(body(desc))
        story.append(Spacer(1, 4))
    story.append(PageBreak())

    # ╔════════════════════════════════════════════════════════════╗
    # ║                PART 3 — DB MANAGEMENT                     ║
    # ╚════════════════════════════════════════════════════════════╝

    story.append(Spacer(1, 1.5 * inch))
    story.append(Paragraph("PART 3", styles["CoverTitle"]))
    story.append(Paragraph("DB Management", styles["PartTitle"]))
    story.append(gold_hr())
    story.append(Paragraph(
        "SQLAlchemy ORM models, async session management, entity relationships, "
        "constraint naming conventions, and database seeding.",
        styles["CoverSub"],
    ))
    story.append(PageBreak())

    # ── 3.1 DB Architecture ─────────────────────────────────────
    story.append(Paragraph("3.1  Database Architecture Overview", styles["SectionHead"]))
    story.append(hr())
    story.append(body(
        "StockPilot uses <b>PostgreSQL</b> as its relational database, accessed through "
        "<b>SQLAlchemy 2.0</b> async ORM with the <b>asyncpg</b> driver. The database layer "
        "consists of 9 models across 9 files, managed via an async session factory."
    ))
    story.append(Spacer(1, 6))

    db_overview = Table([
        ["Model", "Table", "Purpose", "Key Relationships"],
        ["User", "users", "Registered users", "Holdings, Watchlist, Trades, Strategies, Notifications"],
        ["Stock", "stocks", "Tracked stocks", "PriceHistory"],
        ["PriceHistory", "price_history", "Daily OHLCV", "Stock (FK)"],
        ["Prediction", "predictions", "AI predictions", "Referenced by ticker"],
        ["Holding", "holdings", "Portfolio positions", "User (FK)"],
        ["Watchlist", "watchlist", "Watched tickers", "User (FK), UniqueConstraint(user, ticker)"],
        ["Trade", "trades", "Trade journal", "User (FK)"],
        ["Strategy", "strategies", "Factor weight configs", "User (FK), MarketplaceListing (1:1)"],
        ["MarketplaceListing", "marketplace_listings", "Published strategies", "Strategy (FK), Ratings"],
        ["MarketplaceRating", "marketplace_ratings", "User ratings", "Listing (FK), User (FK)"],
        ["Notification", "notifications", "User alerts", "User (FK)"],
    ], colWidths=[1.2 * inch, 1.2 * inch, 1.2 * inch, 2.4 * inch])
    db_overview.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(db_overview)
    story.append(PageBreak())

    # ── 3.2 Base and Naming ─────────────────────────────────────
    story.append(Paragraph("3.2  SQLAlchemy Base and Naming Conventions", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/db/base.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        from sqlalchemy.orm import DeclarativeBase

        convention = {
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }

        class Base(DeclarativeBase):
            metadata = MetaData(naming_convention=convention)
    """)))
    story.append(Spacer(1, 8))
    story.append(body(
        "All ORM models inherit from this Base class. The naming convention ensures deterministic constraint "
        "names across all models:"
    ))
    story.append(bullet("<font face='Courier'>ix_%(column_0_label)s</font> — Index names"))
    story.append(bullet("<font face='Courier'>uq_%(table_name)s_%(column_0_name)s</font> — Unique constraints"))
    story.append(bullet("<font face='Courier'>ck_%(table_name)s_%(constraint_name)s</font> — Check constraints"))
    story.append(bullet("<font face='Courier'>fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s</font> — Foreign keys"))
    story.append(bullet("<font face='Courier'>pk_%(table_name)s</font> — Primary keys"))
    story.append(why_box(
        "<b>Why naming conventions?</b> Without them, SQLAlchemy auto-generates random constraint names. "
        "Deterministic names make migration scripts readable and allow referencing constraints by name in "
        "ALTER TABLE statements."
    ))
    story.append(PageBreak())

    # ── 3.3 Session Management ──────────────────────────────────
    story.append(Paragraph("3.3  Async Engine and Session Management", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/db/session.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

        async def get_db():
            async with AsyncSessionLocal() as session:
                try:
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise
    """)))
    story.append(Spacer(1, 8))
    story.append(body("<b>Module-level objects:</b>"))
    story.append(bullet(
        "<font face='Courier'>engine</font> — <font face='Courier'>create_async_engine(DATABASE_URL, echo=False)</font>. "
        "The async engine connected to PostgreSQL via asyncpg."
    ))
    story.append(bullet(
        "<font face='Courier'>AsyncSessionLocal</font> — Session factory with <font face='Courier'>expire_on_commit=False</font>."
    ))
    story.append(Spacer(1, 6))
    story.append(func_block("get_db", "",
        "Async generator dependency. Yields an AsyncSession, commits on success, rolls back on exception. "
        "Used as a FastAPI dependency in all endpoints needing database access.",
        returns="AsyncSession (yielded)"))
    story.append(why_box(
        "<b>Why expire_on_commit=False?</b> In async code, accessing ORM attributes after commit would "
        "trigger a lazy load — but lazy loading is not supported in async mode. Setting expire_on_commit=False "
        "keeps attribute values cached after commit, so they remain accessible."
    ))
    story.append(why_box(
        "<b>Why the commit-after-yield pattern?</b> If any part of an endpoint fails (e.g., adding a holding "
        "succeeds but live price fetch crashes), the entire transaction is rolled back. No partial data is "
        "committed. This is the unit-of-work pattern."
    ))
    story.append(PageBreak())

    # ── 3.4 User Model ──────────────────────────────────────────
    story.append(Paragraph("3.4  User Model and Role System", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/db/models/user.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        class UserRole(str, enum.Enum):
            investor = "investor"
            analyst = "analyst"
            admin = "admin"

        class User(Base):
            __tablename__ = "users"
            id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
            email = Column(String(255), unique=True, index=True, nullable=False)
            password_hash = Column(String(255), nullable=False)
            full_name = Column(String(255), nullable=False)
            role = Column(SQLEnum(UserRole), default=UserRole.investor)
            # ... phone, bio, avatar_url, is_active, created_at, updated_at

            holdings = relationship("Holding", back_populates="user", cascade="all, delete-orphan")
            watchlist_items = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
            trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")
    """)))
    story.append(Spacer(1, 8))
    story.append(body("<b>UserRole Enum:</b> investor (default), analyst (can publish strategies), admin."))
    story.append(body("<b>User columns:</b>"))
    story.append(bullet("<font face='Courier'>id</font> — UUID primary key, generated server-side"))
    story.append(bullet("<font face='Courier'>email</font> — String, unique, indexed for fast lookup"))
    story.append(bullet("<font face='Courier'>password_hash</font> — bcrypt hash (never stores plain text)"))
    story.append(bullet("<font face='Courier'>full_name</font> — Display name"))
    story.append(bullet("<font face='Courier'>role</font> — UserRole enum, default investor"))
    story.append(bullet("<font face='Courier'>phone, bio, avatar_url</font> — Optional profile fields"))
    story.append(bullet("<font face='Courier'>is_active</font> — Boolean, default True"))
    story.append(bullet("<font face='Courier'>created_at, updated_at</font> — Auto-managed timestamps"))
    story.append(Spacer(1, 6))
    story.append(body("<b>Relationships:</b>"))
    story.append(bullet("holdings — one-to-many with Holding (cascade: all, delete-orphan)"))
    story.append(bullet("watchlist_items — one-to-many with Watchlist"))
    story.append(bullet("trades — one-to-many with Trade"))
    story.append(bullet("strategies — one-to-many with Strategy"))
    story.append(bullet("notifications — one-to-many with Notification"))
    story.append(PageBreak())

    # ── 3.5 Stock Model ─────────────────────────────────────────
    story.append(Paragraph("3.5  Stock and Price History Models", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/db/models/stock.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        class Stock(Base):
            __tablename__ = "stocks"
            id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
            ticker = Column(String(10), unique=True, index=True, nullable=False)
            name = Column(String(255))
            sector = Column(String(100))
            industry = Column(String(100))
            price_history = relationship("PriceHistory", back_populates="stock")

        class PriceHistory(Base):
            __tablename__ = "price_history"
            id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
            ticker = Column(String(10), ForeignKey("stocks.ticker"), nullable=False)
            date = Column(Date, nullable=False)
            open = Column(Float); high = Column(Float); low = Column(Float)
            close = Column(Float); volume = Column(BigInteger)
            __table_args__ = (UniqueConstraint("ticker", "date"),)
    """)))
    story.append(Spacer(1, 8))
    story.append(body(
        "<b>Stock:</b> Represents a tracked stock. ticker is unique and indexed. "
        "Columns: name, sector, industry. Has one-to-many relationship with PriceHistory."
    ))
    story.append(body(
        "<b>PriceHistory:</b> Daily OHLCV records. Composite unique constraint on (ticker, date) "
        "prevents duplicate entries for the same day."
    ))
    story.append(PageBreak())

    # ── 3.6 Prediction Model ────────────────────────────────────
    story.append(Paragraph("3.6  Prediction Model", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/db/models/prediction.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        class SignalType(str, enum.Enum):
            BUY = "BUY"; HOLD = "HOLD"; SELL = "SELL"

        class Prediction(Base):
            __tablename__ = "predictions"
            id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
            ticker = Column(String(10), index=True, nullable=False)
            signal = Column(SQLEnum(SignalType), nullable=False)
            confidence = Column(Float, nullable=False)
            probability_up = Column(Float)
            probability_down = Column(Float)
            composite_score = Column(Float)
            model_version = Column(String(50))
            created_at = Column(DateTime(timezone=True), server_default=func.now())
    """)))
    story.append(Spacer(1, 8))
    story.append(body(
        "<b>SignalType Enum:</b> BUY, HOLD, SELL — stored as strings in PostgreSQL."
    ))
    story.append(body(
        "<b>Prediction columns:</b> ticker, signal (SignalType), confidence (Float), "
        "probability_up, probability_down, composite_score, model_version (tracks which model generated it)."
    ))
    story.append(PageBreak())

    # ── 3.7 Portfolio ────────────────────────────────────────────
    story.append(Paragraph("3.7  Portfolio (Holding) Model", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/db/models/portfolio.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        class Holding(Base):
            __tablename__ = "holdings"
            id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
            user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
            ticker = Column(String(10), nullable=False)
            quantity = Column(Float, nullable=False)
            avg_cost = Column(Float, nullable=False)
            current_price = Column(Float)             # Updated on each GET request
            opened_at = Column(DateTime(timezone=True), server_default=func.now())
            closed_at = Column(DateTime(timezone=True)) # NULL = active position
            user = relationship("User", back_populates="holdings")
    """)))
    story.append(Spacer(1, 8))
    story.append(body(
        "<b>Holding:</b> A user's stock position. user_id foreign key to User. "
        "Columns: ticker, quantity, avg_cost, current_price (updated on each GET), "
        "opened_at, closed_at (nullable — active holdings have closed_at IS NULL)."
    ))
    story.append(PageBreak())

    # ── 3.8 Watchlist ────────────────────────────────────────────
    story.append(Paragraph("3.8  Watchlist Model", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/db/models/watchlist.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        class Watchlist(Base):
            __tablename__ = "watchlist"
            id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
            user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
            ticker = Column(String(10), nullable=False)
            added_at = Column(DateTime(timezone=True), server_default=func.now())
            __table_args__ = (UniqueConstraint("user_id", "ticker"),)
    """)))
    story.append(Spacer(1, 8))
    story.append(body(
        "<b>UniqueConstraint(user_id, ticker)</b> — Prevents a user from watching the same ticker twice. "
        "The database enforces this at the constraint level, so even concurrent requests cannot create duplicates."
    ))
    story.append(PageBreak())

    # ── 3.9 Trade ────────────────────────────────────────────────
    story.append(Paragraph("3.9  Trade Journal Model", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/db/models/trade.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        class TradeSide(str, enum.Enum):
            buy = "buy"; sell = "sell"

        class Trade(Base):
            __tablename__ = "trades"
            id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
            user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
            ticker = Column(String(10), nullable=False)
            side = Column(SQLEnum(TradeSide), nullable=False)
            entry_price = Column(Float, nullable=False)
            exit_price = Column(Float)
            stop_loss = Column(Float); take_profit = Column(Float)
            quantity = Column(Float, nullable=False)
            strategy_label = Column(String(100))
            notes = Column(Text)
    """)))
    story.append(Spacer(1, 8))
    story.append(body(
        "<b>TradeSide Enum:</b> buy, sell — represents the trade direction."
    ))
    story.append(body(
        "<b>Trade columns:</b> ticker, side, entry_price, exit_price (nullable for open trades), "
        "stop_loss, take_profit, quantity, strategy_label (which strategy was used), "
        "opened_at, closed_at, notes (free-text for trade journal entries)."
    ))
    story.append(PageBreak())

    # ── 3.10 Strategy ───────────────────────────────────────────
    story.append(Paragraph("3.10  Strategy Model with JSONB Weights", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/db/models/strategy.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        class Strategy(Base):
            __tablename__ = "strategies"
            id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
            owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # NULL for presets
            name = Column(String(100), nullable=False)
            description = Column(Text)
            weights = Column(JSONB, nullable=False)  # {"sentiment": 14, "momentum": 22, ...}
            is_preset = Column(Boolean, default=False)
            is_published = Column(Boolean, default=False)
    """)))
    story.append(Spacer(1, 8))
    story.append(body(
        "<b>weights column (JSONB):</b> Stores the 6-factor weight configuration as a JSON object. "
        "Example: <font face='Courier'>{\"sentiment\": 14, \"momentum\": 22, \"valuation\": 20, "
        "\"volatility\": 18, \"volume\": 10, \"growth\": 16}</font> (Multi-Factor Balanced defaults)."
    ))
    story.append(why_box(
        "<b>Why JSONB instead of separate columns?</b> The weight structure may evolve (new factors, "
        "removed factors) without requiring database migrations. JSONB also allows PostgreSQL to index "
        "and query inside the JSON structure if needed."
    ))
    story.append(body(
        "<b>is_preset:</b> True for system-provided strategies (Balanced, Momentum, etc.). "
        "<b>is_published:</b> True when available on the marketplace."
    ))
    story.append(PageBreak())

    # ── 3.11 Marketplace ────────────────────────────────────────
    story.append(Paragraph("3.11  Marketplace and Rating Models", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/db/models/marketplace.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        class ListingStatus(str, enum.Enum):
            draft = "draft"; review = "review"; verified = "verified"
            listed = "listed"; removed = "removed"

        class MarketplaceListing(Base):
            __tablename__ = "marketplace_listings"
            id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
            strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id"), unique=True)
            price_cents = Column(Integer, nullable=False)
            status = Column(SQLEnum(ListingStatus), default=ListingStatus.draft)
            avg_rating = Column(Float); rating_count = Column(Integer, default=0)
            strategy = relationship("Strategy", back_populates="listing")
            ratings = relationship("MarketplaceRating", back_populates="listing", cascade="all, delete-orphan")
    """)))
    story.append(Spacer(1, 8))
    story.append(body(
        "<b>ListingStatus Enum:</b> draft, review, verified, listed, removed — represents the lifecycle "
        "of a marketplace listing."
    ))
    story.append(body(
        "<b>MarketplaceListing:</b> Links a Strategy to the marketplace. strategy_id is unique (one listing "
        "per strategy). Columns: price_cents, status, avg_rating, rating_count, sales_count, "
        "backtest_return/sharpe/winrate, listed_at."
    ))
    story.append(body(
        "<b>MarketplaceRating:</b> User ratings for listings. UniqueConstraint(listing_id, user_id) ensures "
        "one rating per user per listing. Columns: rating (int 1-5), review (text)."
    ))
    story.append(PageBreak())

    # ── 3.12 Notification ───────────────────────────────────────
    story.append(Paragraph("3.12  Notification Model", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/app/db/models/notification.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        class NotificationKind(str, enum.Enum):
            verdict_change = "verdict_change"; price_alert = "price_alert"
            marketplace = "marketplace"; weekly_report = "weekly_report"
            security = "security"; system = "system"

        class Notification(Base):
            __tablename__ = "notifications"
            id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
            user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
            kind = Column(SQLEnum(NotificationKind), nullable=False)
            title = Column(String(255), nullable=False)
            body = Column(Text)
            is_read = Column(Boolean, default=False)
            created_at = Column(DateTime(timezone=True), server_default=func.now())
    """)))
    story.append(Spacer(1, 8))
    story.append(body(
        "<b>NotificationKind Enum:</b> verdict_change, price_alert, marketplace, weekly_report, security, system."
    ))
    story.append(body(
        "<b>Notification columns:</b> user_id (FK), kind (NotificationKind), title, body (optional detail text), "
        "is_read (Boolean, default False), created_at."
    ))
    story.append(PageBreak())

    # ── 3.13 ER Diagram ─────────────────────────────────────────
    story.append(Paragraph("3.13  Entity Relationship Diagram", styles["SectionHead"]))
    story.append(hr())
    story.append(body(
        "The following diagram shows the relationships between all 11 database models:"
    ))
    story.append(Spacer(1, 8))
    story.append(code_block(textwrap.dedent("""\
        User (UUID PK)
          |-- 1:N --> Holding (user_id FK)
          |-- 1:N --> Watchlist (user_id FK)  [UniqueConstraint: user_id + ticker]
          |-- 1:N --> Trade (user_id FK)
          |-- 1:N --> Strategy (owner_id FK)
          |            |-- 1:1 --> MarketplaceListing (strategy_id FK, unique)
          |                          |-- 1:N --> MarketplaceRating (listing_id FK)
          |-- 1:N --> Notification (user_id FK)
          |-- 1:N --> MarketplaceRating (user_id FK)  [UniqueConstraint: listing_id + user_id]

        Stock (UUID PK, ticker unique+indexed)
          |-- 1:N --> PriceHistory (ticker FK)  [UniqueConstraint: ticker + date]

        Prediction (UUID PK)
          |-- ticker (string, references Stock.ticker logically)
    """)))
    story.append(Spacer(1, 8))
    story.append(body("<b>Key constraints:</b>"))
    story.append(bullet("All primary keys are UUIDs generated server-side via uuid4"))
    story.append(bullet("User.email has a unique index for fast login lookups"))
    story.append(bullet("Stock.ticker has a unique index"))
    story.append(bullet("Watchlist has UniqueConstraint(user_id, ticker) to prevent duplicates"))
    story.append(bullet("MarketplaceListing.strategy_id is unique (one listing per strategy)"))
    story.append(bullet("MarketplaceRating has UniqueConstraint(listing_id, user_id) for one rating per user"))
    story.append(bullet("All cascade deletes use 'all, delete-orphan' for proper cleanup"))
    story.append(PageBreak())

    # ── 3.14 Database Seeder ────────────────────────────────────
    story.append(Paragraph("3.14  Database Seeder", styles["SectionHead"]))
    story.append(Paragraph("<b>File:</b> <font face='Courier'>backend/seed.py</font>", styles["Body"]))
    story.append(hr())
    story.append(code_block(textwrap.dedent("""\
        async def seed():
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)

            async with AsyncSessionLocal() as db:
                # Create demo user
                demo = User(email="demo@stockpilot.io", full_name="Demo User",
                            password_hash=hash_password("demo1234"), role=UserRole.investor)
                db.add(demo)
                await db.flush()  # Get demo.id for FK references

                # Create stocks, holdings, trades, strategies, etc.
                stocks = [Stock(ticker="AAPL", name="Apple Inc.", sector="Technology"), ...]
                db.add_all(stocks)
                await db.commit()
    """)))
    story.append(Spacer(1, 8))
    story.append(body(
        "Populates the database with demo data for development. Run with "
        "<font face='Courier'>python seed.py</font> from the backend directory."
    ))
    story.append(Spacer(1, 6))
    story.append(body("<b>Data created:</b>"))
    story.append(bullet("1 demo user: demo@stockpilot.io / demo1234 (role: investor)"))
    story.append(bullet("3 analyst users: Sarah Chen, James Park, Alex Rivera"))
    story.append(bullet("10 stocks: AAPL, NVDA, MSFT, GOOGL, AMZN, TSLA, META, AMD, PLTR, COIN"))
    story.append(bullet("10 predictions with BUY/HOLD/SELL signals and confidence levels"))
    story.append(bullet("6 portfolio holdings with realistic cost basis and current prices"))
    story.append(bullet("4 watchlist entries: META, AMD, PLTR, COIN"))
    story.append(bullet("15 detailed trade journal entries with entry/exit prices and notes"))
    story.append(bullet("4 research-backed strategies with JSONB weight configurations (see §3.15)"))
    story.append(bullet("4 marketplace listings (all verified) with ratings and backtest metrics"))
    story.append(bullet("8 notifications of various kinds"))
    story.append(Spacer(1, 8))
    story.append(func_block("seed", "",
        "Async function that drops and recreates all tables, then populates with demo data in a single "
        "transaction. Uses <font face='Courier'>db.flush()</font> after each user creation to obtain the "
        "generated UUID for foreign key references."))
    story.append(why_box(
        "<b>Why drop and recreate?</b> The seeder uses <font face='Courier'>Base.metadata.drop_all</font> "
        "followed by <font face='Courier'>create_all</font> to ensure a clean slate. This prevents "
        "duplicate key errors when re-running the seeder and guarantees consistent demo data."
    ))

    # ── 3.15 Default Strategy Configurations ─────────────────────
    story.append(PageBreak())
    story.append(Paragraph("3.15  Default Strategy Configurations (Research-Backed)", styles["SectionHead"]))
    story.append(body(
        "StockPilot ships with 4 pre-configured strategies whose factor weights are grounded in "
        "peer-reviewed financial research. Each strategy emphasises a well-documented market anomaly "
        "while keeping the remaining factors as diversification anchors. Weights always sum to 100."
    ))
    story.append(Spacer(1, 10))

    # ── Momentum Premium ──
    story.append(Paragraph("Strategy 1 — Momentum Premium", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        weights = {"sentiment": 10, "momentum": 40, "valuation": 5,
                   "volatility": 10, "volume": 20, "growth": 15}
    """)))
    story.append(Spacer(1, 6))
    story.append(body(
        "<b>Academic basis:</b> Jegadeesh &amp; Titman (1993) 'Returns to Buying Winners and Selling "
        "Losers' demonstrated that stocks with strong 3-12 month returns continue to outperform, "
        "generating approximately 1% monthly abnormal returns. This cross-sectional momentum effect "
        "has been replicated across markets and asset classes (Asness, Moskowitz &amp; Pedersen 2013, "
        "'Value and Momentum Everywhere', <i>Journal of Finance</i>)."
    ))
    story.append(body(
        "<b>Volume at 20%:</b> Gervais, Kaniel &amp; Mingelgrin (2001) 'The High-Volume Return Premium' "
        "showed that high-volume stocks subsequently outperform low-volume stocks, and volume expansion "
        "confirms the conviction behind a momentum move. The Money Flow Index (MFI) component adds a "
        "price-volume confirmation layer."
    ))
    story.append(body(
        "<b>Weight rationale:</b> Momentum receives 40% as the primary alpha driver. Volume at 20% "
        "serves as momentum confirmation — strong moves on declining volume are unreliable. Growth at "
        "15% adds rate-of-change confirmation. Sentiment, volatility, and valuation are kept at 5-10% "
        "as weak negative screens."
    ))
    story.append(Spacer(1, 8))

    # ── Low-Volatility Alpha ──
    story.append(Paragraph("Strategy 2 — Low-Volatility Alpha", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        weights = {"sentiment": 5, "momentum": 15, "valuation": 20,
                   "volatility": 40, "volume": 10, "growth": 10}
    """)))
    story.append(Spacer(1, 6))
    story.append(body(
        "<b>Academic basis:</b> Ang, Hodrick, Xing &amp; Zhang (2006) 'The Cross-Section of Volatility "
        "and Expected Returns' (<i>Journal of Finance</i>) documented that high-volatility stocks earn "
        "anomalously low risk-adjusted returns. Baker, Bradley &amp; Wurgler (2011) 'Benchmarks as "
        "Limits to Arbitrage' confirmed this low-volatility anomaly persists because institutional "
        "mandates force managers to chase beta."
    ))
    story.append(body(
        "<b>Frazzini &amp; Pedersen (2014)</b> 'Betting Against Beta' (<i>Journal of Financial "
        "Economics</i>) formalised this into the BAB factor, showing that leveraged low-beta portfolios "
        "consistently beat high-beta portfolios across 20 countries and multiple asset classes."
    ))
    story.append(body(
        "<b>Weight rationale:</b> Volatility factor at 40% is the core — our volatility score is "
        "already inverted (high score = low volatility = safer stock). Valuation at 20% favours "
        "cheap, stable names over expensive, stable ones. Momentum at 15% avoids catching falling "
        "knives — low-vol stocks in downtrends are value traps."
    ))
    story.append(Spacer(1, 8))

    # ── Value-Sentiment Contrarian ──
    story.append(Paragraph("Strategy 3 — Value-Sentiment Contrarian", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        weights = {"sentiment": 25, "momentum": 10, "valuation": 35,
                   "volatility": 10, "volume": 5, "growth": 15}
    """)))
    story.append(Spacer(1, 6))
    story.append(body(
        "<b>Academic basis — Value:</b> Fama &amp; French (1992) 'The Cross-Section of Expected Stock "
        "Returns' (<i>Journal of Finance</i>) established that high book-to-market (value) stocks earn "
        "higher returns than growth stocks. Our valuation factor uses Bollinger Band position and "
        "price-to-SMA ratios as technical proxies for mean-reversion opportunity — stocks trading below "
        "their statistical fair value band."
    ))
    story.append(body(
        "<b>Academic basis — Sentiment:</b> Tetlock (2007) 'Giving Content to Investor Sentiment' "
        "(<i>Journal of Finance</i>) demonstrated that media pessimism predicts downward price pressure "
        "and higher subsequent returns for contrarian buyers. Loughran &amp; McDonald (2011) "
        "'When Is a Liability Not a Liability?' (<i>Journal of Finance</i>) further refined financial "
        "text analysis, which FinBERT builds upon."
    ))
    story.append(body(
        "<b>Weight rationale:</b> Valuation at 35% identifies statistically cheap stocks. Sentiment "
        "at 25% acts as a timing overlay — entering value positions when FinBERT detects improving "
        "sentiment on beaten-down names. Growth at 15% ensures the company has positive rate-of-change "
        "fundamentals (avoiding value traps). Momentum is kept at 10% as a weak trend filter."
    ))
    story.append(Spacer(1, 8))

    # ── Multi-Factor Balanced ──
    story.append(Paragraph("Strategy 4 — Multi-Factor Balanced (System Default)", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        weights = {"sentiment": 14, "momentum": 22, "valuation": 20,
                   "volatility": 18, "volume": 10, "growth": 16}
    """)))
    story.append(Spacer(1, 6))
    story.append(body(
        "<b>Academic basis:</b> Carhart (1997) 'On Persistence in Mutual Fund Performance' "
        "(<i>Journal of Finance</i>) extended the Fama-French three-factor model with a momentum "
        "factor, establishing the four-factor model as the standard benchmark for risk-adjusted "
        "returns. Asness, Moskowitz &amp; Pedersen (2013) 'Value and Momentum Everywhere' showed "
        "that value and momentum are negatively correlated, making their combination particularly "
        "effective at reducing drawdowns."
    ))
    story.append(body(
        "<b>Weight rationale:</b> Near-equal weighting across all 6 factors reduces the risk of any "
        "single factor entering a prolonged drawdown. Momentum receives a slight tilt (22%) given its "
        "historically strongest standalone Sharpe ratio. Valuation (20%) and volatility (18%) are the "
        "next-largest allocations, reflecting the robustness of value and low-vol premia. Growth (16%) "
        "and sentiment (14%) add complementary signals. Volume (10%) is the weakest standalone factor "
        "but provides useful confirmation."
    ))
    story.append(body(
        "This is the <b>system default</b> strategy — when a user calls the analysis API without "
        "specifying custom weights, these values are applied. It is also the only <b>is_preset=True</b> "
        "strategy (no owner), meaning it appears as a system-provided option in the UI."
    ))
    story.append(Spacer(1, 10))

    # ── Weight summary table ──
    story.append(Paragraph("Weight Summary Table", styles["SubSection"]))
    weight_table_data = [
        ["Factor", "Momentum\nPremium", "Low-Vol\nAlpha", "Value-Sentiment\nContrarian", "Multi-Factor\nBalanced"],
        ["Sentiment",  "10", " 5", "25", "14"],
        ["Momentum",   "40", "15", "10", "22"],
        ["Valuation",  " 5", "20", "35", "20"],
        ["Volatility", "10", "40", "10", "18"],
        ["Volume",     "20", "10", " 5", "10"],
        ["Growth",     "15", "10", "15", "16"],
        ["Total",      "100", "100", "100", "100"],
    ]
    wt = Table(weight_table_data, colWidths=[90, 80, 80, 100, 90], repeatRows=1)
    wt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#d4a853")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#333333")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, -1), (-1, -1), colors.HexColor("#d4a853")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.HexColor("#0d0d1a"), colors.HexColor("#12121f")]),
        ("TEXTCOLOR", (0, 1), (-1, -2), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(wt)
    story.append(Spacer(1, 10))

    # ── Academic references ──
    story.append(Paragraph("Academic References", styles["SubSection"]))
    refs = [
        "Ang, A., Hodrick, R.J., Xing, Y. &amp; Zhang, X. (2006). 'The Cross-Section of Volatility and "
        "Expected Returns.' <i>Journal of Finance</i>, 61(1), 259-299.",

        "Asness, C.S., Moskowitz, T.J. &amp; Pedersen, L.H. (2013). 'Value and Momentum Everywhere.' "
        "<i>Journal of Finance</i>, 68(3), 929-985.",

        "Baker, M., Bradley, B. &amp; Wurgler, J. (2011). 'Benchmarks as Limits to Arbitrage: "
        "Understanding the Low-Volatility Anomaly.' <i>Financial Analysts Journal</i>, 67(1), 40-54.",

        "Carhart, M.M. (1997). 'On Persistence in Mutual Fund Performance.' <i>Journal of Finance</i>, "
        "52(1), 57-82.",

        "Fama, E.F. &amp; French, K.R. (1992). 'The Cross-Section of Expected Stock Returns.' "
        "<i>Journal of Finance</i>, 47(2), 427-465.",

        "Frazzini, A. &amp; Pedersen, L.H. (2014). 'Betting Against Beta.' <i>Journal of Financial "
        "Economics</i>, 111(1), 1-25.",

        "Gervais, S., Kaniel, R. &amp; Mingelgrin, D.H. (2001). 'The High-Volume Return Premium.' "
        "<i>Journal of Finance</i>, 56(3), 877-919.",

        "Jegadeesh, N. &amp; Titman, S. (1993). 'Returns to Buying Winners and Selling Losers: "
        "Implications for Stock Market Efficiency.' <i>Journal of Finance</i>, 48(1), 65-91.",

        "Loughran, T. &amp; McDonald, B. (2011). 'When Is a Liability Not a Liability? Textual Analysis, "
        "Dictionaries, and 10-Ks.' <i>Journal of Finance</i>, 66(1), 35-65.",

        "Tetlock, P.C. (2007). 'Giving Content to Investor Sentiment: The Role of Media in the Stock "
        "Market.' <i>Journal of Finance</i>, 62(3), 1139-1168.",
    ]
    for i, ref in enumerate(refs, 1):
        story.append(Paragraph(f"[{i}] {ref}", styles["BodyIndent"]))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 10))
    story.append(why_box(
        "<b>Why these specific weights?</b> Each strategy is designed around a single dominant factor "
        "(35-40%) that captures a well-documented anomaly, with secondary factors (15-25%) providing "
        "confirmation or risk management, and tertiary factors (5-10%) as weak screens. The Multi-Factor "
        "Balanced strategy uses near-equal weights because Asness et al. (2013) showed that diversified "
        "factor exposure reduces maximum drawdown by 30-40% compared to single-factor strategies."
    ))

    # ══════════════════════════════════════════════════════════════
    # APPENDIX A — Dependency List
    # ══════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("Appendix A — Python Dependencies", styles["SectionHead"]))
    story.append(hr())
    story.append(body(
        "All dependencies are managed via <font face='Courier'>uv</font> (a fast Rust-based Python package manager) "
        "and declared in <font face='Courier'>pyproject.toml</font>."
    ))
    story.append(code_block(textwrap.dedent("""\
        [project]
        name = "stockpilot-backend"
        requires-python = ">=3.10"
        dependencies = [
            "fastapi>=0.103.0",
            "uvicorn[standard]>=0.23.0",
            "sqlalchemy>=2.0.51",
            "asyncpg>=0.31.0",
            "xgboost>=2.0.0",
            "transformers>=5.14.0",
            "torch>=2.13.0",
            "yfinance>=0.2.0",
            "ta>=0.9.0",
            # ... plus pydantic, passlib, python-jose, etc.
        ]
    """)))
    story.append(Spacer(1, 8))
    story.append(body("<b>Core dependencies explained:</b>"))

    deps_detail = [
        ("fastapi >= 0.103.0", "Async web framework. Provides automatic OpenAPI docs, dependency injection, and Pydantic integration."),
        ("uvicorn[standard] >= 0.23.0", "ASGI server that runs the FastAPI app. The [standard] extra includes uvloop (fast event loop) and httptools (fast HTTP parsing)."),
        ("sqlalchemy >= 2.0.51", "ORM with native async support. DeclarativeBase models map Python classes to PostgreSQL tables."),
        ("asyncpg >= 0.31.0", "Pure-async PostgreSQL driver written in Cython. 3-5x faster than psycopg2."),
        ("pydantic >= 2.0.0", "Data validation library. v2 is rewritten in Rust for 5-50x speed improvement."),
        ("pydantic-settings >= 2.14.2", "Loads configuration from environment variables with type validation."),
        ("python-jose[cryptography] >= 3.5.0", "JWT creation and verification. The [cryptography] extra provides faster C-based algorithms."),
        ("passlib[bcrypt] >= 1.7.4", "Password hashing library. The [bcrypt] extra adds the bcrypt backend."),
        ("yfinance >= 0.2.0", "Yahoo Finance API wrapper for stock data, quotes, and news headlines."),
        ("xgboost >= 2.0.0", "Gradient boosted decision tree library for next-day price direction prediction."),
        ("scikit-learn >= 1.3.0", "ML utilities: TimeSeriesSplit, accuracy_score, classification_report, confusion_matrix."),
        ("ta >= 0.9.0", "Technical analysis library. Provides RSI, MACD, Bollinger Bands, ATR, MFI, OBV."),
        ("pandas >= 2.0.0", "DataFrame library for time-series data manipulation, rolling windows, resampling."),
        ("numpy >= 1.24.0", "Vectorised math for Sharpe ratios, drawdowns, equity curves."),
        ("transformers >= 5.14.0", "HuggingFace Transformers library. Loads FinBERT (ProsusAI/finbert) for sentiment analysis."),
        ("torch >= 2.13.0", "PyTorch backend for FinBERT transformer inference."),
        ("python-multipart >= 0.0.6", "Required by FastAPI for file upload (multipart/form-data) support."),
        ("email-validator >= 2.3.0", "Validates email format in Pydantic EmailStr fields."),
        ("joblib >= 1.3.0", "Serialisation library for saving/loading XGBoost model bundles."),
    ]
    for dep, desc in deps_detail:
        story.append(Paragraph(f"<b><font face='Courier'>{dep}</font></b>", styles["BodyIndent"]))
        story.append(body_i(desc))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX B — API Endpoint Reference (all routes)
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Appendix B — Complete API Endpoint Reference", styles["SectionHead"]))
    story.append(hr())
    story.append(body(
        "Comprehensive table of all API endpoints with their HTTP methods, authentication requirements, "
        "and request/response types."
    ))
    story.append(Spacer(1, 8))

    all_endpoints = [
        ["Method", "Path", "Auth", "Request Body", "Response"],
        ["POST", "/api/v1/auth/login", "No", "LoginRequest", "TokenResponse"],
        ["POST", "/api/v1/auth/register", "No", "RegisterRequest", "TokenResponse"],
        ["POST", "/api/v1/auth/refresh", "No", "RefreshRequest", "TokenResponse"],
        ["GET", "/api/v1/users/me", "Yes", "-", "UserOut"],
        ["PUT", "/api/v1/users/me", "Yes", "UserUpdate", "UserOut"],
        ["PUT", "/api/v1/users/me/password", "Yes", "PasswordUpdate", "message"],
        ["POST", "/api/v1/users/me/avatar", "Yes", "file (multipart)", "UserOut"],
        ["DELETE", "/api/v1/users/me/avatar", "Yes", "-", "UserOut"],
        ["GET", "/api/v1/stocks", "No", "-", "list[StockOut]"],
        ["GET", "/api/v1/stocks/{ticker}", "No", "-", "StockOut"],
        ["GET", "/api/v1/stocks/{ticker}/history", "No", "-", "list[PriceHistoryOut]"],
        ["GET", "/api/v1/predictions", "Yes", "-", "list[PredictionOut]"],
        ["GET", "/api/v1/predictions/{ticker}", "Yes", "-", "PredictionOut"],
        ["GET", "/api/v1/portfolio", "Yes", "-", "list[HoldingOut]"],
        ["POST", "/api/v1/portfolio", "Yes", "HoldingCreate", "HoldingOut"],
        ["PUT", "/api/v1/portfolio/{id}", "Yes", "HoldingUpdate", "HoldingOut"],
        ["DELETE", "/api/v1/portfolio/{id}", "Yes", "-", "204"],
        ["GET", "/api/v1/watchlist", "Yes", "-", "list[WatchlistOut]"],
        ["POST", "/api/v1/watchlist", "Yes", "WatchlistAdd", "WatchlistOut"],
        ["DELETE", "/api/v1/watchlist/{ticker}", "Yes", "-", "204"],
        ["GET", "/api/v1/trades", "Yes", "-", "list[TradeOut]"],
        ["POST", "/api/v1/trades", "Yes", "TradeCreate", "TradeOut"],
        ["DELETE", "/api/v1/trades/{id}", "Yes", "-", "204"],
        ["GET", "/api/v1/strategies", "Yes", "-", "list[StrategyOut]"],
        ["POST", "/api/v1/strategies", "Yes", "StrategyCreate", "StrategyOut"],
        ["PUT", "/api/v1/strategies/{id}", "Yes", "StrategyUpdate", "StrategyOut"],
        ["DELETE", "/api/v1/strategies/{id}", "Yes", "-", "204"],
        ["GET", "/api/v1/notifications", "Yes", "-", "list[NotificationOut]"],
        ["PUT", "/api/v1/notifications/{id}/read", "Yes", "-", "NotificationOut"],
        ["PUT", "/api/v1/notifications/read-all", "Yes", "-", "message"],
        ["GET", "/api/v1/marketplace", "No", "-", "list[MarketplaceListingOut]"],
        ["GET", "/api/v1/live/market-status", "No", "-", "MarketStatusResponse"],
        ["GET", "/api/v1/live/quote/{ticker}", "No", "-", "QuoteResponse"],
        ["GET", "/api/v1/live/intraday/{ticker}", "No", "-", "list[IntradayPoint]"],
        ["GET", "/api/v1/live/chart/{ticker}", "No", "-", "list[ChartPoint]"],
        ["GET", "/api/v1/analysis/factors/{ticker}", "No", "-", "FactorAnalysisResponse"],
        ["GET", "/api/v1/analysis/backtest/{ticker}", "No", "-", "BacktestMetrics"],
        ["GET", "/api/v1/analysis/bull-bear/{ticker}", "No", "-", "BullBearResponse"],
        ["GET", "/api/v1/analysis/fundamentals/{ticker}", "No", "-", "FundamentalsResponse"],
        ["GET", "/api/v1/sentiment/{ticker}", "No", "-", "SentimentResponse"],
        ["GET", "/api/v1/dashboard/indices", "No", "-", "list[IndexData]"],
        ["GET", "/api/v1/dashboard/sectors", "Yes", "-", "list[SectorData]"],
        ["GET", "/api/v1/dashboard/history", "Yes", "-", "list[HistoryPoint]"],
    ]

    ep_table = Table(all_endpoints, colWidths=[0.6 * inch, 2.4 * inch, 0.5 * inch, 1.2 * inch, 1.5 * inch])
    ep_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("FONTNAME", (1, 1), (1, -1), "Courier"),
        ("FONTNAME", (3, 1), (4, -1), "Courier"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(ep_table)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX C — Technical Indicators Reference
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Appendix C — Technical Indicators Reference", styles["SectionHead"]))
    story.append(hr())
    story.append(body(
        "Complete reference of all 30+ technical indicators computed by the FeatureEngine, "
        "their formulas, and what they measure."
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Moving Averages", styles["SubSection"]))
    story.append(body(
        "<b>Simple Moving Average (SMA):</b> The arithmetic mean of the last N closing prices. "
        "SMA_20 = (Close_1 + Close_2 + ... + Close_20) / 20. Smooths noise but responds slowly to price changes."
    ))
    story.append(body(
        "<b>Exponential Moving Average (EMA):</b> Weighted average that gives more importance to recent prices. "
        "Uses a smoothing factor: multiplier = 2 / (N + 1). EMA_today = Close * multiplier + EMA_yesterday * (1 - multiplier). "
        "More responsive to recent price changes than SMA."
    ))
    story.append(body(
        "<b>Periods used:</b> 5, 10, 20, 50 days. Short-term (5/10) for recent momentum, "
        "medium-term (20) as the standard trading benchmark, long-term (50) for trend direction."
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("RSI (Relative Strength Index)", styles["SubSection"]))
    story.append(body(
        "<b>Formula:</b> RSI = 100 - (100 / (1 + RS)), where RS = average gain / average loss over 14 periods."
    ))
    story.append(body(
        "<b>Interpretation:</b> RSI > 70 indicates overbought conditions (price may pull back). "
        "RSI < 30 indicates oversold conditions (price may bounce). The model uses RSI as a continuous "
        "feature rather than just threshold crossings, capturing the full momentum spectrum."
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("MACD (Moving Average Convergence Divergence)", styles["SubSection"]))
    story.append(body(
        "<b>Components:</b><br/>"
        "&bull; MACD Line = EMA_12 - EMA_26 (difference between short and long-term EMAs)<br/>"
        "&bull; Signal Line = EMA_9 of MACD Line (smoothed version of MACD)<br/>"
        "&bull; Histogram = MACD - Signal (positive = bullish momentum, negative = bearish)"
    ))
    story.append(body(
        "<b>Why these specific periods (12, 26, 9)?</b> These are the original parameters chosen by Gerald "
        "Appel in the 1970s based on trading weeks (12 = half month, 26 = full month, 9 = ~2 weeks). "
        "They remain the industry standard used by Bloomberg, TradingView, and all major platforms."
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Bollinger Bands", styles["SubSection"]))
    story.append(body(
        "<b>Components:</b><br/>"
        "&bull; Middle Band = SMA_20<br/>"
        "&bull; Upper Band = SMA_20 + 2 x standard_deviation_20<br/>"
        "&bull; Lower Band = SMA_20 - 2 x standard_deviation_20<br/>"
        "&bull; BB_Width = (Upper - Lower) / Middle (measures volatility expansion/contraction)<br/>"
        "&bull; BB_Position = (Close - Lower) / (Upper - Lower) (0 = at lower band, 1 = at upper)"
    ))
    story.append(body(
        "<b>Statistical basis:</b> In a normal distribution, 95.4% of data falls within 2 standard deviations. "
        "Prices trading outside the bands are statistically unusual and often revert. BB_Width expanding "
        "signals increasing volatility (breakout potential); contracting signals consolidation."
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Volume Indicators", styles["SubSection"]))
    story.append(body(
        "<b>VWAP (Volume Weighted Average Price):</b> "
        "sum(close_i x volume_i) / sum(volume_i) over 20 days. Shows the average price weighted by "
        "trading volume. Institutional traders often use VWAP as a benchmark — price above VWAP suggests "
        "buyers are paying above average."
    ))
    story.append(body(
        "<b>OBV (On-Balance Volume):</b> Cumulative volume counter. On up days, add the day's volume; "
        "on down days, subtract it. Rising OBV with rising price confirms the trend. Rising OBV with "
        "flat price suggests accumulation (smart money buying before price moves up)."
    ))
    story.append(body(
        "<b>MFI (Money Flow Index):</b> RSI applied to volume-weighted price data. Measures buying and "
        "selling pressure. MFI > 80 = overbought, MFI < 20 = oversold. More reliable than RSI alone "
        "because it incorporates volume data."
    ))
    story.append(body(
        "<b>Volume Ratio:</b> Today's volume / 20-day average volume. Values > 1.5 indicate unusual "
        "activity (potential institutional buying/selling). Volume spikes often precede significant price moves."
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Volatility Indicators", styles["SubSection"]))
    story.append(body(
        "<b>ATR (Average True Range):</b> 14-day average of True Range, where "
        "True Range = max(High - Low, |High - PreviousClose|, |Low - PreviousClose|). "
        "Measures the average daily price range. Used for stop-loss placement — a 2x ATR stop "
        "accounts for normal daily fluctuations."
    ))
    story.append(body(
        "<b>Volatility_20:</b> 20-day rolling standard deviation of daily percentage returns. "
        "Annualised by multiplying by sqrt(252). Values above 40% indicate high volatility stocks."
    ))
    story.append(body(
        "<b>High_Low_Ratio:</b> (High - Low) / Open. Measures intraday price range as a percentage "
        "of the opening price. Wide-range days (> 3%) often signal trend continuation."
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Price Position Indicators", styles["SubSection"]))
    story.append(body(
        "<b>Price_Position:</b> (Close - 20-day Low) / (20-day High - 20-day Low). "
        "Normalises the price to a 0-1 scale within its recent range. Values near 1 = trading near "
        "recent highs (momentum). Values near 0 = trading near recent lows (potential value)."
    ))
    story.append(body(
        "<b>ROC_10 (Rate of Change):</b> (Close - Close_10_days_ago) / Close_10_days_ago x 100. "
        "Direct measure of momentum in percentage terms."
    ))
    story.append(body(
        "<b>Price_to_SMA_20 and Price_to_SMA_50:</b> Close / SMA ratios. Values > 1 mean price is "
        "above its moving average (bullish trend). Values < 1 mean price is below (bearish)."
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX D — Authentication Flow Diagram
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Appendix D — Authentication and Request Flow", styles["SectionHead"]))
    story.append(hr())
    story.append(body("<b>Login Flow:</b>"))
    story.append(code_block(textwrap.dedent("""\
        Client                          Backend
          |                                |
          |-- POST /api/v1/auth/login ---->|
          |   {email, password}            |
          |                                |-- Lookup user by email
          |                                |-- Verify bcrypt hash
          |                                |-- Generate access JWT (120 min)
          |                                |-- Generate refresh JWT (7 days)
          |<-- TokenResponse --------------|
          |   {access_token, refresh_token}|
          |                                |
          |-- Store tokens in localStorage |
    """)))
    story.append(Spacer(1, 8))

    story.append(body("<b>Authenticated Request Flow:</b>"))
    story.append(code_block(textwrap.dedent("""\
        Client                          Backend
          |                                |
          |-- GET /api/v1/portfolio ------->|
          |   Authorization: Bearer <JWT>  |
          |                                |-- get_current_user dependency:
          |                                |   1. Extract token from header
          |                                |   2. Decode JWT (verify signature + expiry)
          |                                |   3. Extract user_id from 'sub' claim
          |                                |   4. SELECT user FROM users WHERE id = user_id
          |                                |   5. Return User object or 401
          |                                |
          |                                |-- Endpoint function runs with user object
          |                                |-- get_db dependency:
          |                                |   1. Create AsyncSession
          |                                |   2. Yield to endpoint
          |                                |   3. Commit on success / Rollback on error
          |                                |
          |<-- Response -------------------|
    """)))
    story.append(Spacer(1, 8))

    story.append(body("<b>Token Refresh Flow:</b>"))
    story.append(code_block(textwrap.dedent("""\
        Client                          Backend
          |                                |
          |-- API call returns 401 ------->|
          |                                |
          |-- POST /api/v1/auth/refresh -->|
          |   {refresh_token}              |
          |                                |-- Decode refresh JWT
          |                                |-- Verify type == 'refresh'
          |                                |-- Lookup user by sub claim
          |                                |-- Generate new token pair
          |<-- New TokenResponse ----------|
          |                                |
          |-- Retry original request ----->|
          |   with new access_token        |
    """)))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX E — XGBoost Model Architecture
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Appendix E — XGBoost Model Architecture Details", styles["SectionHead"]))
    story.append(hr())

    story.append(Paragraph("What is Gradient Boosting?", styles["SubSection"]))
    story.append(body(
        "Gradient boosting is an ensemble learning technique that builds a strong classifier from many "
        "weak classifiers (shallow decision trees). The key idea:"
    ))
    story.append(bullet("Start with a simple prediction (e.g., always predict the majority class)"))
    story.append(bullet("Compute the residual errors (how wrong was the prediction?)"))
    story.append(bullet("Train a new tree to predict these residuals"))
    story.append(bullet("Add the new tree to the ensemble with a small weight (learning_rate)"))
    story.append(bullet("Repeat until validation loss stops improving (early stopping)"))
    story.append(Spacer(1, 6))
    story.append(body(
        "XGBoost ('Extreme Gradient Boosting') adds several enhancements: (1) regularisation terms "
        "(reg_alpha L1, reg_lambda L2) that penalise complex trees, (2) column subsampling per tree "
        "(colsample_bytree=0.8 means each tree sees only 80% of features), (3) Newton's method for "
        "optimisation (uses second-order gradients for faster convergence)."
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Hyperparameter Choices Explained", styles["SubSection"]))
    hyper_table = Table([
        ["Parameter", "Value", "Reasoning"],
        ["n_estimators", "300", "Ceiling, not target. Early stopping typically halts at 80-150 trees."],
        ["max_depth", "4", "Shallow trees prevent overfitting. Deeper trees memorise noise."],
        ["learning_rate", "0.01", "Small steps = more trees needed but better generalisation."],
        ["subsample", "0.8", "Each tree trains on 80% of rows. Random forest-like variance reduction."],
        ["colsample_bytree", "0.8", "Each tree sees 80% of features. Reduces feature correlation between trees."],
        ["min_child_weight", "10", "Minimum samples in a leaf. Higher = more conservative splits."],
        ["scale_pos_weight", "auto", "Set to neg/pos ratio. Handles class imbalance (more UP days than DOWN)."],
        ["early_stopping", "100", "Stop if validation logloss hasn't improved in 100 rounds."],
    ], colWidths=[1.4 * inch, 0.7 * inch, 4 * inch])
    hyper_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 1), (0, -1), "Courier"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(hyper_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Model Persistence and Version Safety", styles["SubSection"]))
    story.append(body(
        "The trained model is saved as a joblib bundle containing:"
    ))
    story.append(bullet("<b>model</b> — The trained XGBClassifier object"))
    story.append(bullet("<b>feature_columns</b> — List of 30+ feature names the model was trained on"))
    story.append(bullet("<b>config</b> — PredictorConfig as a dict (hyperparameters and thresholds)"))
    story.append(bullet("<b>versions</b> — Library versions: xgboost, sklearn, pandas, numpy"))
    story.append(Spacer(1, 4))
    story.append(body(
        "On load, the system compares stored library versions with runtime versions. If XGBoost or "
        "scikit-learn versions have drifted, it logs a warning (or raises an error in strict mode). "
        "This prevents silent model corruption from library API changes."
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Feature Importance and Explainability", styles["SubSection"]))
    story.append(body(
        "XGBoost tracks how much each feature contributed to reducing the loss function (measured by "
        "'gain' — the average reduction in the objective function when a feature is used in a split). "
        "The <font face='Courier'>feature_importance(top_k=15)</font> method returns the top features, "
        "mapping internal names (f0, f1, ...) back to human-readable names (RSI_14, MACD_Histogram, etc.)."
    ))
    story.append(body(
        "This is a key advantage over neural networks: users can see <i>why</i> the model predicts BUY — "
        "for example, 'RSI-14 and MACD histogram were the dominant factors, suggesting strong momentum.' "
        "This builds trust in the predictions and helps users make informed decisions."
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX F — FinBERT Architecture Details
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Appendix F — FinBERT Architecture Details", styles["SectionHead"]))
    story.append(hr())

    story.append(Paragraph("BERT Architecture", styles["SubSection"]))
    story.append(body(
        "FinBERT is based on Google's BERT (Bidirectional Encoder Representations from Transformers). "
        "Key architectural components:"
    ))
    story.append(bullet("<b>12 transformer layers</b> — each containing self-attention and feed-forward networks"))
    story.append(bullet("<b>768-dimensional hidden size</b> — each token is represented as a 768-number vector"))
    story.append(bullet("<b>12 attention heads</b> — multiple parallel attention patterns per layer"))
    story.append(bullet("<b>~110 million parameters</b> — trained on financial corpora"))
    story.append(bullet("<b>30,522 WordPiece vocabulary</b> — subword tokenisation for handling rare words"))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Self-Attention Mechanism", styles["SubSection"]))
    story.append(body(
        "The core innovation of transformers. For each word, self-attention computes how much to "
        "attend to every other word in the sentence. This captures long-range dependencies that "
        "RNNs and LSTMs struggle with."
    ))
    story.append(body(
        "<b>Example:</b> In 'Apple beats Q3 expectations despite supply chain concerns', "
        "self-attention connects 'beats' with 'expectations' (positive context) and 'despite' "
        "with 'concerns' (negative but secondary). The model learns that the primary clause "
        "('beats expectations') dominates the overall sentiment."
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Fine-Tuning for Finance", styles["SubSection"]))
    story.append(body(
        "FinBERT was fine-tuned on 50,000+ financial texts including:"
    ))
    story.append(bullet("Reuters and Bloomberg news articles"))
    story.append(bullet("Earnings call transcripts"))
    story.append(bullet("SEC filing summaries"))
    story.append(bullet("Analyst reports"))
    story.append(Spacer(1, 4))
    story.append(body(
        "This financial domain fine-tuning is critical. General-purpose BERT would classify "
        "'short interest increased 40%' as neutral (just numbers), while FinBERT correctly identifies "
        "it as bearish. Similarly, 'guidance raised' is meaningless to general BERT but FinBERT "
        "understands it's a strong positive signal in financial context."
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Lazy Loading and Memory Management", styles["SubSection"]))
    story.append(body(
        "FinBERT's model weights are approximately <b>420 MB</b>. To avoid delaying server startup, "
        "the model is loaded lazily — only when the first sentiment API call is made:"
    ))
    story.append(code_block(textwrap.dedent("""\
        _pipeline = None   # Module-level cache

        def _get_pipeline():
            global _pipeline
            if _pipeline is None:
                # First call: downloads model from HuggingFace (~420 MB)
                # Takes 5-15 seconds depending on network/disk
                _pipeline = pipeline(
                    "sentiment-analysis",
                    model="ProsusAI/finbert",
                    truncation=True,
                    max_length=512,
                    top_k=None,         # Return all 3 class probabilities
                )
            return _pipeline
    """)))
    story.append(body(
        "After the first load, the model stays in memory and subsequent calls are fast (~50ms per headline). "
        "The model is run in a <font face='Courier'>ThreadPoolExecutor</font> (2 workers) to avoid blocking "
        "the async event loop, since transformer inference is CPU-intensive."
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX G — Database Migration and Maintenance
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Appendix G — Database Operations Guide", styles["SectionHead"]))
    story.append(hr())

    story.append(Paragraph("Schema Creation", styles["SubSection"]))
    story.append(body(
        "Tables are created automatically on server startup via the lifespan context manager:"
    ))
    story.append(code_block(textwrap.dedent("""\
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            yield
    """)))
    story.append(body(
        "<font face='Courier'>create_all</font> is idempotent — it creates tables that don't exist and "
        "skips tables that already exist. This means the server can restart safely without data loss."
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Connection Pool Configuration", styles["SubSection"]))
    story.append(body(
        "The async engine is configured with connection pooling for optimal performance:"
    ))
    story.append(bullet("<b>pool_pre_ping=True</b> — Tests connections before use. Prevents 'connection closed' errors after PostgreSQL restarts."))
    story.append(bullet("<b>pool_size=10</b> — Maintains 10 persistent connections. Avoids the overhead of creating new connections per request."))
    story.append(bullet("<b>max_overflow=20</b> — Allows up to 20 additional connections during traffic spikes. Total maximum: 30 concurrent connections."))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Seeding for Development", styles["SubSection"]))
    story.append(body(
        "The seeder (<font face='Courier'>python seed.py</font>) provides a complete demo environment:"
    ))
    story.append(bullet("Drops all tables and recreates them (clean slate)"))
    story.append(bullet("Creates 4 users (1 demo + 3 analysts) with bcrypt-hashed passwords"))
    story.append(bullet("Populates 10 stocks, 10 predictions, 6 holdings, 4 watchlist items"))
    story.append(bullet("Generates 15 realistic trade journal entries with notes"))
    story.append(bullet("Creates 4 research-backed strategies with JSONB weights and marketplace listings"))
    story.append(bullet("Adds 8 notifications across different types"))
    story.append(body(
        "The demo account credentials are: <font face='Courier'>demo@stockpilot.io / demo1234</font>"
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Transaction Safety", styles["SubSection"]))
    story.append(body(
        "Every API endpoint runs inside a database transaction managed by the <font face='Courier'>get_db</font> "
        "dependency. The transaction lifecycle:"
    ))
    story.append(code_block(textwrap.dedent("""\
        async def get_db():
            async with AsyncSessionLocal() as session:
                try:
                    yield session           # Endpoint runs here
                    await session.commit()  # Success: persist all changes
                except Exception:
                    await session.rollback() # Failure: undo everything
                    raise
    """)))
    story.append(body(
        "This means if an endpoint creates a holding but then crashes while fetching the live price, "
        "the holding is <b>not</b> saved to the database. The user never sees partial data."
    ))

    # ══════════════════════════════════════════════════════════════
    # APPENDIX H — Error Handling Patterns
    # ══════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("Appendix H — Error Handling Patterns", styles["SectionHead"]))
    story.append(hr())

    story.append(Paragraph("HTTP Status Codes Used", styles["SubSection"]))
    status_table = Table([
        ["Code", "Meaning", "When Used"],
        ["200", "OK", "Successful GET, PUT requests returning data"],
        ["201", "Created", "Successful POST creating a new resource (holding, trade, etc.)"],
        ["204", "No Content", "Successful DELETE (no body returned)"],
        ["400", "Bad Request", "Invalid input format, business logic violations"],
        ["401", "Unauthorized", "Missing/invalid/expired JWT token"],
        ["404", "Not Found", "Resource does not exist or not owned by user"],
        ["409", "Conflict", "Duplicate resource (e.g., duplicate watchlist entry)"],
        ["422", "Unprocessable", "Pydantic validation failure (auto-generated by FastAPI)"],
        ["500", "Server Error", "Unhandled exceptions (should not occur in normal operation)"],
    ], colWidths=[0.6 * inch, 1.2 * inch, 4.2 * inch])
    status_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(status_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Owner Scoping Pattern", styles["SubSection"]))
    story.append(body(
        "All user-owned resources (holdings, trades, watchlist, strategies, notifications) are scoped to the "
        "authenticated user. The pattern used throughout:"
    ))
    story.append(code_block(textwrap.dedent("""\
        # Every query filters by the authenticated user's ID
        result = await db.execute(
            select(Holding).where(
                Holding.id == holding_id,
                Holding.user_id == user.id  # Owner scoping
            )
        )
        holding = result.scalar_one_or_none()
        if not holding:
            raise HTTPException(404, "Holding not found")
    """)))
    story.append(body(
        "This prevents users from accessing or modifying other users' data. Even if a user guesses "
        "another user's holding UUID, the query returns nothing because the user_id filter doesn't match."
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Safe Type Conversion (yfinance data)", styles["SubSection"]))
    story.append(body(
        "yfinance returns data from Yahoo Finance's API, which sometimes has missing values, wrong types, "
        "or unexpected formats. The codebase uses safe conversion helpers:"
    ))
    story.append(code_block(textwrap.dedent("""\
        def _safe_float(val):
            '''Convert to float, return None on failure.'''
            try:
                return float(val)
            except (TypeError, ValueError):
                return None

        def _safe_int(val):
            '''Convert to int, return None on failure.'''
            try:
                return int(val)
            except (TypeError, ValueError):
                return None
    """)))
    story.append(body(
        "These are used for every yfinance data point: prices, volume, market cap, P/E ratios. "
        "Without them, a single missing field from Yahoo would crash the entire API response."
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX I — CORS and Security Configuration
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Appendix I — CORS and Security Configuration", styles["SectionHead"]))
    story.append(hr())

    story.append(Paragraph("CORS (Cross-Origin Resource Sharing)", styles["SubSection"]))
    story.append(body(
        "The React frontend runs on <font face='Courier'>http://localhost:5173</font> while the API runs on "
        "<font face='Courier'>http://localhost:8000</font>. Browsers block cross-origin requests by default "
        "as a security measure. CORS middleware tells the browser which origins are allowed:"
    ))
    story.append(code_block(textwrap.dedent("""\
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],     # All origins (restrict in production)
            allow_credentials=True,  # Allow cookies (not used, but enabled)
            allow_methods=["*"],     # All HTTP methods
            allow_headers=["*"],     # All headers (including Authorization)
        )
    """)))
    story.append(why_box(
        "<b>Production hardening:</b> In production, <font face='Courier'>allow_origins</font> should be "
        "restricted to the actual frontend domain (e.g., <font face='Courier'>https://stockpilot.com</font>). "
        "The wildcard is used in development for convenience."
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("JWT Security Properties", styles["SubSection"]))
    story.append(body("<b>What JWTs protect against:</b>"))
    story.append(bullet("Tampering — The HS256 signature ensures the token hasn't been modified"))
    story.append(bullet("Expiry — The exp claim is checked on every request; expired tokens are rejected"))
    story.append(bullet("Token type confusion — Access and refresh tokens have a type field preventing misuse"))
    story.append(Spacer(1, 4))
    story.append(body("<b>What JWTs do NOT protect against:</b>"))
    story.append(bullet("Token theft — If someone steals the JWT, they can use it until expiry (120 min)"))
    story.append(bullet("XSS — JavaScript running on the page can read localStorage tokens"))
    story.append(Spacer(1, 4))
    story.append(body(
        "<b>Mitigation:</b> Short access token TTL (120 min) limits the exploitation window. "
        "In a production deployment, consider httpOnly cookies for token storage (prevents XSS access) "
        "and CSRF tokens for state-changing requests."
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("File Upload Security", styles["SubSection"]))
    story.append(body(
        "The avatar upload endpoint validates uploads before saving:"
    ))
    story.append(bullet("<b>Content type check:</b> Only image/jpeg, image/png, image/webp allowed"))
    story.append(bullet("<b>Size limit:</b> Maximum 2 MB (prevents denial of service via large uploads)"))
    story.append(bullet("<b>Filename sanitisation:</b> Saved as {user_uuid}.{ext}, not the original filename"))
    story.append(body(
        "Using the user's UUID as the filename prevents: directory traversal attacks "
        "(../../etc/passwd), filename collisions, and encoding issues with unicode filenames."
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX J — Backtesting Metrics Explained
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Appendix J — Backtesting Metrics Explained", styles["SectionHead"]))
    story.append(hr())
    story.append(body(
        "Detailed explanation of each metric computed by the backtest engine."
    ))
    story.append(Spacer(1, 6))

    metrics_detail = [
        ("Total Return (%)",
         "The percentage gain/loss of the strategy over the test period. Calculated as: "
         "(final_equity / initial_equity - 1) x 100. For example, +23.5% means $10,000 became $12,350."),
        ("Buy-and-Hold Return (%)",
         "What you would have earned by simply buying the stock at the start and holding until the end. "
         "This is the benchmark — the strategy should outperform buy-and-hold to be useful."),
        ("Edge vs Hold (%)",
         "Total Return minus Buy-and-Hold Return. Positive values mean the strategy added alpha "
         "(outperformed passive investing). Negative values mean it was worse than doing nothing."),
        ("Win Rate",
         "Percentage of trades that were profitable. Calculated as: winning_trades / total_trades. "
         "A win rate above 50% is not strictly necessary if winning trades are larger than losing trades."),
        ("Sharpe Ratio",
         "Risk-adjusted return. Formula: sqrt(252) x mean(daily_returns) / std(daily_returns). "
         "Annualised using 252 trading days. Interpretation: < 1.0 poor, 1.0-2.0 good, > 2.0 excellent. "
         "Accounts for the fact that a volatile 20% return is less attractive than a stable 20% return."),
        ("Max Drawdown (%)",
         "Largest peak-to-trough decline during the test period. Formula: "
         "max(1 - equity[t] / max(equity[0:t])) x 100. A 15% drawdown means the portfolio lost 15% from "
         "its highest point before recovering. Important for understanding worst-case scenarios."),
        ("Profit Factor",
         "Gross profits divided by gross losses. A profit factor of 1.5 means for every $1 lost, $1.50 was "
         "gained. Values > 1.0 indicate net profitability. Values < 1.0 mean the strategy loses money."),
        ("Trade Count",
         "Total number of position changes (entries + exits). Determined by the number of times the position "
         "flips between 0 (flat) and 1 (long). Each flip incurs a transaction cost (default 5 basis points)."),
        ("Equity Curve",
         "Array of daily portfolio values normalised to start at 1.0. Plotted as a line chart on the frontend. "
         "A smooth upward curve indicates consistent returns; a jagged curve indicates high volatility."),
    ]
    for metric, desc in metrics_detail:
        story.append(Paragraph(f"<b>{metric}</b>", styles["SubSection"]))
        story.append(body(desc))
        story.append(Spacer(1, 4))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX K — Data Flow Diagrams
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Appendix K — System Data Flow Diagrams", styles["SectionHead"]))
    story.append(hr())

    story.append(Paragraph("Portfolio Value Calculation Flow", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        GET /api/v1/portfolio
            |
            v
        1. Authenticate user (get_current_user)
            |
            v
        2. Query holdings WHERE user_id = user.id AND closed_at IS NULL
            |
            v
        3. Extract unique tickers from holdings
            |
            v
        4. Fetch live prices in parallel:
           ThreadPoolExecutor(max_workers=4)
           asyncio.gather(
               run_in_executor(yf.Ticker("AAPL").fast_info.last_price),
               run_in_executor(yf.Ticker("NVDA").fast_info.last_price),
               run_in_executor(yf.Ticker("MSFT").fast_info.last_price),
               ...
           )
            |
            v
        5. Update each holding's current_price
            |
            v
        6. Enrich with stock name from Stock table
            |
            v
        7. Return JSON array with live data
    """)))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Advisor Analysis Flow", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        GET /api/v1/analysis/factors/AAPL?momentum=24&valuation=20&...
            |
            v
        1. Fetch 6 months of OHLCV from yfinance
            |
            v
        2. Compute 30+ technical indicators (FeatureEngine)
            |
            v
        3. Calculate 6 factor scores (0-100 each):
           - Sentiment: FinBERT on recent headlines (or OBV fallback)
           - Momentum:  RSI + MACD histogram + price position
           - Valuation: Bollinger position + price/SMA ratios
           - Volatility: Inverse of 20-day vol + ATR
           - Volume:    Volume ratio + MFI
           - Growth:    ROC-10 + trend positioning
            |
            v
        4. Apply custom weights from query params
            |
            v
        5. Compute composite = sum(score_i x weight_i) / sum(weight_i)
            |
            v
        6. Generate signal:
           composite >= 62 -> BUY (confidence = composite)
           composite <= 38 -> SELL (confidence = 100 - composite)
           else            -> HOLD
            |
            v
        7. Return FactorAnalysisResponse
    """)))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Sentiment Analysis Flow", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        GET /api/v1/sentiment/AAPL
            |
            v
        1. Fetch news headlines via yf.Ticker("AAPL").news
           (up to 15 headlines)
            |
            v
        2. Lazy-load FinBERT model if not cached
           (ProsusAI/finbert, ~420 MB, one-time download)
            |
            v
        3. Run in ThreadPoolExecutor(max_workers=2):
           For each headline:
             a. Tokenise with WordPiece tokeniser
             b. Pass through 12 transformer layers
             c. Classify: P(positive), P(negative), P(neutral)
             d. Score = P(pos) x 100 + P(neutral) x 50
            |
            v
        4. Aggregate: overall_score = mean(headline_scores)
            |
            v
        5. Label: >= 62 positive, <= 38 negative, else neutral
            |
            v
        6. Return SentimentResponse with per-headline breakdown
    """)))

    # ══════════════════════════════════════════════════════════════
    # APPENDIX L — Schema Field Details
    # ══════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("Appendix L — Schema Field Reference Tables", styles["SectionHead"]))
    story.append(hr())
    story.append(body(
        "Detailed field-by-field reference for all Pydantic request/response schemas, "
        "including types, constraints, and default values."
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Authentication Schemas", styles["SubSection"]))
    auth_fields = Table([
        ["Schema", "Field", "Type", "Constraints"],
        ["LoginRequest", "email", "EmailStr", "Required, valid email format"],
        ["LoginRequest", "password", "str", "Required"],
        ["RegisterRequest", "email", "EmailStr", "Required, valid email format"],
        ["RegisterRequest", "password", "str", "Required, min 8 chars"],
        ["RegisterRequest", "full_name", "str", "Required"],
        ["RefreshRequest", "refresh_token", "str", "Required"],
        ["TokenResponse", "access_token", "str", "JWT string"],
        ["TokenResponse", "refresh_token", "str", "JWT string"],
        ["TokenResponse", "token_type", "str", "Always 'bearer'"],
    ], colWidths=[1.4 * inch, 1.3 * inch, 1.2 * inch, 2.2 * inch])
    auth_fields.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 1), (1, -1), "Courier"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(auth_fields)
    story.append(Spacer(1, 10))

    story.append(Paragraph("User Schemas", styles["SubSection"]))
    user_fields = Table([
        ["Schema", "Field", "Type", "Constraints"],
        ["UserOut", "id", "UUID", "Primary key"],
        ["UserOut", "email", "str", "Unique"],
        ["UserOut", "full_name", "str", "Display name"],
        ["UserOut", "role", "str", "investor/analyst/admin"],
        ["UserOut", "phone", "str | None", "Optional"],
        ["UserOut", "bio", "str | None", "Optional"],
        ["UserOut", "avatar_url", "str | None", "URL to uploaded image"],
        ["UserOut", "is_active", "bool", "Default True"],
        ["UserOut", "created_at", "datetime", "Auto-set"],
        ["UserUpdate", "full_name", "str | None", "Optional update"],
        ["UserUpdate", "email", "str | None", "Optional update"],
        ["UserUpdate", "phone", "str | None", "Optional update"],
        ["UserUpdate", "bio", "str | None", "Optional update"],
        ["PasswordUpdate", "current_password", "str", "Verified against hash"],
        ["PasswordUpdate", "new_password", "str", "Min 8 chars"],
    ], colWidths=[1.4 * inch, 1.3 * inch, 1.2 * inch, 2.2 * inch])
    user_fields.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 1), (1, -1), "Courier"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(user_fields)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Portfolio Schemas", styles["SubSection"]))
    portfolio_fields = Table([
        ["Schema", "Field", "Type", "Constraints"],
        ["HoldingCreate", "ticker", "str", "Required, uppercase"],
        ["HoldingCreate", "quantity", "float", "Required, gt=0"],
        ["HoldingCreate", "avg_cost", "float", "Required, gt=0"],
        ["HoldingUpdate", "quantity", "float | None", "Optional, gt=0"],
        ["HoldingUpdate", "avg_cost", "float | None", "Optional, gt=0"],
        ["HoldingOut", "id", "UUID", "Primary key"],
        ["HoldingOut", "user_id", "UUID", "Owner FK"],
        ["HoldingOut", "ticker", "str", "Stock symbol"],
        ["HoldingOut", "quantity", "float", "Number of shares"],
        ["HoldingOut", "avg_cost", "float", "Average purchase price"],
        ["HoldingOut", "current_price", "float | None", "Live price from yfinance"],
        ["HoldingOut", "opened_at", "datetime", "Position open date"],
    ], colWidths=[1.4 * inch, 1.3 * inch, 1.2 * inch, 2.2 * inch])
    portfolio_fields.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 1), (1, -1), "Courier"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(portfolio_fields)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Trade Schemas", styles["SubSection"]))
    trade_fields = Table([
        ["Schema", "Field", "Type", "Constraints"],
        ["TradeCreate", "ticker", "str", "Required"],
        ["TradeCreate", "side", "str", "buy or sell"],
        ["TradeCreate", "entry_price", "float", "Required, gt=0"],
        ["TradeCreate", "exit_price", "float | None", "Optional"],
        ["TradeCreate", "stop_loss", "float | None", "Optional"],
        ["TradeCreate", "take_profit", "float | None", "Optional"],
        ["TradeCreate", "quantity", "float", "Required, gt=0"],
        ["TradeCreate", "strategy_label", "str | None", "Optional"],
        ["TradeCreate", "notes", "str | None", "Optional, free-text"],
        ["TradeOut", "id", "UUID", "Primary key"],
        ["TradeOut", "user_id", "UUID", "Owner FK"],
        ["TradeOut", "opened_at", "datetime", "Trade open time"],
        ["TradeOut", "closed_at", "datetime | None", "Trade close time"],
    ], colWidths=[1.4 * inch, 1.3 * inch, 1.2 * inch, 2.2 * inch])
    trade_fields.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 1), (1, -1), "Courier"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(trade_fields)
    story.append(PageBreak())

    story.append(Paragraph("Strategy and Marketplace Schemas", styles["SubSection"]))
    strat_fields = Table([
        ["Schema", "Field", "Type", "Constraints"],
        ["StrategyCreate", "name", "str", "Required"],
        ["StrategyCreate", "description", "str | None", "Optional"],
        ["StrategyCreate", "weights", "dict", "JSONB: {factor: weight}"],
        ["StrategyCreate", "is_preset", "bool", "Default False"],
        ["StrategyCreate", "is_published", "bool", "Default False"],
        ["StrategyOut", "id", "UUID", "Primary key"],
        ["StrategyOut", "owner_id", "UUID | None", "NULL for system presets"],
        ["StrategyOut", "name", "str", "Strategy name"],
        ["StrategyOut", "weights", "dict", "6-factor weight config"],
        ["MarketplaceListingOut", "id", "UUID", "Primary key"],
        ["MarketplaceListingOut", "strategy_id", "UUID", "FK, unique"],
        ["MarketplaceListingOut", "strategy", "StrategyBrief", "Nested strategy data"],
        ["MarketplaceListingOut", "price_cents", "int", "Price in cents"],
        ["MarketplaceListingOut", "status", "str", "draft/review/verified/listed"],
        ["MarketplaceListingOut", "avg_rating", "float | None", "0-5 scale"],
        ["MarketplaceListingOut", "rating_count", "int", "Number of ratings"],
        ["MarketplaceListingOut", "sales_count", "int", "Times purchased"],
        ["MarketplaceListingOut", "backtest_return", "float | None", "Historical return"],
        ["MarketplaceListingOut", "backtest_sharpe", "float | None", "Risk-adjusted return"],
        ["MarketplaceListingOut", "backtest_winrate", "float | None", "Win percentage"],
    ], colWidths=[1.6 * inch, 1.2 * inch, 1.1 * inch, 2.2 * inch])
    strat_fields.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("FONTNAME", (0, 1), (1, -1), "Courier"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(strat_fields)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX M — Project Setup Guide
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Appendix M — Project Setup and Running Guide", styles["SectionHead"]))
    story.append(hr())

    story.append(Paragraph("Prerequisites", styles["SubSection"]))
    story.append(bullet("Python 3.10+ (required by asyncpg and SQLAlchemy async)"))
    story.append(bullet("PostgreSQL 14+ (for JSONB, UUID, and async connection support)"))
    story.append(bullet("<font face='Courier'>uv</font> package manager (fast Rust-based Python dependency manager)"))
    story.append(bullet("Node.js 18+ and npm (for the React frontend)"))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Backend Setup", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        # 1. Navigate to backend directory
        cd backend

        # 2. Create virtual environment and install dependencies
        uv sync

        # 3. Create .env file with database credentials
        echo "DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/stockpilot" > .env
        echo "SECRET_KEY=your-secret-key-change-in-production" >> .env

        # 4. Create the database
        createdb stockpilot

        # 5. Seed with demo data
        uv run python seed.py

        # 6. Start the server
        uv run uvicorn app.main:app --reload --port 8000
    """)))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Frontend Setup", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        # 1. Navigate to frontend directory
        cd Frontend

        # 2. Install dependencies
        npm install

        # 3. Start development server
        npm run dev
        # Opens at http://localhost:5173
    """)))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Verifying the Setup", styles["SubSection"]))
    story.append(bullet("Visit <font face='Courier'>http://localhost:8000/docs</font> for the Swagger API documentation"))
    story.append(bullet("Visit <font face='Courier'>http://localhost:8000/health</font> to verify database connectivity"))
    story.append(bullet("Visit <font face='Courier'>http://localhost:5173</font> for the React frontend"))
    story.append(bullet("Login with demo credentials: <font face='Courier'>demo@stockpilot.io / demo1234</font>"))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Project Directory Structure", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        backend/
        +-- app/
        |   +-- api/
        |   |   +-- v1/
        |   |       +-- endpoints/
        |   |       |   +-- auth.py          # Login, register, refresh
        |   |       |   +-- users.py         # Profile, password, avatar
        |   |       |   +-- stocks.py        # Stock listing, history
        |   |       |   +-- predictions.py   # AI predictions
        |   |       |   +-- portfolio.py     # Holdings CRUD + live prices
        |   |       |   +-- watchlist.py     # Watch/unwatch tickers
        |   |       |   +-- trades.py        # Trade journal
        |   |       |   +-- strategies.py    # Strategy CRUD
        |   |       |   +-- notifications.py # Notification management
        |   |       |   +-- marketplace.py   # Strategy marketplace
        |   |       |   +-- live.py          # Real-time quotes + market status
        |   |       |   +-- analysis.py      # 6-factor analysis + backtest
        |   |       |   +-- dashboard.py     # Market indices + portfolio history
        |   |       |   +-- sentiment.py     # FinBERT sentiment analysis
        |   |       +-- router.py            # Route aggregation
        |   +-- core/
        |   |   +-- config.py               # Pydantic Settings (env vars)
        |   |   +-- security.py             # bcrypt + JWT utilities
        |   |   +-- dependencies.py         # get_current_user dependency
        |   +-- db/
        |   |   +-- base.py                 # SQLAlchemy DeclarativeBase
        |   |   +-- session.py              # Async engine + session factory
        |   |   +-- models/
        |   |       +-- user.py             # User + UserRole
        |   |       +-- stock.py            # Stock + PriceHistory
        |   |       +-- prediction.py       # Prediction + SignalType
        |   |       +-- portfolio.py        # Holding
        |   |       +-- watchlist.py        # Watchlist
        |   |       +-- trade.py            # Trade + TradeSide
        |   |       +-- strategy.py         # Strategy (JSONB weights)
        |   |       +-- marketplace.py      # MarketplaceListing + Rating
        |   |       +-- notification.py     # Notification + NotificationKind
        |   +-- schemas/
        |   |   +-- auth.py, user.py, stock.py, prediction.py,
        |   |   +-- portfolio.py, watchlist.py, trade.py,
        |   |   +-- strategy.py, marketplace.py, notification.py
        |   +-- services/
        |       +-- market_data/
        |       |   +-- fetcher.py          # DataFetcher (OHLCV download)
        |       +-- indicators/
        |       |   +-- featureEngine.py    # 30+ technical indicators
        |       +-- recommendation/
        |       |   +-- engine.py           # XGBoost StockPredictor
        |       +-- sentiment/
        |           +-- finbert.py          # FinBERT sentiment analysis
        +-- seed.py                         # Database seeder (demo data)
        +-- generate_docs.py                # This PDF generator
        +-- pyproject.toml                  # Dependencies + project config
    """)))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX N — Glossary
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Appendix N — Glossary of Technical Terms", styles["SectionHead"]))
    story.append(hr())

    glossary = [
        ("ASGI", "Asynchronous Server Gateway Interface. The protocol that FastAPI/Starlette uses to handle HTTP requests asynchronously. Uvicorn is the ASGI server."),
        ("ATR", "Average True Range. A volatility indicator measuring the average daily price range over 14 periods."),
        ("bcrypt", "A password hashing algorithm designed to be slow (making brute-force attacks impractical) and to include automatic salt generation."),
        ("BERT", "Bidirectional Encoder Representations from Transformers. A pre-trained NLP model by Google that understands word context in both directions."),
        ("Bollinger Bands", "A volatility indicator consisting of a moving average plus/minus 2 standard deviations. Prices outside the bands are statistically unusual."),
        ("CORS", "Cross-Origin Resource Sharing. Browser security mechanism that restricts web pages from making requests to different origins."),
        ("DeclarativeBase", "SQLAlchemy 2.0 base class for ORM models. Maps Python classes to database tables."),
        ("EMA", "Exponential Moving Average. A weighted moving average giving more importance to recent prices."),
        ("FastAPI", "A modern Python web framework built on Starlette and Pydantic, providing automatic OpenAPI docs and async support."),
        ("FinBERT", "A BERT model fine-tuned on 50,000+ financial texts for sentiment classification."),
        ("FK", "Foreign Key. A database constraint linking a column to a primary key in another table."),
        ("HOLD zone", "Probability range (0.43-0.57) where the XGBoost model's prediction is considered too uncertain to act on."),
        ("JSONB", "PostgreSQL binary JSON type. Stores JSON data in a binary format optimised for querying and indexing."),
        ("JWT", "JSON Web Token. A compact, URL-safe token format for securely transmitting claims between parties."),
        ("MACD", "Moving Average Convergence Divergence. A momentum indicator showing the relationship between two EMAs."),
        ("MFI", "Money Flow Index. RSI applied to volume-weighted price data. Measures buying/selling pressure."),
        ("OBV", "On-Balance Volume. Cumulative volume indicator tracking buying/selling pressure."),
        ("OHLCV", "Open, High, Low, Close, Volume. The five standard data points for each trading period."),
        ("ORM", "Object-Relational Mapping. Translates between Python objects and database rows."),
        ("Pydantic", "Python data validation library using type hints. Validates API requests and serialises responses."),
        ("ROC", "Rate of Change. Percentage change in price over a specified number of periods."),
        ("RSI", "Relative Strength Index. A momentum oscillator measuring speed and change of price movements (0-100 scale)."),
        ("Sharpe Ratio", "Risk-adjusted return metric. Higher values indicate better return per unit of risk. Annualised using sqrt(252)."),
        ("SMA", "Simple Moving Average. The arithmetic mean of closing prices over a specified period."),
        ("VWAP", "Volume Weighted Average Price. Average price weighted by trading volume over a period."),
        ("Walk-Forward", "A time-series cross-validation method where each test fold is strictly after its training fold."),
        ("XGBoost", "Extreme Gradient Boosting. An ensemble machine learning algorithm that builds sequential decision trees."),
    ]
    for term, definition in glossary:
        story.append(Paragraph(f"<b>{term}</b>", styles["BodyIndent"]))
        story.append(body_i(definition))
        story.append(Spacer(1, 2))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX O — Live Market Data Implementation Details
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Appendix O — Live Market Data Implementation Details", styles["SectionHead"]))
    story.append(hr())

    story.append(Paragraph("Market Session Status Logic", styles["SubSection"]))
    story.append(body(
        "The <font face='Courier'>GET /api/v1/live/market-status</font> endpoint determines whether major "
        "world stock exchanges are currently open. It checks 3 global sessions:"
    ))
    session_table = Table([
        ["Session", "Exchange", "Open Time", "Close Time", "Timezone"],
        ["US", "NYSE / NASDAQ", "09:30", "16:00", "America/New_York (ET)"],
        ["Europe", "London SE", "08:00", "16:30", "Europe/London (GMT/BST)"],
        ["Asia", "Tokyo SE", "09:00", "15:00", "Asia/Tokyo (JST)"],
    ], colWidths=[0.8 * inch, 1.3 * inch, 0.9 * inch, 0.9 * inch, 2.2 * inch])
    session_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("ALIGN", (2, 0), (3, -1), "CENTER"),
    ]))
    story.append(session_table)
    story.append(Spacer(1, 6))
    story.append(body(
        "The logic converts the current UTC time to each exchange's local timezone, checks if it falls "
        "within trading hours, and also verifies it's a weekday (Mon-Fri). Weekend and holiday checks "
        "use a simple day-of-week filter (holidays are not tracked — this would require a holiday calendar)."
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Quote Data Extraction", styles["SubSection"]))
    story.append(body(
        "The <font face='Courier'>GET /api/v1/live/quote/{ticker}</font> endpoint extracts comprehensive "
        "quote data from yfinance. The data comes from two sources:"
    ))
    story.append(bullet(
        "<b>fast_info</b> — Lightweight data available without a full API call: last_price, previous_close, "
        "market_cap, fifty_two_week_high/low"
    ))
    story.append(bullet(
        "<b>info dict</b> — Full company data requiring a heavier API call: P/E ratio, sector, industry, "
        "forward estimates, dividend data"
    ))
    story.append(body(
        "Every field is wrapped in <font face='Courier'>_safe_float()</font> or <font face='Courier'>_safe_int()</font> "
        "because yfinance may return None, 'Infinity', NaN, or entirely missing keys depending on the ticker "
        "and Yahoo Finance's data availability."
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("4-Hour Chart Aggregation", styles["SubSection"]))
    story.append(body(
        "yfinance does not natively support 4-hour intervals. The <font face='Courier'>_aggregate_4h</font> "
        "function works around this by:"
    ))
    story.append(bullet("Downloading 1-hour data from yfinance"))
    story.append(bullet("Using pandas <font face='Courier'>resample('4h')</font> to aggregate"))
    story.append(bullet("Aggregation rules: Open = first, High = max, Low = min, Close = last, Volume = sum"))
    story.append(bullet("Dropping any bars where volume is 0 (non-trading hours)"))
    story.append(code_block(textwrap.dedent("""\
        agg = {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum",
        }
        df_4h = df.resample("4h").agg(agg).dropna()
    """)))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX P — Analysis Endpoint Implementation Details
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Appendix P — Analysis Endpoint Implementation Details", styles["SectionHead"]))
    story.append(hr())

    story.append(Paragraph("Factor Score Calculation — Detailed Algorithm", styles["SubSection"]))
    story.append(body(
        "Each of the 6 factors is computed from specific technical indicators. Here is the exact "
        "calculation logic for each factor:"
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Sentiment Factor</b>", styles["BodyIndent"]))
    story.append(body(
        "Primary source: FinBERT analysis of recent news headlines (0-100 score). "
        "If no headlines are available, falls back to OBV (On-Balance Volume) trend analysis. "
        "OBV fallback: compares OBV to its 20-day SMA. If OBV > SMA(OBV): score = 65 (mild positive). "
        "If OBV < SMA(OBV): score = 35 (mild negative). This proxy captures institutional accumulation/distribution."
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Momentum Factor</b>", styles["BodyIndent"]))
    story.append(code_block(textwrap.dedent("""\
        # Component 1: RSI-14 (40% of momentum score)
        rsi_score = rsi_14  # RSI is already 0-100

        # Component 2: MACD histogram direction (30%)
        if macd_histogram > 0:
            macd_score = 50 + min(macd_histogram / price * 5000, 50)
        else:
            macd_score = 50 + max(macd_histogram / price * 5000, -50)

        # Component 3: Price position in 20-day range (30%)
        position_score = price_position * 100  # Already 0-1, scale to 0-100

        momentum = rsi_score * 0.4 + macd_score * 0.3 + position_score * 0.3
    """)))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Valuation Factor</b>", styles["BodyIndent"]))
    story.append(body(
        "Inverted scoring: stocks trading below their moving averages and near the lower Bollinger Band "
        "get high valuation scores (potential undervaluation). Combines: BB_Position (inverted, so 0 = overvalued, "
        "1 = undervalued) with Price/SMA-20 and Price/SMA-50 ratios (below 1.0 = undervalued)."
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Volatility Factor</b>", styles["BodyIndent"]))
    story.append(body(
        "Inverse volatility scoring — lower volatility = higher score (safer investment). "
        "Combines: 20-day return standard deviation (normalised to 0-100, inverted) and ATR-14 as a percentage "
        "of current price (also inverted). A stock with 1% daily volatility scores higher than one with 4%."
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Volume Factor</b>", styles["BodyIndent"]))
    story.append(body(
        "Combines volume_ratio (current volume / 20-day average) and MFI-14. High volume with positive "
        "money flow indicates institutional buying conviction. Formula: "
        "volume_score = min(volume_ratio, 2.0) / 2.0 * 50 + mfi_14 * 0.5"
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Growth Factor</b>", styles["BodyIndent"]))
    story.append(body(
        "Combines ROC-10 (rate of change, scaled to 0-100) with trend positioning (price above/below SMA-20). "
        "A stock with positive ROC and price above SMA-20 gets a high growth score. "
        "Formula: growth = roc_score * 0.6 + trend_score * 0.4"
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Bull/Bear Case Generation", styles["SubSection"]))
    story.append(body(
        "The <font face='Courier'>GET /api/v1/analysis/bull-bear/{ticker}</font> endpoint generates "
        "data-driven arguments using rules applied to the fetched data:"
    ))
    story.append(Spacer(1, 4))
    story.append(body("<b>Bull case rules (examples):</b>"))
    story.append(bullet("If RSI < 40: 'RSI at {rsi} suggests oversold conditions with bounce potential'"))
    story.append(bullet("If price > SMA-50: 'Trading above 50-day moving average confirms uptrend'"))
    story.append(bullet("If volume_ratio > 1.5: 'Volume {ratio}x above average signals institutional interest'"))
    story.append(bullet("If P/E < sector_average: 'P/E of {pe} below sector average suggests undervaluation'"))
    story.append(bullet("If dividend_yield > 2%: 'Dividend yield of {yield}% provides income while waiting'"))
    story.append(Spacer(1, 4))
    story.append(body("<b>Bear case rules (examples):</b>"))
    story.append(bullet("If RSI > 70: 'RSI at {rsi} indicates overbought conditions, pullback risk elevated'"))
    story.append(bullet("If price < SMA-50: 'Trading below 50-day moving average, trend is bearish'"))
    story.append(bullet("If volatility > 40%: 'Annualised volatility of {vol}% indicates high risk'"))
    story.append(bullet("If MACD < signal: 'MACD bearish crossover suggests weakening momentum'"))
    story.append(bullet("If MFI > 80: 'Money Flow Index at {mfi} signals potential distribution phase'"))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Fundamentals Data Extraction", styles["SubSection"]))
    story.append(body(
        "The fundamentals endpoint extracts 20+ financial metrics from yfinance's info dict. "
        "Each metric is wrapped in _safe_float/_safe_int for resilience:"
    ))
    fundamentals_table = Table([
        ["Metric", "yfinance Key", "Description"],
        ["market_cap", "marketCap", "Total market capitalisation"],
        ["pe_ratio", "trailingPE", "Price-to-earnings (trailing 12 months)"],
        ["forward_pe", "forwardPE", "Expected P/E based on forward estimates"],
        ["pb_ratio", "priceToBook", "Price-to-book value"],
        ["eps", "trailingEps", "Earnings per share"],
        ["dividend_yield", "dividendYield", "Annual dividend / price"],
        ["revenue", "totalRevenue", "Total annual revenue"],
        ["net_income", "netIncomeToCommon", "Net income (common shareholders)"],
        ["profit_margin", "profitMargins", "Net income / revenue"],
        ["operating_margin", "operatingMargins", "Operating income / revenue"],
        ["debt_to_equity", "debtToEquity", "Total debt / shareholder equity"],
        ["current_ratio", "currentRatio", "Current assets / current liabilities"],
        ["roe", "returnOnEquity", "Net income / shareholder equity"],
        ["roa", "returnOnAssets", "Net income / total assets"],
        ["free_cash_flow", "freeCashflow", "Cash from operations minus CapEx"],
        ["beta", "beta", "Volatility relative to S&P 500"],
    ], colWidths=[1.3 * inch, 1.5 * inch, 3.3 * inch])
    fundamentals_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (1, 1), (1, -1), "Courier"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(fundamentals_table)

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX Q — Database Column Reference
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Appendix Q — Complete Database Column Reference", styles["SectionHead"]))
    story.append(hr())
    story.append(body(
        "Every column across all 11 database tables, with SQLAlchemy types and constraints."
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("users table", styles["SubSection"]))
    users_cols = Table([
        ["Column", "SQLAlchemy Type", "Nullable", "Constraint"],
        ["id", "UUID (PK)", "No", "server_default=uuid4"],
        ["email", "String(255)", "No", "unique=True, index=True"],
        ["password_hash", "String(255)", "No", "-"],
        ["full_name", "String(255)", "No", "-"],
        ["role", "Enum(UserRole)", "No", "default=investor"],
        ["phone", "String(20)", "Yes", "-"],
        ["bio", "Text", "Yes", "-"],
        ["avatar_url", "String(500)", "Yes", "-"],
        ["is_active", "Boolean", "No", "default=True"],
        ["created_at", "DateTime(tz)", "No", "server_default=now()"],
        ["updated_at", "DateTime(tz)", "Yes", "onupdate=now()"],
    ], colWidths=[1.3 * inch, 1.5 * inch, 0.7 * inch, 2.6 * inch])
    users_cols.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 1), (1, -1), "Courier"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(users_cols)
    story.append(Spacer(1, 10))

    story.append(Paragraph("holdings table", styles["SubSection"]))
    holdings_cols = Table([
        ["Column", "SQLAlchemy Type", "Nullable", "Constraint"],
        ["id", "UUID (PK)", "No", "server_default=uuid4"],
        ["user_id", "UUID (FK -> users.id)", "No", "ondelete=CASCADE"],
        ["ticker", "String(10)", "No", "-"],
        ["quantity", "Float", "No", "-"],
        ["avg_cost", "Float", "No", "-"],
        ["current_price", "Float", "Yes", "Updated on GET"],
        ["opened_at", "DateTime(tz)", "No", "server_default=now()"],
        ["closed_at", "DateTime(tz)", "Yes", "NULL for active positions"],
    ], colWidths=[1.3 * inch, 1.8 * inch, 0.7 * inch, 2.3 * inch])
    holdings_cols.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 1), (1, -1), "Courier"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(holdings_cols)
    story.append(Spacer(1, 10))

    story.append(Paragraph("trades table", styles["SubSection"]))
    trades_cols = Table([
        ["Column", "SQLAlchemy Type", "Nullable", "Constraint"],
        ["id", "UUID (PK)", "No", "server_default=uuid4"],
        ["user_id", "UUID (FK -> users.id)", "No", "ondelete=CASCADE"],
        ["ticker", "String(10)", "No", "-"],
        ["side", "Enum(TradeSide)", "No", "buy or sell"],
        ["entry_price", "Float", "No", "-"],
        ["exit_price", "Float", "Yes", "NULL if still open"],
        ["stop_loss", "Float", "Yes", "-"],
        ["take_profit", "Float", "Yes", "-"],
        ["quantity", "Float", "No", "-"],
        ["strategy_label", "String(100)", "Yes", "-"],
        ["opened_at", "DateTime(tz)", "No", "server_default=now()"],
        ["closed_at", "DateTime(tz)", "Yes", "-"],
        ["notes", "Text", "Yes", "Free-text journal entry"],
    ], colWidths=[1.3 * inch, 1.8 * inch, 0.7 * inch, 2.3 * inch])
    trades_cols.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 1), (1, -1), "Courier"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(trades_cols)
    story.append(Spacer(1, 10))

    story.append(Paragraph("strategies table", styles["SubSection"]))
    strats_cols = Table([
        ["Column", "SQLAlchemy Type", "Nullable", "Constraint"],
        ["id", "UUID (PK)", "No", "server_default=uuid4"],
        ["owner_id", "UUID (FK -> users.id)", "Yes", "NULL for system presets"],
        ["name", "String(100)", "No", "-"],
        ["description", "Text", "Yes", "-"],
        ["weights", "JSONB", "No", "{factor: int_weight}"],
        ["is_preset", "Boolean", "No", "default=False"],
        ["is_published", "Boolean", "No", "default=False"],
        ["created_at", "DateTime(tz)", "No", "server_default=now()"],
        ["updated_at", "DateTime(tz)", "Yes", "onupdate=now()"],
    ], colWidths=[1.3 * inch, 1.8 * inch, 0.7 * inch, 2.3 * inch])
    strats_cols.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 1), (1, -1), "Courier"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(strats_cols)
    story.append(Spacer(1, 10))

    story.append(Paragraph("marketplace_listings table", styles["SubSection"]))
    market_cols = Table([
        ["Column", "SQLAlchemy Type", "Nullable", "Constraint"],
        ["id", "UUID (PK)", "No", "server_default=uuid4"],
        ["strategy_id", "UUID (FK -> strategies.id)", "No", "unique=True"],
        ["price_cents", "Integer", "No", "Price in cents"],
        ["status", "Enum(ListingStatus)", "No", "draft/review/verified/listed/removed"],
        ["avg_rating", "Float", "Yes", "0.0-5.0 scale"],
        ["rating_count", "Integer", "No", "default=0"],
        ["sales_count", "Integer", "No", "default=0"],
        ["backtest_return", "Float", "Yes", "-"],
        ["backtest_sharpe", "Float", "Yes", "-"],
        ["backtest_winrate", "Float", "Yes", "-"],
        ["listed_at", "DateTime(tz)", "Yes", "When listing went live"],
        ["created_at", "DateTime(tz)", "No", "server_default=now()"],
    ], colWidths=[1.3 * inch, 2 * inch, 0.7 * inch, 2.1 * inch])
    market_cols.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 1), (1, -1), "Courier"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(market_cols)
    story.append(Spacer(1, 10))

    story.append(Paragraph("predictions table", styles["SubSection"]))
    pred_cols = Table([
        ["Column", "SQLAlchemy Type", "Nullable", "Constraint"],
        ["id", "UUID (PK)", "No", "server_default=uuid4"],
        ["ticker", "String(10)", "No", "index=True"],
        ["signal", "Enum(SignalType)", "No", "BUY/HOLD/SELL"],
        ["confidence", "Float", "No", "0-100 scale"],
        ["probability_up", "Float", "Yes", "0.0-1.0"],
        ["probability_down", "Float", "Yes", "0.0-1.0"],
        ["composite_score", "Float", "Yes", "0-100 composite"],
        ["model_version", "String(50)", "Yes", "e.g. xgboost_v1"],
        ["created_at", "DateTime(tz)", "No", "server_default=now()"],
    ], colWidths=[1.3 * inch, 1.8 * inch, 0.7 * inch, 2.3 * inch])
    pred_cols.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 1), (1, -1), "Courier"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(pred_cols)

    # ══════════════════════════════════════════════════════════════
    # APPENDIX R — Async Patterns in StockPilot
    # ══════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("Appendix R — Async Patterns and Concurrency", styles["SectionHead"]))
    story.append(hr())

    story.append(Paragraph("Why Async Matters for StockPilot", styles["SubSection"]))
    story.append(body(
        "StockPilot makes <b>heavy use of external API calls</b> — every quote, chart, analysis, and sentiment "
        "request requires fetching data from Yahoo Finance. A synchronous server would block on each call, "
        "serving only one user at a time during the 200-800ms wait. Async architecture is not optional here — "
        "it's a fundamental requirement."
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Pattern 1: Async Database Queries", styles["SubSection"]))
    story.append(body(
        "All database operations use SQLAlchemy's <font face='Courier'>AsyncSession</font>. This means "
        "database queries don't block the event loop while waiting for PostgreSQL responses."
    ))
    story.append(code_block(textwrap.dedent("""\
        # CORRECT: async query - doesn't block event loop
        result = await db.execute(select(Holding).where(Holding.user_id == user.id))
        holdings = result.scalars().all()

        # WRONG: synchronous ORM access - blocks the event loop
        # holdings = db.query(Holding).filter_by(user_id=user.id).all()
    """)))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Pattern 2: ThreadPoolExecutor for CPU-bound Work", styles["SubSection"]))
    story.append(body(
        "yfinance and FinBERT inference are synchronous, CPU-bound operations. Running them directly in an "
        "async endpoint would block the event loop. The solution: run them in a thread pool."
    ))
    story.append(code_block(textwrap.dedent("""\
        # In portfolio.py - parallel price fetching
        _executor = ThreadPoolExecutor(max_workers=4)

        async def _fetch_live_prices(tickers):
            loop = asyncio.get_event_loop()
            tasks = [loop.run_in_executor(_executor, _fetch_price, t) for t in tickers]
            return dict(await asyncio.gather(*tasks))

        # In sentiment.py - FinBERT inference in thread pool
        _executor = ThreadPoolExecutor(max_workers=2)

        result = await asyncio.get_event_loop().run_in_executor(
            _executor, analyzer.analyze_ticker, ticker
        )
    """)))
    story.append(why_box(
        "<b>Why 4 workers for prices but only 2 for FinBERT?</b> "
        "Price fetching is I/O-bound (waiting for Yahoo's API) — more workers means more parallel requests. "
        "FinBERT is CPU-bound (transformer inference) — more than 2 concurrent inferences would saturate "
        "the CPU and slow everything down, including the event loop."
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Pattern 3: asyncio.gather for Parallel Requests", styles["SubSection"]))
    story.append(body(
        "When multiple independent API calls are needed, <font face='Courier'>asyncio.gather</font> "
        "runs them concurrently:"
    ))
    story.append(code_block(textwrap.dedent("""\
        # Dashboard: fetch 4 market indices in parallel (~200ms total instead of ~800ms sequential)
        async def get_market_indices():
            indices = {"^GSPC": "S&P 500", "^IXIC": "NASDAQ", "^DJI": "Dow Jones", "^VIX": "VIX"}
            loop = asyncio.get_event_loop()
            tasks = [loop.run_in_executor(_executor, _fetch_index, sym, name)
                     for sym, name in indices.items()]
            results = await asyncio.gather(*tasks)
            return [r for r in results if r]
    """)))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Pattern 4: Lazy Loading for Heavy Resources", styles["SubSection"]))
    story.append(body(
        "FinBERT's model weights are ~420 MB. Loading on server startup would add 5-15 seconds to boot time "
        "and waste memory if sentiment analysis is never used. The lazy-load pattern solves this:"
    ))
    story.append(code_block(textwrap.dedent("""\
        _pipeline = None  # Module-level cache

        def _get_pipeline():
            global _pipeline
            if _pipeline is None:
                _pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert",
                                     truncation=True, max_length=512, top_k=None)
            return _pipeline
    """)))
    story.append(body(
        "First call: 5-15 seconds (downloads from HuggingFace if not cached). "
        "Subsequent calls: instant (uses the module-level cached pipeline). "
        "Thread-safe because Python's GIL ensures only one thread initialises the pipeline."
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Pattern 5: expire_on_commit=False", styles["SubSection"]))
    story.append(body(
        "After <font face='Courier'>session.commit()</font>, SQLAlchemy normally marks all loaded objects "
        "as 'expired'. The next attribute access triggers a lazy load — but lazy loading is not supported "
        "in async mode. <font face='Courier'>expire_on_commit=False</font> keeps cached values available:"
    ))
    story.append(code_block(textwrap.dedent("""\
        # Without expire_on_commit=False:
        await db.commit()
        print(user.email)  # ERROR: lazy load not supported in async!

        # With expire_on_commit=False (our setting):
        await db.commit()
        print(user.email)  # Works - uses cached value from before commit
    """)))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX S — Testing and Debugging Guide
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Appendix S — Testing and Debugging Guide", styles["SectionHead"]))
    story.append(hr())

    story.append(Paragraph("Swagger Interactive API Documentation", styles["SubSection"]))
    story.append(body(
        "FastAPI automatically generates interactive API documentation at "
        "<font face='Courier'>http://localhost:8000/docs</font> (Swagger UI) and "
        "<font face='Courier'>http://localhost:8000/redoc</font> (ReDoc). Every endpoint, its parameters, "
        "request body schema, and response schema are listed. You can test endpoints directly from the browser."
    ))
    story.append(Spacer(1, 6))
    story.append(body("<b>Testing authenticated endpoints:</b>"))
    story.append(bullet("1. Call POST /api/v1/auth/login with demo credentials"))
    story.append(bullet("2. Copy the access_token from the response"))
    story.append(bullet("3. Click 'Authorize' button in Swagger UI"))
    story.append(bullet("4. Paste the token (without 'Bearer ' prefix)"))
    story.append(bullet("5. All subsequent requests include the Authorization header"))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Common Debugging Scenarios", styles["SubSection"]))

    story.append(Paragraph("<b>1. 'Connection refused' on startup</b>", styles["BodyIndent"]))
    story.append(body(
        "PostgreSQL is not running or the DATABASE_URL in .env is incorrect. Check: "
        "(a) PostgreSQL service is running, (b) database 'stockpilot' exists (run <font face='Courier'>createdb stockpilot</font>), "
        "(c) credentials in .env match your PostgreSQL setup."
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>2. '401 Unauthorized' on every request</b>", styles["BodyIndent"]))
    story.append(body(
        "The JWT has expired (120-minute TTL). The frontend should automatically refresh tokens via "
        "the refresh endpoint. If testing manually, get a fresh token from /api/v1/auth/login."
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>3. 'No data for ticker' errors</b>", styles["BodyIndent"]))
    story.append(body(
        "yfinance cannot find the ticker on Yahoo Finance. Possible causes: "
        "(a) ticker doesn't exist or is delisted, (b) Yahoo Finance API is temporarily unavailable, "
        "(c) network connectivity issues. The retry logic will attempt 3 times with exponential backoff."
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>4. FinBERT 'model not found' error</b>", styles["BodyIndent"]))
    story.append(body(
        "First run requires downloading the ProsusAI/finbert model (~420 MB) from HuggingFace. "
        "Ensure: (a) internet connectivity, (b) sufficient disk space in the HuggingFace cache directory "
        "(<font face='Courier'>~/.cache/huggingface/</font>)."
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>5. 'duplicate key' errors in seeder</b>", styles["BodyIndent"]))
    story.append(body(
        "The seeder was run without dropping existing tables first. Solution: the seeder already "
        "drops and recreates all tables via <font face='Courier'>Base.metadata.drop_all</font>. "
        "If errors persist, manually drop the database: <font face='Courier'>dropdb stockpilot &amp;&amp; createdb stockpilot</font>."
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Performance Characteristics", styles["SubSection"]))
    story.append(body(
        "Typical response times for key endpoints (measured on development hardware):"
    ))
    perf_table = Table([
        ["Endpoint", "Cold", "Warm", "Notes"],
        ["GET /portfolio", "300-500ms", "200-400ms", "Parallel yfinance calls (4 workers)"],
        ["GET /live/quote/{ticker}", "200-500ms", "200-500ms", "Single yfinance call, no caching"],
        ["GET /analysis/factors/{ticker}", "800-1500ms", "500-1000ms", "6-month OHLCV + indicator calc"],
        ["GET /sentiment/{ticker}", "5-15s", "200-500ms", "First call loads FinBERT model"],
        ["GET /dashboard/indices", "200-400ms", "200-400ms", "4 parallel index fetches"],
        ["GET /analysis/backtest/{ticker}", "1-3s", "1-2s", "Full backtest simulation"],
        ["POST /auth/login", "100-150ms", "100-150ms", "bcrypt verification (~100ms by design)"],
        ["GET /stocks", "<10ms", "<10ms", "Simple PostgreSQL query"],
    ], colWidths=[2.2 * inch, 0.9 * inch, 0.9 * inch, 2.1 * inch])
    perf_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 1), (0, -1), "Courier"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("ALIGN", (1, 0), (2, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(perf_table)
    story.append(Spacer(1, 6))
    story.append(body(
        "'Cold' = first call (model loading, cache miss). 'Warm' = subsequent calls. "
        "The biggest bottleneck is yfinance API latency — all external calls take 200-500ms. "
        "Database queries are consistently fast (<10ms for simple selects)."
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX T — Design Decisions and Trade-offs
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Appendix T — Design Decisions and Trade-offs", styles["SectionHead"]))
    story.append(hr())

    decisions = [
        ("UUID Primary Keys vs Auto-increment",
         "UUIDs prevent ID enumeration attacks (guessing /api/v1/users/1, /api/v1/users/2, ...) and enable "
         "client-side ID generation. The trade-off: UUIDs are 16 bytes vs 4 bytes for integers, making indexes "
         "slightly larger. For StockPilot's scale (<100K records), this is negligible.",
         "Security and flexibility outweigh the minimal storage overhead."),

        ("Single File per Route vs Modular Controllers",
         "Each endpoint group lives in a single file (e.g., portfolio.py contains all portfolio endpoints). "
         "Alternative: separate files per function (list_holdings.py, add_holding.py, etc.). "
         "StockPilot's endpoints are short enough (10-30 lines each) that splitting would create unnecessary "
         "file fragmentation.",
         "Keep related endpoints together until files exceed ~300 lines."),

        ("JSONB for Strategy Weights vs Separate Columns",
         "Strategy weights are stored as JSONB (<font face='Courier'>{\"momentum\": 24, ...}</font>) instead of "
         "6 separate Float columns. This means the weight structure can evolve without database migrations. "
         "Trade-off: JSONB queries are slightly slower than column queries, and there's no type validation "
         "at the database level.",
         "Flexibility for evolving factor system outweighs strict column typing."),

        ("yfinance (Free) vs Premium Data Providers",
         "yfinance is free but has rate limits, occasional outages, and no SLA. "
         "Premium alternatives: Alpha Vantage ($50/mo), IEX Cloud ($20/mo), Polygon ($30/mo). "
         "For a university/demo project, yfinance is appropriate. Production deployment should use "
         "a reliable paid provider with SLA guarantees.",
         "Free is acceptable for development; budget for a paid provider in production."),

        ("Bcrypt (Slow) vs SHA-256 (Fast) for Passwords",
         "Bcrypt is intentionally slow (~100ms per hash with 12 rounds). SHA-256 would be microseconds. "
         "This slowness is the security feature: a brute-force attacker can try millions of SHA-256 hashes "
         "per second but only ~10 bcrypt hashes per second. The 100ms per login is imperceptible to users "
         "but devastates attack throughput.",
         "Always use bcrypt/scrypt/Argon2 for passwords. Never use SHA or MD5."),

        ("Drop-and-Recreate Seeder vs Incremental Seeding",
         "The seeder drops all tables and recreates them. Alternative: check for existing data and skip. "
         "Drop-and-recreate guarantees a clean, consistent state every time — no stale data from previous "
         "runs. Trade-off: cannot be used in production (would destroy real user data).",
         "Clean-slate seeding for development; use incremental migrations for production."),

        ("No Alembic Migrations (Yet)",
         "StockPilot uses <font face='Courier'>Base.metadata.create_all</font> for schema management instead "
         "of Alembic migration scripts. This works because the project is in active development with no "
         "production data to preserve. Once deployed, Alembic should be added for safe schema evolution "
         "(<font face='Courier'>alembic init</font>, generate migrations, apply with <font face='Courier'>alembic upgrade head</font>).",
         "Add Alembic before any production deployment."),

        ("Monolithic API vs Microservices",
         "All endpoints, ML inference, and database access run in a single FastAPI process. "
         "Alternative: separate services for auth, data, ML inference, etc. StockPilot's scale doesn't "
         "justify the operational complexity of microservices (service discovery, inter-service auth, "
         "distributed tracing). A single process is simpler to develop, deploy, and debug.",
         "Start monolithic; extract services only when scale demands it."),
    ]

    for title, description, takeaway in decisions:
        story.append(Paragraph(f"<b>{title}</b>", styles["SubSection"]))
        story.append(body(description))
        story.append(why_box(f"<b>Decision:</b> {takeaway}"))
        story.append(Spacer(1, 6))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX U — Production Deployment Checklist
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Appendix U — Production Deployment Checklist", styles["SectionHead"]))
    story.append(hr())
    story.append(body(
        "Items to address before deploying StockPilot to a production environment:"
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Security Hardening", styles["SubSection"]))
    story.append(bullet("<b>SECRET_KEY:</b> Generate a cryptographically random key: "
        "<font face='Courier'>python -c \"import secrets; print(secrets.token_hex(32))\"</font>"))
    story.append(bullet("<b>CORS origins:</b> Restrict from <font face='Courier'>*</font> to the actual "
        "frontend domain (e.g., <font face='Courier'>https://stockpilot.com</font>)"))
    story.append(bullet("<b>HTTPS:</b> Deploy behind a reverse proxy (nginx/Caddy) with TLS certificates"))
    story.append(bullet("<b>Rate limiting:</b> Add slowapi or custom middleware to prevent API abuse"))
    story.append(bullet("<b>Token storage:</b> Consider httpOnly cookies instead of localStorage for JWT storage"))
    story.append(bullet("<b>Input validation:</b> Add request body size limits to prevent abuse"))
    story.append(bullet("<b>Database credentials:</b> Use environment variables, never commit .env files"))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Infrastructure", styles["SubSection"]))
    story.append(bullet("<b>Database:</b> Use a managed PostgreSQL instance (AWS RDS, Google Cloud SQL, etc.)"))
    story.append(bullet("<b>Connection pooling:</b> Configure pool_size and max_overflow based on expected load"))
    story.append(bullet("<b>Process manager:</b> Run with gunicorn + uvicorn workers for multi-process deployment: "
        "<font face='Courier'>gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4</font>"))
    story.append(bullet("<b>Health checks:</b> Use the /health endpoint for container orchestration probes"))
    story.append(bullet("<b>Logging:</b> Configure structured JSON logging for log aggregation services"))
    story.append(bullet("<b>Monitoring:</b> Add Prometheus metrics or application performance monitoring (APM)"))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Data and ML", styles["SubSection"]))
    story.append(bullet("<b>Market data:</b> Replace yfinance with a paid provider (Alpha Vantage, Polygon) "
        "with SLA guarantees"))
    story.append(bullet("<b>Caching:</b> Add Redis cache for frequently requested stock data (quotes, charts) "
        "with 1-5 minute TTL"))
    story.append(bullet("<b>FinBERT:</b> Pre-download the model to avoid first-request latency. "
        "Consider running inference as a separate service"))
    story.append(bullet("<b>Model retraining:</b> Implement periodic XGBoost retraining pipeline "
        "(monthly or when accuracy degrades)"))
    story.append(bullet("<b>Migrations:</b> Add Alembic for database schema versioning"))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Scalability Considerations", styles["SubSection"]))
    story.append(body(
        "<b>Current capacity:</b> A single StockPilot server can handle approximately 50-100 concurrent "
        "users. The bottleneck is yfinance API calls (200-500ms each, rate-limited). Strategies for scaling:"
    ))
    story.append(Spacer(1, 4))
    story.append(bullet(
        "<b>Horizontal scaling:</b> Deploy multiple API server instances behind a load balancer. "
        "The stateless JWT auth design makes this straightforward — any server can validate any token."
    ))
    story.append(bullet(
        "<b>Caching layer:</b> Redis cache for stock data eliminates redundant yfinance calls. "
        "When 50 users request the same AAPL quote within 1 minute, only 1 yfinance call is needed."
    ))
    story.append(bullet(
        "<b>Background workers:</b> Move heavy computations (backtesting, retraining) to a task queue "
        "(Celery + Redis) so they don't block API endpoints."
    ))
    story.append(bullet(
        "<b>Read replicas:</b> PostgreSQL read replicas for query-heavy endpoints (stocks, predictions). "
        "Writes (trades, holdings) stay on the primary."
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Deployment Commands", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        # Docker deployment example
        FROM python:3.12-slim
        WORKDIR /app
        COPY pyproject.toml uv.lock ./
        RUN pip install uv && uv sync --no-dev
        COPY app/ app/
        EXPOSE 8000
        CMD ["uv", "run", "gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker",
             "-w", "4", "-b", "0.0.0.0:8000"]
    """)))
    story.append(Spacer(1, 6))
    story.append(code_block(textwrap.dedent("""\
        # Docker Compose with PostgreSQL
        services:
          db:
            image: postgres:16
            environment:
              POSTGRES_DB: stockpilot
              POSTGRES_PASSWORD: ${DB_PASSWORD}
            volumes:
              - pgdata:/var/lib/postgresql/data

          api:
            build: ./backend
            ports:
              - "8000:8000"
            environment:
              DATABASE_URL: postgresql+asyncpg://postgres:${DB_PASSWORD}@db:5432/stockpilot
              SECRET_KEY: ${SECRET_KEY}
            depends_on:
              - db
    """)))

    # ══════════════════════════════════════════════════════════════
    # APPENDIX V — Frontend-Backend Integration Guide
    # ══════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("Appendix V — Frontend-Backend Integration", styles["SectionHead"]))
    story.append(hr())

    story.append(Paragraph("Axios Client Configuration", styles["SubSection"]))
    story.append(body(
        "The React frontend communicates with the backend via an Axios instance configured with "
        "automatic JWT token attachment and refresh logic:"
    ))
    story.append(code_block(textwrap.dedent("""\
        // api/client.js
        import axios from 'axios';

        const api = axios.create({ baseURL: 'http://localhost:8000' });

        // Attach JWT to every request
        api.interceptors.request.use((config) => {
            const token = localStorage.getItem('sp_access_token');
            if (token) config.headers.Authorization = 'Bearer ' + token;
            return config;
        });

        // Auto-refresh on 401
        api.interceptors.response.use(
            (response) => response,
            async (error) => {
                if (error.response?.status === 401) {
                    const refresh = localStorage.getItem('sp_refresh_token');
                    const { data } = await axios.post('/api/v1/auth/refresh',
                        { refresh_token: refresh });
                    localStorage.setItem('sp_access_token', data.access_token);
                    error.config.headers.Authorization = 'Bearer ' + data.access_token;
                    return api(error.config); // Retry original request
                }
                return Promise.reject(error);
            }
        );
    """)))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Custom React Hooks", styles["SubSection"]))
    story.append(body(
        "The frontend uses custom hooks to fetch and cache API data. Each hook handles loading states, "
        "error handling, and data transformation:"
    ))
    story.append(code_block(textwrap.dedent("""\
        // hooks/usePortfolio.js
        function usePortfolio() {
            const [holdings, setHoldings] = useState([]);
            const [loading, setLoading] = useState(true);

            const fetchHoldings = async () => {
                setLoading(true);
                try {
                    const { data } = await api.get('/api/v1/portfolio');
                    setHoldings(data);
                } catch (err) {
                    console.error('Failed to fetch portfolio:', err);
                } finally {
                    setLoading(false);
                }
            };

            useEffect(() => { fetchHoldings(); }, []);
            return { holdings, loading, refetch: fetchHoldings };
        }
    """)))
    story.append(Spacer(1, 6))
    story.append(body(
        "Similar hooks exist for: <font face='Courier'>useWatchlist</font>, "
        "<font face='Courier'>useTrades</font>, <font face='Courier'>usePredictions</font>, "
        "<font face='Courier'>useNotifications</font>, <font face='Courier'>useMarketplace</font>, "
        "and <font face='Courier'>useLiveMarket</font>."
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Data Flow: Frontend to Backend", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        React Component               Custom Hook                  Backend API
            |                              |                            |
            |-- User clicks "Add AAPL" --> |                            |
            |                              |-- POST /api/v1/portfolio ->|
            |                              |   {ticker:"AAPL",          |
            |                              |    quantity:10, avg:178}    |
            |                              |                            |-- Validate with Pydantic
            |                              |                            |-- Create Holding in DB
            |                              |                            |-- Fetch live price (yfinance)
            |                              |<-- 201 Created ------------|
            |                              |   {id, ticker, price, ...} |
            |<-- Update UI state ---------|                            |
            |   (show new holding)         |                            |
    """)))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Error Handling in the Frontend", styles["SubSection"]))
    story.append(body(
        "The frontend handles backend errors gracefully by reading the <font face='Courier'>detail</font> "
        "field from FastAPI error responses:"
    ))
    story.append(code_block(textwrap.dedent("""\
        try {
            await api.post('/api/v1/portfolio', { ticker, quantity, avg_cost });
        } catch (err) {
            // FastAPI returns: { "detail": "Stock not found" }
            const message = err.response?.data?.detail || 'Something went wrong';
            setError(message);
        }
    """)))
    story.append(body(
        "Common error responses from the backend: "
        "'Invalid email or password' (401), 'Stock not found' (404), "
        "'Duplicate watchlist entry' (409), 'File exceeds 2 MB limit' (400)."
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX W — Walk-Forward Validation Deep Dive (renamed from V)
    # ══════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("Appendix W — Walk-Forward Validation Deep Dive", styles["SectionHead"]))
    story.append(hr())

    story.append(Paragraph("Why Standard Cross-Validation Fails for Time Series", styles["SubSection"]))
    story.append(body(
        "Standard k-fold cross-validation randomly shuffles data into folds. This is <b>invalid</b> for "
        "stock data because it causes <b>data leakage</b> — the model trains on future data and predicts "
        "past data. Example: if fold 3 contains January data and fold 1 contains March data, the model "
        "trained on March data 'predicts' January — it already knows what happened."
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("TimeSeriesSplit — The Correct Approach", styles["SubSection"]))
    story.append(body(
        "StockPilot uses scikit-learn's <font face='Courier'>TimeSeriesSplit(n_splits=5)</font> for "
        "walk-forward validation. Each fold's test data is <b>strictly after</b> its training data:"
    ))
    story.append(code_block(textwrap.dedent("""\
        # 5-fold walk-forward validation with expanding training window
        # Assume 1,000 rows of daily data (4 years)

        Fold 1: Train on rows   0-332,  Test on rows 333-499   (10 months train, 5 months test)
        Fold 2: Train on rows   0-499,  Test on rows 500-666   (20 months train, 5 months test)
        Fold 3: Train on rows   0-666,  Test on rows 667-833   (30 months train, 5 months test)
        Fold 4: Train on rows   0-833,  Test on rows 834-999   (40 months train, 5 months test)
        Fold 5: Train on rows   0-999,  Test on rows 1000-1166 (48 months train, 5 months test)

        # Each fold: train a new XGBoost model from scratch
        # Report: mean accuracy across all 5 test folds + standard deviation
    """)))
    story.append(Spacer(1, 6))
    story.append(body(
        "<b>Expanding window:</b> Each fold uses all data up to the split point for training. "
        "This mirrors real-world usage: you always have more historical data available as time passes."
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Interpreting Walk-Forward Results", styles["SubSection"]))
    story.append(body(
        "The walk-forward evaluation returns two key numbers:"
    ))
    story.append(bullet(
        "<b>Mean accuracy:</b> Average classification accuracy across all test folds. "
        "For binary stock prediction (UP/DOWN), random guessing gives 50%. "
        "A model with 55-60% accuracy is considered strong for daily stock prediction."
    ))
    story.append(bullet(
        "<b>Standard deviation:</b> How consistent the model is across different time periods. "
        "Low std (< 3%) means stable performance. High std (> 8%) means the model's accuracy "
        "varies wildly depending on market conditions (e.g., works in bull markets, fails in bear markets)."
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Walk-Forward vs Single Train/Test Split", styles["SubSection"]))
    story.append(body(
        "StockPilot uses both approaches:"
    ))
    story.append(bullet(
        "<b>Single split (64/16/20):</b> Used for the actual deployed model. Fast, provides a single "
        "accuracy number. The 16% validation set is used for early stopping."
    ))
    story.append(bullet(
        "<b>Walk-forward (5 folds):</b> Used for honest performance estimation. More robust but "
        "5x slower (trains 5 separate models). Reports in the WalkForwardReport dataclass."
    ))
    story.append(code_block(textwrap.dedent("""\
        @dataclass
        class WalkForwardReport:
            mean_accuracy: float           # Average across all folds
            std_accuracy: float            # Standard deviation
            fold_accuracies: list[float]   # Per-fold accuracy
            n_splits: int                  # Number of folds (default 5)
    """)))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX W — Request/Response Examples
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Appendix X — Request/Response Examples", styles["SectionHead"]))
    story.append(hr())
    story.append(body(
        "Example API interactions showing request payloads and response structures."
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Login and Get Token", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        # Request
        POST /api/v1/auth/login
        Content-Type: application/json
        {
            "email": "demo@stockpilot.io",
            "password": "demo1234"
        }

        # Response (200 OK)
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    """)))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Create a Portfolio Holding", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        # Request
        POST /api/v1/portfolio
        Authorization: Bearer eyJhbGciOiJIUzI1...
        Content-Type: application/json
        {
            "ticker": "AAPL",
            "quantity": 10.0,
            "avg_cost": 178.50
        }

        # Response (201 Created)
        {
            "id": "a3b4c5d6-e7f8-9012-3456-789abcdef012",
            "user_id": "12345678-1234-1234-1234-123456789abc",
            "ticker": "AAPL",
            "quantity": 10.0,
            "avg_cost": 178.50,
            "current_price": 195.23,
            "opened_at": "2024-12-15T10:30:00Z"
        }
    """)))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Get Factor Analysis with Custom Weights", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        # Request (custom momentum-heavy strategy)
        GET /api/v1/analysis/factors/NVDA?sentiment=10&momentum=35&valuation=15&volatility=10&volume=15&growth=15

        # Response (200 OK)
        {
            "ticker": "NVDA",
            "factors": {
                "sentiment": {"score": 72.5, "weight": 10},
                "momentum": {"score": 81.3, "weight": 35},
                "valuation": {"score": 38.2, "weight": 15},
                "volatility": {"score": 45.0, "weight": 10},
                "volume": {"score": 67.8, "weight": 15},
                "growth": {"score": 85.1, "weight": 15}
            },
            "composite": 68.4,
            "signal": "BUY",
            "confidence": 68.4
        }
    """)))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Get Sentiment Analysis", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        # Request
        GET /api/v1/sentiment/TSLA

        # Response (200 OK)
        {
            "ticker": "TSLA",
            "overall_score": 58.3,
            "overall_label": "neutral",
            "headline_count": 8,
            "headlines": [
                {
                    "text": "Tesla reports record quarterly deliveries",
                    "score": 89.2,
                    "label": "positive",
                    "positive": 0.91,
                    "negative": 0.03,
                    "neutral": 0.06
                },
                {
                    "text": "Competition intensifies in EV market",
                    "score": 35.1,
                    "label": "negative",
                    "positive": 0.08,
                    "negative": 0.72,
                    "neutral": 0.20
                }
            ]
        }
    """)))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Create a Trade Journal Entry", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        # Request
        POST /api/v1/trades
        Authorization: Bearer eyJhbGciOiJIUzI1...
        Content-Type: application/json
        {
            "ticker": "MSFT",
            "side": "buy",
            "entry_price": 415.30,
            "exit_price": 428.75,
            "stop_loss": 405.00,
            "take_profit": 440.00,
            "quantity": 5.0,
            "strategy_label": "Momentum Pro",
            "notes": "Entered on MACD crossover, exited at first resistance."
        }

        # Response (201 Created)
        {
            "id": "f1e2d3c4-b5a6-7890-1234-567890abcdef",
            "ticker": "MSFT",
            "side": "buy",
            "entry_price": 415.30,
            "exit_price": 428.75,
            "quantity": 5.0,
            "strategy_label": "Momentum Pro",
            "notes": "Entered on MACD crossover, exited at first resistance.",
            "opened_at": "2024-12-15T14:00:00Z"
        }
    """)))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Get Live Quote", styles["SubSection"]))
    story.append(code_block(textwrap.dedent("""\
        # Request
        GET /api/v1/live/quote/GOOGL

        # Response (200 OK)
        {
            "ticker": "GOOGL",
            "price": 175.42,
            "change": 2.15,
            "change_percent": 1.24,
            "open": 173.80,
            "high": 176.30,
            "low": 173.10,
            "volume": 24500000,
            "market_cap": 2150000000000,
            "pe_ratio": 23.5,
            "week_52_high": 191.75,
            "week_52_low": 130.67,
            "previous_close": 173.27
        }
    """)))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # APPENDIX X — Feature Column Reference
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("Appendix Y — Complete Feature Column Reference", styles["SectionHead"]))
    story.append(hr())
    story.append(body(
        "All 30+ features computed by FeatureEngine and used as input to the XGBoost classifier:"
    ))
    story.append(Spacer(1, 8))

    feature_table = Table([
        ["Feature", "Formula/Source", "Category"],
        ["SMA_5", "5-day simple moving average of Close", "Moving Avg"],
        ["SMA_10", "10-day simple moving average of Close", "Moving Avg"],
        ["SMA_20", "20-day simple moving average of Close", "Moving Avg"],
        ["SMA_50", "50-day simple moving average of Close", "Moving Avg"],
        ["EMA_5", "5-day exponential moving average of Close", "Moving Avg"],
        ["EMA_10", "10-day exponential moving average of Close", "Moving Avg"],
        ["EMA_20", "20-day exponential moving average of Close", "Moving Avg"],
        ["EMA_50", "50-day exponential moving average of Close", "Moving Avg"],
        ["RSI_14", "14-period Relative Strength Index", "Momentum"],
        ["MACD", "EMA_12 - EMA_26", "Momentum"],
        ["MACD_Signal", "9-day EMA of MACD line", "Momentum"],
        ["MACD_Histogram", "MACD - MACD_Signal", "Momentum"],
        ["BB_Upper", "SMA_20 + 2 x std_20", "Volatility"],
        ["BB_Lower", "SMA_20 - 2 x std_20", "Volatility"],
        ["BB_Width", "(Upper - Lower) / Middle", "Volatility"],
        ["BB_Position", "(Close - Lower) / (Upper - Lower)", "Volatility"],
        ["VWAP_20", "20-day volume-weighted average price", "Volume"],
        ["OBV", "Cumulative on-balance volume", "Volume"],
        ["Volume_Ratio", "Volume / 20-day avg volume", "Volume"],
        ["MFI_14", "14-period Money Flow Index", "Volume"],
        ["ATR_14", "14-period Average True Range", "Volatility"],
        ["Daily_Return", "(Close - Prev_Close) / Prev_Close", "Return"],
        ["Volatility_20", "20-day rolling std of returns", "Volatility"],
        ["High_Low_Ratio", "(High - Low) / Open", "Volatility"],
        ["Close_Open_Ratio", "(Close - Open) / Open", "Return"],
        ["Price_Position", "(Close - 20d_Low) / (20d_High - 20d_Low)", "Position"],
        ["ROC_10", "10-day Rate of Change (%)", "Momentum"],
        ["Price_to_SMA_20", "Close / SMA_20", "Position"],
        ["Price_to_SMA_50", "Close / SMA_50", "Position"],
        ["Above_SMA_20", "1 if Close > SMA_20, else 0", "Position"],
        ["Above_SMA_50", "1 if Close > SMA_50, else 0", "Position"],
    ], colWidths=[1.4 * inch, 2.8 * inch, 1 * inch])
    feature_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("FONTNAME", (0, 1), (0, -1), "Courier"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(feature_table)
    story.append(Spacer(1, 8))
    story.append(body(
        "<b>Note:</b> The Close column is <b>dropped</b> from features before training. Including "
        "the raw price would cause leakage — the model would learn absolute price levels rather than "
        "price patterns. All features above are either relative (ratios), bounded (RSI 0-100), or "
        "derived (indicators)."
    ))
    story.append(why_box(
        "<b>Why 30+ features?</b> XGBoost's built-in feature selection (via column subsampling and "
        "gain-based importance) automatically ignores unhelpful features. Providing more features "
        "gives the model more potential signals to learn from. The feature_importance() method shows "
        "which features the model actually uses — typically 8-12 features dominate."
    ))

    # ── CLOSING ─────────────────────────────────────────────────
    story.append(Spacer(1, 1 * inch))
    story.append(gold_hr())
    story.append(Paragraph("End of Documentation", styles["CoverSub"]))
    story.append(Paragraph(
        "This document covers the complete StockPilot backend system: "
        "all API endpoints, ML services, database models, and configuration.",
        styles["CoverSub"],
    ))
    story.append(Paragraph(
        f"Total source files documented: 40+  |  Generated: {datetime.now().strftime('%B %d, %Y')}",
        styles["CoverSub"],
    ))

    # ── BUILD ───────────────────────────────────────────────────
    doc.build(story)
    print("PDF generated: StockPilot_Backend_Documentation.pdf")


if __name__ == "__main__":
    build_pdf()
