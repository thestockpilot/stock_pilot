"""Generate StockPilot Database Documentation PDF."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether,
)

# ── Colours ──
BG_DARK    = HexColor("#09090b")
SURFACE    = HexColor("#18181b")
ACCENT     = HexColor("#d4a853")
ACCENT2    = HexColor("#b8943f")
BULL       = HexColor("#22c55e")
BEAR       = HexColor("#ef4444")
MUTED      = HexColor("#71717a")
LIGHT_BLUE = HexColor("#eef4fb")
LIGHT_GOLD = HexColor("#fdf6e3")
LIGHT_GREEN= HexColor("#eefbf3")
LIGHT_RED  = HexColor("#fef2f2")
LIGHT_GRAY = HexColor("#f4f4f5")
BORDER     = HexColor("#d4d4d8")
TEXT_DARK  = HexColor("#18181b")

PAGE_W, PAGE_H = A4
MARGIN = 54
CONTENT_W = PAGE_W - 2 * MARGIN

OUT = os.path.join(os.path.dirname(__file__), "StockPilot_Database_Documentation.pdf")

doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=MARGIN, bottomMargin=MARGIN,
)

styles = getSampleStyleSheet()

styles.add(ParagraphStyle("Title2", parent=styles["Title"], fontSize=28, leading=34,
                          textColor=TEXT_DARK, spaceAfter=6, alignment=TA_LEFT))
styles.add(ParagraphStyle("Sub", parent=styles["Normal"], fontSize=12, leading=16,
                          textColor=MUTED, spaceAfter=20))
styles.add(ParagraphStyle("H1", parent=styles["Heading1"], fontSize=20, leading=26,
                          textColor=ACCENT2, spaceBefore=28, spaceAfter=10))
styles.add(ParagraphStyle("H2", parent=styles["Heading2"], fontSize=15, leading=20,
                          textColor=TEXT_DARK, spaceBefore=20, spaceAfter=8))
styles.add(ParagraphStyle("H3", parent=styles["Heading3"], fontSize=12, leading=16,
                          textColor=HexColor("#3f3f46"), spaceBefore=14, spaceAfter=6))
styles.add(ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=15,
                          textColor=TEXT_DARK, spaceAfter=8, alignment=TA_JUSTIFY))
styles.add(ParagraphStyle("BodyBold", parent=styles["Normal"], fontSize=10, leading=15,
                          textColor=TEXT_DARK, spaceAfter=8, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle("BulletItem", parent=styles["Normal"], fontSize=10, leading=15,
                          textColor=TEXT_DARK, spaceAfter=4, leftIndent=18,
                          bulletIndent=6, bulletFontSize=10))
styles.add(ParagraphStyle("CodeBlock", parent=styles["Normal"], fontSize=8.5, leading=12,
                          textColor=HexColor("#1e1e1e"), fontName="Courier",
                          backColor=LIGHT_GRAY, borderPadding=8,
                          spaceBefore=6, spaceAfter=10, leftIndent=8, rightIndent=8))
styles.add(ParagraphStyle("CalloutTitle", fontSize=10, leading=13, fontName="Helvetica-Bold",
                          textColor=TEXT_DARK, spaceAfter=2))
styles.add(ParagraphStyle("CalloutBody", fontSize=9.5, leading=14, textColor=TEXT_DARK,
                          alignment=TA_JUSTIFY))
styles.add(ParagraphStyle("CellText", fontSize=9, leading=12, textColor=TEXT_DARK))
styles.add(ParagraphStyle("CellHead", fontSize=9, leading=12, textColor=white,
                          fontName="Helvetica-Bold"))
styles.add(ParagraphStyle("CellCode", fontSize=8, leading=11, textColor=HexColor("#1e1e1e"),
                          fontName="Courier"))
styles.add(ParagraphStyle("Caption", fontSize=8.5, leading=11, textColor=MUTED,
                          alignment=TA_CENTER, spaceBefore=4, spaceAfter=12))
styles.add(ParagraphStyle("TOCItem", fontSize=11, leading=16, textColor=TEXT_DARK,
                          spaceAfter=3, leftIndent=12))
styles.add(ParagraphStyle("Footer", fontSize=8, leading=10, textColor=MUTED,
                          alignment=TA_CENTER))


def _p(text):
    return Paragraph(text, styles["CellText"])

def _pc(text):
    return Paragraph(text, styles["CellCode"])

def _ph(text):
    return Paragraph(text, styles["CellHead"])


def callout_box(title, body, bg_color=LIGHT_BLUE, accent_color=ACCENT):
    title_para = Paragraph(f"<b>{title}</b>", styles["CalloutTitle"])
    body_para = Paragraph(body, styles["CalloutBody"])
    t = Table([[title_para], [body_para]], colWidths=[CONTENT_W - 16])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg_color),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (0, 0), 10),
        ("BOTTOMPADDING", (-1, -1), (-1, -1), 10),
        ("LINEBEFORE", (0, 0), (0, -1), 4, accent_color),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def make_table(headers, rows, col_widths=None):
    wrapped_headers = [_ph(h) for h in headers]
    wrapped_rows = [[_p(cell) if not isinstance(cell, Paragraph) else cell for cell in row] for row in rows]
    data = [wrapped_headers] + wrapped_rows
    if col_widths is None:
        n = len(headers)
        col_widths = [CONTENT_W / n] * n
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT2),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
    ]))
    return t


def section_divider():
    t = Table([[""]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 1, HexColor("#e4e4e7")),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    return t


# ━━━━━━━━━━━━━━━━━━━━ BUILD THE STORY ━━━━━━━━━━━━━━━━━━━━

story = []

# ── COVER PAGE ──
story.append(Spacer(1, 100))
story.append(Paragraph("StockPilot", styles["Title2"]))
story.append(Paragraph("Database Layer Documentation", ParagraphStyle(
    "CoverSub", parent=styles["Title2"], fontSize=18, leading=24, textColor=ACCENT2,
    spaceAfter=16)))
story.append(Paragraph(
    "A comprehensive, beginner-friendly guide covering every table, entity, attribute, "
    "relationship, cardinality ratio, and backend code file that interacts with the database.",
    styles["Sub"]))
story.append(Spacer(1, 20))
story.append(callout_box(
    "Who is this for?",
    "This document is written for beginners. Every concept is explained from the ground up: "
    "what a database table is, why we need foreign keys, what ORM means, and how each piece "
    "of code connects to the database. No prior database experience is assumed.",
    LIGHT_GOLD, ACCENT))
story.append(Spacer(1, 30))

cover_info = [
    ["Project", "StockPilot - AI-Powered Investment Advisor"],
    ["Database", "PostgreSQL 16 (async via asyncpg)"],
    ["ORM", "SQLAlchemy 2.0 (async, Mapped columns)"],
    ["Migration Tool", "Alembic"],
    ["Backend Framework", "FastAPI (Python)"],
    ["Total Tables", "11"],
    ["Total Relationships", "9 foreign-key relationships"],
]
t = Table([[_p(f"<b>{r[0]}</b>"), _p(r[1])] for r in cover_info],
          colWidths=[1.6 * inch, CONTENT_W - 1.6 * inch])
t.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
    ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
story.append(t)
story.append(PageBreak())

# ── TABLE OF CONTENTS ──
story.append(Paragraph("Table of Contents", styles["H1"]))
toc_items = [
    "1. What is a Database? (Beginner Primer)",
    "2. Technologies Used",
    "3. Database Connection & Session Management",
    "4. Complete Table Reference (11 Tables)",
    "5. Enumerations (Enums)",
    "6. Entity-Relationship Map",
    "7. Cardinality Ratios Explained",
    "8. Backend Code Files & Database Interactions",
    "9. The Seed Script",
    "10. Alembic Migrations",
    "11. Query Patterns & Best Practices",
    "12. Glossary",
]
for item in toc_items:
    story.append(Paragraph(item, styles["TOCItem"]))
story.append(PageBreak())

# ━━━━━━ CHAPTER 1: BEGINNER PRIMER ━━━━━━
story.append(Paragraph("1. What is a Database? (Beginner Primer)", styles["H1"]))
story.append(Paragraph(
    "A <b>database</b> is a structured system for storing, organising, and retrieving data. "
    "Think of it like a collection of spreadsheets (called <b>tables</b>), where each spreadsheet "
    "has columns (called <b>attributes</b> or <b>fields</b>) and rows (called <b>records</b> or <b>entities</b>).",
    styles["Body"]))
story.append(Paragraph(
    "StockPilot uses <b>PostgreSQL</b>, a powerful open-source relational database. "
    '"Relational" means the tables can be connected to each other through references called '
    "<b>foreign keys</b>. For example, a trade record points to the user who made it.",
    styles["Body"]))

story.append(Paragraph("Key Concepts", styles["H2"]))

concepts = [
    ["Table", "A structured collection of related data, like a spreadsheet. Example: the 'users' table stores all user accounts."],
    ["Row / Record", "A single entry in a table. Example: one specific user with their email, name, and role."],
    ["Column / Attribute", "A named field in a table that holds one type of data. Example: 'email' holds text, 'is_active' holds true/false."],
    ["Primary Key (PK)", "A column (or set of columns) that uniquely identifies each row. No two rows can have the same PK. StockPilot uses UUIDs as primary keys."],
    ["Foreign Key (FK)", "A column that references the primary key of another table. This creates a link between two tables. Example: trades.user_id references users.id."],
    ["Relationship", "A logical connection between two tables via a foreign key. Can be one-to-many (1:N), one-to-one (1:1), or many-to-many (M:N)."],
    ["ORM", "Object-Relational Mapping. A technique that lets you interact with database tables using Python classes instead of writing raw SQL queries."],
    ["Migration", "A versioned script that changes the database structure (add a table, add a column, etc.) in a controlled, repeatable way."],
]
story.append(make_table(["Term", "Explanation"], concepts,
                        [1.2 * inch, CONTENT_W - 1.2 * inch]))
story.append(PageBreak())

# ━━━━━━ CHAPTER 2: TECHNOLOGIES ━━━━━━
story.append(Paragraph("2. Technologies Used", styles["H1"]))
story.append(Paragraph(
    "StockPilot's backend uses a modern Python stack to interact with the database. "
    "Here is every technology involved and what role it plays:",
    styles["Body"]))

tech_rows = [
    ["PostgreSQL 16", "The database engine itself. It stores all data on disk, handles queries, enforces constraints (like unique emails), and manages concurrent access from multiple users.", "Core database"],
    ["asyncpg", "A high-performance, asynchronous PostgreSQL driver for Python. 'Asynchronous' means it can handle many database requests simultaneously without blocking, which is critical for a web API that serves many users at once.", "DB driver"],
    ["SQLAlchemy 2.0", "The ORM (Object-Relational Mapper). Instead of writing raw SQL like 'SELECT * FROM users WHERE id = ...', you write Python code like select(User).where(User.id == ...). SQLAlchemy translates this to SQL automatically.", "ORM"],
    ["Alembic", "The migration tool. When you add a new column or table to your code, Alembic generates a migration script that applies that change to the actual database. This keeps your code and database structure in sync.", "Migrations"],
    ["psycopg2", "A synchronous PostgreSQL driver used only by Alembic (which does not support async operations). The main application never uses it directly.", "Alembic driver"],
    ["Pydantic", "A data validation library. It defines 'schemas' that validate incoming API data before it reaches the database. For example, it ensures an email field is actually a valid email address.", "Validation"],
    ["pydantic-settings", "Reads configuration (like the database URL) from environment variables or .env files, so sensitive data like passwords never appear in the code.", "Configuration"],
    ["FastAPI", "The web framework. It defines API endpoints (URLs) that receive requests, interact with the database via SQLAlchemy, and return responses. It integrates deeply with SQLAlchemy's async sessions via its dependency injection system.", "Web framework"],
]
story.append(make_table(["Technology", "What It Does & Why", "Role"],
                        tech_rows, [1.2 * inch, CONTENT_W - 2.2 * inch, 1.0 * inch]))
story.append(Spacer(1, 10))
story.append(callout_box(
    "How do these fit together?",
    "A user sends an HTTP request to FastAPI. FastAPI creates an async database session (via asyncpg + SQLAlchemy). "
    "The endpoint handler queries or modifies data using SQLAlchemy ORM classes. SQLAlchemy translates the Python code "
    "to SQL and sends it to PostgreSQL via asyncpg. The result comes back, gets validated by Pydantic, and is returned "
    "as a JSON response. If the database structure needs to change, Alembic generates and runs a migration script.",
    LIGHT_BLUE, HexColor("#3b82f6")))
story.append(PageBreak())

# ━━━━━━ CHAPTER 3: CONNECTION & SESSION ━━━━━━
story.append(Paragraph("3. Database Connection & Session Management", styles["H1"]))

story.append(Paragraph("3.1 The Connection URL", styles["H2"]))
story.append(Paragraph(
    "The database connection is configured in the <font face='Courier' size=9>.env</font> file:",
    styles["Body"]))
story.append(Paragraph(
    "DATABASE_URL=postgresql+asyncpg://postgres:4569@localhost:5432/stockpilot",
    styles["CodeBlock"]))
story.append(Paragraph(
    "Let's break this URL down piece by piece:",
    styles["Body"]))
url_parts = [
    ["postgresql", "The database type (PostgreSQL)"],
    ["+asyncpg", "The driver to use (asyncpg for async support)"],
    ["postgres:4569", "Username and password for the database"],
    ["@localhost:5432", "The server address and port (local machine, default PostgreSQL port)"],
    ["/stockpilot", "The database name"],
]
story.append(make_table(["Part", "Meaning"], url_parts, [1.8 * inch, CONTENT_W - 1.8 * inch]))

story.append(Paragraph("3.2 Configuration (app/core/config.py)", styles["H2"]))
story.append(Paragraph(
    "This file uses <b>pydantic-settings</b> to load the database URL from the .env file into a Python class. "
    "The <font face='Courier' size=9>Settings</font> class validates that the URL exists and is a valid string. "
    "It also loads other settings like the JWT secret key and token expiration times.",
    styles["Body"]))

story.append(Paragraph("3.3 The Declarative Base (app/db/base.py)", styles["H2"]))
story.append(Paragraph(
    "Every database model (table definition) inherits from a shared <b>Base</b> class. "
    "This Base class tells SQLAlchemy: 'any class that inherits from me represents a database table.' "
    "It also defines a <b>naming convention</b> for database constraints:",
    styles["Body"]))
naming_rows = [
    ["Index", "ix_%(column_0_label)s", "ix_users_email"],
    ["Unique constraint", "uq_%(table_name)s_%(column_0_name)s", "uq_users_email"],
    ["Check constraint", "ck_%(table_name)s_%(constraint_name)s", "ck_users_role_valid"],
    ["Foreign key", "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s", "fk_holdings_user_id_users"],
    ["Primary key", "pk_%(table_name)s", "pk_users"],
]
story.append(make_table(["Constraint Type", "Naming Pattern", "Example"],
                        naming_rows, [1.4 * inch, 2.6 * inch, CONTENT_W - 4.0 * inch]))

story.append(Paragraph("3.4 Engine & Session Factory (app/db/session.py)", styles["H2"]))
story.append(Paragraph(
    "This file creates two critical objects:",
    styles["Body"]))
story.append(Paragraph(
    "<b>1. Engine</b> - The connection pool to PostgreSQL. It manages a pool of up to 10 connections "
    "(with overflow up to 20 more). <font face='Courier' size=9>pool_pre_ping=True</font> means it checks "
    "if a connection is still alive before using it, preventing errors from stale connections.",
    styles["BulletItem"]))
story.append(Paragraph(
    "<b>2. Session Factory</b> - Creates individual database sessions for each request. "
    "<font face='Courier' size=9>expire_on_commit=False</font> means objects remain usable after a commit "
    "(without this, accessing an attribute after commit would trigger another database query).",
    styles["BulletItem"]))

story.append(Paragraph("3.5 The get_db() Dependency (app/db/session.py)", styles["H2"]))
story.append(Paragraph(
    "This is an <b>async generator</b> that FastAPI calls for every request that needs database access. It:",
    styles["Body"]))
story.append(Paragraph("1. Creates a new database session", styles["BulletItem"]))
story.append(Paragraph("2. Yields it to the endpoint handler (the handler runs its queries)", styles["BulletItem"]))
story.append(Paragraph("3. If the handler succeeds: commits all changes to the database", styles["BulletItem"]))
story.append(Paragraph("4. If the handler throws an exception: rolls back all changes (nothing is saved)", styles["BulletItem"]))
story.append(Paragraph("5. Always closes the session when done", styles["BulletItem"]))
story.append(Spacer(1, 6))
story.append(callout_box(
    "Why is this important?",
    "This pattern ensures <b>atomicity</b>: either ALL changes in a request succeed together, or NONE of them "
    "are saved. If something goes wrong halfway through (e.g., creating a listing but failing to update the strategy), "
    "the rollback ensures the database stays in a consistent state. No partial, broken data.",
    LIGHT_GREEN, BULL))

story.append(Paragraph("3.6 Startup Initialization (app/main.py)", styles["H2"]))
story.append(Paragraph(
    "When the FastAPI application starts, it runs <font face='Courier' size=9>Base.metadata.create_all</font> "
    "inside a <b>lifespan</b> context manager. This checks every model class registered with Base and creates "
    "any tables that don't already exist in the database. It does NOT modify existing tables (that's Alembic's job).",
    styles["Body"]))
story.append(PageBreak())

# ━━━━━━ CHAPTER 4: TABLE REFERENCE ━━━━━━
story.append(Paragraph("4. Complete Table Reference", styles["H1"]))
story.append(Paragraph(
    "StockPilot's database contains <b>11 tables</b>. This chapter documents every single one: "
    "what it stores, why it exists, every column and its type, and all relationships to other tables.",
    styles["Body"]))

# ── Helper for table docs ──
def table_doc(table_name, model_name, file_path, purpose, why, columns, relationships=None, enums=None, notes=None):
    elems = []
    elems.append(Paragraph(f'Table: {table_name}', styles["H2"]))
    elems.append(Paragraph(f'<b>Model class:</b> <font face="Courier" size=9>{model_name}</font> &nbsp; | &nbsp; '
                           f'<b>File:</b> <font face="Courier" size=9>{file_path}</font>', styles["Body"]))
    elems.append(callout_box("Purpose", purpose, LIGHT_GOLD, ACCENT))
    elems.append(Spacer(1, 6))
    elems.append(Paragraph(f"<b>Why does this table exist?</b> {why}", styles["Body"]))

    if enums:
        for ename, evalues in enums:
            elems.append(Paragraph(
                f'<b>Enum - {ename}:</b> {", ".join(evalues)}', styles["Body"]))

    col_widths = [1.3 * inch, 1.5 * inch, CONTENT_W - 4.2 * inch, 1.4 * inch]
    elems.append(make_table(
        ["Column", "Type", "Description", "Constraints"],
        columns, col_widths))

    if relationships:
        elems.append(Spacer(1, 6))
        elems.append(Paragraph("<b>Relationships:</b>", styles["BodyBold"]))
        for rel in relationships:
            elems.append(Paragraph(rel, styles["BulletItem"]))

    if notes:
        elems.append(Spacer(1, 6))
        elems.append(callout_box("Note", notes, LIGHT_BLUE, HexColor("#3b82f6")))

    elems.append(Spacer(1, 8))
    elems.append(section_divider())
    return elems


# 4.1 USERS
story.extend(table_doc(
    "users", "User", "app/db/models/user.py",
    "Stores every registered user account: their credentials, profile information, role, and account status.",
    "Every application needs to know who its users are. This table is the central identity store. "
    "It connects to almost every other table because users own holdings, make trades, create strategies, "
    "and receive notifications. The role system (investor/analyst/admin) controls access to different features.",
    [
        ["id", "UUID", "Unique identifier for each user, auto-generated", "PRIMARY KEY"],
        ["email", "String(320)", "User's email address, used for login", "UNIQUE, NOT NULL, INDEX"],
        ["password_hash", "String(200)", "Bcrypt-hashed password (never stored in plain text)", "NOT NULL"],
        ["full_name", "String(120)", "Display name shown in the UI", "NOT NULL"],
        ["role", "Enum(UserRole)", "Access level: investor, analyst, or admin", "NOT NULL, default=investor"],
        ["phone", "String(30)", "Optional phone number", "NULLABLE"],
        ["bio", "String(500)", "Short biography for the user's profile", "NULLABLE"],
        ["avatar_url", "String(500)", "Path to uploaded profile picture", "NULLABLE"],
        ["is_active", "Boolean", "Whether the account is active (admin can deactivate)", "NOT NULL, default=True"],
        ["created_at", "DateTime(tz)", "When the account was created", "server_default=now()"],
        ["updated_at", "DateTime(tz)", "Last time the profile was modified", "server_default=now(), auto-update"],
    ],
    [
        "<b>1:N to Watchlist</b> - A user can have many watchlist items",
        "<b>1:N to Holding</b> - A user can own many stock holdings",
        "<b>1:N to Trade</b> - A user can record many journal trades",
        "<b>1:N to Strategy</b> - A user can create many strategies",
        "<b>1:N to Notification</b> - A user receives many notifications",
    ],
    [("UserRole", ["investor", "analyst", "admin"])],
    "The password is never stored directly. The backend hashes it with bcrypt before saving. "
    "When a user logs in, the entered password is hashed and compared to the stored hash."
))

# 4.2 STOCKS
story.extend(table_doc(
    "stocks", "Stock", "app/db/models/stock.py",
    "A catalogue of all stocks tracked by the platform, with their ticker symbol, company name, sector, and industry.",
    "The application needs a master list of tradeable stocks. This table serves as the reference "
    "for ticker symbols used across holdings, watchlists, trades, and predictions. It also stores "
    "sector/industry data used for portfolio diversification analysis.",
    [
        ["id", "UUID", "Unique identifier", "PRIMARY KEY"],
        ["ticker", "String(10)", "Stock ticker symbol (e.g., AAPL, NVDA)", "UNIQUE, INDEX, NOT NULL"],
        ["name", "String(200)", "Full company name", "NOT NULL"],
        ["sector", "String(100)", "Market sector (e.g., Technology)", "NULLABLE"],
        ["industry", "String(100)", "Specific industry within the sector", "NULLABLE"],
        ["updated_at", "DateTime(tz)", "Last time stock info was refreshed", "server_default=now()"],
    ],
    notes="This table has no foreign key relationships. It is a standalone reference table. "
          "Other tables reference stocks by ticker string, not by foreign key, because ticker symbols "
          "are stable identifiers and this avoids complex join queries for simple lookups."
))

# 4.3 PRICE HISTORY
story.extend(table_doc(
    "price_history", "PriceHistory", "app/db/models/stock.py",
    "Stores historical daily OHLCV (Open, High, Low, Close, Volume) price data for each stock.",
    "The AI/ML models (XGBoost) need historical price data to compute technical indicators like "
    "moving averages, RSI, and MACD. This table caches that data locally so the system doesn't need "
    "to fetch it from Yahoo Finance every time. It also powers the price history charts in the UI.",
    [
        ["ticker", "String(10)", "Stock ticker symbol", "COMPOSITE PK (part 1)"],
        ["date", "Date", "The trading date", "COMPOSITE PK (part 2)"],
        ["open", "Numeric(18,4)", "Opening price for the day", "NOT NULL"],
        ["high", "Numeric(18,4)", "Highest price during the day", "NOT NULL"],
        ["low", "Numeric(18,4)", "Lowest price during the day", "NOT NULL"],
        ["close", "Numeric(18,4)", "Closing price for the day", "NOT NULL"],
        ["volume", "BigInteger", "Number of shares traded", "NOT NULL"],
    ],
    notes="This is the only table with a <b>composite primary key</b> (ticker + date together). "
          "This means there can only be one price record per stock per day, which makes sense because "
          "a stock has exactly one set of OHLCV values for each trading day."
))

# 4.4 PREDICTIONS
story.extend(table_doc(
    "predictions", "Prediction", "app/db/models/prediction.py",
    "Stores AI-generated stock predictions: the signal (BUY/HOLD/SELL), confidence level, "
    "probability estimates, and composite score from the XGBoost model.",
    "This is the output of the AI engine. Each time the model analyses a stock, it creates a prediction "
    "record. The frontend reads these predictions to show the verdict cards, confidence bars, and "
    "signal badges. Historical predictions are kept for backtesting and model evaluation.",
    [
        ["id", "UUID", "Unique identifier", "PRIMARY KEY"],
        ["ticker", "String(10)", "Stock ticker being predicted", "INDEX, NOT NULL"],
        ["signal", "Enum(SignalType)", "BUY, HOLD, or SELL recommendation", "NOT NULL"],
        ["confidence", "Numeric(5,2)", "Model confidence (0-100%)", "NOT NULL"],
        ["probability_up", "Numeric(5,2)", "Probability the stock price will go up", "NOT NULL"],
        ["probability_down", "Numeric(5,2)", "Probability the stock price will go down", "NOT NULL"],
        ["composite_score", "Integer", "Combined 6-factor score (0-100)", "NULLABLE"],
        ["model_version", "String(50)", "Which AI model version generated this", "NOT NULL, default='xgboost_v1'"],
        ["created_at", "DateTime(tz)", "When this prediction was made", "server_default=now()"],
    ],
    enums=[("SignalType", ["BUY", "HOLD", "SELL"])],
    notes="Predictions are standalone records without foreign keys to stocks. They reference stocks "
          "by ticker string. The model_version column allows tracking which version of the AI generated "
          "each prediction, important when the model is retrained and improved over time."
))

story.append(PageBreak())

# 4.5 HOLDINGS
story.extend(table_doc(
    "holdings", "Holding", "app/db/models/portfolio.py",
    "Tracks each stock position a user currently holds: how many shares, at what average cost, "
    "and the current market price.",
    "The portfolio feature needs to know what stocks each user owns. Each row represents one stock position. "
    "The avg_cost and current_price columns enable calculating unrealised profit/loss. "
    "The closed_at column allows marking positions as sold without deleting the historical record.",
    [
        ["id", "UUID", "Unique identifier", "PRIMARY KEY"],
        ["user_id", "UUID", "Which user owns this holding", "FK -> users.id, CASCADE, NOT NULL"],
        ["ticker", "String(10)", "Stock ticker symbol", "NOT NULL"],
        ["quantity", "Numeric(18,4)", "Number of shares held", "NOT NULL"],
        ["avg_cost", "Numeric(18,4)", "Average purchase price per share", "NOT NULL"],
        ["current_price", "Numeric(18,4)", "Latest market price (updated on fetch)", "NULLABLE"],
        ["opened_at", "DateTime(tz)", "When the position was opened", "server_default=now()"],
        ["closed_at", "DateTime(tz)", "When the position was closed (NULL if still open)", "NULLABLE"],
    ],
    ["<b>N:1 to User</b> - Many holdings belong to one user (user_id -> users.id)"],
))

# 4.6 WATCHLIST
story.extend(table_doc(
    "watchlist", "Watchlist", "app/db/models/watchlist.py",
    "Stores which stocks each user is watching. A simple 'favourites' list.",
    "Users want to monitor stocks without necessarily owning them. The watchlist lets them track "
    "tickers they're interested in and see AI predictions for those stocks on the dashboard. "
    "The unique constraint on (user_id, ticker) prevents a user from adding the same stock twice.",
    [
        ["id", "UUID", "Unique identifier", "PRIMARY KEY"],
        ["user_id", "UUID", "Which user added this to their watchlist", "FK -> users.id, CASCADE, NOT NULL"],
        ["ticker", "String(10)", "Stock ticker symbol", "NOT NULL"],
        ["added_at", "DateTime(tz)", "When the stock was added to the watchlist", "server_default=now()"],
    ],
    ["<b>N:1 to User</b> - Many watchlist items belong to one user"],
    notes="Has a <b>UniqueConstraint('user_id', 'ticker')</b> to prevent duplicate entries. "
          "If a user tries to add AAPL twice, the database will reject the second insert."
))

# 4.7 TRADES
story.extend(table_doc(
    "trades", "Trade", "app/db/models/trade.py",
    "The trading journal: records every completed trade a user logs, with entry/exit prices, "
    "quantity, strategy used, and optional notes.",
    "A trading journal is essential for serious investors. It lets users review their past trades, "
    "calculate statistics (win rate, profit factor, net P/L), and learn from their decisions. "
    "The equity curve chart on the Journal page is built from this data.",
    [
        ["id", "UUID", "Unique identifier", "PRIMARY KEY"],
        ["user_id", "UUID", "Who made this trade", "FK -> users.id, CASCADE, NOT NULL"],
        ["ticker", "String(10)", "Stock ticker traded", "INDEX, NOT NULL"],
        ["side", "Enum(TradeSide)", "Whether this was a buy or sell", "NOT NULL"],
        ["entry_price", "Numeric(18,4)", "Price at which the position was opened", "NOT NULL"],
        ["exit_price", "Numeric(18,4)", "Price at which the position was closed", "NOT NULL"],
        ["stop_loss", "Numeric(18,4)", "Stop-loss price level set for this trade", "NULLABLE"],
        ["take_profit", "Numeric(18,4)", "Take-profit target price", "NULLABLE"],
        ["quantity", "Numeric(18,4)", "Number of shares traded", "NOT NULL"],
        ["strategy_label", "String(80)", "Which strategy was used for this trade", "NULLABLE"],
        ["opened_at", "DateTime(tz)", "When the trade was opened", "NOT NULL"],
        ["closed_at", "DateTime(tz)", "When the trade was closed", "NOT NULL"],
        ["notes", "Text", "User's personal notes about this trade", "NULLABLE"],
        ["created_at", "DateTime(tz)", "When this record was created", "server_default=now()"],
    ],
    ["<b>N:1 to User</b> - Many trades belong to one user"],
    [("TradeSide", ["buy", "sell"])],
))

story.append(PageBreak())

# 4.8 STRATEGIES
story.extend(table_doc(
    "strategies", "Strategy", "app/db/models/strategy.py",
    "Stores factor weight configurations: custom or preset combinations of the 6 scoring factors "
    "(sentiment, momentum, valuation, volatility, volume, growth).",
    "The AI advisor uses a 6-factor scoring system where each factor has a weight (percentage). "
    "Different weight combinations suit different investment styles. Users create custom strategies, "
    "and the platform ships preset strategies. Analysts can publish strategies to the marketplace "
    "to earn revenue from sales.",
    [
        ["id", "UUID", "Unique identifier", "PRIMARY KEY"],
        ["owner_id", "UUID", "Who created this strategy (NULL for system presets)", "FK -> users.id, CASCADE, NULLABLE"],
        ["name", "String(80)", "Display name for the strategy", "NOT NULL"],
        ["description", "Text", "Detailed description of the strategy's approach", "NULLABLE"],
        ["weights", "JSONB", "Factor weights as JSON: {sentiment: 20, momentum: 30, ...}", "NOT NULL"],
        ["is_preset", "Boolean", "Whether this is a system-provided preset", "NOT NULL, default=False"],
        ["is_published", "Boolean", "Whether this is listed on the marketplace", "NOT NULL, default=False"],
        ["created_at", "DateTime(tz)", "When the strategy was created", "server_default=now()"],
        ["updated_at", "DateTime(tz)", "Last modification time", "server_default=now(), auto-update"],
    ],
    [
        "<b>N:1 to User</b> - Many strategies can be owned by one user (owner_id -> users.id)",
        "<b>1:1 to MarketplaceListing</b> - A strategy can have at most one marketplace listing",
    ],
    notes="The <b>weights</b> column uses PostgreSQL's JSONB type, which stores structured JSON data efficiently. "
          "Example value: {\"sentiment\": 20, \"momentum\": 25, \"valuation\": 15, \"volatility\": 10, \"volume\": 15, \"growth\": 15}. "
          "owner_id is NULLABLE because system preset strategies have no owner."
))

# 4.9 MARKETPLACE LISTINGS
story.extend(table_doc(
    "marketplace_listings", "MarketplaceListing", "app/db/models/marketplace.py",
    "Represents a strategy published on the marketplace: its price, approval status, ratings, "
    "sales count, and complete backtest performance results.",
    "The marketplace is how analysts monetise their strategies. When an analyst publishes a strategy, "
    "a listing record is created with status='review'. An admin reviews the backtest results and either "
    "approves it (status='verified') or rejects it (status='removed'). The listing tracks sales revenue "
    "and user ratings over time.",
    [
        ["id", "UUID", "Unique identifier", "PRIMARY KEY"],
        ["strategy_id", "UUID", "Which strategy this listing is for", "FK -> strategies.id, UNIQUE, NOT NULL"],
        ["price_cents", "Integer", "Price in cents (e.g., 999 = $9.99). 0 = free", "NOT NULL, default=0"],
        ["status", "Enum(ListingStatus)", "Approval status: draft/review/verified/listed/removed", "NOT NULL, default=draft"],
        ["avg_rating", "Numeric(3,2)", "Average user rating (1.00 to 5.00)", "NULLABLE"],
        ["rating_count", "Integer", "How many users have rated this strategy", "NOT NULL, default=0"],
        ["sales_count", "Integer", "How many times this strategy has been purchased", "NOT NULL, default=0"],
        ["backtest_return", "Numeric(6,3)", "Backtest total return (e.g., 0.245 = 24.5%)", "NULLABLE"],
        ["backtest_sharpe", "Numeric(6,3)", "Backtest Sharpe ratio (risk-adjusted return)", "NULLABLE"],
        ["backtest_winrate", "Numeric(4,3)", "Backtest win rate (e.g., 0.680 = 68%)", "NULLABLE"],
        ["backtest_trades", "Integer", "Total number of trades in the backtest", "NULLABLE"],
        ["backtest_max_drawdown", "Numeric(5,4)", "Maximum drawdown during backtest (e.g., 0.1200 = 12%)", "NULLABLE"],
        ["backtest_profit_factor", "Numeric(5,2)", "Ratio of gross profits to gross losses", "NULLABLE"],
        ["listed_at", "DateTime(tz)", "When the listing was approved and went live", "NULLABLE"],
        ["created_at", "DateTime(tz)", "When the listing was first created", "server_default=now()"],
    ],
    [
        "<b>N:1 to Strategy</b> - Each listing belongs to exactly one strategy (1:1 enforced by UNIQUE constraint)",
        "<b>1:N to MarketplaceRating</b> - A listing can receive many user ratings/reviews",
    ],
    [("ListingStatus", ["draft", "review", "verified", "listed", "removed"])],
    "The strategy_id has a UNIQUE constraint, meaning each strategy can have at most one listing. "
    "This makes the relationship effectively 1:1. Prices are stored in cents (integers) to avoid "
    "floating-point rounding errors that plague currency calculations."
))

# 4.10 MARKETPLACE RATINGS
story.extend(table_doc(
    "marketplace_ratings", "MarketplaceRating", "app/db/models/marketplace.py",
    "Stores user ratings and reviews for marketplace strategies.",
    "After purchasing and using a strategy, users can leave a rating (1-5 stars) and an optional "
    "text review. These ratings help other users decide which strategies to buy and create "
    "accountability for strategy creators.",
    [
        ["id", "UUID", "Unique identifier", "PRIMARY KEY"],
        ["listing_id", "UUID", "Which listing is being rated", "FK -> marketplace_listings.id, CASCADE, NOT NULL"],
        ["user_id", "UUID", "Who wrote this rating", "FK -> users.id, CASCADE, NOT NULL"],
        ["rating", "Integer", "Star rating (1 to 5)", "NOT NULL"],
        ["review", "String(500)", "Optional text review", "NULLABLE"],
        ["created_at", "DateTime(tz)", "When the rating was submitted", "server_default=now()"],
    ],
    [
        "<b>N:1 to MarketplaceListing</b> - Many ratings belong to one listing",
        "<b>N:1 to User</b> - Many ratings come from different users (FK only, no ORM relationship)",
    ],
))

# 4.11 NOTIFICATIONS
story.extend(table_doc(
    "notifications", "Notification", "app/db/models/notification.py",
    "Stores in-app notifications for users: verdict changes, price alerts, marketplace events, "
    "security alerts, and system messages.",
    "Users need to be informed about important events: a stock's prediction changed, a strategy was "
    "approved, a security event occurred, etc. Each notification has a 'kind' that determines its icon "
    "and category in the UI, plus a read/unread status for the notification bell badge.",
    [
        ["id", "UUID", "Unique identifier", "PRIMARY KEY"],
        ["user_id", "UUID", "Which user receives this notification", "FK -> users.id, CASCADE, NOT NULL"],
        ["kind", "Enum(NotificationKind)", "Category of notification", "NOT NULL"],
        ["title", "String(200)", "Short notification title", "NOT NULL"],
        ["body", "Text", "Detailed notification content", "NULLABLE"],
        ["is_read", "Boolean", "Whether the user has seen this", "NOT NULL, default=False"],
        ["created_at", "DateTime(tz)", "When the notification was created", "server_default=now()"],
    ],
    ["<b>N:1 to User</b> - Many notifications belong to one user"],
    [("NotificationKind", ["verdict_change", "price_alert", "marketplace", "weekly_report", "security", "system"])],
))

story.append(PageBreak())

# ━━━━━━ CHAPTER 5: ENUMS ━━━━━━
story.append(Paragraph("5. Enumerations (Enums)", styles["H1"]))
story.append(Paragraph(
    "Enums are restricted value sets. Instead of allowing any string in a column, an enum limits "
    "the column to a specific set of valid values. This prevents invalid data from entering the database.",
    styles["Body"]))

enum_rows = [
    ["UserRole", "User.role", "investor, analyst, admin",
     "Controls access: investors trade, analysts publish strategies, admins manage everything"],
    ["SignalType", "Prediction.signal", "BUY, HOLD, SELL",
     "The three possible AI recommendations for a stock"],
    ["TradeSide", "Trade.side", "buy, sell",
     "Whether the user bought or sold shares in a journal entry"],
    ["ListingStatus", "MarketplaceListing.status", "draft, review, verified, listed, removed",
     "Tracks the lifecycle of a marketplace listing from creation through approval to potential removal"],
    ["NotificationKind", "Notification.kind", "verdict_change, price_alert, marketplace, weekly_report, security, system",
     "Categorises notifications so the UI can show the right icon and filter by type"],
]
story.append(make_table(["Enum Name", "Used By", "Values", "Purpose"],
                        enum_rows, [1.2 * inch, 1.4 * inch, 1.8 * inch, CONTENT_W - 4.4 * inch]))
story.append(PageBreak())

# ━━━━━━ CHAPTER 6: ER MAP ━━━━━━
story.append(Paragraph("6. Entity-Relationship Map", styles["H1"]))
story.append(Paragraph(
    "This diagram shows how all 11 tables connect to each other. Arrows indicate foreign key relationships, "
    "and labels show the cardinality (how many records on each side).",
    styles["Body"]))

er_rows = [
    ["User", "1 : N", "Watchlist", "user_id FK", "A user can watch many stocks"],
    ["User", "1 : N", "Holding", "user_id FK", "A user can hold many stock positions"],
    ["User", "1 : N", "Trade", "user_id FK", "A user can log many trades"],
    ["User", "1 : N", "Strategy", "owner_id FK", "A user can create many strategies"],
    ["User", "1 : N", "Notification", "user_id FK", "A user receives many notifications"],
    ["Strategy", "1 : 1", "MarketplaceListing", "strategy_id FK (UNIQUE)", "A strategy can have at most one listing"],
    ["MarketplaceListing", "1 : N", "MarketplaceRating", "listing_id FK", "A listing can receive many ratings"],
    ["User", "1 : N", "MarketplaceRating", "user_id FK", "A user can rate many listings"],
]
story.append(make_table(
    ["Parent Table", "Cardinality", "Child Table", "FK Column", "Meaning"],
    er_rows,
    [1.1 * inch, 0.7 * inch, 1.4 * inch, 1.5 * inch, CONTENT_W - 4.7 * inch]))
story.append(Spacer(1, 12))

story.append(Paragraph("<b>Standalone Tables (No Foreign Keys):</b>", styles["BodyBold"]))
story.append(Paragraph(
    "<b>Stock</b> - Reference catalogue of ticker symbols. Other tables use the ticker string directly.",
    styles["BulletItem"]))
story.append(Paragraph(
    "<b>PriceHistory</b> - Historical OHLCV data. Referenced by ticker string, not by FK.",
    styles["BulletItem"]))
story.append(Paragraph(
    "<b>Prediction</b> - AI model outputs. Referenced by ticker string, not by FK.",
    styles["BulletItem"]))

story.append(Spacer(1, 12))
story.append(callout_box(
    "Why don't Stock, PriceHistory, and Prediction use foreign keys?",
    "These tables use ticker strings (like 'AAPL') as the linking field instead of foreign keys to the stocks table. "
    "This is a pragmatic design choice: ticker symbols are stable, human-readable identifiers that are also "
    "used by external APIs (Yahoo Finance). Using FKs would require JOIN queries every time you want to look up "
    "a stock's data, adding complexity with no real benefit since ticker symbols don't change.",
    LIGHT_BLUE, HexColor("#3b82f6")))
story.append(PageBreak())

# ━━━━━━ CHAPTER 7: CARDINALITY ━━━━━━
story.append(Paragraph("7. Cardinality Ratios Explained", styles["H1"]))
story.append(Paragraph(
    "Cardinality describes how many records on one side of a relationship can be associated "
    "with records on the other side. Understanding this is crucial for database design.",
    styles["Body"]))

card_types = [
    ["1:1 (One-to-One)", "Each record in Table A relates to at most one record in Table B, and vice versa.",
     "Strategy <-> MarketplaceListing. Each strategy can have at most one listing (enforced by a UNIQUE constraint on strategy_id). A listing always belongs to exactly one strategy.",
     "Used when you want to split a single entity's data across two tables, either for separation of concerns or because the second table is optional."],
    ["1:N (One-to-Many)", "One record in the parent table can relate to many records in the child table, but each child belongs to exactly one parent.",
     "User -> Holdings. One user can have many holdings, but each holding belongs to exactly one user. The foreign key (user_id) lives in the child table (holdings).",
     "The most common relationship type. Used whenever one entity 'owns' or 'contains' multiple instances of another entity."],
    ["N:1 (Many-to-One)", "The inverse perspective of 1:N. Many children point to one parent.",
     "MarketplaceRating -> MarketplaceListing. Many ratings point to one listing. This is 1:N seen from the ratings side.",
     "Technically identical to 1:N, just described from the child's perspective."],
]
for row in card_types:
    story.append(Paragraph(row[0], styles["H2"]))
    story.append(Paragraph(f"<b>Definition:</b> {row[1]}", styles["Body"]))
    story.append(Paragraph(f"<b>Example in StockPilot:</b> {row[2]}", styles["Body"]))
    story.append(Paragraph(f"<b>When to use:</b> {row[3]}", styles["Body"]))

story.append(Spacer(1, 10))
story.append(Paragraph("Cascade Deletes", styles["H2"]))
story.append(Paragraph(
    "When a parent record is deleted, what happens to its children? StockPilot uses <b>ON DELETE CASCADE</b> "
    "on most foreign keys. This means: if a user is deleted, all their holdings, trades, strategies, "
    "notifications, and watchlist items are automatically deleted too. This prevents 'orphan' records "
    "that point to a user that no longer exists.",
    styles["Body"]))

cascade_rows = [
    ["users.id", "holdings, watchlist, trades, strategies, notifications", "CASCADE", "Deleting a user removes all their data"],
    ["marketplace_listings.id", "marketplace_ratings", "CASCADE", "Deleting a listing removes all its ratings"],
    ["strategies.id", "marketplace_listings", "RESTRICT (default)", "Cannot delete a strategy that has a listing (must delete listing first)"],
]
story.append(make_table(
    ["Parent PK", "Child Tables Affected", "Delete Rule", "Effect"],
    cascade_rows, [1.3 * inch, 2.0 * inch, 1.2 * inch, CONTENT_W - 4.5 * inch]))
story.append(PageBreak())

# ━━━━━━ CHAPTER 8: BACKEND CODE FILES ━━━━━━
story.append(Paragraph("8. Backend Code Files & Database Interactions", styles["H1"]))
story.append(Paragraph(
    "This chapter documents every backend code file that directly interacts with the database. "
    "For each file, we explain what it does, which tables it queries, and what operations it performs.",
    styles["Body"]))

# Helper for endpoint docs
def endpoint_doc(file_path, prefix, description, endpoints):
    elems = []
    elems.append(Paragraph(f"File: {file_path}", styles["H2"]))
    elems.append(Paragraph(f"<b>Route prefix:</b> <font face='Courier' size=9>{prefix}</font>", styles["Body"]))
    elems.append(Paragraph(description, styles["Body"]))
    elems.append(make_table(
        ["Endpoint", "Tables Used", "Operations", "What It Does"],
        endpoints,
        [1.6 * inch, 1.2 * inch, 1.0 * inch, CONTENT_W - 3.8 * inch]))
    elems.append(Spacer(1, 8))
    return elems

# Auth
story.extend(endpoint_doc(
    "app/api/v1/endpoints/auth.py", "/api/v1/auth",
    "Handles user authentication: login with email/password, registration, and token refresh. "
    "Issues JWT (JSON Web Token) access and refresh tokens stored in the frontend.",
    [
        ["POST /login", "users", "SELECT", "Finds user by email, verifies password hash, returns JWT tokens"],
        ["POST /register", "users", "SELECT, INSERT", "Checks for duplicate email, creates new user with hashed password"],
        ["POST /refresh", "users", "SELECT", "Validates refresh token, finds user by ID, issues new access token"],
    ]))

# Users
story.extend(endpoint_doc(
    "app/api/v1/endpoints/users.py", "/api/v1/users",
    "User profile management: view and edit profile, change password, upload/remove avatar.",
    [
        ["GET /me", "users", "SELECT", "Returns current user profile (from JWT dependency)"],
        ["PUT /me", "users", "UPDATE", "Updates full_name, email, phone, bio fields"],
        ["PUT /me/password", "users", "UPDATE", "Verifies old password, sets new password_hash"],
        ["POST /me/avatar", "users", "UPDATE", "Saves uploaded file, updates avatar_url"],
        ["DELETE /me/avatar", "users", "UPDATE", "Deletes file, sets avatar_url to NULL"],
    ]))

# Stocks
story.extend(endpoint_doc(
    "app/api/v1/endpoints/stocks.py", "/api/v1/stocks",
    "Stock catalogue and historical price data retrieval.",
    [
        ["GET /", "stocks", "SELECT", "Returns all stocks ordered by ticker"],
        ["GET /{ticker}", "stocks", "SELECT", "Returns one stock by ticker symbol"],
        ["GET /{ticker}/history", "price_history", "SELECT", "Returns OHLCV price data for the last N days"],
    ]))

# Predictions
story.extend(endpoint_doc(
    "app/api/v1/endpoints/predictions.py", "/api/v1/predictions",
    "AI prediction retrieval. These endpoints read prediction records; the AI engine writes them separately.",
    [
        ["GET /", "predictions", "SELECT", "Returns all predictions (newest first)"],
        ["GET /{ticker}", "predictions", "SELECT", "Returns the latest prediction for a specific ticker"],
    ]))

story.append(PageBreak())

# Portfolio
story.extend(endpoint_doc(
    "app/api/v1/endpoints/portfolio.py", "/api/v1/portfolio",
    "Portfolio management: view holdings, add new positions, update quantities, close positions. "
    "Also fetches live prices from Yahoo Finance and joins with stock names.",
    [
        ["GET /", "holdings, stocks", "SELECT", "Lists open holdings with live prices and stock names"],
        ["POST /", "holdings", "INSERT", "Creates a new holding with current market price"],
        ["PUT /{id}", "holdings", "SELECT, UPDATE", "Updates quantity or average cost of a holding"],
        ["DELETE /{id}", "holdings", "SELECT, DELETE", "Removes a holding record"],
    ]))

# Watchlist
story.extend(endpoint_doc(
    "app/api/v1/endpoints/watchlist.py", "/api/v1/watchlist",
    "Watchlist management: add and remove stocks from the user's watch list.",
    [
        ["GET /", "watchlist", "SELECT", "Lists all watched tickers for the current user"],
        ["POST /", "watchlist", "SELECT, INSERT", "Adds a ticker (checks for duplicates first)"],
        ["DELETE /{ticker}", "watchlist", "SELECT, DELETE", "Removes a ticker from the watchlist"],
    ]))

# Trades
story.extend(endpoint_doc(
    "app/api/v1/endpoints/trades.py", "/api/v1/trades",
    "Trading journal: log completed trades with entry/exit prices, strategy, and notes.",
    [
        ["GET /", "trades", "SELECT", "Lists all trades for the user (newest closed first)"],
        ["POST /", "trades", "INSERT", "Records a new trade with all fields"],
        ["DELETE /{id}", "trades", "SELECT, DELETE", "Deletes a trade journal entry"],
    ]))

# Strategies
story.extend(endpoint_doc(
    "app/api/v1/endpoints/strategies.py", "/api/v1/strategies",
    "Strategy CRUD and marketplace publishing. Users create, edit, and delete strategies. "
    "Analysts can submit strategies for marketplace review after passing backtest thresholds.",
    [
        ["GET /", "strategies", "SELECT", "Lists user's own strategies + system presets"],
        ["POST /", "strategies", "INSERT", "Creates a new strategy with factor weights"],
        ["PUT /{id}", "strategies", "SELECT, UPDATE", "Updates name, description, or weights"],
        ["DELETE /{id}", "strategies", "SELECT, DELETE", "Deletes a strategy"],
        ["POST /{id}/publish", "strategies, marketplace_listings", "SELECT, INSERT/UPDATE",
         "Validates 5 backtest thresholds, creates/updates listing with status=review"],
    ]))

story.append(PageBreak())

# Notifications
story.extend(endpoint_doc(
    "app/api/v1/endpoints/notifications.py", "/api/v1/notifications",
    "In-app notification management: fetch recent notifications and mark them as read.",
    [
        ["GET /", "notifications", "SELECT", "Returns last 50 notifications for the user"],
        ["PUT /{id}/read", "notifications", "SELECT, UPDATE", "Marks a single notification as read"],
        ["PUT /read-all", "notifications", "BULK UPDATE", "Marks all unread notifications as read at once"],
    ]))

# Marketplace
story.extend(endpoint_doc(
    "app/api/v1/endpoints/marketplace.py", "/api/v1/marketplace",
    "Public marketplace listing retrieval. Uses eager loading to include strategy details and creator info.",
    [
        ["GET /", "marketplace_listings, strategies, users", "SELECT (eager load)",
         "Lists all marketplace listings with strategy names, weights, and owner names via selectinload()"],
    ]))

# Dashboard
story.extend(endpoint_doc(
    "app/api/v1/endpoints/dashboard.py", "/api/v1/dashboard",
    "Dashboard aggregation endpoints. Combines data from multiple tables plus live market data.",
    [
        ["GET /market-indices", "(none)", "—", "Fetches live index data from Yahoo Finance (no DB)"],
        ["GET /sector-breakdown", "holdings, stocks", "SELECT", "Calculates portfolio allocation by sector"],
        ["GET /portfolio-history", "trades, holdings", "SELECT", "Reconstructs monthly P&L curve from trades"],
        ["GET /batch", "(all above)", "SELECT", "Calls all three endpoints in parallel via asyncio.gather"],
    ]))

# Admin
story.extend(endpoint_doc(
    "app/api/v1/endpoints/admin.py", "/api/v1/admin",
    "Full administrative control panel. Requires admin role. Manages users, strategies, listings, and revenue.",
    [
        ["GET /stats", "users, strategies, marketplace_listings", "COUNT, SUM",
         "Aggregate stats: user count, strategy count, pending reviews, revenue totals"],
        ["GET /revenue", "marketplace_listings, strategies, users", "SELECT (eager)",
         "Revenue breakdown with top 10 earning strategies"],
        ["GET /users", "users", "SELECT", "Lists all users with role and status"],
        ["PATCH /users/{id}/role", "users", "SELECT, UPDATE", "Changes a user's role"],
        ["PATCH /users/{id}/status", "users", "SELECT, UPDATE", "Toggles a user's active/inactive status"],
        ["DELETE /users/{id}", "users", "SELECT, DELETE", "Permanently deletes a user account"],
        ["GET /pending", "marketplace_listings, strategies, users", "SELECT (eager)",
         "Lists strategies awaiting admin review with full backtest report"],
        ["GET /listings", "marketplace_listings, strategies, users", "SELECT (eager)", "Lists all marketplace listings"],
        ["GET /strategies", "strategies, users", "SELECT (eager)", "Lists all strategies with owner info"],
        ["POST /listings/{id}/approve", "marketplace_listings, strategies", "SELECT, UPDATE",
         "Sets status to verified, marks strategy as published, records listed_at timestamp"],
        ["POST /listings/{id}/reject", "marketplace_listings, strategies", "SELECT, UPDATE",
         "Sets status to removed, marks strategy as unpublished"],
        ["POST /listings/{id}/remove", "marketplace_listings, strategies", "SELECT, UPDATE",
         "Delists any active listing (not just pending ones)"],
        ["DELETE /listings/{id}", "marketplace_listings, strategies", "SELECT, DELETE",
         "Permanently deletes a listing and unpublishes the strategy"],
        ["DELETE /strategies/{id}", "strategies, marketplace_listings", "SELECT, DELETE",
         "Deletes a strategy and its listing (if any)"],
    ]))

story.append(PageBreak())

# Non-DB endpoints note
story.append(Paragraph("Files With No Database Interaction", styles["H2"]))
story.append(Paragraph(
    "These endpoint files exist in the backend but do not interact with the database at all:",
    styles["Body"]))
no_db_rows = [
    ["app/api/v1/endpoints/live.py", "/api/v1/live", "Fetches real-time stock quotes from Yahoo Finance via yfinance"],
    ["app/api/v1/endpoints/sentiment.py", "/api/v1/sentiment", "Runs FinBERT NLP sentiment analysis on news headlines from Yahoo Finance"],
    ["app/api/v1/endpoints/analysis.py", "/api/v1/analysis", "Computes the 6-factor composite score using technical indicators, FinBERT, and yfinance data"],
]
story.append(make_table(["File", "Route Prefix", "What It Does Instead"],
                        no_db_rows, [2.0 * inch, 1.2 * inch, CONTENT_W - 3.2 * inch]))

# Core dependencies
story.append(Paragraph("Core Dependencies (app/core/dependencies.py)", styles["H2"]))
story.append(Paragraph(
    "This file provides two FastAPI <b>dependencies</b> that are used by almost every endpoint:",
    styles["Body"]))
story.append(Paragraph(
    "<b>get_current_user:</b> Extracts the JWT token from the Authorization header, decodes it, "
    "reads the user ID from the token's 'sub' claim, then queries "
    "<font face='Courier' size=9>SELECT * FROM users WHERE id = ...</font> to load the full user object. "
    "Returns 401 Unauthorized if the token is invalid or the user doesn't exist.",
    styles["BulletItem"]))
story.append(Paragraph(
    "<b>require_role(*roles):</b> A factory that returns a dependency. It calls get_current_user first, "
    "then checks if the user's role is in the allowed list. Returns 403 Forbidden if not. "
    "Example: <font face='Courier' size=9>require_role(UserRole.admin)</font> restricts an endpoint to admins only.",
    styles["BulletItem"]))
story.append(PageBreak())

# ━━━━━━ CHAPTER 9: SEED SCRIPT ━━━━━━
story.append(Paragraph("9. The Seed Script", styles["H1"]))
story.append(Paragraph(
    "The seed script (<font face='Courier' size=9>backend/seed.py</font>) populates the database with "
    "realistic test data for development. It runs synchronously and:",
    styles["Body"]))

seed_steps = [
    ["1", "Drop & recreate", "Drops all tables and recreates them from the model definitions. WARNING: this destroys all existing data."],
    ["2", "Create users", "Creates 5 users: 1 demo investor, 1 admin, and 3 analysts. Passwords are bcrypt-hashed."],
    ["3", "Create stocks", "Inserts 10 stocks: AAPL, NVDA, MSFT, GOOGL, AMZN, TSLA, META, AMD, PLTR, COIN with real sector/industry data."],
    ["4", "Create predictions", "Generates 10 AI predictions (one per stock) with realistic signal, confidence, and probability values."],
    ["5", "Create holdings", "Adds 6 stock positions to the demo user's portfolio with varying quantities and costs."],
    ["6", "Create watchlist", "Adds 4 stocks to the demo user's watchlist."],
    ["7", "Create trades", "Logs 15 historical trades for the demo user spanning December 2025 to June 2026."],
    ["8", "Create strategies", "Creates 5 strategies (mix of presets and analyst-created) with marketplace listings. 4 verified, 1 in review."],
    ["9", "Create notifications", "Generates 8 notifications for the demo user across different kinds."],
]
story.append(make_table(["Step", "Action", "Details"], seed_steps,
                        [0.5 * inch, 1.3 * inch, CONTENT_W - 1.8 * inch]))
story.append(Spacer(1, 10))
story.append(callout_box(
    "Default Login Credentials (from seed)",
    "Demo user: demo@stockpilot.io / demo1234 (investor role)<br/>"
    "Admin: admin@stockpilot.io / admin1234 (admin role)<br/>"
    "Analysts: sarah@stockpilot.io, james@stockpilot.io, alex@stockpilot.io / analyst1234",
    LIGHT_GOLD, ACCENT))
story.append(PageBreak())

# ━━━━━━ CHAPTER 10: MIGRATIONS ━━━━━━
story.append(Paragraph("10. Alembic Migrations", styles["H1"]))
story.append(Paragraph(
    "Alembic is the migration tool that manages database schema changes over time. Instead of "
    "modifying the database directly, developers create migration scripts that can be applied (upgrade) "
    "or reversed (downgrade) in a controlled way.",
    styles["Body"]))

story.append(Paragraph("10.1 How Alembic Works", styles["H2"]))
story.append(Paragraph(
    "Alembic maintains a version history in the database itself (in a table called alembic_version). "
    "Each migration has a unique revision ID and knows which migration comes before it (down_revision). "
    "This creates a chain: initial -> add_backtest_fields -> (future migrations).",
    styles["Body"]))

story.append(Paragraph("10.2 Configuration (alembic/env.py)", styles["H2"]))
story.append(Paragraph(
    "The env.py file is Alembic's runtime configuration. It loads the database URL from settings, "
    "replaces <font face='Courier' size=9>+asyncpg</font> with <font face='Courier' size=9>+psycopg2</font> "
    "(because Alembic runs synchronously), and sets <font face='Courier' size=9>target_metadata = Base.metadata</font> "
    "so Alembic can compare the model definitions to the actual database and auto-generate migrations.",
    styles["Body"]))

story.append(Paragraph("10.3 Migration History", styles["H2"]))
migration_rows = [
    ["f78f1f226fbd", "(none)", "2026-07-05", "Initial schema",
     "Creates all 11 tables, all indexes, all foreign keys, all enums. This is the foundation."],
    ["a2b3c4d5e6f7", "f78f1f226fbd", "2026-07-18", "Add backtest fields",
     "Adds 3 columns to marketplace_listings: backtest_trades (Integer), backtest_max_drawdown (Numeric), backtest_profit_factor (Numeric). Needed for full backtest report in admin review."],
]
story.append(make_table(
    ["Revision ID", "Revises", "Date", "Name", "What It Does"],
    migration_rows,
    [1.2 * inch, 1.0 * inch, 0.8 * inch, 1.0 * inch, CONTENT_W - 4.0 * inch]))
story.append(PageBreak())

# ━━━━━━ CHAPTER 11: QUERY PATTERNS ━━━━━━
story.append(Paragraph("11. Query Patterns & Best Practices", styles["H1"]))
story.append(Paragraph(
    "The codebase follows consistent patterns for database operations. Understanding these patterns "
    "makes the entire backend predictable and easy to read.",
    styles["Body"]))

story.append(Paragraph("11.1 The SELECT Pattern", styles["H2"]))
story.append(Paragraph(
    "result = await db.execute(select(Model).where(Model.column == value))<br/>"
    "item = result.scalar_one_or_none()  # returns one item or None<br/>"
    "items = result.scalars().all()  # returns a list of all matches",
    styles["CodeBlock"]))
story.append(Paragraph(
    "This is SQLAlchemy 2.0 style. The <font face='Courier' size=9>select()</font> function builds a SQL SELECT query. "
    "<font face='Courier' size=9>.where()</font> adds a WHERE clause. The result is awaited (async) and then "
    "extracted with either <font face='Courier' size=9>scalar_one_or_none()</font> (for single results) or "
    "<font face='Courier' size=9>scalars().all()</font> (for lists).",
    styles["Body"]))

story.append(Paragraph("11.2 The INSERT Pattern", styles["H2"]))
story.append(Paragraph(
    "item = Model(column1=value1, column2=value2)<br/>"
    "db.add(item)<br/>"
    "await db.flush()  # sends to DB but doesn't commit yet<br/>"
    "await db.refresh(item)  # reloads from DB to get auto-generated values (id, created_at)",
    styles["CodeBlock"]))

story.append(Paragraph("11.3 The UPDATE Pattern", styles["H2"]))
story.append(Paragraph(
    "# First, fetch the item<br/>"
    "result = await db.execute(select(Model).where(Model.id == item_id))<br/>"
    "item = result.scalar_one_or_none()<br/>"
    "# Then, modify attributes directly<br/>"
    "item.name = new_name<br/>"
    "item.updated_at = datetime.now()<br/>"
    "await db.flush()  # SQLAlchemy tracks changes and generates UPDATE SQL",
    styles["CodeBlock"]))

story.append(Paragraph("11.4 The DELETE Pattern", styles["H2"]))
story.append(Paragraph(
    "result = await db.execute(select(Model).where(Model.id == item_id))<br/>"
    "item = result.scalar_one_or_none()<br/>"
    "if not item: raise HTTPException(404)<br/>"
    "await db.delete(item)<br/>"
    "await db.flush()",
    styles["CodeBlock"]))

story.append(Paragraph("11.5 Eager Loading (selectinload)", styles["H2"]))
story.append(Paragraph(
    "select(MarketplaceListing)<br/>"
    "&nbsp;&nbsp;.options(selectinload(MarketplaceListing.strategy).selectinload(Strategy.owner))",
    styles["CodeBlock"]))
story.append(Paragraph(
    "Without eager loading, accessing <font face='Courier' size=9>listing.strategy.owner.full_name</font> "
    "would trigger 2 extra database queries (one for strategy, one for owner). "
    "<font face='Courier' size=9>selectinload</font> tells SQLAlchemy to fetch all related data in a single "
    "efficient query using SQL IN clauses. This is used in the marketplace and admin endpoints.",
    styles["Body"]))

story.append(Paragraph("11.6 Aggregate Queries", styles["H2"]))
story.append(Paragraph(
    "# Count all users<br/>"
    "count = (await db.execute(select(func.count(User.id)))).scalar()<br/><br/>"
    "# Sum revenue with COALESCE (returns 0 instead of NULL if no rows match)<br/>"
    "revenue = (await db.execute(<br/>"
    "&nbsp;&nbsp;select(func.coalesce(func.sum(Listing.price_cents * Listing.sales_count), 0))<br/>"
    "&nbsp;&nbsp;.where(Listing.status.in_([ListingStatus.verified, ListingStatus.listed]))<br/>"
    ")).scalar()",
    styles["CodeBlock"]))
story.append(Paragraph(
    "Used in admin stats to compute totals without loading every row into Python.",
    styles["Body"]))

story.append(Paragraph("11.7 Bulk Updates", styles["H2"]))
story.append(Paragraph(
    "await db.execute(<br/>"
    "&nbsp;&nbsp;update(Notification)<br/>"
    "&nbsp;&nbsp;.where(Notification.user_id == user.id, Notification.is_read == False)<br/>"
    "&nbsp;&nbsp;.values(is_read=True)<br/>"
    ")",
    styles["CodeBlock"]))
story.append(Paragraph(
    "The 'mark all notifications as read' endpoint uses a bulk UPDATE instead of loading each notification "
    "one by one. This is much more efficient when there are many unread notifications.",
    styles["Body"]))
story.append(PageBreak())

# ━━━━━━ CHAPTER 12: GLOSSARY ━━━━━━
story.append(Paragraph("12. Glossary", styles["H1"]))
glossary = [
    ["Async / Asynchronous", "A programming model where operations can run concurrently without blocking each other. The backend can handle multiple database queries at the same time."],
    ["asyncpg", "A PostgreSQL driver optimised for Python's async/await syntax. Much faster than synchronous drivers for web applications."],
    ["Alembic", "A database migration tool for SQLAlchemy. Generates and runs versioned scripts that modify the database schema."],
    ["CASCADE", "A foreign key rule: when the parent record is deleted, all related child records are automatically deleted too."],
    ["Composite Primary Key", "A primary key made of two or more columns. Used in price_history where (ticker + date) uniquely identifies a row."],
    ["Dependency Injection", "A design pattern where FastAPI automatically provides objects (like database sessions) to endpoint functions that request them."],
    ["Eager Loading", "Pre-fetching related data in a single query instead of doing separate queries for each relationship."],
    ["FastAPI", "A modern Python web framework for building REST APIs. It's asynchronous, type-safe, and auto-generates API documentation."],
    ["Foreign Key (FK)", "A column that references the primary key of another table, creating a link between the two tables."],
    ["JSONB", "A PostgreSQL data type that stores JSON documents in an efficient binary format, with support for indexing and querying."],
    ["JWT", "JSON Web Token. A compact, signed token that the backend issues after login. The frontend sends it with every request to prove identity."],
    ["Mapped Column", "SQLAlchemy 2.0's way of defining a database column with Python type hints: Mapped[str] = mapped_column(String(80))."],
    ["Migration", "A versioned script that modifies the database schema (adding tables, columns, etc.) in a controlled, repeatable way."],
    ["ORM", "Object-Relational Mapping. Maps Python classes to database tables so you can use Python objects instead of raw SQL."],
    ["Pool", "A set of pre-opened database connections that are reused across requests, avoiding the overhead of opening a new connection for every query."],
    ["Primary Key (PK)", "A column (or columns) that uniquely identifies each row in a table. No two rows can share the same PK value."],
    ["Rollback", "Undoing all database changes made during a failed transaction, restoring the database to its previous state."],
    ["selectinload", "SQLAlchemy's eager loading strategy that uses SQL IN clauses to batch-load related objects efficiently."],
    ["Session", "A workspace for database operations. Changes are tracked and committed (saved) or rolled back (discarded) as a unit."],
    ["UUID", "Universally Unique Identifier. A 128-bit random ID (like '550e8400-e29b-41d4-a716-446655440000') used as primary keys."],
]
story.append(make_table(["Term", "Definition"], glossary,
                        [1.6 * inch, CONTENT_W - 1.6 * inch]))

story.append(Spacer(1, 30))
story.append(Paragraph("— End of Document —", ParagraphStyle(
    "EndDoc", parent=styles["Normal"], fontSize=10, textColor=MUTED, alignment=TA_CENTER)))


# ── Page numbering ──
def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(PAGE_W / 2, 28, f"StockPilot Database Documentation  |  Page {doc.page}")
    canvas.restoreState()

doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
print(f"Generated: {OUT}")
