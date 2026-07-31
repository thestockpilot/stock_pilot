"""StockPilot — Diagram Design Specification.

A machine-readable briefing whose single purpose is to let another AI (or a
designer) produce accurate UML, ERD, DFD and related diagrams without needing
access to the source code. Every fact is verified against the implementation.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether,
)

NAVY = HexColor("#1b2a4a"); BLUE = HexColor("#2E5496"); ACCENT = HexColor("#b8801f")
GREEN = HexColor("#1E7E45"); RED = HexColor("#b03a2e"); GREY = HexColor("#5a5a64")
LIGHTB = HexColor("#eef2f9"); LIGHTG = HexColor("#eaf6ee"); LIGHTGOLD = HexColor("#fbf6e9")
LIGHTRED = HexColor("#fbeeec"); LIGHTGREY = HexColor("#f3f3f5"); BORDER = HexColor("#c9d3e6")
TEXT = HexColor("#16161a")

PAGE_W, PAGE_H = A4
MARGIN = 42
CW = PAGE_W - 2 * MARGIN
OUT = os.path.join(os.path.dirname(__file__), "StockPilot_Diagram_Specification.pdf")

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                        topMargin=MARGIN, bottomMargin=MARGIN,
                        title="StockPilot - Diagram Design Specification",
                        author="Group 13 - CSE5015")

S = getSampleStyleSheet()
S.add(ParagraphStyle("T1", fontName="Helvetica-Bold", fontSize=23, leading=27, textColor=NAVY, spaceAfter=3))
S.add(ParagraphStyle("T2", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=ACCENT, spaceAfter=9))
S.add(ParagraphStyle("Sub", fontName="Helvetica-Oblique", fontSize=10, leading=14, textColor=GREY, spaceAfter=12))
S.add(ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=14.5, leading=18, textColor=NAVY, spaceBefore=16, spaceAfter=7))
S.add(ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=BLUE, spaceBefore=12, spaceAfter=5))
S.add(ParagraphStyle("H3", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=HexColor("#333338"), spaceBefore=9, spaceAfter=4))
S.add(ParagraphStyle("Body", fontName="Helvetica", fontSize=9.3, leading=13.4, textColor=TEXT, alignment=TA_JUSTIFY, spaceAfter=6))
S.add(ParagraphStyle("Bul", fontName="Helvetica", fontSize=9.3, leading=13, textColor=TEXT, alignment=TA_JUSTIFY, spaceAfter=2, leftIndent=13, bulletIndent=3))
S.add(ParagraphStyle("Mono", fontName="Courier", fontSize=7.6, leading=10.3, textColor=HexColor("#14141a"),
                     backColor=LIGHTGREY, borderPadding=7, spaceBefore=3, spaceAfter=7, leftIndent=4, rightIndent=4))
S.add(ParagraphStyle("Cell", fontName="Helvetica", fontSize=7.9, leading=10.4, textColor=TEXT))
S.add(ParagraphStyle("CellC", fontName="Courier", fontSize=7.3, leading=9.9, textColor=HexColor("#14141a")))
S.add(ParagraphStyle("Head", fontName="Helvetica-Bold", fontSize=8, leading=10.4, textColor=white))
S.add(ParagraphStyle("CoTitle", fontName="Helvetica-Bold", fontSize=9.3, leading=12, textColor=TEXT))
S.add(ParagraphStyle("CoBody", fontName="Helvetica", fontSize=8.8, leading=12.4, textColor=TEXT, alignment=TA_JUSTIFY))

def P(t, s="Body"): return Paragraph(t, S[s])
def _p(t): return Paragraph(str(t), S["Cell"])
def _pc(t): return Paragraph(str(t), S["CellC"])
def _ph(t): return Paragraph(str(t), S["Head"])
def bullet(t): return Paragraph(t, S["Bul"], bulletText="•")

def rule(color=ACCENT, w=1.1, after=9):
    t = Table([[""]], colWidths=[CW])
    t.setStyle(TableStyle([("LINEBELOW",(0,0),(-1,-1),w,color),("BOTTOMPADDING",(0,0),(-1,-1),after)]))
    return t

def callout(title, body, bg=LIGHTB, ac=BLUE):
    t = Table([[Paragraph(f"<b>{title}</b>", S["CoTitle"])],[Paragraph(body, S["CoBody"])]], colWidths=[CW-14])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),("LEFTPADDING",(0,0),(-1,-1),11),
        ("RIGHTPADDING",(0,0),(-1,-1),9),("TOPPADDING",(0,0),(0,0),7),("BOTTOMPADDING",(-1,-1),(-1,-1),8),
        ("LINEBEFORE",(0,0),(0,-1),3,ac),("VALIGN",(0,0),(-1,-1),"TOP")]))
    return t

def table(headers, rows, widths, code_cols=()):
    data=[[_ph(h) for h in headers]]
    for r in rows:
        data.append([_pc(c) if i in code_cols else _p(c) for i,c in enumerate(r)])
    t=Table(data,colWidths=widths,repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("GRID",(0,0),(-1,-1),0.4,BORDER),
        ("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[white,HexColor("#f7f8fb")]),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
    return t

def mono(txt):
    e = txt.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return Paragraph(e.replace("\n","<br/>"), S["Mono"])

st = []

# ─────────────── COVER ───────────────
st.append(P("StockPilot", "T1"))
st.append(P("Diagram Design Specification", "T2"))
st.append(P("A complete, verified description of the system structured specifically for producing "
            "ERD, UML (class, use case, sequence, state, activity, component), and DFD diagrams. "
            "Every entity, attribute, relationship, actor, method and state transition below was "
            "read from the implementation rather than from design intent.", "Sub"))
st.append(rule())
st.append(callout("Instructions for the AI or designer consuming this document",
    "Each section is a direct specification for one diagram type &mdash; entities and cardinalities for the ERD, "
    "classes with attributes and method signatures for the class diagram, actors and use cases for the use-case "
    "diagram, and so on. <b>Use only the facts stated here.</b> Where the system deviates from a conventional "
    "design, Section 11 records it explicitly; prefer that section over any assumption. Names are given exactly "
    "as they appear in the code, so diagrams can be traced back to the implementation.", LIGHTGOLD, ACCENT))
st.append(Spacer(1, 8))

st.append(table(["Section","Diagram it supports"], [
    ["2. Entity specification", "Entity-Relationship Diagram (ERD), relational schema, normalisation"],
    ["3. Class specification", "UML Class Diagram (domain + service layers)"],
    ["4. Actor &amp; use case specification", "UML Use Case Diagram"],
    ["5. Data flow specification", "DFD Context, Level 0 and Level 1"],
    ["6. Sequence specification", "UML Sequence Diagrams (6 scenarios)"],
    ["7. State specification", "UML State Machine Diagrams (4 lifecycles)"],
    ["8. Activity specification", "UML Activity Diagrams (3 workflows)"],
    ["9. Component &amp; deployment", "UML Component and Deployment Diagrams"],
    ["10. Business rules", "Constraints and notes to annotate any diagram"],
    ["11. Design deviations", "Facts that override conventional assumptions"],
], [1.75*inch, CW-1.75*inch]))

# ─────────────── 1. OVERVIEW ───────────────
st.append(P("1. System Overview", "H1"))
st.append(P("StockPilot is an AI-powered investment advisory web application. For any stock ticker it produces an "
            "explainable BUY / HOLD / SELL verdict with a confidence score, derived from a weighted six-factor model "
            "(sentiment, momentum, valuation, volatility, volume, growth). It additionally provides portfolio "
            "tracking, a watchlist, a trading journal, and a marketplace where users publish factor-weight "
            "strategies that must pass an objective backtest before an administrator lists them."))
st.append(table(["Property","Value"], [
    ["Architecture", "Five layers: Presentation, Application, AI &amp; Analytics, Data, Storage"],
    ["Frontend", "React 18, Vite, react-router-dom, axios, Chart.js"],
    ["Backend", "FastAPI (async), SQLAlchemy 2.0 async ORM, asyncpg, Pydantic"],
    ["Database", "PostgreSQL 16 &mdash; 12 tables"],
    ["AI / ML", "XGBoost (signal model), FinBERT (news sentiment), vectorbt (backtesting)"],
    ["External API", "Yahoo Finance via yfinance (prices, fundamentals, news headlines)"],
    ["Auth", "JWT access + refresh tokens, bcrypt hashing, role-based access control"],
    ["User roles", "investor, analyst, admin"],
    ["API surface", "56 REST endpoints under /api/v1"],
], [1.15*inch, CW-1.15*inch]))

# ─────────────── 2. ERD ───────────────
st.append(PageBreak())
st.append(P("2. Entity Specification &mdash; for the ERD", "H1"))
st.append(P("12 entities. <b>PK</b> = primary key, <b>FK</b> = foreign key, <b>U</b> = unique, "
            "<b>N</b> = nullable. All UUID keys default to a generated uuid4."))

ents = [
 ("users", "Registered accounts. Central identity entity.", [
   ["id","UUID","PK",""],["email","VARCHAR(320)","U, indexed","not null"],
   ["password_hash","VARCHAR(200)","","bcrypt, not null"],["full_name","VARCHAR(120)","","not null"],
   ["role","ENUM UserRole","","default 'investor'"],["phone","VARCHAR(30)","N",""],
   ["bio","VARCHAR(500)","N",""],["avatar_url","VARCHAR(500)","N",""],
   ["is_active","BOOLEAN","","default true"],["created_at","TIMESTAMPTZ","","server default now()"],
   ["updated_at","TIMESTAMPTZ","","auto-updates on change"]]),
 ("stocks", "Reference catalogue of tradeable instruments.", [
   ["id","UUID","PK",""],["ticker","VARCHAR(10)","U, indexed","not null"],
   ["name","VARCHAR(200)","","not null"],["sector","VARCHAR(100)","N",""],
   ["industry","VARCHAR(100)","N",""],["updated_at","TIMESTAMPTZ","",""]]),
 ("price_history", "Historical daily OHLCV. Only entity with a composite key.", [
   ["ticker","VARCHAR(10)","PK (part 1)",""],["date","DATE","PK (part 2)",""],
   ["open","NUMERIC(18,4)","","not null"],["high","NUMERIC(18,4)","","not null"],
   ["low","NUMERIC(18,4)","","not null"],["close","NUMERIC(18,4)","","not null"],
   ["volume","BIGINT","","not null"]]),
 ("predictions", "AI-generated signals produced by the XGBoost model.", [
   ["id","UUID","PK",""],["ticker","VARCHAR(10)","indexed","not null"],
   ["signal","ENUM SignalType","","not null"],["confidence","NUMERIC(5,2)","","percent"],
   ["probability_up","NUMERIC(5,2)","","percent"],["probability_down","NUMERIC(5,2)","","percent"],
   ["composite_score","INTEGER","N","0-100"],["model_version","VARCHAR(50)","","default 'xgboost_v1'"],
   ["created_at","TIMESTAMPTZ","",""]]),
 ("holdings", "Portfolio positions owned by a user.", [
   ["id","UUID","PK",""],["user_id","UUID","FK -> users.id","CASCADE, not null"],
   ["ticker","VARCHAR(10)","","not null"],["quantity","NUMERIC(18,4)","","not null"],
   ["avg_cost","NUMERIC(18,4)","","not null"],["current_price","NUMERIC(18,4)","N","refreshed live"],
   ["opened_at","TIMESTAMPTZ","",""],["closed_at","TIMESTAMPTZ","N","null = position open"]]),
 ("watchlist", "Tickers a user monitors.", [
   ["id","UUID","PK",""],["user_id","UUID","FK -> users.id","CASCADE, not null"],
   ["ticker","VARCHAR(10)","","not null"],["added_at","TIMESTAMPTZ","",""],
   ["(constraint)","UNIQUE(user_id, ticker)","","prevents duplicates"]]),
 ("trades", "Trading-journal entries for completed trades.", [
   ["id","UUID","PK",""],["user_id","UUID","FK -> users.id","CASCADE, not null"],
   ["ticker","VARCHAR(10)","indexed","not null"],["side","ENUM TradeSide","","not null"],
   ["entry_price","NUMERIC(18,4)","","not null"],["exit_price","NUMERIC(18,4)","","not null"],
   ["stop_loss","NUMERIC(18,4)","N",""],["take_profit","NUMERIC(18,4)","N",""],
   ["quantity","NUMERIC(18,4)","","not null"],["strategy_label","VARCHAR(80)","N",""],
   ["opened_at","TIMESTAMPTZ","","not null"],["closed_at","TIMESTAMPTZ","","not null"],
   ["notes","TEXT","N",""],["created_at","TIMESTAMPTZ","",""]]),
 ("strategies", "Six-factor weight configurations.", [
   ["id","UUID","PK",""],["owner_id","UUID","FK -> users.id, N","CASCADE; null = system preset"],
   ["name","VARCHAR(80)","","not null"],["description","TEXT","N",""],
   ["weights","JSONB","","not null; six factor keys summing to 100"],
   ["is_preset","BOOLEAN","","default false"],["is_published","BOOLEAN","","default false"],
   ["created_at","TIMESTAMPTZ","",""],["updated_at","TIMESTAMPTZ","",""]]),
 ("marketplace_listings", "A strategy offered on the marketplace.", [
   ["id","UUID","PK",""],["strategy_id","UUID","FK -> strategies.id, U","not null; UNIQUE makes it 1:1"],
   ["price_cents","INTEGER","","default 0; 0 = free"],["status","ENUM ListingStatus","","default 'draft'"],
   ["avg_rating","NUMERIC(3,2)","N","1.00-5.00"],["rating_count","INTEGER","","default 0"],
   ["sales_count","INTEGER","","default 0"],["backtest_return","NUMERIC(6,3)","N",""],
   ["backtest_sharpe","NUMERIC(6,3)","N",""],["backtest_winrate","NUMERIC(4,3)","N",""],
   ["backtest_trades","INTEGER","N",""],["backtest_max_drawdown","NUMERIC(5,4)","N",""],
   ["backtest_profit_factor","NUMERIC(5,2)","N",""],["listed_at","TIMESTAMPTZ","N","set on approval"],
   ["created_at","TIMESTAMPTZ","",""]]),
 ("marketplace_ratings", "User ratings and reviews of a listing.", [
   ["id","UUID","PK",""],["listing_id","UUID","FK -> marketplace_listings.id","CASCADE, not null"],
   ["user_id","UUID","FK -> users.id","CASCADE, not null"],["rating","INTEGER","","1-5, not null"],
   ["review","VARCHAR(500)","N",""],["created_at","TIMESTAMPTZ","",""]]),
 ("notifications", "In-app notifications for a user.", [
   ["id","UUID","PK",""],["user_id","UUID","FK -> users.id","CASCADE, not null"],
   ["kind","ENUM NotificationKind","","not null"],["title","VARCHAR(200)","","not null"],
   ["body","TEXT","N",""],["is_read","BOOLEAN","","default false"],["created_at","TIMESTAMPTZ","",""]]),
 ("platform_settings", "Singleton row holding admin-configurable thresholds.", [
   ["id","INTEGER","PK","always 1 (singleton)"],["min_trades","INTEGER","","default 100"],
   ["min_winrate","NUMERIC(4,3)","","default 0.650"],["min_sharpe","NUMERIC(5,2)","","default 1.00"],
   ["max_drawdown","NUMERIC(5,4)","","default 0.1500"],["min_profit_factor","NUMERIC(5,2)","","default 1.50"]]),
]
for name, desc, cols in ents:
    st.append(KeepTogether([
        P(f"2.{ents.index((name,desc,cols))+1} &nbsp; <font face='Courier'>{name}</font> &mdash; {desc}", "H3"),
        table(["Attribute","Type","Key / Index","Notes"], cols,
              [1.5*inch, 1.25*inch, 1.35*inch, CW-4.1*inch], code_cols=(0,1)),
        Spacer(1,3)]))

st.append(P("2.13 Relationships and cardinality", "H2"))
st.append(table(["Parent","Cardinality","Child","Foreign key","On delete","Reading"], [
 ["users","1 : N","holdings","holdings.user_id","CASCADE","A user owns many holdings"],
 ["users","1 : N","watchlist","watchlist.user_id","CASCADE","A user watches many tickers"],
 ["users","1 : N","trades","trades.user_id","CASCADE","A user logs many trades"],
 ["users","1 : N","strategies","strategies.owner_id","CASCADE","A user creates many strategies"],
 ["users","1 : N","notifications","notifications.user_id","CASCADE","A user receives many notifications"],
 ["users","1 : N","marketplace_ratings","ratings.user_id","CASCADE","A user writes many ratings"],
 ["strategies","1 : 1","marketplace_listings","listings.strategy_id (UNIQUE)","RESTRICT","A strategy has at most one listing"],
 ["marketplace_listings","1 : N","marketplace_ratings","ratings.listing_id","CASCADE","A listing receives many ratings"],
], [1.05*inch,0.62*inch,1.15*inch,1.35*inch,0.62*inch,CW-4.79*inch], code_cols=(0,2,3)))
st.append(Spacer(1,5))
st.append(callout("Participation and ERD notation notes",
    "<b>strategies &rarr; marketplace_listings is 1:1</b> because <font face='Courier'>strategy_id</font> carries a UNIQUE "
    "constraint; model it as one-to-one with optional participation on the strategy side (a strategy need not be listed). "
    "<b>strategies.owner_id is nullable</b> &mdash; a NULL owner denotes a system-provided preset, so participation is "
    "optional on the users side. <b>stocks, price_history and predictions have no foreign keys</b>: they associate with "
    "instruments by ticker string rather than a relational key (see Section 11.1), so on a strict ERD they appear as "
    "independent entities linked only by the shared <font face='Courier'>ticker</font> attribute.", LIGHTB, BLUE))

st.append(P("2.14 Enumerations", "H2"))
st.append(table(["Enum","Used by","Values"], [
 ["UserRole","users.role","investor, analyst, admin"],
 ["SignalType","predictions.signal","BUY, HOLD, SELL"],
 ["TradeSide","trades.side","buy, sell"],
 ["ListingStatus","marketplace_listings.status","draft, review, verified, listed, removed"],
 ["NotificationKind","notifications.kind","verdict_change, price_alert, marketplace, weekly_report, security, system"],
], [1.2*inch,1.75*inch,CW-2.95*inch], code_cols=(0,1)))

# ─────────────── 3. CLASS ───────────────
st.append(PageBreak())
st.append(P("3. Class Specification &mdash; for the UML Class Diagram", "H1"))
st.append(P("Two clusters: <b>persistent domain classes</b> (the ORM models, one per table in Section 2) and "
            "<b>service classes</b> (the AI/analytics layer). Domain-class attributes are the table columns already "
            "listed, so only their associations are repeated here."))

st.append(P("3.1 Domain (ORM) classes and their associations", "H2"))
st.append(table(["Class","Maps to table","Declared relationships (SQLAlchemy)"], [
 ["User","users","watchlist, holdings, trades, strategies, notifications &mdash; all one-to-many with cascade delete"],
 ["Stock","stocks","none"],
 ["PriceHistory","price_history","none"],
 ["Prediction","predictions","none"],
 ["Holding","holdings","many-to-one &rarr; User"],
 ["Watchlist","watchlist","many-to-one &rarr; User"],
 ["Trade","trades","many-to-one &rarr; User"],
 ["Strategy","strategies","many-to-one &rarr; User (owner); one-to-one &rarr; MarketplaceListing"],
 ["MarketplaceListing","marketplace_listings","many-to-one &rarr; Strategy; one-to-many &rarr; MarketplaceRating"],
 ["MarketplaceRating","marketplace_ratings","many-to-one &rarr; MarketplaceListing; FK to User"],
 ["Notification","notifications","many-to-one &rarr; User"],
 ["PlatformSettings","platform_settings","none (singleton)"],
], [1.25*inch,1.35*inch,CW-2.6*inch], code_cols=(0,1)))

st.append(P("3.2 Service classes (AI &amp; Analytics / Data layers)", "H2"))
st.append(mono(
"""+-------------------------------------------------------------+
|                       DataFetcher                           |
+-------------------------------------------------------------+
| - data_path        : Path      (default "data_storage/...")  |
| - default_period   : str       ("6mo")                       |
| - default_interval : str       ("1d")                        |
| - max_retries      : int       (3)                           |
| - retry_backoff    : float     (1.0)                         |
+-------------------------------------------------------------+
| + fetch_historical(ticker, period, interval) : DataFrame     |
| + save_to_csv(data, ticker, period, interval) : Path         |
| + load_from_csv(ticker, period, interval) : DataFrame        |
| + fetch_and_save(ticker, period, interval) : DataFrame       |
| + get_available_tickers() : list[str]                        |
| + get_data_summary(ticker) : dict                            |
+-------------------------------------------------------------+

