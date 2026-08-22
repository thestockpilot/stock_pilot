"""Generate two testing-plan PDFs for StockPilot:
   1. Integration Test Plan - AI Layer
   2. Unit Test Plan - Rest of the System
Grounded in the real components of the codebase.
"""
import os
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)

OUT_DIR = os.path.dirname(__file__)
TODAY = date.today().strftime("%d %B %Y")

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1x", parent=styles["Heading1"], fontSize=15, spaceBefore=10, spaceAfter=6, textColor=colors.HexColor("#111827"))
H2 = ParagraphStyle("H2x", parent=styles["Heading2"], fontSize=12, spaceBefore=10, spaceAfter=4, textColor=colors.HexColor("#1D4ED8"))
BODY = ParagraphStyle("BODYx", parent=styles["Normal"], fontSize=9.5, leading=13, spaceAfter=5)
CELL = ParagraphStyle("CELLx", parent=styles["Normal"], fontSize=8, leading=10)
CELLH = ParagraphStyle("CELLHx", parent=styles["Normal"], fontSize=8, leading=10, textColor=colors.white, fontName="Helvetica-Bold")
TITLE = ParagraphStyle("TITLEx", parent=styles["Title"], fontSize=20, textColor=colors.HexColor("#111827"))
SUB = ParagraphStyle("SUBx", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#6B7280"), spaceAfter=2)
BULLET = ParagraphStyle("BULx", parent=BODY, leftIndent=12, bulletIndent=2, spaceAfter=2)


def bullets(items):
    return [Paragraph(f"•&nbsp;&nbsp;{x}", BULLET) for x in items]


def case_table(rows, widths):
    header = [Paragraph(h, CELLH) for h in rows[0]]
    body = [[Paragraph(str(c), CELL) for c in r] for r in rows[1:]]
    t = Table([header] + body, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9CA3AF")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def doc_header(story, title, subtitle):
    story.append(Paragraph(title, TITLE))
    story.append(Paragraph(subtitle, SUB))
    story.append(Spacer(1, 4))
    info = Table([
        [Paragraph("<b>Project</b>", CELL), Paragraph("StockPilot &mdash; AI Investment Advisory Platform (CSE5015)", CELL),
         Paragraph("<b>Date</b>", CELL), Paragraph(TODAY, CELL)],
        [Paragraph("<b>Group / Batch</b>", CELL), Paragraph("Group 13 / Batch 131", CELL),
         Paragraph("<b>Version</b>", CELL), Paragraph("1.0", CELL)],
    ], colWidths=[70, 250, 55, 90])
    info.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D1D5DB")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F3F4F6")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#F3F4F6")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(info)
    story.append(Spacer(1, 8))


# ============================================================
# 1. INTEGRATION TEST PLAN - AI LAYER
# ============================================================
def build_integration():
    path = os.path.join(OUT_DIR, "StockPilot_Integration_Test_Plan_AI.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=16*mm, bottomMargin=14*mm,
                            leftMargin=15*mm, rightMargin=15*mm)
    s = []
    doc_header(s, "Integration Test Plan", "AI / Analytics Layer")

    s.append(Paragraph("1. Objective", H2))
    s.append(Paragraph(
        "Verify that the components of the AI layer work correctly <b>together</b> and with their "
        "adjacent systems (the external market-data provider, the database, and the REST API). "
        "Unlike unit tests, these tests exercise data flowing across component boundaries: from raw "
        "market data, through feature engineering, into the models, and out as a persisted, "
        "contract-compliant verdict.", BODY))

    s.append(Paragraph("2. Scope &mdash; components under integration", H2))
    s += bullets([
        "<b>DataFetcher</b> (yfinance client) &rarr; <b>FeatureEngine</b> (23 technical indicators)",
        "<b>FeatureEngine</b> &rarr; <b>StockPredictor</b> (XGBoost) feature-column contract",
        "<b>FactorAnalysisService</b> (six-factor engine) integrating DataFetcher, FeatureEngine and FinBERT",
        "<b>FinBERT</b> sentiment with its <b>OBV trend-proxy</b> fallback",
        "<b>Prediction persistence</b> &rarr; <b>PostgreSQL</b> (<font face='Courier'>predictions</font> table)",
        "REST endpoints: <font face='Courier'>/predictions/{ticker}/live</font>, "
        "<font face='Courier'>/analysis/{ticker}/factors</font>, <font face='Courier'>/analysis/{ticker}/backtest</font>",
        "Backtesting via <b>vectorbt</b>, parameterised by risk tolerance and time horizon",
    ])

    s.append(Paragraph("3. Test strategy", H2))
    s.append(Paragraph(
        "A <b>bottom-up</b> integration approach: adjacent pairs are integrated and tested first "
        "(fetcher&rarr;features, features&rarr;model), then progressively larger flows up to the full "
        "endpoint. External non-determinism is removed by <b>stubbing the yfinance call with a frozen "
        "OHLCV fixture</b>, so the same input always yields the same output and tests are repeatable. "
        "A small pre-trained <b>fixture model</b> is used so tests do not retrain on every run. Database "
        "integration runs against a <b>transactional test database</b> rolled back after each test.", BODY))

    s.append(Paragraph("4. Environment &amp; tools", H2))
    s += bullets([
        "<b>pytest</b> + <b>pytest-asyncio</b> (async endpoints and DB sessions)",
        "<b>httpx.AsyncClient</b> against the FastAPI app for endpoint-level integration",
        "<b>monkeypatch / respx</b> to stub the yfinance network call with fixture data",
        "Dedicated PostgreSQL <b>test schema</b>; each test wrapped in a rolled-back transaction",
        "A committed <b>fixture model bundle</b> and a frozen 6-month OHLCV CSV as test data",
    ])

    s.append(Paragraph("5. Entry &amp; exit criteria", H2))
    s += bullets([
        "<b>Entry:</b> unit tests for the individual AI components pass; fixture data and fixture model available.",
        "<b>Exit:</b> 100% of integration cases below pass; no unhandled exception on any boundary; "
        "output contracts validated; determinism (regression) test stable within tolerance.",
    ])

    s.append(Paragraph("6. Integration test cases", H2))
    rows = [
        ["ID", "Integration point", "Scenario / precondition", "Expected result"],
        ["INT-AI-01", "DataFetcher → FeatureEngine", "Frozen OHLCV fixture passed to the indicator engine",
         "23 indicators produced; no NaN rows leak into the feature matrix; row count consistent"],
        ["INT-AI-02", "FeatureEngine → StockPredictor", "Engineered features fed to prepare_data",
         "Feature columns exactly match the model's expected stationary feature set; no shape mismatch"],
        ["INT-AI-03", "StockPredictor.predict (end-to-end)", "Valid ticker, stubbed 6-month data, fixture model",
         "Returns signal ∈ {BUY,HOLD,SELL}; confidence 0–100; probability_up + probability_down ≈ 100"],
        ["INT-AI-04", "predict → signal mapping", "Model probability near 0.50 (inside hold band)",
         "Maps to HOLD; probabilities outside 0.43–0.57 map to SELL/BUY respectively"],
        ["INT-AI-05", "/predictions/{ticker}/live (full flow)", "Authenticated GET request, stubbed data",
         "200 response; one new row inserted in predictions table matching PredictionOut schema"],
        ["INT-AI-06", "Lazy model load", "First call after process start; then model file missing",
         "model.pkl loaded once per process; 503 returned when the model file is absent"],
        ["INT-AI-07", "FactorAnalysisService (six-factor)", "computeFactorScores with stubbed data + FinBERT",
         "Returns all six factors (sentiment, momentum, valuation, volatility, volume, growth)"],
        ["INT-AI-08", "FinBERT → OBV fallback", "News source returns zero headlines / FinBERT raises",
         "Fallback to OBV trend proxy engaged; sentiment score still returned in 0–100 range"],
        ["INT-AI-09", "/analysis/{ticker}/factors", "Custom weight query parameters supplied",
         "Weights applied; composite maps to BUY/HOLD/SELL with confidence and per-factor breakdown"],
        ["INT-AI-10", "/analysis/{ticker}/backtest (vectorbt)", "Fewer than 60 rows / then sufficient rows",
         "400 Insufficient data for short series; otherwise metrics + equity curve + trade ledger returned"],
        ["INT-AI-11", "Backtest risk/horizon config", "Conservative+Short vs Aggressive+Long parameters",
         "Buy threshold, stop-loss and take-profit differ per configuration; trade count changes accordingly"],
        ["INT-AI-12", "External failure handling", "yfinance stubbed to time out / return empty",
         "Graceful 400/502; no unhandled exception; no partial row written to the database"],
        ["INT-AI-13", "Output contract & persistence", "Successful live prediction",
         "Persisted row fields (signal, confidence, probabilities, model_version) match the API response"],
        ["INT-AI-14", "Determinism / regression guard", "Fixed seed + fixed fixture, run twice",
         "walk_forward accuracy and log loss reproduce within a small tolerance across runs"],
    ]
    s.append(case_table(rows, [52, 96, 150, 190]))

    s.append(Spacer(1, 8))
    s.append(Paragraph("7. Test data &amp; fixtures", H2))
    s += bullets([
        "Frozen 6-month and 5-year OHLCV CSVs (so tests never depend on live yfinance).",
        "Stub headline set (positive, negative, empty) to drive the FinBERT / OBV fallback paths.",
        "A committed fixture model bundle to avoid retraining during CI.",
    ])
    s.append(Paragraph("8. Risks &amp; assumptions", H2))
    s += bullets([
        "External market data is non-deterministic &rarr; mitigated by stubbing yfinance.",
        "Model training is slow &rarr; mitigated by a small fixture model and cached features.",
        "Model accuracy is out of scope here (covered by ML evaluation); these tests verify "
        "<b>correct wiring and contracts</b>, not predictive quality.",
    ])
    s.append(Paragraph("9. Reporting &amp; traceability", H2))
    s.append(Paragraph(
        "Each case ID traces to the component it integrates and to the corresponding sequence-diagram "
        "step. Results are recorded as Pass/Fail with the failing boundary noted; a run summary "
        "(passed / failed / skipped) is produced by pytest for the milestone evidence pack.", BODY))

    doc.build(s)
    print("wrote", os.path.basename(path))
    return path


# ============================================================
# 2. UNIT TEST PLAN - REST OF SYSTEM
# ============================================================
def build_unit():
    path = os.path.join(OUT_DIR, "StockPilot_Unit_Test_Plan_System.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=16*mm, bottomMargin=14*mm,
                            leftMargin=15*mm, rightMargin=15*mm)
    s = []
    doc_header(s, "Unit Test Plan", "Application, Security, Persistence &amp; Domain Logic")

    s.append(Paragraph("1. Objective", H2))
    s.append(Paragraph(
        "Verify each unit &mdash; a function, method or endpoint handler &mdash; behaves correctly in "
        "<b>isolation</b>, independent of the AI layer. Dependencies such as the database or external "
        "services are replaced with test doubles so a failure points to one unit only.", BODY))

    s.append(Paragraph("2. Scope", H2))
    s += bullets([
        "<b>Security</b>: password hashing, JWT creation/decoding, access/refresh separation",
        "<b>RBAC</b>: require_role authorisation",
        "<b>Schemas</b>: Pydantic request validation (including the role Literal guard)",
        "<b>CRUD</b>: portfolio, watchlist, trades, strategies endpoints",
        "<b>Marketplace</b>: publish threshold re-validation and state guards",
        "<b>Admin</b>: role change (incl. role subtype tables), approve/reject/remove, user suspension",
        "<b>Settings</b>: threshold bounds and singleton self-healing",
        "<b>Domain calculations</b>: profit, market value, risk/reward, weight validation",
        "<b>Models</b>: constraints and cascade-delete behaviour",
    ])

    s.append(Paragraph("3. Strategy, tools &amp; coverage", H2))
    s.append(Paragraph(
        "Pure functions (hashing, calculations, validation) are tested directly. Endpoint handlers are "
        "tested with a mocked async DB session or a transactional test DB. Time-dependent logic (token "
        "expiry) uses a frozen clock. Target: <b>&ge; 80% line coverage</b> on core modules "
        "(security, dependencies, schemas, marketplace, admin, settings).", BODY))
    s += bullets([
        "<b>pytest</b>, <b>pytest-asyncio</b>, <b>unittest.mock</b>",
        "<b>httpx.AsyncClient</b> / FastAPI dependency overrides for handler tests",
        "<b>freezegun</b> for token-expiry tests; <b>pytest-cov</b> for coverage",
    ])

    s.append(Paragraph("4. Entry &amp; exit criteria", H2))
    s += bullets([
        "<b>Entry:</b> code compiles; test DB/fixtures available.",
        "<b>Exit:</b> all cases pass; coverage target met; no critical/ high defect open.",
    ])

    s.append(Paragraph("5. Unit test cases", H2))
    rows = [
        ["ID", "Module / target", "Scenario", "Expected result"],
        ["UT-SEC-01", "security.hash_password / verify_password", "Hash a password, verify right vs wrong",
         "Correct password verifies True; wrong password False; hash ≠ plaintext"],
        ["UT-SEC-02", "security.create_*_token", "Create access and refresh tokens",
         "Access token carries type='access'; refresh carries type='refresh'; both decode with correct sub"],
        ["UT-SEC-03", "security.decode_token", "Valid, expired, and tampered tokens",
         "Valid returns payload; expired/tampered/invalid-signature return None"],
        ["UT-SEC-04", "dependencies.get_current_user", "A refresh token presented as a Bearer credential",
         "Rejected with 401 (type != 'access'); a valid access token for an active user is accepted"],
        ["UT-RBAC-01", "dependencies.require_role", "Investor calls an analyst/admin-only dependency",
         "403 Insufficient permissions; matching role passes through"],
        ["UT-SCH-01", "schemas.RegisterRequest", "role = 'admin' submitted at registration",
         "422 validation error (Literal allows only investor/analyst); default role is investor"],
        ["UT-SCH-02", "schemas.LoginRequest", "Malformed email address",
         "422 validation error before any DB access"],
        ["UT-PF-01", "portfolio endpoint / Holding", "Add holding with valid and invalid quantity",
         "Valid creates 201; non-positive quantity rejected with 4xx"],
        ["UT-PF-02", "Holding.calculateMarketValue / calculateProfit", "Known quantity, cost and current price",
         "Market value = qty×price; profit = (price−cost)×qty (exact arithmetic)"],
        ["UT-WL-01", "watchlist endpoint", "Add duplicate (user, ticker)",
         "First add succeeds; duplicate rejected by the unique constraint"],
        ["UT-TR-01", "Trade.calculateProfit / calculateRiskReward", "Entry, exit, stop, target values",
         "Profit and risk/reward ratio computed correctly; side (BUY/SELL) respected"],
        ["UT-ST-01", "Strategy.validateWeights", "Six weights summing to 100 and to 97",
         "Sum=100 valid; sum≠97 rejected"],
        ["UT-MP-01", "strategies publish - threshold check", "A metric below the platform threshold",
         "400 with per-metric breakdown; nothing written to the listing"],
        ["UT-MP-02", "strategies publish - RBAC", "Investor calls POST /strategies/{id}/publish",
         "403 before any DB access (require_role(analyst, admin))"],
        ["UT-MP-03", "strategies publish - state guard", "Listing already in 'review' / 'verified'",
         "400 Already pending review / Already published"],
        ["UT-AD-01", "admin.update_user_role - self", "Admin changes their own role",
         "400 Cannot change your own role"],
        ["UT-AD-02", "admin.update_user_role - invalid", "role = 'superuser'",
         "400 Invalid role"],
        ["UT-AD-03", "admin.update_user_role - subtype sync", "Investor promoted to analyst (Option A)",
         "Investor profile row removed; analyst profile row created; users.role updated"],
        ["UT-AD-04", "admin approve listing", "Approve a listing not in 'review'",
         "400 Only listings in review can be approved; valid case sets status='verified'"],
        ["UT-SET-01", "settings threshold bounds", "min_winrate = 1.5 (out of range)",
         "400 with the specific reason; in-range values persist to the singleton row"],
        ["UT-SET-02", "settings.get_settings", "platform_settings row missing",
         "Self-heals by creating the singleton (id=1) with default thresholds"],
        ["UT-MD-01", "model cascade delete", "Delete a user with holdings, trades and a profile row",
         "Child rows (holdings, trades, watchlist, notifications, role profile) are removed"],
        ["UT-MD-02", "enum / constraint validation", "Insert invalid enum value / null on NOT NULL column",
         "Rejected by the model constraint (IntegrityError)"],
    ]
    s.append(case_table(rows, [58, 118, 138, 176]))

    s.append(Spacer(1, 8))
    s.append(Paragraph("6. Test data &amp; fixtures", H2))
    s += bullets([
        "Factory fixtures for User (each role), Holding, Trade, Strategy and Listing.",
        "A transactional test database rolled back per test for isolation.",
        "Frozen clock for token-expiry cases.",
    ])
    s.append(Paragraph("7. Risks &amp; assumptions", H2))
    s += bullets([
        "Endpoint tests depend on DB availability &rarr; mitigated by a disposable test schema.",
        "The AI layer is out of scope here and is stubbed where a handler touches it.",
    ])
    s.append(Paragraph("8. Reporting", H2))
    s.append(Paragraph(
        "pytest-cov produces a coverage report; each case ID maps to the module under test. Pass/Fail and "
        "coverage figures form part of the milestone evidence pack.", BODY))

    doc.build(s)
    print("wrote", os.path.basename(path))
    return path


if __name__ == "__main__":
    build_integration()
    build_unit()
    print("done")
