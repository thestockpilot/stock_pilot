"""Generate a beginner-friendly PDF explaining all AI/ML components in StockPilot."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Flowable,
)

# ── Colours ──────────────────────────────────────────────────────────────
GOLD      = HexColor("#d4a853")
BORDER    = HexColor("#2e2e33")
MUTED     = HexColor("#a1a1aa")
BEAR      = HexColor("#ef4444")
PURPLE    = HexColor("#a855f7")

BG_WHITE     = HexColor("#FFFFFF")
ACCENT       = HexColor("#1a5276")
ACCENT2      = HexColor("#148f77")
CODE_BG      = HexColor("#f4f4f4")
HEADING_COL  = HexColor("#1a1a2e")
BODY_COL     = HexColor("#2c3e50")
LIGHT_BLUE   = HexColor("#ebf5fb")
LIGHT_GREEN  = HexColor("#e8f8f5")
LIGHT_GOLD   = HexColor("#fef9e7")
LIGHT_PURPLE = HexColor("#f4ecf7")
LIGHT_RED    = HexColor("#fdedec")

W, H = A4
CONTENT_W = W - 2 * inch


# ── Custom Flowables ─────────────────────────────────────────────────────
class SectionDivider(Flowable):
    def __init__(self, width=None):
        super().__init__()
        self._width = width or CONTENT_W

    def wrap(self, availWidth, availHeight):
        return min(self._width, availWidth), 8

    def draw(self):
        self.canv.setStrokeColor(GOLD)
        self.canv.setLineWidth(1.5)
        self.canv.line(0, 4, self._width, 4)


# ── Styles ───────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    "CoverTitle", fontName="Helvetica-Bold", fontSize=32,
    textColor=HEADING_COL, alignment=TA_CENTER, spaceAfter=8, leading=38,
))
styles.add(ParagraphStyle(
    "CoverSub", fontName="Helvetica", fontSize=14,
    textColor=MUTED, alignment=TA_CENTER, spaceAfter=4,
))
styles.add(ParagraphStyle(
    "ChapterTitle", fontName="Helvetica-Bold", fontSize=22,
    textColor=HEADING_COL, spaceBefore=0, spaceAfter=12, leading=28,
))
styles.add(ParagraphStyle(
    "SectionTitle", fontName="Helvetica-Bold", fontSize=15,
    textColor=ACCENT, spaceBefore=18, spaceAfter=8, leading=20,
))
styles.add(ParagraphStyle(
    "SubSection", fontName="Helvetica-Bold", fontSize=12,
    textColor=ACCENT2, spaceBefore=14, spaceAfter=6, leading=16,
))
styles.add(ParagraphStyle(
    "Body", fontName="Helvetica", fontSize=10,
    textColor=BODY_COL, alignment=TA_JUSTIFY, spaceAfter=8, leading=15,
))
styles.add(ParagraphStyle(
    "BodyBold", fontName="Helvetica-Bold", fontSize=10,
    textColor=BODY_COL, spaceAfter=4, leading=15,
))
styles.add(ParagraphStyle(
    "CodeBlock", fontName="Courier", fontSize=8.5,
    textColor=HexColor("#c0392b"), backColor=CODE_BG,
    spaceBefore=4, spaceAfter=8, leading=12,
    leftIndent=12, rightIndent=12, borderPadding=6,
))
styles.add(ParagraphStyle(
    "TOCEntry", fontName="Helvetica", fontSize=11,
    textColor=BODY_COL, spaceBefore=3, spaceAfter=3, leading=16,
    leftIndent=20,
))
styles.add(ParagraphStyle(
    "TOCChapter", fontName="Helvetica-Bold", fontSize=12,
    textColor=HEADING_COL, spaceBefore=8, spaceAfter=3, leading=18,
    leftIndent=0,
))
styles.add(ParagraphStyle(
    "BulletBody", fontName="Helvetica", fontSize=10,
    textColor=BODY_COL, spaceAfter=4, leading=14,
    leftIndent=24, bulletIndent=12,
))
# Callout styles
styles.add(ParagraphStyle(
    "CalloutTitle", fontName="Helvetica-Bold", fontSize=10,
    textColor=ACCENT, spaceAfter=4, leading=14,
))
styles.add(ParagraphStyle(
    "CalloutBody", fontName="Helvetica", fontSize=9.5,
    textColor=BODY_COL, alignment=TA_JUSTIFY, leading=14, spaceAfter=0,
))
# Table cell style
styles.add(ParagraphStyle(
    "CellText", fontName="Helvetica", fontSize=9,
    textColor=BODY_COL, leading=12, spaceAfter=0,
))
styles.add(ParagraphStyle(
    "CellHeader", fontName="Helvetica-Bold", fontSize=9,
    textColor=white, leading=12, spaceAfter=0,
))


# ── Helper functions ─────────────────────────────────────────────────────
def bullet_list(items):
    return [Paragraph(f"<bullet>&bull;</bullet> {item}", styles["BulletBody"]) for item in items]


def code_block(text):
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(escaped, styles["CodeBlock"])


def callout_box(title, body, bg_color=LIGHT_BLUE, accent_color=ACCENT):
    """A callout box using a Table so it auto-sizes properly (no overlap)."""
    title_para = Paragraph(f"<b>{title}</b>", styles["CalloutTitle"])
    body_para = Paragraph(body, styles["CalloutBody"])

    t = Table(
        [[title_para], [body_para]],
        colWidths=[CONTENT_W - 16],
    )
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg_color),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (0, 0), 10),
        ("BOTTOMPADDING", (-1, -1), (-1, -1), 10),
        ("TOPPADDING", (0, 1), (0, 1), 2),
        ("LINEBEFOREENABLED", (0, 0), (0, -1)),
        ("LINEBEFORE", (0, 0), (0, -1), 4, accent_color),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    return t


def _p(text):
    """Wrap raw string in a Paragraph for table cells (enables word wrap)."""
    return Paragraph(text, styles["CellText"])


def _ph(text):
    """Wrap raw string in a header Paragraph for table header cells."""
    return Paragraph(text, styles["CellHeader"])


def make_table(headers, rows, col_widths=None):
    """Table with Paragraph-wrapped cells so text wraps properly."""
    wrapped_headers = [_ph(h) for h in headers]
    wrapped_rows = [[_p(cell) for cell in row] for row in rows]
    data = [wrapped_headers] + wrapped_rows
    w = col_widths or [None] * len(headers)
    t = Table(data, colWidths=w, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BG_WHITE, LIGHT_BLUE]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


# ── Page templates ────────────────────────────────────────────────────────
def _header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(0.5)
    canvas.line(inch, H - 0.6 * inch, W - inch, H - 0.6 * inch)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(inch, H - 0.55 * inch, "StockPilot -- AI/ML Technical Guide")
    canvas.drawRightString(W - inch, H - 0.55 * inch, "Beginner-Friendly Edition")
    canvas.line(inch, 0.6 * inch, W - inch, 0.6 * inch)
    canvas.drawCentredString(W / 2, 0.4 * inch, f"Page {doc.page}")
    canvas.restoreState()


# ── Build document ────────────────────────────────────────────────────────
def build_pdf():
    doc = SimpleDocTemplate(
        "StockPilot_AI_ML_Guide.pdf",
        pagesize=A4,
        topMargin=0.85 * inch,
        bottomMargin=0.85 * inch,
        leftMargin=inch,
        rightMargin=inch,
    )

    story = []

    # ════════════════════════════════════════════════════════════════════
    # COVER PAGE
    # ════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 1.5 * inch))
    story.append(Paragraph("StockPilot", styles["CoverTitle"]))
    story.append(Paragraph("AI &amp; Machine Learning", styles["CoverTitle"]))
    story.append(Paragraph("Technical Guide", styles["CoverTitle"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(SectionDivider())
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("A Beginner-Friendly Deep Dive into Every AI/ML Component", styles["CoverSub"]))
    story.append(Paragraph("XGBoost Predictions  &#183;  FinBERT Sentiment  &#183;  6-Factor Composite Scoring", styles["CoverSub"]))
    story.append(Paragraph("Feature Engineering  &#183;  Backtesting  &#183;  Live Market Integration", styles["CoverSub"]))
    story.append(Spacer(1, 1.0 * inch))
    story.append(Paragraph("Version 1.0  &#183;  July 2026", styles["CoverSub"]))
    story.append(Paragraph("StockPilot Development Team", styles["CoverSub"]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Table of Contents", styles["ChapterTitle"]))
    story.append(SectionDivider())
    story.append(Spacer(1, 12))

    toc = [
        ("Chapter 1", "The Big Picture -- How AI Powers StockPilot"),
        ("Chapter 2", "Understanding the Data Pipeline"),
        ("Chapter 3", "Feature Engineering -- Teaching the Model to See Patterns"),
        ("Chapter 4", "XGBoost -- The Prediction Engine"),
        ("Chapter 5", "FinBERT -- Understanding Market Sentiment with NLP"),
        ("Chapter 6", "The 6-Factor Composite Scoring System"),
        ("Chapter 7", "Backtesting -- Proving the Strategy Works"),
        ("Chapter 8", "Putting It All Together -- The Full Pipeline"),
        ("Chapter 9", "Key Configuration and Hyperparameters"),
        ("Chapter 10", "Glossary of Terms"),
    ]
    for ch, title in toc:
        story.append(Paragraph(f"<b>{ch}</b>", styles["TOCChapter"]))
        story.append(Paragraph(title, styles["TOCEntry"]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════
    # CHAPTER 1: THE BIG PICTURE
    # ════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 1", styles["CoverSub"]))
    story.append(Paragraph("The Big Picture", styles["ChapterTitle"]))
    story.append(SectionDivider())
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "StockPilot uses artificial intelligence and machine learning to help investors make smarter decisions about stocks. "
        "But what does that actually mean? Let us break it down into simple terms before diving into the technical details.",
        styles["Body"]
    ))

    story.append(callout_box(
        "What is Machine Learning?",
        "Machine learning is when a computer learns patterns from historical data, rather than being explicitly "
        "programmed with rules. Instead of telling the computer <i>'buy when the price goes up for 3 days'</i>, "
        "we show it thousands of examples of stock movements and let it discover which patterns tend to predict "
        "future price increases.<br/><br/>"
        "Think of it like teaching a child to recognize cats. You do not describe every possible cat. Instead, "
        "you show the child hundreds of pictures of cats and non-cats. Eventually the child learns to spot "
        "patterns (pointy ears, whiskers, fur) on their own. Machine learning works the same way -- "
        "it finds patterns humans might miss by processing massive amounts of data.",
        LIGHT_BLUE, ACCENT
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("StockPilot has three main AI systems working together:", styles["BodyBold"]))
    story.append(Spacer(1, 4))

    story.append(make_table(
        ["Component", "What It Does", "Technology Used"],
        [
            ["XGBoost Predictor", "Predicts if a stock price will go UP or DOWN tomorrow", "XGBoost (Gradient Boosting)"],
            ["FinBERT Sentiment Analyzer", "Reads financial news and understands if headlines are positive or negative for a stock", "FinBERT (NLP Transformer)"],
            ["Composite Scorer", "Combines 6 different analysis factors into one easy-to-read overall score (0 to 100)", "Weighted Average Formula"],
        ],
        [1.4*inch, 2.6*inch, 2.0*inch],
    ))
    story.append(Spacer(1, 10))

    story.append(callout_box(
        "Think of it like a team of analysts",
        "Imagine you hired three financial analysts:<br/><br/>"
        "<b>Analyst #1 (XGBoost)</b> studies price charts and numbers obsessively. They look at 27 different "
        "measurements every day and use past patterns to predict what happens next.<br/><br/>"
        "<b>Analyst #2 (FinBERT)</b> reads every news article and headline about the company. They tell you "
        "whether the news is good, bad, or neutral.<br/><br/>"
        "<b>Analyst #3 (Composite Scorer)</b> takes everyone's opinions, weighs them by importance, and gives "
        "you a single final recommendation.<br/><br/>"
        "That is exactly what StockPilot does -- automatically, in seconds, for any stock you choose.",
        LIGHT_GREEN, ACCENT2
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("How These Three Systems Connect", styles["SectionTitle"]))
    story.append(Paragraph(
        "The three AI systems do not work in isolation -- they feed into each other in a pipeline. "
        "Here is the simplified flow from raw data to final recommendation:",
        styles["Body"]
    ))

    story.append(make_table(
        ["Step", "What Happens", "Output"],
        [
            ["1. Data Collection", "Yahoo Finance API fetches stock prices, trading volumes, and news headlines", "Raw price data + news articles"],
            ["2. Feature Engineering", "Raw data is transformed into 27+ calculated indicators (like RSI, MACD, Bollinger Bands)", "A spreadsheet of numbers the model can read"],
            ["3. XGBoost Prediction", "The trained model processes these numbers and predicts direction", "BUY / HOLD / SELL + confidence %"],
            ["4. Sentiment Analysis", "FinBERT reads up to 15 news headlines and classifies each one", "Sentiment score (0 to 100)"],
            ["5. Composite Scoring", "All 6 analysis factors are weighted and combined into one score", "Composite score (0-100) + breakdown"],
            ["6. User Interface", "Results displayed with interactive charts, verdict cards, and action plans", "The dashboard you see on screen"],
        ],
        [1.3*inch, 2.5*inch, 2.1*inch],
    ))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════
    # CHAPTER 2: THE DATA PIPELINE
    # ════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 2", styles["CoverSub"]))
    story.append(Paragraph("Understanding the Data Pipeline", styles["ChapterTitle"]))
    story.append(SectionDivider())
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "Every AI system needs data -- and the quality of predictions depends entirely on the quality of data. "
        "StockPilot uses Yahoo Finance as its data source, fetching real-time and historical market data. "
        "This chapter explains what that data looks like and how it is collected.",
        styles["Body"]
    ))

    story.append(Paragraph("What is OHLCV Data?", styles["SectionTitle"]))
    story.append(Paragraph(
        "Stock market data comes in a standard format called <b>OHLCV</b>. Each row represents one trading day "
        "and contains five key numbers. Think of it as a daily summary card for a stock:",
        styles["Body"]
    ))

    story.append(make_table(
        ["Letter", "Stands For", "What It Means", "Example"],
        [
            ["O", "Open", "The price when trading started that day", "$150.00"],
            ["H", "High", "The highest price reached during the day", "$155.50"],
            ["L", "Low", "The lowest price reached during the day", "$148.25"],
            ["C", "Close", "The price when trading ended that day", "$153.75"],
            ["V", "Volume", "How many shares were bought/sold that day", "45,000,000"],
        ],
        [0.5*inch, 0.8*inch, 2.6*inch, 1.0*inch],
    ))
    story.append(Spacer(1, 10))

    story.append(callout_box(
        "Why Volume Matters",
        "Volume tells you how actively a stock is being traded. High volume means lots of people are buying and "
        "selling, which usually means the price movement is 'real' and significant. Low volume moves can be "
        "misleading.<br/><br/>"
        "Think of it like a vote: if 10,000 people vote for something, the result is more meaningful than if "
        "only 3 people voted. Volume is the stock market's version of voter turnout.",
        LIGHT_GOLD, HexColor("#d4a853")
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("The DataFetcher Class", styles["SectionTitle"]))
    story.append(Paragraph(
        "The DataFetcher is StockPilot's data collection system. It lives in "
        "<font face='Courier' size=9>backend/app/services/market_data/fetcher.py</font> and handles all "
        "communication with Yahoo Finance. Here is what makes it reliable:",
        styles["Body"]
    ))
    story.extend(bullet_list([
        "<b>Retry logic with exponential backoff</b> -- If Yahoo Finance is slow or temporarily down, the system "
        "does not give up immediately. It tries up to 3 times, waiting longer between each attempt (1 second, then "
        "2 seconds, then 4 seconds). This pattern is called 'exponential backoff' and is a standard practice in "
        "software engineering.",
        "<b>Column standardization</b> -- Yahoo Finance sometimes returns column names in different formats "
        "(like 'Close_AAPL' instead of just 'Close'). The fetcher automatically cleans these up so the rest of "
        "the system always gets consistent data.",
        "<b>Local CSV caching</b> -- Once data is downloaded, it is saved as a CSV file on the server. If the same "
        "data is needed again, it reads from the local file instead of making another internet request. This makes "
        "the system faster and reduces load on Yahoo Finance.",
        "<b>Configurable time period</b> -- By default it fetches 6 months of daily data, but this can be extended "
        "up to 5 years for model training purposes.",
    ]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════
    # CHAPTER 3: FEATURE ENGINEERING
    # ════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 3", styles["CoverSub"]))
    story.append(Paragraph("Feature Engineering", styles["ChapterTitle"]))
    story.append(Paragraph("Teaching the Model to See Patterns", styles["CoverSub"]))
    story.append(SectionDivider())
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "Raw OHLCV data tells you <i>what</i> happened, but not <i>what it means</i>. Feature engineering is "
        "the process of transforming raw data into meaningful signals that the ML model can learn from. It is one "
        "of the most important steps in any machine learning project.",
        styles["Body"]
    ))

    story.append(callout_box(
        "Analogy: Features are like a doctor's tests",
        "When you visit a doctor, they do not just look at you -- they measure your temperature, blood pressure, "
        "heart rate, oxygen levels, and more. Each measurement (called a 'feature' in ML) reveals something "
        "different about your health.<br/><br/>"
        "Similarly, each technical indicator reveals something different about a stock's 'health'. The RSI tells "
        "you if the stock is 'overheated' (gone up too fast). The MACD tells you if the trend is speeding up or "
        "slowing down. Volume tells you how much attention the stock is getting.<br/><br/>"
        "The ML model is like the doctor -- it looks at ALL the test results together to make a diagnosis "
        "(BUY, HOLD, or SELL).",
        LIGHT_PURPLE, PURPLE
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "StockPilot's FeatureEngine (in <font face='Courier' size=9>backend/app/services/indicators/featureEngine.py</font>) "
        "computes <b>27+ technical indicators</b> from raw OHLCV data. Let us understand each group:",
        styles["Body"]
    ))

    # --- Moving Averages ---
    story.append(Paragraph("1. Moving Averages (SMA and EMA)", styles["SectionTitle"]))
    story.append(Paragraph(
        "A <b>moving average</b> smooths out daily price noise by averaging prices over a window of days. "
        "It reveals the general trend direction by filtering out day-to-day randomness.",
        styles["Body"]
    ))

    story.append(make_table(
        ["Indicator", "Window", "What It Tells You"],
        [
            ["SMA_5", "5 days", "Very short-term trend (this week's direction)"],
            ["SMA_20", "20 days", "Short-term trend (roughly one month)"],
            ["SMA_50", "50 days", "Medium-term trend (roughly one quarter)"],
            ["EMA_20", "20 days", "Same as SMA_20 but gives MORE weight to recent prices, so it reacts faster to new changes"],
        ],
        [0.9*inch, 0.8*inch, 4.0*inch],
    ))
    story.append(Spacer(1, 8))

    story.append(callout_box(
        "SMA vs EMA -- What is the difference?",
        "<b>SMA (Simple Moving Average)</b> treats every day in the window equally. If you average the last 20 "
        "days, each day counts as 1/20th.<br/><br/>"
        "<b>EMA (Exponential Moving Average)</b> gives more importance to recent days. Yesterday's price matters "
        "more than the price from 18 days ago.<br/><br/>"
        "Imagine averaging your exam scores: SMA would count every exam equally, while EMA would weight your most "
        "recent exams more heavily. EMA reacts faster to new trends, which is useful for catching changes early.",
        LIGHT_BLUE, ACCENT
    ))
    story.append(Spacer(1, 10))

    # --- RSI ---
    story.append(Paragraph("2. RSI -- Relative Strength Index", styles["SectionTitle"]))
    story.append(Paragraph(
        "RSI measures <b>how fast and how much</b> a stock's price has been going up versus down recently. "
        "It produces a single number between 0 and 100. Think of it as a speedometer for price changes:",
        styles["Body"]
    ))
    story.extend(bullet_list([
        "<b>RSI above 70</b> -- The stock is <i>overbought</i>. It has gone up too fast and might be due for a pullback. "
        "Like a car going 150 mph -- unsustainable speed.",
        "<b>RSI below 30</b> -- The stock is <i>oversold</i>. It has dropped too fast and might bounce back. "
        "Like a rubber band stretched too far -- it tends to snap back.",
        "<b>RSI around 50</b> -- The stock is in a neutral zone. No extreme in either direction.",
    ]))
    story.append(Paragraph(
        "StockPilot uses a <b>14-day RSI</b> (the industry standard). It compares the average size of 'up days' to "
        "the average size of 'down days' over the last 14 trading sessions.",
        styles["Body"]
    ))

    # --- MACD ---
    story.append(Paragraph("3. MACD -- Moving Average Convergence Divergence", styles["SectionTitle"]))
    story.append(Paragraph(
        "MACD tracks the relationship between two moving averages to show whether a trend is getting "
        "<b>stronger or weaker</b>. It has three parts:",
        styles["Body"]
    ))
    story.extend(bullet_list([
        "<b>MACD Line</b> = 12-day EMA minus 26-day EMA. When positive, the short-term trend is above the long-term trend, which is bullish (good).",
        "<b>Signal Line</b> = 9-day EMA of the MACD Line. This is a smoothed version used for comparison.",
        "<b>Histogram</b> = MACD Line minus Signal Line. The height of the bars shows momentum strength.",
    ]))

    story.append(callout_box(
        "How to read MACD simply",
        "Think of two runners in a race. The 'fast runner' represents the 12-day average and the 'slow runner' "
        "represents the 26-day average.<br/><br/>"
        "When the fast runner pulls ahead of the slow runner, the market is gaining upward speed -- that is a "
        "<b>bullish signal</b> (consider buying).<br/><br/>"
        "When the fast runner falls behind, the market is losing steam -- that is a <b>bearish signal</b> "
        "(consider selling).<br/><br/>"
        "The bigger the gap between them, the stronger the momentum.",
        LIGHT_GREEN, ACCENT2
    ))
    story.append(Spacer(1, 10))

    # --- Bollinger Bands ---
    story.append(Paragraph("4. Bollinger Bands", styles["SectionTitle"]))
    story.append(Paragraph(
        "Bollinger Bands create a dynamic envelope around the stock price. The envelope automatically widens "
        "when the market is volatile and narrows when it is calm. They have three lines:",
        styles["Body"]
    ))
    story.extend(bullet_list([
        "<b>Middle Band</b> = 20-day SMA (the average price over 20 days)",
        "<b>Upper Band</b> = Middle Band + 2 standard deviations (acts as a 'ceiling')",
        "<b>Lower Band</b> = Middle Band - 2 standard deviations (acts as a 'floor')",
        "<b>BB_Width</b> = Distance between upper and lower bands (wider = more volatile market)",
        "<b>BB_Position</b> = Where the current price sits between the bands. A value of 0 means at the bottom band, 1 means at the top band, and 0.5 means right at the average.",
    ]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Statistically, about 95% of price action stays within the bands. When the price touches or breaks "
        "through a band, it signals an unusual condition worth paying attention to.",
        styles["Body"]
    ))

    # --- Volume Indicators ---
    story.append(Paragraph("5. Volume Indicators", styles["SectionTitle"]))
    story.append(Paragraph(
        "These indicators analyze trading activity to understand buying and selling pressure:",
        styles["Body"]
    ))
    story.append(make_table(
        ["Indicator", "What It Measures"],
        [
            ["Volume_Ratio", "Today's trading volume divided by the 20-day average. A ratio of 2.0 means twice the normal activity -- something significant is happening."],
            ["OBV (On-Balance Volume)", "A running total: adds volume on up-days, subtracts on down-days. Rising OBV while price is flat suggests 'smart money' is quietly accumulating shares."],
            ["MFI_14 (Money Flow Index)", "Similar to RSI but also considers volume. It measures both price AND volume to gauge buying/selling pressure. Ranges from 0 to 100."],
            ["VWAP_20", "Volume Weighted Average Price -- the average price weighted by how much was traded at each price. Institutional traders (big funds) use this as their benchmark."],
        ],
        [1.4*inch, 4.7*inch],
    ))
    story.append(Spacer(1, 8))

    # --- Volatility ---
    story.append(Paragraph("6. Volatility Indicators", styles["SectionTitle"]))
    story.append(Paragraph(
        "Volatility measures how much a stock's price swings up and down. Higher volatility means more risk "
        "but also more potential reward:",
        styles["Body"]
    ))
    story.append(make_table(
        ["Indicator", "What It Measures"],
        [
            ["ATR_14 (Average True Range)", "The average daily price swing over 14 days. If ATR is $5, the stock typically moves $5 per day. Higher ATR = more volatile stock."],
            ["Volatility_20", "The statistical standard deviation of daily returns over 20 days. Measures how 'jumpy' or 'calm' the stock price is."],
            ["Daily_Return", "Today's percentage change from yesterday's close. This is the raw building block that volatility is calculated from."],
        ],
        [1.7*inch, 4.4*inch],
    ))
    story.append(Spacer(1, 8))

    # --- Price Position ---
    story.append(Paragraph("7. Price Position Indicators", styles["SectionTitle"]))
    story.append(Paragraph(
        "These show where the current price sits relative to its recent history:",
        styles["Body"]
    ))
    story.append(make_table(
        ["Indicator", "What It Measures"],
        [
            ["Price_Position", "Where the current price sits in its 52-week range. 0% = at the yearly low, 100% = at the yearly high. Helps you see if the stock is near its highs or lows."],
            ["ROC_10 (Rate of Change)", "The percentage price change over the last 10 days. Positive values mean the stock is trending upward."],
            ["Price_to_SMA_20", "The ratio of current price to its 20-day moving average. Above 1.0 means trading above average (bullish sign)."],
            ["Price_Above_SMA_20", "A simple yes/no (1 or 0): is the price currently above the 20-day moving average? This is a basic trend indicator."],
        ],
        [1.5*inch, 4.6*inch],
    ))
    story.append(Spacer(1, 10))

    story.append(callout_box(
        "Important: Avoiding Look-Ahead Bias",
        "The FeatureEngine trims the first ~35 rows of data (the 'warmup' period needed to calculate indicators "
        "like 50-day SMA) rather than filling them in with estimates.<br/><br/>"
        "Why does this matter? If you filled in those missing values with estimates, the model could accidentally "
        "learn from 'future' information during training. This would make it appear more accurate than it actually "
        "is in the real world. This mistake is called <b>'look-ahead bias'</b> and is one of the most common and "
        "dangerous errors in financial machine learning. StockPilot avoids it by design.",
        LIGHT_RED, BEAR
    ))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════
    # CHAPTER 4: XGBOOST
    # ════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 4", styles["CoverSub"]))
    story.append(Paragraph("XGBoost -- The Prediction Engine", styles["ChapterTitle"]))
    story.append(SectionDivider())
    story.append(Spacer(1, 8))

    story.append(Paragraph("What is XGBoost?", styles["SectionTitle"]))
    story.append(Paragraph(
        "XGBoost (which stands for <b>eXtreme Gradient Boosting</b>) is one of the most popular and powerful machine "
        "learning algorithms in the world. It has won more Kaggle competitions (data science contests with real prizes) "
        "than any other algorithm. But what does it actually do?",
        styles["Body"]
    ))

    story.append(callout_box(
        "The Forest of Decision Trees -- XGBoost Explained Simply",
        "Imagine you are trying to decide whether to buy a stock. You ask <b>300 different advisors</b> for "
        "their opinion. Each advisor uses a simple checklist of yes/no questions:<br/><br/>"
        "'Is RSI above 70?'  --  'Is volume higher than average?'  --  'Is the price above its 50-day moving average?'"
        "<br/><br/>"
        "Each individual advisor is intentionally simple and not very accurate on their own. They are called "
        "<b>decision trees</b> because their yes/no questions form a tree-like structure.<br/><br/>"
        "But here is the magic of XGBoost: <b>each new advisor specifically focuses on the cases where previous "
        "advisors were wrong</b>. Advisor #2 gets extra training on the stocks that Advisor #1 got wrong. "
        "Advisor #3 focuses on what #1 and #2 both missed. And so on, for all 300 advisors.<br/><br/>"
        "The final prediction is the <b>combined vote</b> of all 300 advisors. This 'wisdom of the crowd' "
        "approach is remarkably accurate.",
        LIGHT_GREEN, ACCENT2
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("How StockPilot Trains the XGBoost Model", styles["SectionTitle"]))
    story.append(Paragraph(
        "The training code lives in <font face='Courier' size=9>backend/app/services/recommendation/engine.py</font>. "
        "Here is the step-by-step process:",
        styles["Body"]
    ))

    # Step 1
    story.append(Paragraph("Step 1: Define the Target -- What Are We Predicting?", styles["SubSection"]))
    story.append(Paragraph(
        "The model predicts a simple <b>binary outcome</b>: will the stock price go UP or DOWN tomorrow? "
        "Specifically, it looks at the next day's closing price compared to today's:",
        styles["Body"]
    ))
    story.extend(bullet_list([
        "If tomorrow's close is <b>more than +0.3%</b> above today's close, the label is <b>1 (UP)</b>.",
        "If tomorrow's close is <b>more than -0.3%</b> below today's close, the label is <b>0 (DOWN)</b>.",
        "If the change is within +/-0.3%, the row is <b>removed from training data</b>. These tiny moves are too ambiguous for the model to learn from reliably.",
    ]))
    story.append(Paragraph(
        "This +/-0.3% buffer is called the <b>deadband</b>. It filters out meaningless price noise "
        "so the model only learns from clear, decisive moves in either direction.",
        styles["Body"]
    ))

    # Step 2
    story.append(Paragraph("Step 2: Split the Data -- Train / Validation / Test", styles["SubSection"]))
    story.append(Paragraph(
        "In regular machine learning, you can randomly shuffle data before splitting it. But with stock market data, "
        "you <b>must keep the time order intact</b>. You cannot use future prices to predict the past! "
        "Here is how StockPilot splits 5 years of historical data:",
        styles["Body"]
    ))

    story.append(make_table(
        ["Split", "Percentage", "Purpose", "Example Dates"],
        [
            ["Training", "64%", "The model learns patterns from this data. It sees the features AND the correct answers.", "2019 - 2022"],
            ["Validation", "16%", "Used DURING training to check if the model is improving. The model does NOT learn from this data directly.", "2022 - 2023"],
            ["Test", "20%", "The final exam. The model has NEVER seen this data. Used only to measure real-world accuracy.", "2023 - 2024"],
        ],
        [0.8*inch, 0.8*inch, 2.5*inch, 1.2*inch],
    ))
    story.append(Spacer(1, 10))

    story.append(callout_box(
        "What is Overfitting? (A Common Pitfall)",
        "Overfitting is when a model <b>memorizes</b> the training data instead of learning general patterns. "
        "It is like a student who memorizes the exact answers to practice exams but cannot solve new problems they "
        "have never seen before.<br/><br/>"
        "An overfitted model looks amazing on training data (99% accuracy!) but performs terribly on new, unseen data. "
        "This is why the validation and test splits are so important -- they catch overfitting before the model "
        "goes live.<br/><br/>"
        "XGBoost uses <b>early stopping</b> to fight overfitting: it monitors performance on the validation set "
        "after each tree is added. If there is no improvement for 100 consecutive rounds, training stops -- even "
        "if the training accuracy could still go higher.",
        LIGHT_GOLD, HexColor("#d4a853")
    ))
    story.append(Spacer(1, 10))

    # Step 3
    story.append(Paragraph("Step 3: Configure the Model -- Hyperparameters", styles["SubSection"]))
    story.append(Paragraph(
        "<b>Hyperparameters</b> are settings you choose BEFORE training begins. They control how the model "
        "learns. Think of them as the 'rules of engagement' for the learning process. StockPilot uses:",
        styles["Body"]
    ))

    story.append(make_table(
        ["Parameter", "Value", "What It Controls (in simple terms)"],
        [
            ["max_estimators", "300", "Maximum number of 'advisor' trees. More trees = potentially smarter, but also slower and risk of overthinking."],
            ["max_depth", "4", "How many yes/no questions each tree can ask (4 levels deep). Deeper trees can capture complex patterns but might memorize noise."],
            ["learning_rate", "0.01", "How much each new tree is allowed to change the overall prediction. Smaller = more cautious and careful learning."],
            ["subsample", "0.8", "Each tree randomly sees only 80% of the training data. This randomness prevents overfitting by ensuring no tree memorizes the full dataset."],
            ["colsample_bytree", "0.8", "Each tree randomly sees only 80% of the features. Ensures the model does not over-rely on any single indicator."],
            ["min_child_weight", "10", "Each 'leaf' (final answer) in a tree must be based on at least 10 data points. Prevents trees from making decisions based on too little evidence."],
            ["early_stopping", "100 rounds", "If the model has not improved on the validation set for 100 consecutive rounds, stop training early."],
            ["scale_pos_weight", "auto", "Automatically adjusts if there are more UP days than DOWN days in the data, ensuring balanced learning."],
        ],
        [1.2*inch, 0.7*inch, 4.0*inch],
    ))
    story.append(PageBreak())

    # Step 4
    story.append(Paragraph("Step 4: Train with Early Stopping", styles["SubSection"]))
    story.append(Paragraph(
        "During training, XGBoost builds decision trees one at a time. After each tree is added, it checks "
        "how well the overall model performs on the validation set. If performance stops improving, training halts. "
        "Here is the simplified process:",
        styles["Body"]
    ))
    story.append(code_block(
        "Training loop (simplified):\n"
        "  for round 1 to 300:\n"
        "      add a new decision tree that focuses on previous mistakes\n"
        "      check validation loss (error metric called 'logloss')\n"
        "      if no improvement for 100 consecutive rounds:\n"
        "          STOP training early\n"
        "  save the best model to disk"
    ))

    # Step 5
    story.append(Paragraph("Step 5: Making Live Predictions", styles["SubSection"]))
    story.append(Paragraph(
        "When a user asks for a prediction on a stock like AAPL, here is exactly what happens behind the scenes:",
        styles["Body"]
    ))
    story.extend(bullet_list([
        "Fetch the most recent 6 months of OHLCV data for AAPL from Yahoo Finance.",
        "Run it through the FeatureEngine to compute all 27+ technical indicators (Chapter 3).",
        "Take only the <b>latest row</b> -- today's data with all indicators calculated.",
        "Feed that single row into the trained XGBoost model.",
        "The model outputs <b>probability_up</b> -- for example, 0.72 means '72% chance the stock goes up tomorrow'.",
    ]))

    story.append(Paragraph(
        "This probability is then converted to an actionable signal using the <b>HOLD zone</b>:",
        styles["Body"]
    ))

    story.append(make_table(
        ["Probability Range", "Signal", "What It Means"],
        [
            ["57% or higher", "BUY", "The model is fairly confident the stock will rise tomorrow. Consider buying."],
            ["43% or lower", "SELL", "The model is fairly confident the stock will fall tomorrow. Consider selling."],
            ["Between 43% and 57%", "HOLD", "The model is uncertain -- not enough confidence in either direction. Do nothing."],
        ],
        [1.3*inch, 0.6*inch, 3.8*inch],
    ))
    story.append(Spacer(1, 10))

    story.append(callout_box(
        "Why is the HOLD zone so wide (43% to 57%)?",
        "The HOLD zone is deliberately wide to reduce <b>false signals</b>. In the stock market, being wrong is "
        "expensive -- you lose money on bad trades AND pay transaction fees each time.<br/><br/>"
        "By only acting when the model has reasonable confidence (above 57% for BUY, below 43% for SELL), "
        "StockPilot avoids 'churning' -- making too many trades based on weak signals.<br/><br/>"
        "It is better to miss some opportunities than to act on noise. Quality over quantity.",
        LIGHT_BLUE, ACCENT
    ))
    story.append(Spacer(1, 10))

    # Walk-forward
    story.append(Paragraph("Walk-Forward Validation", styles["SectionTitle"]))
    story.append(Paragraph(
        "To honestly evaluate how the model performs, StockPilot uses <b>TimeSeriesSplit</b> (also called "
        "walk-forward validation). This simulates real-world usage by training on past data and testing on "
        "future data, multiple times:",
        styles["Body"]
    ))
    story.append(code_block(
        "Fold 1:  Train on [2019-2020]  then  Test on [2020-2021]\n"
        "Fold 2:  Train on [2019-2021]  then  Test on [2021-2022]\n"
        "Fold 3:  Train on [2019-2022]  then  Test on [2022-2023]\n"
        "Fold 4:  Train on [2019-2023]  then  Test on [2023-2024]\n"
        "Fold 5:  Train on [2019-2024]  then  Test on [2024-now]\n\n"
        "Each fold trains on everything BEFORE the test period.\n"
        "The average accuracy across all 5 folds gives a reliable\n"
        "estimate of real-world performance."
    ))

    # Model persistence
    story.append(Paragraph("Saving the Trained Model", styles["SectionTitle"]))
    story.append(Paragraph(
        "After training, the model is saved as a <b>joblib bundle</b> at "
        "<font face='Courier' size=9>backend/models/xgboost/current/model.pkl</font>. This file contains everything "
        "needed to make predictions without retraining:",
        styles["Body"]
    ))
    story.extend(bullet_list([
        "The trained XGBoost model itself (all decision trees and their learned patterns)",
        "The list of feature column names (ensures prediction uses the same features as training)",
        "The configuration used for training (hyperparameters, deadband threshold, etc.)",
        "Library version numbers (xgboost, sklearn, pandas, numpy) for compatibility checking",
    ]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════
    # CHAPTER 5: FINBERT
    # ════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 5", styles["CoverSub"]))
    story.append(Paragraph("FinBERT -- Understanding Market Sentiment", styles["ChapterTitle"]))
    story.append(SectionDivider())
    story.append(Spacer(1, 8))

    story.append(Paragraph("What is Sentiment Analysis?", styles["SectionTitle"]))
    story.append(Paragraph(
        "<b>Sentiment analysis</b> is the AI technique of understanding emotions and opinions in text. When applied "
        "to financial news, it answers one key question: <i>Is this headline good news or bad news for the stock?</i>",
        styles["Body"]
    ))
    story.append(Paragraph(
        "Here are three examples to illustrate the range:",
        styles["Body"]
    ))
    story.append(make_table(
        ["Headline", "Sentiment", "Score"],
        [
            ["'Apple Reports Record Quarter, Revenue Beats Expectations'", "Positive", "92 / 100"],
            ["'Tesla Faces Major Recall, Stock Drops 8% in Pre-Market'", "Negative", "15 / 100"],
            ["'Microsoft Announces New Office Update Coming Next Month'", "Neutral", "52 / 100"],
        ],
        [3.5*inch, 0.8*inch, 0.8*inch],
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("What is FinBERT?", styles["SectionTitle"]))
    story.append(Paragraph(
        "FinBERT is a specialized AI language model built specifically for understanding financial text. "
        "To understand FinBERT, let us first understand what BERT is:",
        styles["Body"]
    ))
    story.extend(bullet_list([
        "<b>BERT</b> (by Google) is a general-purpose language model trained on all of Wikipedia and BookCorpus -- "
        "about 3.3 billion words. It understands grammar, context, and meaning in regular English.",
        "<b>FinBERT</b> (by ProsusAI) takes BERT and <b>further trains it</b> on millions of financial news articles "
        "and reports. After this extra training, it understands financial jargon like 'earnings beat', 'revenue miss', "
        "'guidance raised', and 'margin compression'.",
        "The model file is about <b>420 MB</b> in size and is downloaded automatically from HuggingFace (an AI model "
        "sharing platform) the first time StockPilot uses it.",
        "It runs <b>entirely on your server</b> -- no data is sent to external APIs for analysis.",
    ]))

    story.append(Paragraph("How FinBERT Works in StockPilot", styles["SectionTitle"]))
    story.append(Paragraph(
        "The sentiment analysis code lives in <font face='Courier' size=9>backend/app/services/sentiment/finbert.py</font>. "
        "Here is the complete process:",
        styles["Body"]
    ))

    story.append(make_table(
        ["Step", "What Happens", "Details"],
        [
            ["1. Fetch Headlines", "Get recent news", "Downloads up to 15 of the most recent news headlines from Yahoo Finance for the chosen stock ticker."],
            ["2. Classify Each", "Run through FinBERT", "Each headline is individually passed through the FinBERT model, which outputs three probabilities: positive, negative, and neutral. These always add up to 1.0 (100%)."],
            ["3. Score Each", "Convert to 0-100", "Each headline's probabilities are converted to a single score using the formula explained below."],
            ["4. Aggregate", "Average all scores", "All individual headline scores are averaged into one overall sentiment score for the stock."],
            ["5. Label", "Assign final label", "The overall score is labeled: Positive (62 or above), Negative (38 or below), or Neutral (between 38 and 62)."],
        ],
        [0.5*inch, 1.2*inch, 4.0*inch],
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("The Scoring Formula", styles["SubSection"]))
    story.append(Paragraph(
        "For each headline, FinBERT outputs three probabilities that always sum to 1.0:",
        styles["Body"]
    ))
    story.append(code_block(
        "Example headline: 'Apple beats earnings expectations'\n\n"
        "FinBERT output:\n"
        "  positive probability:  0.85  (85% likely positive)\n"
        "  neutral probability:   0.12  (12% likely neutral)\n"
        "  negative probability:  0.03  (3% likely negative)\n\n"
        "StockPilot's scoring formula:\n"
        "  Score = positive_prob x 100 + neutral_prob x 50\n"
        "  Score = 0.85 x 100 + 0.12 x 50\n"
        "  Score = 85 + 6 = 91 out of 100"
    ))
    story.append(Paragraph(
        "This formula gives full weight (x100) to the positive probability and half weight (x50) to neutral. "
        "The reasoning: neutral news is not negative, so it should contribute some positive signal. "
        "Negative probability is implicitly captured since all three probabilities sum to 1.0. "
        "The result is a single number from 0 (very negative) to 100 (very positive).",
        styles["Body"]
    ))

    story.append(callout_box(
        "Why use FinBERT instead of simple keyword matching?",
        "Simple approaches (counting positive vs negative words) fail badly on financial text. "
        "Consider this headline:<br/><br/>"
        "<i>'The company's losses narrowed significantly'</i><br/><br/>"
        "A keyword counter sees the word 'losses' and marks it as negative. But the full meaning is actually "
        "<b>positive</b> -- losses are getting smaller, which means the company is improving!<br/><br/>"
        "FinBERT understands context and nuance because it was trained on millions of financial sentences. "
        "It knows that 'beat expectations' is positive even though 'beat' alone sounds violent, and that "
        "'losses narrowed' is good news even though 'losses' is a negative word.",
        LIGHT_PURPLE, PURPLE
    ))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════
    # CHAPTER 6: COMPOSITE SCORING
    # ════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 6", styles["CoverSub"]))
    story.append(Paragraph("The 6-Factor Composite Scoring System", styles["ChapterTitle"]))
    story.append(SectionDivider())
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "The composite scoring system is StockPilot's most <b>user-facing</b> AI feature. It combines six different "
        "analysis dimensions into one actionable score from 0 to 100. Unlike XGBoost (which is a 'black box' -- "
        "you cannot easily see why it made a decision), the composite system is fully <b>transparent</b>. Users "
        "can see exactly how each factor contributes and even adjust the weights to match their style.",
        styles["Body"]
    ))

    story.append(Paragraph("The Six Factors Explained", styles["SectionTitle"]))
    story.append(Paragraph(
        "Each factor is scored from 0 to 100 independently, then combined using weights:",
        styles["Body"]
    ))

    story.append(Paragraph("Factor 1: Sentiment (Default Weight: 14%)", styles["SubSection"]))
    story.append(Paragraph(
        "This is the FinBERT score from Chapter 5. It measures how positive or negative recent news coverage is "
        "about the stock. If no news headlines are available, it falls back to using OBV (On-Balance Volume) as "
        "a proxy -- rising OBV suggests positive market sentiment even without explicit news.",
        styles["Body"]
    ))

    story.append(Paragraph("Factor 2: Momentum (Default Weight: 22%)", styles["SubSection"]))
    story.append(Paragraph(
        "Measures how strong and fast the current price trend is. A stock that has been steadily rising with "
        "strong momentum gets a high score. Calculated from three indicators combined:",
        styles["Body"]
    ))
    story.append(code_block(
        "Momentum Score = RSI_14 x 0.4    (40% from overbought/oversold level)\n"
        "               + MACD_clip x 0.3  (30% from trend strength)\n"
        "               + Price_Position x 0.3  (30% from where in 52-week range)\n\n"
        "Result is clipped to stay between 0 and 100"
    ))

    story.append(Paragraph("Factor 3: Valuation (Default Weight: 20%)", styles["SubSection"]))
    story.append(Paragraph(
        "Measures whether the stock is <b>cheap or expensive</b> relative to its recent trading range. "
        "Uses the Bollinger Band position (Chapter 3) and distance from moving averages. "
        "A stock trading near the bottom of its Bollinger Band is considered undervalued (high score). "
        "A stock at the top is considered overvalued (low score).",
        styles["Body"]
    ))

    story.append(Paragraph("Factor 4: Volatility / Risk (Default Weight: 18%)", styles["SubSection"]))
    story.append(Paragraph(
        "Measures how risky or stable the stock is. <b>Lower volatility = higher score</b>. The system rewards "
        "stability because calm, predictable stocks are safer investments. "
        "Calculated from 20-day historical volatility and ATR percentage, then inverted.",
        styles["Body"]
    ))

    story.append(Paragraph("Factor 5: Volume Trend (Default Weight: 10%)", styles["SubSection"]))
    story.append(Paragraph(
        "Measures trading activity and money flow. High volume combined with price increases signals strong "
        "buying conviction -- many investors are putting money in. Combines Volume Ratio and MFI.",
        styles["Body"]
    ))

    story.append(Paragraph("Factor 6: Growth / Fundamentals (Default Weight: 16%)", styles["SubSection"]))
    story.append(Paragraph(
        "Measures recent price momentum and trend direction using Rate of Change (ROC) and whether the price "
        "is trading above its 20-day moving average.",
        styles["Body"]
    ))

    story.append(Paragraph("How the Final Score is Calculated", styles["SectionTitle"]))
    story.append(code_block(
        "Composite Score = sentiment  x 0.14  (14% weight)\n"
        "                + momentum  x 0.22  (22% weight)\n"
        "                + valuation x 0.20  (20% weight)\n"
        "                + volatility x 0.18  (18% weight)\n"
        "                + volume    x 0.10  (10% weight)\n"
        "                + growth    x 0.16  (16% weight)\n"
        "                = Single score from 0 to 100\n\n"
        "WORKED EXAMPLE:\n"
        "  Sentiment=55, Momentum=72, Valuation=48,\n"
        "  Volatility=65, Volume=40, Growth=58\n\n"
        "  = 55x0.14 + 72x0.22 + 48x0.20 + 65x0.18 + 40x0.10 + 58x0.16\n"
        "  = 7.7 + 15.8 + 9.6 + 11.7 + 4.0 + 9.3\n"
        "  = 58.1 out of 100"
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Per-Factor Signal Interpretation", styles["SubSection"]))
    story.append(make_table(
        ["Score Range", "Signal", "What It Means"],
        [
            ["Above 60", "Bullish", "This factor is showing positive, favorable signals for the stock"],
            ["40 to 60", "Neutral", "This factor is not showing a clear direction one way or the other"],
            ["Below 40", "Bearish", "This factor is showing negative, unfavorable signals for the stock"],
        ],
        [1.0*inch, 0.8*inch, 3.8*inch],
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Customizable Weights -- Tailoring to Your Style", styles["SectionTitle"]))
    story.append(Paragraph(
        "One of StockPilot's most powerful features is that users can adjust the weight of each factor to match "
        "their personal investment style. StockPilot comes with four researched presets:",
        styles["Body"]
    ))

    story.append(make_table(
        ["Strategy Name", "Sent.", "Mom.", "Val.", "Vol.", "VolTr.", "Growth", "Best For"],
        [
            ["Multi-Factor Balanced", "14%", "22%", "20%", "18%", "10%", "16%", "General use (default)"],
            ["Growth / Momentum", "18%", "38%", "6%", "10%", "16%", "22%", "Trend followers who ride momentum"],
            ["Value", "10%", "10%", "36%", "16%", "6%", "30%", "Bargain hunters looking for undervalued stocks"],
            ["Conservative", "12%", "8%", "26%", "30%", "6%", "18%", "Risk-averse investors who prioritize safety"],
        ],
        [1.3*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.6*inch, 1.3*inch],
    ))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════
    # CHAPTER 7: BACKTESTING
    # ════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 7", styles["CoverSub"]))
    story.append(Paragraph("Backtesting -- Proving the Strategy Works", styles["ChapterTitle"]))
    story.append(SectionDivider())
    story.append(Spacer(1, 8))

    story.append(callout_box(
        "What is Backtesting?",
        "Backtesting means testing a trading strategy on <b>historical data</b> to see how it <i>would have</i> "
        "performed in the past. It answers the question: 'If I had used this exact strategy last year with real "
        "stock prices, would I have made money or lost money?'<br/><br/>"
        "Think of it like a <b>flight simulator</b> for trading. Pilots practice flying in a simulator before "
        "flying a real plane with passengers. Similarly, backtesting lets you 'practice' your trading strategy "
        "with real historical prices before risking real money.<br/><br/>"
        "Important: good backtest results do NOT guarantee future profits. Markets change. But poor backtest "
        "results are a strong warning sign that a strategy is unlikely to work.",
        LIGHT_BLUE, ACCENT
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "StockPilot has <b>two separate backtesting engines</b>, one for each prediction system:",
        styles["Body"]
    ))

    story.append(Paragraph("Backtest Engine 1: XGBoost Model Backtest", styles["SectionTitle"]))
    story.append(Paragraph(
        "Located in the <font face='Courier' size=9>StockPredictor.backtest()</font> method. "
        "This tests how the ML model's BUY/SELL signals would have performed on historical data that the model "
        "was never trained on:",
        styles["Body"]
    ))
    story.extend(bullet_list([
        "Uses the trained XGBoost model to generate BUY/SELL/HOLD signals for each historical day",
        "<b>Long-only strategy</b> -- buys when signal is BUY (probability above 57%), exits position otherwise",
        "Includes <b>5 basis points (0.05%) transaction cost</b> per trade to simulate real-world brokerage fees",
        "Compares the strategy's total return against simple buy-and-hold (just buying the stock and doing nothing)",
    ]))

    story.append(Paragraph("Backtest Engine 2: Composite Score Backtest", styles["SectionTitle"]))
    story.append(Paragraph(
        "Located in <font face='Courier' size=9>backend/app/api/v1/endpoints/analysis.py</font>. "
        "This is the backtest that users interact with in the app's Advisor page. It uses the 6-factor composite "
        "score (not XGBoost) and includes sophisticated risk management features:",
        styles["Body"]
    ))

    story.append(Paragraph("Risk Profiles", styles["SubSection"]))
    story.append(Paragraph(
        "Users choose a risk profile that controls how aggressively the strategy trades:",
        styles["Body"]
    ))
    story.append(make_table(
        ["Profile", "Buy When", "Sell When", "Trailing Stop", "Description"],
        [
            ["Conservative", "Score above 51", "Score below 50", "0.8%", "Very cautious. Tight stop-loss means small losses but also frequent exits. Best for capital preservation."],
            ["Moderate", "Score above 53", "Score below 47", "1.8%", "Balanced approach. Gives trades room to breathe while still limiting downside. The default choice."],
            ["Aggressive", "Score above 50", "Score below 42", "4.0%", "Rides trends longer with wide stops. Bigger potential gains but also bigger potential losses."],
        ],
        [0.8*inch, 0.9*inch, 0.9*inch, 0.7*inch, 2.6*inch],
    ))
    story.append(Spacer(1, 8))

    story.append(callout_box(
        "What is a Trailing Stop?",
        "A trailing stop is a safety mechanism that automatically sells your stock if it drops by a certain "
        "percentage from its highest point since you bought it.<br/><br/>"
        "Example with a 1.8% trailing stop: You buy at $100. The stock rises to $110 (your new high). "
        "The trailing stop is now at $110 x (1 - 0.018) = $108.02. If the stock drops to $108.02, "
        "it automatically sells, locking in your $8.02 profit. But if the stock keeps rising to $120, "
        "the stop moves up to $117.84. It only moves UP, never down -- protecting your gains while "
        "letting winners run.",
        LIGHT_GREEN, ACCENT2
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Time Horizon Settings", styles["SubSection"]))
    story.append(make_table(
        ["Horizon", "Min Hold", "Max Hold", "Cooldown", "Trading Style"],
        [
            ["Short", "1 day", "5 days", "0 days", "Quick in-and-out day/swing trades"],
            ["Medium", "2 days", "15 days", "1 day", "Swing trading over days to weeks"],
            ["Long", "5 days", "40 days", "2 days", "Position trading over weeks to months"],
        ],
        [0.7*inch, 0.7*inch, 0.7*inch, 0.8*inch, 2.4*inch],
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Understanding Backtest Metrics", styles["SubSection"]))
    story.append(Paragraph(
        "After a backtest completes, StockPilot shows several performance metrics. Here is what each means:",
        styles["Body"]
    ))
    story.append(make_table(
        ["Metric", "What It Measures", "What is Good?"],
        [
            ["Total Return", "Overall profit or loss as a percentage of starting capital", "Above 0% (any profit). Compare against buy-and-hold."],
            ["Sharpe Ratio", "Return per unit of risk taken. Adjusts returns for how bumpy the ride was.", "Above 1.0 is good. Above 2.0 is excellent. Below 0 means you lost money."],
            ["Win Rate", "What percentage of individual trades were profitable", "Above 50% means more winning trades than losing trades."],
            ["Max Drawdown", "The worst peak-to-trough decline. How much you would have lost at the worst moment.", "Less than -20% is acceptable. Less than -10% is good."],
            ["Profit Factor", "Total gross profits divided by total gross losses", "Above 1.5 means profits significantly exceed losses."],
            ["Edge vs Hold", "Strategy return minus buy-and-hold return. Did the strategy beat just holding?", "Above 0% means the strategy added value over doing nothing."],
        ],
        [0.9*inch, 2.3*inch, 2.3*inch],
    ))
    story.append(Spacer(1, 10))

    story.append(callout_box(
        "The Sentiment Proxy Problem in Backtesting",
        "There is an honest limitation in backtesting: FinBERT cannot analyze old news headlines because they "
        "are not available historically through Yahoo Finance. The news feed only has recent articles.<br/><br/>"
        "So during backtesting, StockPilot uses <b>OBV (On-Balance Volume)</b> as a proxy for sentiment. OBV "
        "tracks whether volume flows correlate with price direction -- a reasonable substitute since both measure "
        "market conviction, though not identical to actual news sentiment.<br/><br/>"
        "This means backtest results for the sentiment factor are approximate. Live predictions use real FinBERT "
        "analysis and should be more accurate.",
        LIGHT_GOLD, HexColor("#d4a853")
    ))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════
    # CHAPTER 8: THE FULL PIPELINE
    # ════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 8", styles["CoverSub"]))
    story.append(Paragraph("Putting It All Together", styles["ChapterTitle"]))
    story.append(SectionDivider())
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "Now that you understand each component individually, let us see how everything connects end-to-end. "
        "When a user opens the Advisor page and selects a stock like AAPL, here is the complete sequence of events "
        "that happens behind the scenes:",
        styles["Body"]
    ))

    story.append(make_table(
        ["#", "System", "What Happens", "Time"],
        [
            ["1", "DataFetcher", "Fetches 6 months of daily OHLCV data from Yahoo Finance", "1-2 sec"],
            ["2", "FeatureEngine", "Computes 27+ technical indicators from the raw price data", "Under 100 ms"],
            ["3", "XGBoost", "Loads the saved model file and feeds in today's features to get a probability", "Under 50 ms"],
            ["4", "Signal Logic", "Converts the probability to BUY/HOLD/SELL using the HOLD zone thresholds", "Under 1 ms"],
            ["5", "FinBERT", "Fetches 15 news headlines and classifies each through the transformer model", "2-5 sec"],
            ["6", "Factor Scorer", "Computes all 6 factor scores from technical indicators plus sentiment", "Under 50 ms"],
            ["7", "Composite", "Applies the user's chosen weights to produce the final composite score", "Under 1 ms"],
            ["8", "Bull/Bear Gen", "Generates text arguments for and against the stock from scores and fundamentals", "Under 100 ms"],
            ["9", "Action Plan", "Calculates suggested entry price zone, stop-loss level, profit target, and position size", "Under 10 ms"],
            ["10", "UI Render", "Frontend displays everything with interactive charts, gauges, and verdict cards", "Under 200 ms"],
        ],
        [0.3*inch, 0.9*inch, 3.2*inch, 0.8*inch],
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("File Map -- Where Everything Lives in the Code", styles["SectionTitle"]))

    story.append(make_table(
        ["File Path (under backend/app/)", "Purpose"],
        [
            ["services/market_data/fetcher.py", "Downloads and caches stock data from Yahoo Finance"],
            ["services/indicators/featureEngine.py", "Computes all 27+ technical indicators from raw data"],
            ["services/recommendation/engine.py", "XGBoost model: training, prediction, and backtesting"],
            ["services/sentiment/finbert.py", "FinBERT sentiment analysis pipeline"],
            ["api/v1/endpoints/analysis.py", "6-factor scoring, bull/bear cases, composite backtesting"],
            ["api/v1/endpoints/predictions.py", "Serves stored XGBoost predictions from the database"],
            ["api/v1/endpoints/sentiment.py", "Sentiment analysis API endpoint (runs FinBERT in a thread pool)"],
            ["api/v1/endpoints/live.py", "Real-time quotes, intraday charts, and market status"],
            ["models/xgboost/current/model.pkl", "The trained XGBoost model file (saved with joblib)"],
            ["train.py", "Script to retrain the XGBoost model on new data"],
        ],
        [2.5*inch, 3.6*inch],
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Two Prediction Systems -- Why Does StockPilot Have Both?", styles["SectionTitle"]))
    story.append(Paragraph(
        "You might wonder why StockPilot has both XGBoost predictions AND composite scoring. They serve "
        "different purposes and complement each other:",
        styles["Body"]
    ))

    story.append(make_table(
        ["Aspect", "XGBoost Predictions", "Composite Scoring"],
        [
            ["Type", "Black-box ML model", "Transparent rule-based system"],
            ["Explainability", "Difficult to explain WHY it made a particular decision (300 decision trees voting internally)", "Easy to understand -- you can see each factor's score and how they combine"],
            ["Customizable?", "No -- the model is pre-trained and fixed", "Yes -- users can adjust the 6 factor weights with sliders"],
            ["Speed", "Very fast (under 50 ms)", "Fast overall, but FinBERT sentiment adds 2-5 seconds"],
            ["Basis", "Learns patterns from historical data automatically", "Based on established financial theory and indicators"],
            ["Updates", "Needs periodic retraining as market conditions change", "Always uses live data -- no retraining needed"],
        ],
        [1.0*inch, 2.2*inch, 2.8*inch],
    ))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════
    # CHAPTER 9: KEY CONFIGURATION
    # ════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 9", styles["CoverSub"]))
    story.append(Paragraph("Key Configuration and Hyperparameters", styles["ChapterTitle"]))
    story.append(SectionDivider())
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "This chapter is a quick reference for all the important numbers and settings used throughout "
        "StockPilot's AI/ML systems. These are the values you would adjust to tune the system's behavior.",
        styles["Body"]
    ))

    story.append(Paragraph("XGBoost Model Configuration", styles["SectionTitle"]))
    story.append(Paragraph(
        "Defined in the <font face='Courier' size=9>PredictorConfig</font> dataclass (engine.py):",
        styles["Body"]
    ))
    story.append(make_table(
        ["Parameter", "Value", "What Happens If You Change It"],
        [
            ["target_horizon", "1 day", "Increase to predict further ahead. Longer horizons are harder and less accurate."],
            ["target_deadband", "0.3%", "Increase = fewer training samples but clearer, more decisive signals."],
            ["training_period", "5 years", "More data = more patterns learned, but very old data may be less relevant to today's market."],
            ["max_estimators", "300", "More trees = potentially more accurate but slower training and higher overfitting risk."],
            ["max_depth", "4", "Deeper trees = more complex pattern detection but much higher overfitting risk."],
            ["learning_rate", "0.01", "Lower = more cautious learning. Needs more trees (estimators) to compensate."],
            ["hold_lower", "0.43", "Lower = the model generates more BUY signals. Makes the strategy more aggressive."],
            ["hold_upper", "0.57", "Higher = the model generates fewer BUY signals. Makes the strategy more conservative."],
        ],
        [1.1*inch, 0.6*inch, 4.0*inch],
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("FinBERT Configuration", styles["SectionTitle"]))
    story.append(make_table(
        ["Parameter", "Value", "Purpose"],
        [
            ["Model name", "ProsusAI/finbert", "The pre-trained transformer model from HuggingFace model hub"],
            ["Max headlines", "15", "Maximum number of recent news articles to analyze per stock"],
            ["Positive threshold", "62 or above", "Overall sentiment score at or above this value is labeled 'Positive'"],
            ["Negative threshold", "38 or below", "Overall sentiment score at or below this value is labeled 'Negative'"],
        ],
        [1.2*inch, 1.2*inch, 3.5*inch],
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Composite Score Thresholds", styles["SectionTitle"]))
    story.append(make_table(
        ["Threshold", "Value", "Meaning"],
        [
            ["Bullish factor signal", "Above 60", "This individual factor is showing positive signals"],
            ["Bearish factor signal", "Below 40", "This individual factor is showing negative signals"],
            ["P/E bull case", "Below 15", "Price-to-Earnings ratio suggests the stock may be undervalued"],
            ["P/E bear case", "Above 35", "Price-to-Earnings ratio suggests the stock may be overvalued"],
            ["Margin bull case", "Above 20%", "Profit margins indicate strong profitability"],
            ["Debt bear case", "Above 150%", "Debt-to-equity ratio indicates high financial leverage risk"],
        ],
        [1.3*inch, 0.8*inch, 3.6*inch],
    ))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════
    # CHAPTER 10: GLOSSARY
    # ════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Chapter 10", styles["CoverSub"]))
    story.append(Paragraph("Glossary of Terms", styles["ChapterTitle"]))
    story.append(SectionDivider())
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "A quick reference for all the technical terms used in this guide:",
        styles["Body"]
    ))

    glossary = [
        ["Term", "Definition"],
        ["ATR", "Average True Range -- measures the average daily price swing over 14 days. Higher ATR = more volatile stock."],
        ["Backtest", "Testing a trading strategy on historical data to see how it would have performed in the past."],
        ["BERT", "Bidirectional Encoder Representations from Transformers -- Google's foundational language AI model."],
        ["Bollinger Bands", "A price envelope showing 2 standard deviations above and below a 20-day moving average."],
        ["Classification", "A type of ML task where the output is a category (like BUY/HOLD/SELL) rather than a number."],
        ["Composite Score", "A weighted average of multiple factor scores, producing a single overall value from 0 to 100."],
        ["Cross-validation", "Testing model accuracy across multiple time periods for more reliable performance estimates."],
        ["Deadband", "A buffer zone (+/-0.3%) that filters out insignificant price moves during model training."],
        ["Decision Tree", "A model that makes predictions using a series of yes/no questions, forming a tree-like structure."],
        ["Early Stopping", "A technique that halts training when the model stops improving on validation data, preventing overfitting."],
        ["EMA", "Exponential Moving Average -- a moving average that gives more weight to recent prices."],
        ["Feature", "A calculated input variable (like RSI or MACD) that the ML model uses to make predictions."],
        ["FinBERT", "A version of BERT that has been further trained on financial text for sentiment analysis."],
        ["Gradient Boosting", "An ensemble technique that builds models one at a time, each one correcting the errors of previous models."],
        ["HOLD Zone", "The probability range (43-57%) where the model does not generate a trading signal due to low confidence."],
        ["Hyperparameter", "A setting that controls the learning process, chosen before training begins (not learned from data)."],
        ["Joblib", "A Python library used for saving and loading trained ML models to and from disk files."],
        ["Look-ahead Bias", "A critical error where a model accidentally uses future information during training, inflating apparent accuracy."],
        ["MACD", "Moving Average Convergence Divergence -- an indicator that shows trend momentum and direction changes."],
        ["MFI", "Money Flow Index -- similar to RSI but also incorporates trading volume data."],
        ["NLP", "Natural Language Processing -- AI techniques for understanding and analyzing human language text."],
        ["OBV", "On-Balance Volume -- a cumulative volume indicator that measures buying vs selling pressure over time."],
        ["OHLCV", "Open, High, Low, Close, Volume -- the standard format for representing stock price data."],
        ["Overfitting", "When a model memorizes training data instead of learning general, reusable patterns."],
        ["Profit Factor", "The ratio of total gross profits to total gross losses. Above 1.0 means overall profitable."],
        ["ROC", "Rate of Change -- the percentage price change over a specified lookback period."],
        ["RSI", "Relative Strength Index -- a momentum oscillator (0-100). Above 70 = overbought, below 30 = oversold."],
        ["Sharpe Ratio", "A risk-adjusted return metric: higher values mean better returns per unit of risk taken."],
        ["SMA", "Simple Moving Average -- the equal-weight average of closing prices over a specified number of days."],
        ["Trailing Stop", "A dynamic stop-loss that moves up with the price to protect gains while letting winners run."],
        ["Transformer", "The neural network architecture behind BERT, GPT, and most modern language AI models."],
        ["Walk-forward", "A validation method that trains on past data and tests on future data, sliding through time."],
        ["XGBoost", "eXtreme Gradient Boosting -- a fast, powerful ensemble ML algorithm popular in competitions and industry."],
    ]
    story.append(make_table(glossary[0], glossary[1:], [1.2*inch, 5.0*inch]))
    story.append(Spacer(1, 20))

    # ── Final disclaimer ──
    story.append(SectionDivider())
    story.append(Spacer(1, 10))
    story.append(callout_box(
        "Important Disclaimer",
        "StockPilot's AI/ML systems are tools for analysis, not financial advice. All predictions, scores, and "
        "verdicts are generated by machine learning models and mathematical formulas. They must not be treated "
        "as investment recommendations.<br/><br/>"
        "Past performance in backtesting does <b>not</b> guarantee future results. Markets are unpredictable "
        "and can behave in ways no model has seen before. Always do your own research and consult with a licensed "
        "financial advisor before making investment decisions with real money.",
        LIGHT_RED, BEAR
    ))

    # ── Build ──
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    import os
    size_kb = os.path.getsize("StockPilot_AI_ML_Guide.pdf") / 1024
    print(f"Generated: StockPilot_AI_ML_Guide.pdf ({size_kb:.0f} KB)")


if __name__ == "__main__":
    build_pdf()