+-------------------------------------------------------------+
|                      FeatureEngine                          |
+-------------------------------------------------------------+
| + calculate_all_features(data) : DataFrame   <<main entry>>  |
| + calculate_moving_averages(data) : DataFrame                |
| + calculate_rsi(data) : DataFrame                            |
| + calculate_macd(data) : DataFrame                           |
| + calculate_bollinger_bands(data) : DataFrame                |
| + calculate_volume_indicators(data) : DataFrame              |
| + calculate_volatility(data) : DataFrame                     |
| + calculate_price_position(data) : DataFrame                 |
| + handle_nan_values(df) : DataFrame                          |
| + validate_data(data) : None                                 |
| + get_feature_names() : list[str]                            |
| + get_feature_summary() : DataFrame                          |
| + get_feature_correlation(method) : DataFrame                |
+-------------------------------------------------------------+
        Produces 23 indicator columns (RSI_14, MACD, MACD_Signal,
        MACD_Histogram, BB_*, ATR_14, OBV, MFI_14, VWAP_20, ROC_10,
        SMA/EMA_5..50, Volatility_20, Volume_Ratio, Price_Position, ...)

+-------------------------------------------------------------+
|                     StockPredictor                          |
+-------------------------------------------------------------+
| - model_path      : Path                                     |
| - config          : PredictorConfig                          |
| - model           : XGBClassifier | None                     |
| - feature_columns : list[str] | None                         |
+-------------------------------------------------------------+
| + prepare_data(ticker, period) : (DataFrame, Series)         |
| + train(ticker, period, test_size, save) : XGBClassifier     |
| + walk_forward_evaluate(ticker, n_splits) : WalkForwardReport|
| + evaluate(X_test, y_test) : dict[str, float]                |
| + backtest(...) : BacktestReport                             |
| + predict(ticker) : dict     <<used by the live endpoint>>   |
| + save_model() : Path                                        |
| + load_model() : None                                        |
+-------------------------------------------------------------+

