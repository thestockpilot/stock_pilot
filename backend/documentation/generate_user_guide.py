"""Generate a professional StockPilot User Guide (.docx)."""
import os
from datetime import date
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(__file__)
STUDY_IMG = os.path.join(HERE, "StockPilot_AI_StudyGuide.png")
OUT = os.path.join(HERE, "StockPilot_User_Guide.docx")

BLUE = RGBColor(0x1D, 0x4E, 0xD8)
INK = RGBColor(0x11, 0x18, 0x27)
GREY = RGBColor(0x6B, 0x72, 0x80)
GREEN = RGBColor(0x16, 0xA3, 0x4A)

doc = Document()
# base style
st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11)


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), hexcolor)
    tcPr.append(sh)


def h1(t):
    p = doc.add_heading(level=1); r = p.add_run(t); r.font.color.rgb = INK; r.font.size = Pt(17)
    return p


def h2(t):
    p = doc.add_heading(level=2); r = p.add_run(t); r.font.color.rgb = BLUE; r.font.size = Pt(13.5)
    return p


def body(t, bold=False):
    p = doc.add_paragraph(); r = p.add_run(t); r.bold = bold; r.font.size = Pt(11); p.paragraph_format.space_after = Pt(6)
    return p


def bullet(t):
    p = doc.add_paragraph(style="List Bullet"); p.add_run(t); return p


def screenshot_slot(caption):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"[  Screenshot:  {caption}  ]")
    r.italic = True; r.font.color.rgb = GREY; r.font.size = Pt(10)
    # a light box feel via border
    pPr = p._p.get_or_add_pPr(); pbdr = OxmlElement("w:pBdr")
    for edge in ("top", "bottom", "left", "right"):
        e = OxmlElement(f"w:{edge}"); e.set(qn("w:val"), "dashed"); e.set(qn("w:sz"), "6")
        e.set(qn("w:space"), "8"); e.set(qn("w:color"), "9CA3AF"); pbdr.append(e)
    pPr.append(pbdr)
    p.paragraph_format.space_before = Pt(4); p.paragraph_format.space_after = Pt(10)


def kv_table(headers, rows, widths):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, hh in enumerate(headers):
        c = t.rows[0].cells[i]; shade(c, "374151")
        run = c.paragraphs[0].add_run(hh); run.bold = True; run.font.color.rgb = RGBColor(255, 255, 255); run.font.size = Pt(9.5)
        c.width = Inches(widths[i])
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].width = Inches(widths[i])
            run = cells[i].paragraphs[0].add_run(val); run.font.size = Pt(9.5)
            if i == 0: run.bold = True
    doc.add_paragraph()
    return t


# ============================ COVER ============================
for _ in range(4): doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("StockPilot"); r.font.size = Pt(40); r.bold = True; r.font.color.rgb = INK
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("AI-Powered Investment Advisory Platform"); r.font.size = Pt(15); r.font.color.rgb = BLUE
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("User Guide"); r.font.size = Pt(22); r.font.color.rgb = GREY
for _ in range(2): doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run(f"Version 1.0  ·  {date.today().strftime('%B %Y')}"); r.font.size = Pt(11); r.font.color.rgb = GREY
doc.add_page_break()

# ============================ 1. INTRO ============================
h1("1.  Introduction")
body("StockPilot is a web-based investment advisory platform that helps you decide whether to "
     "buy, hold or sell a stock. For any stock you choose, it produces a clear recommendation with "
     "a confidence level, an explanation of the reasoning behind it, and a simulation of how the "
     "strategy would have performed in the past. StockPilot is a decision-support tool - it helps "
     "you make informed decisions, but it does not place trades or manage money on your behalf.")
h2("Who uses StockPilot")
kv_table(["Role", "What they can do"], [
    ["Investor", "Get AI verdicts, manage a portfolio and watchlist, keep a trading journal, browse and buy strategies."],
    ["Financial Analyst", "Everything an investor can do, plus create strategies and submit them to the marketplace."],
    ["Administrator", "Manage users, review and approve strategies, configure platform thresholds."],
], [1.5, 4.8])

# ============================ 2. GETTING STARTED ============================
h1("2.  Getting Started")
h2("2.1  Signing in")
body("Open StockPilot in your web browser. On the sign-in page you can either log in with your "
     "email and password, or create a new account. When registering, you choose your role - "
     "Investor or Financial Analyst.")
