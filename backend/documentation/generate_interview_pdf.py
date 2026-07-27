"""Generate the Expert Interview (Requirement Gathering) PDF for StockPilot."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether,
)

NAVY   = HexColor("#1F3864")
BLUE   = HexColor("#2E5496")
ACCENT = HexColor("#C0A062")
GREEN  = HexColor("#1E7E45")
GREY   = HexColor("#595959")
LIGHTB = HexColor("#EEF2F9")
LIGHTG = HexColor("#EEF7F1")
LIGHTGOLD = HexColor("#FBF6E9")
BORDER = HexColor("#C9D3E6")
TEXT   = HexColor("#1A1A1F")

PAGE_W, PAGE_H = A4
MARGIN = 54
CONTENT_W = PAGE_W - 2 * MARGIN
OUT = os.path.join(os.path.dirname(__file__), "StockPilot_Expert_Interview.pdf")

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                        topMargin=MARGIN, bottomMargin=MARGIN,
                        title="StockPilot - Expert Interview (Requirement Gathering)")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle("TitleX", parent=styles["Title"], fontName="Times-Bold",
                          fontSize=24, leading=28, textColor=NAVY, alignment=TA_LEFT, spaceAfter=4))
styles.add(ParagraphStyle("Sub", parent=styles["Normal"], fontName="Times-Italic",
                          fontSize=12, leading=16, textColor=GREY, spaceAfter=14))
styles.add(ParagraphStyle("QHead", parent=styles["Heading2"], fontName="Times-Bold",
                          fontSize=13.5, leading=17, textColor=BLUE, spaceBefore=16, spaceAfter=6))
styles.add(ParagraphStyle("Question", parent=styles["Normal"], fontName="Times-Italic",
                          fontSize=11, leading=16, textColor=NAVY, spaceAfter=6,
                          leftIndent=10, alignment=TA_JUSTIFY))
styles.add(ParagraphStyle("ALabel", parent=styles["Normal"], fontName="Times-Bold",
                          fontSize=10.5, leading=14, textColor=TEXT))
styles.add(ParagraphStyle("Answer", parent=styles["Normal"], fontName="Times-Roman",
                          fontSize=10.5, leading=15.5, textColor=TEXT, alignment=TA_JUSTIFY,
                          spaceAfter=6))
styles.add(ParagraphStyle("Body", parent=styles["Normal"], fontName="Times-Roman",
                          fontSize=10.5, leading=15.5, textColor=TEXT, alignment=TA_JUSTIFY,
                          spaceAfter=8))
styles.add(ParagraphStyle("ReqLine", parent=styles["Normal"], fontName="Times-Roman",
                          fontSize=10, leading=14, textColor=GREEN, alignment=TA_JUSTIFY))
styles.add(ParagraphStyle("CalloutBody", parent=styles["Normal"], fontName="Times-Roman",
                          fontSize=9.5, leading=14, textColor=TEXT, alignment=TA_JUSTIFY))
styles.add(ParagraphStyle("Cell", parent=styles["Normal"], fontName="Times-Roman",
                          fontSize=10, leading=13, textColor=TEXT))
styles.add(ParagraphStyle("CellB", parent=styles["Normal"], fontName="Times-Bold",
                          fontSize=10, leading=13, textColor=TEXT))


def rule(color=ACCENT, w=1.2, after=12):
    t = Table([[""]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), w, color),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), after)]))
    return t


def callout(title, bodytext, bg, accent):
    tp = Paragraph(f"<b>{title}</b>", ParagraphStyle("ct", fontName="Times-Bold",
                   fontSize=10, leading=13, textColor=TEXT))
    bp = Paragraph(bodytext, styles["CalloutBody"])
    t = Table([[tp], [bp]], colWidths=[CONTENT_W - 16])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (0, 0), 8), ("BOTTOMPADDING", (-1, -1), (-1, -1), 9),
        ("LINEBEFORE", (0, 0), (0, -1), 3, accent), ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


story = []

# Header
story.append(Paragraph("StockPilot", styles["TitleX"]))
story.append(Paragraph("Expert Interview - Requirement Gathering", ParagraphStyle(
    "t2", fontName="Times-Bold", fontSize=15, leading=19, textColor=ACCENT, spaceAfter=6)))
story.append(Paragraph("A structured interview with a Quality Assurance Engineer to elicit "
                       "professional requirements for an AI-based investment advisory platform.",
                       styles["Sub"]))
story.append(rule())

# Metadata table
meta = [
    ["Interviewee role", "Quality Assurance Engineer"],
    ["Organisation", "London Stock Exchange Group (LSEG)"],
    ["Technique", "Semi-structured expert interview (requirement gathering)"],
    ["Purpose", "Validate the problem and elicit functional / non-functional requirements"],
    ["Date", "________________________"],
    ["Conducted by", "Group 77 - CSE5015 Computing Project"],
]
mt = Table([[Paragraph(f"<b>{r[0]}</b>", styles["Cell"]), Paragraph(r[1], styles["Cell"])] for r in meta],
           colWidths=[1.7 * inch, CONTENT_W - 1.7 * inch])
mt.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
    ("BACKGROUND", (0, 0), (0, -1), LIGHTB),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(mt)
story.append(Spacer(1, 12))

story.append(callout(
    "Note on this record",
    "The responses below capture expert input on the requirements for a system of this type. They are "
    "used as evidence in the requirement-gathering phase and are to be read alongside the user survey "
    "(which provides the end-user perspective). Each answer is followed by the specific requirement it "
    "elicits for StockPilot.",
    LIGHTGOLD, ACCENT))
story.append(Spacer(1, 8))

# ---- Q&A data ----
QA = [
    ("1. Problem validation",
     "From your industry perspective, is the problem we are targeting - retail investors overwhelmed "
     "by scattered data and opaque 'black-box' signals - a real, worthwhile gap? What would you add to "
     "how we have framed it?",
     "Yes, it is a real and well-known gap. Retail investors do not just have scattered data, they have "
     "inconsistent data: two sources disagree on a price or a fundamental, and a non-professional cannot "
     "tell which is correct. The bigger issue is that opaque signal services give a verdict with no basis, "
     "so the user cannot judge whether to trust it, and cannot learn from it. I would frame the problem not "
     "only as 'information overload' but as a decision-confidence and auditability gap: users need to see "
     "why a recommendation was made and be able to trace it back to the underlying data.",
     "Refines the problem statement to include data inconsistency and the need for an auditable, "
     "traceable recommendation."),

    ("2. Essential vs. nice-to-have features",
     "For a tool giving retail investors Buy / Hold / Sell guidance, which features would you consider "
     "absolutely essential, and which are just nice-to-have?",
     "Essential features are reliable market data, a clear signal accompanied by its reasoning, and "
     "historical validation of that signal through backtesting; without those three you do not have a "
     "credible product. Portfolio tracking and secure accounts are also table-stakes. The community "
     "features - a strategy marketplace, ratings, social sharing, and deep news sentiment - are valuable "
     "but the product stands without them, so I would treat those as secondary.",
     "MoSCoW split - Must: market data, explainable signal, backtesting, portfolio, secure auth; "
     "Should: trade journal, sentiment, marketplace; Could: ratings, sharing."),

    ("3. Data requirements",
     "What data - types, quality, and freshness - does a system like this need to be credible? Is a free "
     "source like yfinance good enough for an advisory tool, or where is the minimum bar?",
     "You need OHLCV prices, corporate actions such as splits and dividends, and fundamentals, all on a "
     "point-in-time basis - the classic mistake is using data you could not have known on the date in "
     "question. Prices must be split- and dividend-adjusted. For an advisory tool performing end-of-day "
     "analysis and backtests, daily data is acceptable; intraday use would demand lower latency. A free "
     "source like yfinance is fine for a prototype or educational build and for end-of-day backtesting, but "
     "it has gaps, no service-level agreement, and rate limits, so for a production system the minimum bar "
     "is a licensed, corporate-action-adjusted feed. The key design requirement is to abstract the data "
     "source so it can be swapped, and to validate and clean the incoming data.",
     "Data-layer requirements - point-in-time correctness, adjusted prices, gap handling, and a swappable, "
     "validated data-access layer."),

    ("4. Trust and accuracy expectations",
     "What level of accuracy and reliability would a user (or you) need before trusting an AI "
     "recommendation? What would instantly make you distrust such a tool?",
     "No one expects it to be right every time - they expect it to be honest and consistent. What instantly "
     "destroys trust is a confident recommendation that turns out wrong with no explanation, results that "
     "change between runs for no visible reason, or a backtest that looks excellent only because it used "
     "future information. So calibrated confidence, reproducible results, and a clearly shown 'data as of' "
     "timestamp matter more than raw predictive accuracy.",
     "Non-functional requirements - deterministic and reproducible output, calibrated confidence scores, a "
     "visible data-as-of timestamp, and honest disclaimers."),

    ("5. Explainability requirement",
     "Our survey showed users only trust AI that explains itself. In your experience, what kind and depth "
     "of explanation does a financial recommendation need to feel credible?",
     "A number on its own is not enough. A credible financial recommendation shows which factors drove it, "
     "in which direction, and how strongly, together with the data it used and when. Ideally it also hints "
     "at what would change the call. For your six-factor model, that means surfacing each factor's "
     "contribution and the overall confidence in plain language, rather than a single opaque score.",
     "Functional requirement - a per-verdict factor-contribution breakdown with confidence, timestamp, and "
     "a plain-language rationale."),

    ("6. What makes a strategy 'proven'",
     "We plan to verify marketplace strategies via backtesting. What would a credible verification need to "
     "show before a strategy is considered genuinely proven rather than lucky?",
     "In-sample results prove nothing - anyone can curve-fit. I would want out-of-sample or walk-forward "
     "testing, a trade count large enough to be statistically meaningful, and risk-adjusted metrics such as "
     "the Sharpe ratio, maximum drawdown, and profit factor, not just total return. Critically, the test "
     "must include realistic transaction costs and slippage, and the strategy should hold up across "
     "different market conditions. Without those safeguards, a 'winning' strategy is probably just lucky or "
     "over-fitted.",
     "Marketplace verification requirement - approval gated on trade count, win rate, Sharpe, drawdown and "
     "profit factor, with fees and slippage applied, and out-of-sample testing where possible."),

    ("7. Non-functional expectations",
     "What performance, availability, and responsiveness would a financial app need to meet - what are the "
     "non-negotiables even for a basic version?",
     "For a basic version, analysis requests should return within a couple of seconds, the application "
     "should stay responsive during market hours, and it must degrade gracefully when the data source is "
     "slow or unavailable - it should cache and show last-known values rather than crash. Rate limits "
     "should be handled with caching. On security, proper authentication, encrypted storage, and role "
     "separation are non-negotiable.",
     "Non-functional requirements - a sub-two-second response target, caching, graceful degradation, uptime "
     "during market hours, and secure authentication with role-based access control."),

    ("8. Compliance, privacy and the advice boundary",
     "What legal, disclaimer, and data-privacy requirements should a stock-advisory platform build in from "
     "day one - especially the 'not licensed financial advice' line?",
     "The single most important thing is a prominent, unambiguous disclaimer that the platform provides "
     "educational decision-support and not licensed financial advice; that boundary protects you legally. "
     "Beyond that, apply privacy-by-design to user data - collect the minimum, secure it, and honour data "
     "rights - hash credentials, keep an audit log of every administrative action, and respect the data "
     "provider's terms of use.",
     "Legal and non-functional requirements - a clear advice disclaimer, data-privacy compliance, secure "
     "credential storage, administrative audit logging, and data-source terms compliance."),

    ("9. Trustworthy marketplace requirements",
     "We are building a marketplace where analysts publish strategies. What would make such a marketplace "
     "trustworthy and genuinely useful - verification, transparency, ratings, seller accountability?",
     "The verification has to be system-run, not self-reported - sellers must not be able to submit their "
     "own numbers. Show the methodology and metrics transparently, tie ratings to verified purchases so "
     "they cannot be gamed, keep sellers accountable through a real identity, and give administrators the "
     "ability to flag or remove strategies. Versioning matters too, so a seller cannot quietly swap a "
     "verified strategy for a different one after approval.",
     "Marketplace functional requirements - system-run backtest verification, verified-buyer ratings, "
     "seller accountability, administrative moderation, strategy versioning, and transparent metrics."),

    ("10. Safeguards and risk requirements",
     "What scenarios must the system handle safely - bad or missing data, extreme volatility, misleading "
     "signals - so it does not push users toward harmful decisions?",
     "The system must fail safe. If data is missing, stale, or a stock is halted, it should report "
     "'insufficient data' rather than emit a confident signal from bad inputs. Validate every input, bound "
     "the outputs, and consider suppressing or flagging signals during extreme volatility or on data gaps. "
     "A circuit-breaker on the data feed and clear messaging about uncertainty protect the user from acting "
     "on unreliable information.",
     "Risk and functional requirements - input validation, insufficient-data handling, fail-safe defaults, "
     "volatility and stale-data guards, and a data-source circuit-breaker."),
]

for head, q, a, req in QA:
    block = [
        Paragraph(head, styles["QHead"]),
        Paragraph(f'<b>Q:</b> "{q}"', styles["Question"]),
        Paragraph("<b>A (QA Engineer):</b>", styles["ALabel"]),
        Paragraph(a, styles["Answer"]),
        callout("Requirement elicited", req, LIGHTG, GREEN),
        Spacer(1, 6),
    ]
    story.append(KeepTogether(block))

# Closing
story.append(Spacer(1, 6))
story.append(rule(after=8))
story.append(Paragraph("How these findings feed the requirements", styles["QHead"]))
story.append(Paragraph(
    "Each 'Requirement elicited' line maps directly into the project's requirement tables and risk "
    "analysis: questions 2, 6 and 9 feed the functional requirements; questions 3, 4, 7 and 8 feed the "
    "non-functional requirements and feasibility study; and questions 1 and 10 refine the problem statement "
    "and risk register. Read together with the end-user survey, this expert input completes the "
    "requirement-gathering evidence for StockPilot.",
    styles["Body"]))


def footer(canvas, d):
    canvas.saveState()
    canvas.setFont("Times-Roman", 8)
    canvas.setFillColor(GREY)
    canvas.drawCentredString(PAGE_W / 2, 30,
                             f"StockPilot - Expert Interview (Requirement Gathering)  |  Group 77  |  Page {d.page}")
    canvas.restoreState()


doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("Generated:", OUT)