+-------------------------------------------------------------+
|                  PredictorConfig  <<dataclass>>             |
+-------------------------------------------------------------+
| target_horizon    : int   = 5      (days ahead)              |
| target_deadband   : float = 0.01   (neutral band)            |
| training_period   : str   = "5y"                             |
| stationary_only   : bool  = True   (scale-free features)     |
| max_estimators    : int   = 300                              |
| early_stopping_rounds : int = 100                            |
| max_depth         : int   = 4                                |
| learning_rate     : float = 0.03                             |
| subsample         : float = 0.8                              |
| colsample_bytree  : float = 0.8                              |
| reg_alpha         : float = 0.0                              |
| reg_lambda        : float = 1.0                              |
| hold_lower        : float = 0.43   (HOLD band lower bound)   |
| hold_upper        : float = 0.57   (HOLD band upper bound)   |
+-------------------------------------------------------------+

+-------------------------------------------------------------+
|             FinBERT sentiment module  <<module>>            |
+-------------------------------------------------------------+
| + fetch_news_headlines(ticker, max_headlines) : list[str]    |
| + analyze_headline(text) : HeadlineSentiment                 |
| + analyze_ticker(ticker, max_headlines) : SentimentResult    |
+-------------------------------------------------------------+
        HeadlineSentiment <<dataclass>> : headline, label, scores
        SentimentResult   <<dataclass>> : overall_score,
                                          headline_count, headlines[]

  Result value objects returned by StockPredictor:
    BacktestReport    <<dataclass>>  + as_dict() : dict
    WalkForwardReport <<dataclass>>  n_splits, accuracies[], loglosses[],
                                     mean_accuracy, std_accuracy, mean_logloss"""))

st.append(P("3.3 Dependencies to draw between service classes", "H2"))
st.append(bullet("<b>StockPredictor</b> &rarr; <i>uses</i> &rarr; <b>DataFetcher</b> (lazy, via <font face='Courier'>_get_fetcher()</font>) and <b>FeatureEngine</b> (via <font face='Courier'>_get_engine()</font>) &mdash; model as dependency or aggregation, both injectable for testing."))
st.append(bullet("<b>StockPredictor</b> &rarr; <i>composed of</i> &rarr; <b>PredictorConfig</b> (one config instance per predictor)."))
st.append(bullet("<b>StockPredictor</b> &rarr; <i>produces</i> &rarr; <b>BacktestReport</b>, <b>WalkForwardReport</b>."))
st.append(bullet("<b>Analysis endpoints</b> &rarr; <i>use</i> &rarr; <b>DataFetcher</b>, <b>FeatureEngine</b>, <b>FinBERT module</b>, and <b>vectorbt</b> (external library)."))
st.append(bullet("<b>Prediction endpoints</b> &rarr; <i>use</i> &rarr; <b>StockPredictor</b> (process-wide singleton) and persist a <b>Prediction</b> entity."))

# ─────────────── 4. USE CASE ───────────────
st.append(PageBreak())
st.append(P("4. Actor and Use Case Specification &mdash; for the Use Case Diagram", "H1"))
st.append(P("Four actors. <b>Financial Analyst</b> and <b>Administrator</b> both generalise from <b>Investor</b> "
            "(they inherit every investor capability), which should be drawn as a generalisation arrow."))
st.append(table(["Actor","Type","Description"], [
 ["Investor","Primary human","Registered end user: analyses stocks, manages a portfolio, journals trades, buys strategies"],
 ["Financial Analyst","Primary human","An investor who additionally authors and publishes strategies"],
 ["Administrator","Primary human","Moderates the platform: users, listings, thresholds, reports"],
 ["Yahoo Finance API","External system","Supplies live quotes, historical OHLCV, fundamentals and news headlines"],
], [1.15*inch,0.95*inch,CW-2.1*inch]))

st.append(P("4.1 Use cases by actor", "H2"))
st.append(table(["ID","Use case","Actor(s)","Notes for the diagram"], [
 ["UC-01","Register account","Investor",""],
 ["UC-02","Log in","All human actors","&laquo;include&raquo; Authenticate"],
 ["UC-03","Manage profile","All human actors","Includes password change and avatar"],
 ["UC-04","Search stock","Investor","&laquo;include&raquo; Fetch market data"],
 ["UC-05","Configure factor weights","Investor","Six sliders, must total 100"],
 ["UC-06","Generate AI verdict","Investor","&laquo;include&raquo; Fetch market data, Analyse news sentiment"],
 ["UC-07","View live model prediction","Investor","&laquo;include&raquo; Run XGBoost model"],
 ["UC-08","Run backtest","Investor, Analyst","&laquo;include&raquo; Fetch historical data"],
 ["UC-09","Download backtest log","Investor, Analyst","&laquo;extend&raquo; Run backtest"],
 ["UC-10","Save strategy","Investor",""],
 ["UC-11","Manage portfolio","Investor","Add / update / close holdings"],
 ["UC-12","Manage watchlist","Investor","Add / remove tickers"],
 ["UC-13","Log trade in journal","Investor",""],
 ["UC-14","View journal statistics","Investor","Win rate, profit factor, equity curve"],
 ["UC-15","Browse marketplace","Investor","Search, filter, sort"],
 ["UC-16","Purchase strategy","Investor","Payment is simulated"],
 ["UC-17","Rate purchased strategy","Investor",""],
 ["UC-18","Request strategy publication","Investor, Analyst","&laquo;include&raquo; Validate against thresholds"],
 ["UC-19","Review pending listing","Administrator","Views the full backtest report"],
 ["UC-20","Approve / reject listing","Administrator","&laquo;extend&raquo; Review pending listing"],
 ["UC-21","Remove or delete listing","Administrator",""],
 ["UC-22","Manage users","Administrator","Change role, suspend, delete"],
 ["UC-23","Configure approval thresholds","Administrator","Updates platform_settings"],
 ["UC-24","View revenue and statistics","Administrator",""],
 ["UC-25","Receive notifications","Investor","Mark read / mark all read"],
], [0.55*inch,1.7*inch,1.15*inch,CW-3.4*inch], code_cols=(0,)))

st.append(P("4.2 Included / extended use cases (shared sub-behaviour)", "H2"))
st.append(table(["Sub use case","Included by","Involves"], [
 ["Authenticate","UC-02 and every protected use case","Validate JWT, check role"],
 ["Fetch market data","UC-04, UC-06, UC-07, UC-08","Yahoo Finance API actor"],
 ["Analyse news sentiment","UC-06","FinBERT model, Yahoo Finance headlines"],
 ["Run XGBoost model","UC-07","StockPredictor; persists a Prediction"],
 ["Validate against thresholds","UC-18","Reads platform_settings"],
], [1.35*inch,1.9*inch,CW-3.25*inch]))

# ─────────────── 5. DFD ───────────────
st.append(PageBreak())
st.append(P("5. Data Flow Specification &mdash; for the DFD", "H1"))
st.append(P("5.1 Context diagram (Level 0 of the levelling scheme)", "H2"))
st.append(mono(
"""  Investor ------ credentials, ticker, weights, trades, orders ------>
  Analyst -------- strategy definitions, publish requests ----------->  [ 0 ]
  Administrator -- approvals, user actions, threshold settings ----->  StockPilot
                                                                       System
            <----- verdicts, portfolio valuations, reports, alerts ---
                          ^                              |
       OHLCV, quotes,     |                              |  ticker / period
       fundamentals,      |                              v  requests
       news headlines     +---------- Yahoo Finance API -+"""))

st.append(P("5.2 Level 0 &mdash; processes, stores and flows", "H2"))
st.append(table(["Process","Name","Main inputs","Main outputs","Stores used"], [
 ["1.0","User Authentication &amp; Profiles","credentials, profile edits","session token, profile","D1"],
 ["2.0","AI Stock Analysis","ticker, factor weights","verdict, confidence, factor scores","D2, D3, D7"],
 ["3.0","Portfolio &amp; Watchlist","position data, tickers","valuation, P/L, watch list","D2, D4"],
 ["4.0","Trading Journal","trade entries","win rate, profit factor, equity curve","D5"],
 ["5.0","Strategy &amp; Marketplace","weights, publish request, purchase","backtest report, listings","D6, D8, D9"],
 ["6.0","Administration","approvals, user actions, thresholds","platform reports","D1, D8, D9"],
], [0.55*inch,1.5*inch,1.3*inch,1.35*inch,CW-4.7*inch], code_cols=(0,)))
st.append(Spacer(1,4))
st.append(table(["Store","Contents (tables)"], [
 ["D1","users"],["D2","stocks"],["D3","predictions, price_history"],["D4","holdings, watchlist"],
 ["D5","trades"],["D6","strategies"],["D7","notifications"],
 ["D8","marketplace_listings, marketplace_ratings"],["D9","platform_settings"],
], [0.6*inch,CW-0.6*inch], code_cols=(0,)))

st.append(P("5.3 Level 1 &mdash; decomposition of process 2.0 (AI Stock Analysis)", "H2"))
st.append(mono(
"""  Investor --(ticker, six factor weights)--> [2.1] Retrieve Market Data
                                                  |  <--> Yahoo Finance API
                                                  v  (OHLCV, fundamentals)
                                            [2.2] Compute Technical Indicators
                                                  |  (23 indicator columns)
                                                  v
      Yahoo Finance --(headlines)--> [2.3] Analyse News Sentiment (FinBERT)
                                                  |  (0-100 sentiment score)
                                                  v
                                            [2.4] Compute Six-Factor Scores
                                                  |  (sentiment, momentum, valuation,
                                                  v   volatility, volume, growth)
                                            [2.5] Apply Weights -> Composite Score
                                                  |
                                                  v
                                            [2.6] Derive Verdict + Confidence
                                                  |
              +-----------------------------------+------------------------+
              v                                                            v
   Investor <-- BUY / HOLD / SELL, confidence,                   D7 notifications
                per-factor breakdown                             (verdict_change)

  Parallel path, same actor:
   Investor --(ticker)--> [2.7] Run XGBoost Model --> writes D3 predictions
                                 (StockPredictor.predict)  --> signal to Investor"""))

st.append(P("5.4 Level 1 &mdash; decomposition of process 5.0 (Strategy &amp; Marketplace)", "H2"))
st.append(mono(
"""  Analyst --(name, weights)--> [5.1] Create / Edit Strategy --> D6 strategies
  Analyst --(ticker, period)--> [5.2] Run Backtest Engine (vectorbt)
                                       |  <-- historical OHLCV (Yahoo Finance)
                                       v  metrics + trade ledger
                                 [5.3] Validate Against Thresholds <-- D9 settings
                                       |
                     fail <------------+------------> pass
                       |                                |
          error to Analyst                   [5.4] Create Listing (status=review)
                                                        |--> D8 listings
  Investor --(browse/filter)--> [5.5] Publish Listings --> listings to Investor
  Investor --(purchase)-------> [5.6] Record Purchase --> increments sales_count
  Investor --(rating)---------> [5.7] Submit Rating ---> D8 ratings"""))

# ─────────────── 6. SEQUENCE ───────────────
st.append(PageBreak())
st.append(P("6. Sequence Specification &mdash; for UML Sequence Diagrams", "H1"))
st.append(P("Six representative scenarios. Participants are given in lifeline order; messages are numbered "
            "in execution order, with returns shown as dashed replies in the diagram."))

seqs = [
 ("6.1 Log in", "Investor, LoginUI, AuthContext, APIClient, AuthEndpoint, UserRepository(DB)",
"""1  Investor -> LoginUI            : enter email + password
2  LoginUI -> AuthContext          : login(email, password)
3  AuthContext -> APIClient        : POST /api/v1/auth/login
4  APIClient -> AuthEndpoint       : HTTP request
5  AuthEndpoint -> DB              : SELECT user WHERE email = ?
6  DB --> AuthEndpoint             : user row (or none)
   alt credentials invalid