screenshot_slot("The Sign-in / Register page")
h2("2.2  Navigating the app")
body("After signing in you land on your Dashboard. The top navigation bar lets you move between "
     "the main areas: Dashboard, Advisor, Marketplace, Portfolio and Journal (and Admin, for "
     "administrators).")
screenshot_slot("The top navigation bar")

# ============================ 3. HOW IT WORKS ============================
h1("3.  How StockPilot Works")
body("For every stock, StockPilot combines two independent methods to reach a recommendation: an "
     "explainable six-factor scoring engine that shows its reasoning, and a machine-learning model "
     "(XGBoost) that has learned patterns from years of historical data. A backtest then checks "
     "whether following the signals would have been profitable. The diagram below summarises the flow.")
if os.path.exists(STUDY_IMG):
    doc.add_picture(STUDY_IMG, width=Inches(6.3))
    cap = doc.add_paragraph(); cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cr = cap.add_run("Figure 1 - How the StockPilot AI layer works."); cr.italic = True; cr.font.size = Pt(9); cr.font.color.rgb = GREY

# ============================ 4. THE ADVISOR ============================
doc.add_page_break()
h1("4.  Using the Advisor")
body("The Advisor is the heart of StockPilot. It is where you analyse a stock and receive a verdict.")

h2("4.1  Selecting a stock")
body("Type a ticker symbol (for example AAPL for Apple, TSLA for Tesla) into the search box, or "
     "click one of the popular stock buttons. The analysis runs automatically.")
screenshot_slot("The stock search box and popular-stock buttons")

h2("4.2  Reading the verdict")
body("The verdict card shows the recommendation in large text - BUY, HOLD or SELL - along with a "
     "confidence percentage. A MODEL LIVE badge indicates the recommendation was produced by the "
     "live machine-learning model. The card also shows the composite score (0-100) and the current price.")
bullet("BUY - the model sees upside potential; consider accumulating.")
bullet("HOLD - the signal is neutral; wait for a clearer opportunity.")
bullet("SELL - the model sees downside risk; consider reducing or avoiding.")
screenshot_slot("The BUY / HOLD / SELL verdict card with confidence and MODEL LIVE badge")

h2("4.3  The Six Factors explained")
body("The explainable verdict is built from six factors, each scored from 0 to 100. A score above "
     "60 is bullish (positive), below 40 is bearish (negative), and in between is neutral. "
     "Understanding each factor helps you understand the recommendation.")
kv_table(["Factor", "What it measures", "A high score means"], [
    ["Sentiment", "The mood of recent financial news about the stock, read by an AI language model (FinBERT).",
     "Recent news is positive / optimistic."],
    ["Momentum", "Whether the price has been trending upward and how strongly.",
     "A strong, established upward trend."],
    ["Valuation", "Whether the stock looks cheap or expensive relative to its fundamentals.",
     "The stock appears attractively valued (not overpriced)."],
    ["Volatility", "How sharply the price swings - a measure of risk.",
     "Calmer, more stable price behaviour (lower risk)."],
    ["Volume", "Whether trading activity is confirming the price move.",
     "Strong participation is backing the move."],
    ["Growth", "Whether the underlying company is growing (earnings and revenue).",
     "The company shows solid growth."],
], [1.1, 3.3, 1.9])
body("The six factor scores are combined using weights (see 4.4) to produce the composite score, "
     "which summarises the overall picture in a single number.")
screenshot_slot("The six factor bars / radar chart")

h2("4.4  Choosing a strategy and adjusting weights")
body("Not every investor cares about the same things. A strategy decides how much weight each of "
     "the six factors carries. You can pick a ready-made strategy (for example Balanced, Growth, "
     "Value or Preservation) or move the sliders to build your own. The weights must total 100%. "
     "Changing the weights instantly re-calculates the composite score.")
screenshot_slot("The strategy presets and the six weight sliders")

h2("4.5  Risk tolerance and time horizon")
body("Two further controls tailor the advice to you:")
bullet("Risk tolerance - Conservative, Moderate or Aggressive. This adjusts how cautious the "
       "suggested action and the backtest stop-losses are.")
bullet("Time horizon - Short, Medium or Long, describing how long you intend to hold.")
screenshot_slot("The Risk tolerance and Time horizon selectors")

h2("4.6  News sentiment")
body("The News Sentiment panel shows the mood score derived from recent headlines by the FinBERT "
     "AI model. When no headlines are available, StockPilot falls back to a volume-based measure so "
     "the factor is always populated.")
screenshot_slot("The News Sentiment panel")