7a AuthEndpoint --> APIClient      : 401 Unauthorized
   else valid
7b AuthEndpoint -> AuthEndpoint    : verify_password(bcrypt)
8b AuthEndpoint -> AuthEndpoint    : create_access_token / create_refresh_token
9b AuthEndpoint --> APIClient      : 200 {access, refresh, user}
   end
10 APIClient --> AuthContext       : token response
11 AuthContext -> LocalStorage     : store sp_access_token, sp_refresh_token
12 AuthContext --> LoginUI         : session established
13 LoginUI -> Router               : navigate to Dashboard"""),

 ("6.2 Generate an AI verdict (six-factor)", "Investor, AdvisorUI, useFactorAnalysis, APIClient, AnalysisEndpoint, DataFetcher, FeatureEngine, FinBERT, YahooFinance",
"""1  Investor -> AdvisorUI          : select ticker, adjust weight sliders
2  AdvisorUI -> useFactorAnalysis  : ticker + weights changed
3  useFactorAnalysis -> APIClient  : GET /analysis/{ticker}/factors?w_*=..
4  APIClient -> AnalysisEndpoint   : HTTP request (JWT attached)
5  AnalysisEndpoint -> DataFetcher : fetch_historical(ticker, "6mo")
6  DataFetcher -> YahooFinance     : download OHLCV
7  YahooFinance --> DataFetcher    : price DataFrame
8  DataFetcher --> AnalysisEndpoint: raw OHLCV
9  AnalysisEndpoint -> FeatureEngine : calculate_all_features(raw)
10 FeatureEngine --> AnalysisEndpoint : 23 indicator columns
11 AnalysisEndpoint -> FinBERT     : analyze_ticker(ticker, max=10)
12 FinBERT -> YahooFinance         : fetch news headlines
13 YahooFinance --> FinBERT        : headlines
14 FinBERT --> AnalysisEndpoint    : sentiment score 0-100
   alt no headlines or error
14a AnalysisEndpoint -> AnalysisEndpoint : fall back to OBV-trend proxy
   end
15 AnalysisEndpoint -> AnalysisEndpoint : compute 6 factor scores
16 AnalysisEndpoint -> AnalysisEndpoint : composite = SUM(score * weight / total)
17 AnalysisEndpoint -> AnalysisEndpoint : derive verdict + confidence
18 AnalysisEndpoint --> APIClient  : 200 {factors, composite, verdict, confidence}
19 APIClient --> AdvisorUI         : render verdict card and factor bars"""),

 ("6.3 Live XGBoost prediction", "Investor, AdvisorUI, useLivePrediction, APIClient, PredictionEndpoint, StockPredictor, DataFetcher, FeatureEngine, DB",
"""1  AdvisorUI -> useLivePrediction : ticker selected
2  useLivePrediction -> APIClient  : GET /predictions/{ticker}/live
3  APIClient -> PredictionEndpoint : HTTP request (JWT)
4  PredictionEndpoint -> StockPredictor : predict(ticker)   [in threadpool]
   opt model not yet loaded
5a StockPredictor -> StockPredictor : load_model() from model.pkl
   end
6  StockPredictor -> DataFetcher   : fetch_historical(ticker, "6mo")
7  DataFetcher --> StockPredictor  : OHLCV
8  StockPredictor -> FeatureEngine : calculate_all_features()
9  FeatureEngine --> StockPredictor: indicators
10 StockPredictor -> StockPredictor: select stationary feature columns
11 StockPredictor -> StockPredictor: model.predict_proba(latest row)
12 StockPredictor --> PredictionEndpoint : {signal, confidence, p_up, p_down}
13 PredictionEndpoint -> DB        : INSERT INTO predictions
14 DB --> PredictionEndpoint       : persisted row
15 PredictionEndpoint --> APIClient: 200 PredictionOut
16 APIClient --> AdvisorUI         : render verdict + MODEL LIVE badge"""),

 ("6.4 Run a backtest", "Investor, AdvisorUI, useBacktest, APIClient, AnalysisEndpoint, DataFetcher, FeatureEngine, vectorbt",
"""1  Investor -> AdvisorUI          : choose period, click Run Backtest
2  AdvisorUI -> useBacktest        : refetch()
3  useBacktest -> APIClient        : GET /analysis/{t}/backtest?period&risk&horizon&w_*
4  APIClient -> AnalysisEndpoint   : HTTP request
5  AnalysisEndpoint -> AnalysisEndpoint : resolve RISK_CONFIG + HORIZON_CONFIG
                                          -> buy/sell thresholds, sl_stop, tp_stop