# ============================ 5. BACKTEST ============================
h1("5.  Backtesting a Strategy")
body("A backtest answers a simple question: 'If I had followed this strategy over the past few "
     "years, how would it have performed?' StockPilot simulates the trades on real historical "
     "prices, including realistic costs (fees and slippage), and reports the results. Choose a "
     "period and click Run Backtest.")
screenshot_slot("The Backtest panel with metrics and the equity-curve chart")
body("The metrics tell you how the strategy behaved:", bold=True)
kv_table(["Metric", "What it means"], [
    ["Total return", "The overall percentage gain or loss of the strategy over the period."],
    ["Buy & hold return", "What you would have made by simply buying and holding - the benchmark to beat."],
    ["Win rate", "The percentage of individual trades that were profitable."],
    ["Sharpe ratio", "Return earned per unit of risk. Higher is better; above 1 is good."],
    ["Profit factor", "Gross profit divided by gross loss. Above 1 means the winners outweigh the losers."],
    ["Max drawdown", "The largest peak-to-trough drop - how much you would have lost at the worst point."],
], [1.5, 4.8])
body("Tip: a strategy can be profitable even with a win rate below 50%, if its winning trades are "
     "larger than its losing ones (a high profit factor). That is why we look at several metrics "
     "together, not just accuracy.")
body("You can also click Download log to export a CSV of every trade for your own records.")

# ============================ 6. PORTFOLIO / WATCHLIST / JOURNAL ============================
doc.add_page_break()
h1("6.  Portfolio, Watchlist and Journal")
h2("6.1  Portfolio")
body("The Portfolio page tracks the stocks you own. Add a holding with its ticker, quantity and "
     "cost, and StockPilot looks up the live price to show your current value, profit or loss, and "
     "how your holdings are spread across sectors.")
screenshot_slot("The Portfolio page with holdings and allocation charts")
h2("6.2  Watchlist")
body("The Watchlist lets you follow stocks you are interested in without owning them, each shown "
     "with its latest AI signal so you can spot opportunities at a glance.")
screenshot_slot("The Watchlist panel")
h2("6.3  Trading Journal")
body("The Journal is your record of trades. Logging each trade lets StockPilot show your win rate, "
     "equity curve, monthly profit and loss, and performance by strategy - so you can learn from "
     "your own history.")
screenshot_slot("The Trading Journal with statistics")

# ============================ 7. MARKETPLACE ============================
h1("7.  The Strategy Marketplace")
body("The Marketplace is where strategies are shared. Investors can browse, buy and rate "
     "published strategies. Financial Analysts can additionally submit their own strategies for "
     "publication: after validating a strategy with a backtest, the analyst requests publication, "
     "and an administrator reviews it against the platform's quality thresholds before it goes live.")
screenshot_slot("The Strategy Marketplace")

# ============================ 8. GLOSSARY ============================
h1("8.  Glossary")
kv_table(["Term", "Meaning"], [
    ["Ticker", "The short symbol for a stock (e.g. AAPL = Apple)."],
    ["OHLCV", "A stock's daily data: Open, High, Low, Close price and Volume traded."],
    ["Composite score", "The single 0-100 score combining all six weighted factors."],
    ["Confidence", "How sure the model is about its verdict, shown as a percentage."],
    ["Backtest", "A simulation of a strategy on past data to see how it would have performed."],
    ["Sharpe ratio", "A measure of return relative to risk."],
    ["Sentiment", "The mood of the news, positive or negative, scored 0-100."],
    ["Watchlist", "A list of stocks you follow without owning them."],
], [1.5, 4.8])

# ============================ APPENDIX: SS CHECKLIST ============================
h1("Appendix - Screenshot checklist")
body("This guide has labelled slots for screenshots. To complete it, capture each screen below "
     "(press Win + Shift + S, drag a box, then paste into the matching slot). All screenshots "
     "should be genuine captures of the running application.")
for i, s in enumerate([
    "Sign-in / Register page", "Top navigation bar", "Stock search + popular buttons",
    "Verdict card (BUY/HOLD/SELL + MODEL LIVE)", "Six factor bars / radar",
    "Strategy presets + weight sliders", "Risk tolerance + time horizon",
    "News Sentiment panel", "Backtest metrics + equity curve",
    "Portfolio page", "Watchlist panel", "Trading Journal", "Strategy Marketplace",
], 1):
    bullet(f"{i}.  {s}")

doc.save(OUT)
print("saved", OUT)