6  AnalysisEndpoint -> DataFetcher : fetch_historical(ticker, period)
7  DataFetcher --> AnalysisEndpoint: OHLCV
8  AnalysisEndpoint -> FeatureEngine : calculate_all_features()
   alt fewer than 60 rows
9a AnalysisEndpoint --> APIClient  : 400 Insufficient data
   else enough data
9b AnalysisEndpoint -> vectorbt    : Portfolio.from_signals(entries, exits,
                                       sl_stop, tp_stop, fees, slippage)
10b vectorbt --> AnalysisEndpoint  : portfolio simulation
11b AnalysisEndpoint -> AnalysisEndpoint : extract metrics + trade ledger
12b AnalysisEndpoint --> APIClient : 200 BacktestMetrics
   end
13 APIClient --> AdvisorUI         : render stats, equity curve, Download log"""),

 ("6.5 Publish a strategy and get it approved", "Analyst, MarketplaceUI, APIClient, StrategyEndpoint, DB, Administrator, AdminUI, AdminEndpoint",
"""1  Analyst -> MarketplaceUI       : open publish dialog, select strategy, set price
2  MarketplaceUI -> APIClient      : POST /strategies/{id}/publish {metrics, price}
3  APIClient -> StrategyEndpoint   : HTTP request
4  StrategyEndpoint -> DB          : SELECT strategy WHERE id AND owner_id = me
5  DB --> StrategyEndpoint         : strategy (or none -> 404)
6  StrategyEndpoint -> DB          : SELECT platform_settings (thresholds)
7  StrategyEndpoint -> StrategyEndpoint : validate 5 metrics against thresholds
   alt any threshold fails
8a StrategyEndpoint --> APIClient  : 400 with per-metric breakdown, nothing stored
   else all pass
8b StrategyEndpoint -> DB          : INSERT/UPDATE listing SET status = 'review'
9b StrategyEndpoint --> APIClient  : 200 {status: review, listing_id}
   end
--- later, different actor ---
10 Administrator -> AdminUI        : open Pending Reviews
11 AdminUI -> AdminEndpoint        : GET /admin/pending
12 AdminEndpoint -> DB             : SELECT listings WHERE status='review'
13 AdminEndpoint --> AdminUI       : listings + full backtest reports
14 Administrator -> AdminUI        : click Approve
15 AdminUI -> AdminEndpoint        : POST /admin/listings/{id}/approve
16 AdminEndpoint -> DB             : status='verified', listed_at=now(),
                                     strategy.is_published = true
17 AdminEndpoint --> AdminUI       : 200 -> listing now public"""),

 ("6.6 Load the portfolio with live valuation", "Investor, PortfolioUI, usePortfolio, APIClient, PortfolioEndpoint, DB, YahooFinance",
"""1  Investor -> PortfolioUI        : open Portfolio
2  PortfolioUI -> usePortfolio     : mount
3  usePortfolio -> APIClient       : GET /api/v1/portfolio
4  APIClient -> PortfolioEndpoint  : HTTP request
5  PortfolioEndpoint -> DB         : SELECT holdings WHERE user_id AND closed_at IS NULL
6  DB --> PortfolioEndpoint        : holdings
7  PortfolioEndpoint -> DB         : SELECT stocks WHERE ticker IN (...)
8  DB --> PortfolioEndpoint        : name / sector map
   par for each ticker (thread pool, max 4 concurrent)
9  PortfolioEndpoint -> YahooFinance : fast_info last_price
10 YahooFinance --> PortfolioEndpoint : price (or failure -> keep stored price)
   end
11 PortfolioEndpoint -> PortfolioEndpoint : merge name + live price into each holding
12 PortfolioEndpoint --> APIClient : 200 holdings[]
13 APIClient --> PortfolioUI       : compute market value, cost basis, P/L; render"""),
]
for title, parts, body in seqs:
    st.append(P(title, "H2"))
    st.append(P(f"<b>Participants (lifeline order):</b> {parts}"))
    st.append(mono(body))

# ─────────────── 7. STATE ───────────────
st.append(PageBreak())
st.append(P("7. State Specification &mdash; for UML State Machine Diagrams", "H1"))

st.append(P("7.1 MarketplaceListing lifecycle (the richest state machine)", "H2"))
st.append(mono(
"""   [*] --> draft            : listing row created

   draft    --> review      : owner submits, all 5 thresholds pass
   review   --> verified    : administrator approves
                              (sets listed_at, strategy.is_published = true)
   review   --> removed     : administrator rejects
   verified --> listed      : listing made publicly visible
   verified --> removed     : administrator removes an active listing
   listed   --> removed     : administrator removes an active listing
   removed  --> review      : owner resubmits with new backtest metrics
   any      --> [*]         : administrator deletes the listing permanently

   Guards / notes:
     - draft -> review requires: trades >= min_trades AND winrate >= min_winrate
       AND sharpe >= min_sharpe AND drawdown <= max_drawdown
       AND profit_factor >= min_profit_factor   (all read from platform_settings)
     - approve and reject are only legal from 'review' (else HTTP 400)
     - remove is legal from any active state
     - re-submitting while already in 'review' is rejected (400 Already pending)
     - re-submitting while 'verified' is rejected (400 Already published)"""))

st.append(P("7.2 Holding lifecycle", "H2"))
st.append(mono(
"""   [*] --> open      : holding created (closed_at IS NULL)
   open --> open     : quantity or avg_cost updated
   open --> open     : current_price refreshed from Yahoo Finance on each read
   open --> closed   : closed_at set (position closed, history retained)
   open --> [*]      : holding deleted outright"""))

st.append(P("7.3 Strategy lifecycle", "H2"))
st.append(mono(
"""   [*] --> unpublished        : created (is_preset=false, is_published=false)
   unpublished --> unpublished : name / description / weights edited
   unpublished --> pending     : publish requested -> listing enters 'review'
   pending     --> published   : administrator approves (is_published = true)
   published   --> unpublished : listing rejected or removed (is_published = false)
   unpublished --> [*]         : deleted (blocked by RESTRICT while a listing exists)

   Note: a system preset (is_preset = true, owner_id = NULL) is visible to every
         user and is never owned or published through this flow."""))

st.append(P("7.4 User account status", "H2"))
st.append(mono(
"""   [*] --> active            : registration (role = investor)
   active   --> suspended     : administrator toggles status (is_active = false)
   suspended --> active       : administrator toggles status back
   active   --> active        : role changed (investor <-> analyst <-> admin)
   any      --> [*]           : administrator deletes the account
                                (cascades to holdings, watchlist, trades,
                                 strategies, notifications, ratings)

   Note: a suspended user's next request fails authentication with 401,
         because get_current_user rejects accounts where is_active is false."""))

# ─────────────── 8. ACTIVITY ───────────────
st.append(P("8. Activity Specification &mdash; for UML Activity Diagrams", "H1"))

st.append(P("8.1 Generate an investment verdict", "H2"))
st.append(mono(
"""  (start)
    |
  [Select ticker]
    |
  [Choose preset strategy]  --or--  [Adjust six factor weights]
    |
  <weights total 100?> --no--> [Show validation error] --> back to adjust
    | yes
  [Request analysis]
    |
  fork
    |-- [Fetch OHLCV from Yahoo Finance]
    |-- [Fetch news headlines]
  join
    |
  [Compute 23 technical indicators]
    |
  [Classify headlines with FinBERT]
    |
  <headlines available?> --no--> [Use OBV-trend sentiment proxy]
    | yes                              |
  [Use FinBERT sentiment score] <------+
    |
  [Compute six factor scores]
    |
  [Apply weights -> composite score]
    |
  <composite vs thresholds>
    |-- >= buy  --> [Verdict = BUY]
    |-- <= sell --> [Verdict = SELL]
    |-- else    --> [Verdict = HOLD]
    |
  [Compute confidence from factor consensus]
    |
  [Display verdict, confidence and per-factor breakdown]
    |
  (end)"""))

st.append(P("8.2 Publish a strategy to the marketplace", "H2"))
st.append(mono(
"""  (start)
    |
  [Open publish dialog]
    |
  <has an unpublished saved strategy?> --no--> [Prompt to create one in Advisor] -> (end)
    | yes
  [Select strategy and set price]
    |
  [Run backtest to auto-fill metrics]  --or--  [Enter metrics manually]
    |
  [Evaluate metrics against live thresholds (client preview)]
    |
  <all five thresholds met?> --no--> [Disable submit, show failing checks] -> back
    | yes
  [Submit publish request]
    |
  [Server re-validates against platform_settings]     <<authoritative>>
    |
  <server validation passes?> --no--> [400 with per-metric breakdown; nothing stored] -> (end)
    | yes
  <existing listing state?>
    |-- review    --> [400 Already pending review] -> (end)
    |-- verified  --> [400 Already published]      -> (end)
    |-- none      --> [Create listing, status = review]
    |-- other     --> [Update listing, status = review]
    |
  [Notify: awaiting administrator review]
    |
  ==== administrator ====
  [Administrator opens Pending Reviews]
    |
  [Inspect backtest report and threshold checklist]
    |
  <decision>
    |-- approve --> [status = verified, listed_at = now, is_published = true] --> [Listing is public]
    |-- reject  --> [status = removed, is_published = false]
    |
  (end)"""))

st.append(P("8.3 Authenticated request with token refresh", "H2"))
st.append(mono(
"""  (start)
    |
  [Component calls API through axios client]
    |
  [Request interceptor attaches Bearer access token]
    |
  [Send HTTP request]
    |
  <response status>
    |-- 2xx --> [Return data to component] --> (end)
    |-- 401 -->
          |
        <already retried once?> --yes--> [Reject error] --> (end)
          | no
        <refresh already in flight?> --yes--> [Queue request; await new token]
          | no                                        |
        [Read refresh token from localStorage]        |
          |                                           |
        <refresh token present?> --no--> [Clear tokens; redirect /auth] --> (end)
          | yes                                       |
        [POST /auth/refresh]                          |
          |                                           |
        <refresh succeeded?>                          |
          |-- no  --> [Reject queued requests; clear tokens; redirect /auth] -> (end)
          |-- yes --> [Store new token; release queue] <-+
                        |
                      [Retry original request with new token] --> (end)"""))

# ─────────────── 9. COMPONENT ───────────────
st.append(PageBreak())
st.append(P("9. Component and Deployment Specification", "H1"))
st.append(P("9.1 Components and their interfaces", "H2"))
st.append(table(["Component","Layer","Provides","Requires"], [
 ["React SPA","Presentation","User interface, client-side routing and state","REST API over HTTPS"],
 ["API Router","Application","56 REST endpoints under /api/v1","Auth, services, ORM session"],
 ["Auth &amp; RBAC","Application","get_current_user, require_role","users table, JWT secret"],
 ["Analysis Service","AI &amp; Analytics","Six-factor scoring, verdict, backtest","DataFetcher, FeatureEngine, FinBERT, vectorbt"],
 ["StockPredictor","AI &amp; Analytics","Trained XGBoost signal + probabilities","DataFetcher, FeatureEngine, model.pkl"],
 ["FinBERT Module","AI &amp; Analytics","News headline sentiment 0-100","Transformers model, Yahoo Finance"],
 ["FeatureEngine","Data","23 technical indicator columns","raw OHLCV DataFrame"],
 ["DataFetcher","Data","Historical and live market data","Yahoo Finance API"],
 ["ORM / Session","Storage","Async session, transaction boundary","PostgreSQL via asyncpg"],
], [1.15*inch,0.9*inch,1.65*inch,CW-3.7*inch]))

st.append(P("9.2 Deployment nodes", "H2"))
st.append(mono(
"""  +-------------------+        HTTPS / JSON        +--------------------------+
  |   Client Device   | <------------------------> |   Application Server     |
  |  <<device>>       |                            |   <<node>>               |
  |  Browser          |                            |  Uvicorn + FastAPI       |
  |   - React SPA     |                            |   - API Router           |
  |   - localStorage  |                            |   - AI/Analytics services|
  |     (JWT tokens)  |                            |   - model.pkl (XGBoost)  |
  +-------------------+                            |   - FinBERT weights      |
                                                   +--------------------------+
                                                        |                |
                                          asyncpg (TCP) |                | HTTPS
                                                        v                v
                                          +---------------------+  +------------------+
                                          |  Database Server    |  | Yahoo Finance    |
                                          |  <<node>>           |  | <<external>>     |
                                          |  PostgreSQL 16      |  |  quotes, OHLCV,  |
                                          |   - 12 tables       |  |  fundamentals,   |
                                          +---------------------+  |  news headlines  |
                                                                   +------------------+
  Static files: /uploads (avatars) served by the application server."""))

# ─────────────── 10. RULES ───────────────
st.append(P("10. Business Rules and Constraints", "H1"))
st.append(P("Use these to annotate diagrams with constraints, guards and notes."))
st.append(table(["ID","Rule","Enforced where"], [
 ["BR-01","Email must be unique across users","DB unique constraint + registration check"],
 ["BR-02","Passwords are stored only as bcrypt hashes","core/security.py"],
 ["BR-03","New passwords must be at least 8 characters","users endpoint"],
 ["BR-04","A user cannot add the same ticker to their watchlist twice","UNIQUE(user_id, ticker) + app check"],
 ["BR-05","Factor weights must total 100","Client validation before save"],
 ["BR-06","A strategy may have at most one marketplace listing","UNIQUE strategy_id"],
 ["BR-07","A listing may only be published after passing all five backtest thresholds","publish endpoint, server-side"],
 ["BR-08","Thresholds are configurable at runtime and apply immediately","platform_settings singleton"],
 ["BR-09","Only an administrator may approve, reject, remove or delete listings","require_role(admin)"],
 ["BR-10","Approve and reject are valid only from status 'review'","admin endpoint guards"],
 ["BR-11","An administrator cannot change their own role, suspend or delete themselves","admin endpoint self-guards"],
 ["BR-12","Deleting a user cascades to all of their owned records","FK ON DELETE CASCADE"],
 ["BR-13","A strategy cannot be deleted while a listing references it","FK RESTRICT"],
 ["BR-14","Users may only read or modify their own holdings, trades, watchlist and strategies","Ownership in the WHERE clause; returns 404, not 403"],
 ["BR-15","A suspended account is refused on the next request","get_current_user checks is_active"],
 ["BR-16","A backtest requires at least 60 rows of history","analysis endpoint guard"],
 ["BR-17","Backtests apply 0.1% fees and 0.05% slippage","vectorbt configuration"],
 ["BR-18","Every request commits as one transaction or rolls back entirely","get_db() session scope"],
 ["BR-19","Marketplace purchases are simulated; no payment processor is integrated","Design scope"],
 ["BR-20","Verdicts are decision support, not licensed financial advice","Disclaimer requirement"],
], [0.55*inch,2.75*inch,CW-3.3*inch], code_cols=(0,)))

# ─────────────── 11. DEVIATIONS ───────────────
st.append(PageBreak())
st.append(P("11. Design Deviations &mdash; read before assuming", "H1"))
st.append(callout("These override conventional expectations",
    "The points below are places where the implementation deliberately or accidentally differs from what a "
    "designer would normally assume. Diagrams should follow <b>this section</b> rather than the textbook pattern.",
    LIGHTRED, RED))
st.append(Spacer(1,6))

st.append(P("11.1 Instrument association is by ticker string, not foreign key", "H3"))
st.append(P("<font face='Courier'>holdings</font>, <font face='Courier'>watchlist</font>, "
            "<font face='Courier'>trades</font>, <font face='Courier'>predictions</font> and "
            "<font face='Courier'>price_history</font> all store a <font face='Courier'>ticker</font> string; none "
            "has a foreign key to <font face='Courier'>stocks</font>. Ticker symbols are stable and are the same keys "
            "used by the external API, so this avoids a join on every lookup. On a strict ERD these appear as "
            "independent entities; if a conceptual ERD is wanted, model <font face='Courier'>Stock</font> as an "
            "associated entity and note that the link is logical rather than referential."))

st.append(P("11.2 Two independent recommendation engines", "H3"))
st.append(table(["Engine","Where","Used for","Persists?"], [
 ["Six-factor weighted model","/analysis/{t}/factors","The explainable verdict, factor bars and backtest signals","No"],
 ["XGBoost classifier","/predictions/{t}/live","Probabilistic BUY/HOLD/SELL with confidence","Yes &mdash; writes a predictions row"],
], [1.5*inch,1.5*inch,CW-3.65*inch,0.65*inch]))
st.append(P("They are separate models that can disagree. Class and sequence diagrams should show both paths "
            "rather than a single 'AI engine'."))

st.append(P("11.3 Sentiment differs between live analysis and backtest", "H3"))
st.append(P("The live verdict uses <b>FinBERT</b> over recent Yahoo Finance headlines. The backtest cannot &mdash; "
            "historical per-day sentiment is not stored &mdash; so it substitutes an <b>on-balance-volume trend proxy</b> "
            "for the sentiment factor. Any diagram covering the backtest path must not show FinBERT."))

st.append(P("11.4 No RSS pipeline and no scheduler", "H3"))
st.append(P("News headlines are fetched <b>on demand</b> during a request. There is no scheduled ingestion job, no "
            "message queue, no daily-sentiment table and no pipeline log. Do not draw a batch or scheduler component."))

st.append(P("11.5 Tables that exist but are not on the live path", "H3"))
st.append(P("<font face='Courier'>price_history</font> is read only by <font face='Courier'>/stocks/{ticker}/history</font> "
            "and is populated by the seed script; the live analysis and backtest fetch fresh data from Yahoo Finance "
            "instead. <font face='Courier'>marketplace_ratings</font> has no endpoint yet, although "
            "<font face='Courier'>avg_rating</font> and <font face='Courier'>rating_count</font> on the listing are "
            "displayed. Both remain part of the designed schema and should appear on the ERD."))

st.append(P("11.6 Purchases are not a separate entity", "H3"))
st.append(P("There is no <font face='Courier'>purchases</font> table. A sale is recorded by incrementing "
            "<font face='Courier'>sales_count</font> on the listing, so no purchase entity should appear on the ERD."))

st.append(P("11.7 Backtesting is single-ticker", "H3"))
st.append(P("The vectorbt simulation runs on one ticker over the selected period; it does not aggregate across a "
            "basket. Note this on any activity or sequence diagram covering the backtest."))

st.append(P("11.8 Publishing is open to all authenticated users", "H3"))
st.append(P("Although an <font face='Courier'>analyst</font> role exists, the publish endpoint accepts any signed-in "
            "user; quality is gated by the threshold check and administrator approval rather than by role. On the "
            "use-case diagram, associate UC-18 with Investor as well as Financial Analyst."))

def footer(canvas, d):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.4)
    canvas.setFillColor(GREY)
    canvas.drawCentredString(PAGE_W/2, 24,
        f"StockPilot - Diagram Design Specification  |  Group 13, CSE5015  |  Page {d.page}")
    canvas.restoreState()

doc.build(st, onFirstPage=footer, onLaterPages=footer)
print("Generated:", OUT)
