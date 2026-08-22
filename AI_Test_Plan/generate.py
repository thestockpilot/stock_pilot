"""Render captured test outputs as terminal-style screenshots and build the
AI-Layer Test Plan PDF (plan + test cases + embedded result screenshots).
Everything is written inside this AI_Test_Plan folder.
"""
import os
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak,
)

HERE = os.path.dirname(__file__)
SS = os.path.join(HERE, "screenshots")
TODAY = date.today().strftime("%d %B %Y")


# ---------- terminal-style screenshot renderer ----------
def render_terminal(txt_file, png_file, title):
    with open(txt_file, encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f if ln.strip()]
    n = len(lines)
    fig = plt.figure(figsize=(11, 0.30 * n + 1.1), facecolor="#0d1117")
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    # window chrome
    ax.add_patch(plt.Rectangle((0, 0.93), 1, 0.07, transform=ax.transAxes,
                               facecolor="#161b22", edgecolor="none"))
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        ax.add_patch(plt.Circle((0.018 + i * 0.02, 0.965), 0.008,
                                transform=ax.transAxes, facecolor=c, edgecolor="none"))
    ax.text(0.5, 0.965, title, color="#c9d1d9", fontsize=10, family="monospace",
            ha="center", va="center", transform=ax.transAxes)
    step = 0.9 / (n + 1)
    y = 0.90
    for ln in lines:
        color = "#c9d1d9"
        if "PASSED" in ln or "passed" in ln:
            color = "#3fb950"
        elif "FAILED" in ln or "ERROR" in ln or "error" in ln:
            color = "#f85149"
        elif ln.startswith("=") or ln.startswith("-"):
            color = "#6e7681"
        elif "mean_accuracy" in ln or "mean_logloss" in ln:
            color = "#58a6ff"
        ax.text(0.015, y, ln, color=color, fontsize=8.6, family="monospace",
                va="top", ha="left", transform=ax.transAxes)
        y -= step
    fig.savefig(png_file, dpi=150, facecolor="#0d1117", bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    print("rendered", os.path.basename(png_file))
    return png_file


shots = [
    render_terminal(os.path.join(SS, "01_pytest.txt"), os.path.join(SS, "01_pytest.png"),
                    "pytest  —  AI-layer test suite"),
    render_terminal(os.path.join(SS, "02_walkforward.txt"), os.path.join(SS, "02_walkforward.png"),
                    "walk-forward evaluation"),
    render_terminal(os.path.join(SS, "03_backtest.txt"), os.path.join(SS, "03_backtest.png"),
                    "cost-aware backtest"),
]

# ---------- PDF ----------
st = getSampleStyleSheet()
TITLE = ParagraphStyle("T", parent=st["Title"], fontSize=20, textColor=colors.HexColor("#111827"))
SUB = ParagraphStyle("S", parent=st["Normal"], fontSize=10.5, textColor=colors.HexColor("#6B7280"))
H1 = ParagraphStyle("H1", parent=st["Heading1"], fontSize=15, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#111827"))
H2 = ParagraphStyle("H2", parent=st["Heading2"], fontSize=12, spaceBefore=10, spaceAfter=4, textColor=colors.HexColor("#1D4ED8"))
BODY = ParagraphStyle("B", parent=st["Normal"], fontSize=9.5, leading=13, spaceAfter=5, alignment=4)
BUL = ParagraphStyle("BU", parent=BODY, leftIndent=13, spaceAfter=2)
CELL = ParagraphStyle("CE", parent=st["Normal"], fontSize=7.6, leading=9.5)
CELLH = ParagraphStyle("CEH", parent=st["Normal"], fontSize=7.6, leading=9.5, textColor=colors.white, fontName="Helvetica-Bold")
CAP = ParagraphStyle("CAP", parent=st["Normal"], fontSize=8.5, textColor=colors.HexColor("#6B7280"), alignment=1, spaceAfter=10)


def P(t): return Paragraph(t, BODY)
def bullets(x): return [Paragraph(f"&bull;&nbsp;&nbsp;{i}", BUL) for i in x]


def tbl(rows, w):
    data = [[Paragraph(c, CELLH) for c in rows[0]]] + \
           [[Paragraph(str(c), CELL) for c in r] for r in rows[1:]]
    t = Table(data, colWidths=w, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9CA3AF")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    return t


def figure(png, caption, width=170*mm):
    from PIL import Image as PILImage
    iw, ih = PILImage.open(png).size
    h = width * ih / iw
    return [Image(png, width=width, height=h), Paragraph(caption, CAP)]


doc = SimpleDocTemplate(os.path.join(HERE, "StockPilot_AI_Test_Plan.pdf"), pagesize=A4,
                        topMargin=15*mm, bottomMargin=14*mm, leftMargin=16*mm, rightMargin=16*mm)
s = []
s.append(Paragraph("AI Layer &mdash; Test Plan &amp; Test Cases", TITLE))
s.append(Paragraph("StockPilot &bull; CSE5015 Computing Project &bull; Group 13 / Batch 131 &bull; " + TODAY, SUB))
s.append(Spacer(1, 8))

s.append(Paragraph("1. Purpose &amp; scope", H1))
s.append(P(
    "This document defines the test plan for the StockPilot <b>AI layer</b> and records the results of "
    "executing it. The AI layer spans data acquisition (DataFetcher), feature engineering (FeatureEngine), "
    "the XGBoost predictor and the six-factor / backtesting logic (StockPredictor). Because these components "
    "only produce value when they cooperate, an <b>integration + evaluation</b> approach is used: the tests "
    "verify that data flows correctly across the pipeline and that the model's outputs satisfy their "
    "contracts and valid ranges."))

s.append(Paragraph("2. Test approach", H1))
s += bullets([
    "<b>Framework:</b> pytest, executed with <font face='Courier'>uv run python -m pytest</font>.",
    "<b>Contract-based assertions:</b> tests check structure and valid ranges (e.g. probabilities sum to "
    "100%, accuracy in [0,1]) rather than exact values, so results are deterministic pass/fail.",
    "<b>Evaluation method:</b> the model is assessed with a chronological 80:20 split and 5-fold "
    "walk-forward validation &mdash; never a random split, which would leak future data.",
    "<b>Baselines:</b> results are read against random (50%), majority-class and buy-and-hold.",
])

s.append(Paragraph("3. Train / test data split", H1))
s.append(P(
    "The dataset is five years of daily OHLCV per ticker. Because the data is a time series, it is split "
    "<b>chronologically</b> &mdash; the oldest data trains the model and the most recent, unseen data tests "
    "it. A random shuffle is deliberately avoided as it would place future days in the training set."))
s.append(tbl([
    ["Split", "Proportion", "Period", "Role"],
    ["Train", "~64%", "oldest", "Model learns the patterns"],
    ["Validation", "~16%", "middle", "Early stopping / tuning (not scored)"],
    ["Test", "~20%", "most recent", "Final unbiased evaluation (used once)"],
], [70, 65, 70, 205]))
s.append(Spacer(1, 3))
s.append(P(
    "Walk-forward validation extends this by repeating the train-past / test-future split across five "
    "expanding-window folds, producing a mean accuracy with a standard deviation instead of a single split."))

s.append(Paragraph("4. Test cases", H1))
s.append(tbl([
    ["ID", "Component", "Scenario", "Expected result", "Status"],
    ["TC-AI-01", "DataFetcher", "Fetch OHLCV for a valid ticker",
     "Non-empty frame with Open/High/Low/Close/Volume; &gt;100 rows", "Pass"],
    ["TC-AI-02", "FeatureEngine", "Compute indicators from OHLCV",
     "Indicator columns added; no fully-empty column", "Pass"],
    ["TC-AI-03", "prepare_data", "Build labelled dataset (±1% dead-band)",
     "Labels strictly binary {0,1}; feature matrix non-empty", "Pass"],
    ["TC-AI-04", "predict()", "Live prediction output contract",
     "signal ∈ {BUY,HOLD,SELL}; confidence 0–100; probs sum ≈ 100%", "Pass"],
    ["TC-AI-05", "walk_forward_evaluate", "5-fold walk-forward run",
     "5 folds; each accuracy in [0,1]; positive log loss", "Pass"],
    ["TC-AI-06", "backtest()", "Cost-aware strategy backtest",
     "Returns trades, win_rate, returns, sharpe, profit_factor, equity curve", "Pass"],
    ["TC-AI-07", "PredictorConfig", "HOLD-band sanity",
     "0 &lt; hold_lower &lt; 0.5 &lt; hold_upper &lt; 1", "Pass"],
], [46, 74, 118, 190, 34]))

s.append(PageBreak())
s.append(Paragraph("5. Test results (evidence)", H1))
s.append(P(
    "The suite was executed with pytest. All seven AI-layer test cases passed. The screenshots below are "
    "the actual console output of the run and of the model-evaluation utilities."))

s.append(Paragraph("5.1 Test suite execution", H2))
s += figure(shots[0], "Figure 1 — pytest run: 7 AI-layer test cases, all passed.")

s.append(Paragraph("5.2 Walk-forward evaluation", H2))
s += figure(shots[1], "Figure 2 — Walk-forward validation (AAPL, 5 folds): per-fold accuracy and log loss.")

s.append(Paragraph("5.3 Cost-aware backtest", H2))
s += figure(shots[2], "Figure 3 — Backtest metrics (AAPL): trades, win rate, returns vs buy-and-hold, Sharpe.")

s.append(Paragraph("6. Observations", H1))
s += bullets([
    "All structural / contract tests pass, confirming the AI pipeline is correctly wired end to end.",
    "Walk-forward accuracy is modestly above random with visible fold-to-fold variance &mdash; expected for "
    "near-efficient daily direction, and honestly reported rather than cherry-picked.",
    "The backtest result varies with each retraining run; it is evaluated against buy-and-hold, and both "
    "the edge and the risk-adjusted metrics (Sharpe, profit factor, drawdown) are reported.",
    "These tests verify correctness and contracts; predictive quality is assessed separately by the "
    "evaluation metrics above.",
])

s.append(Paragraph("7. How to reproduce", H1))
s.append(Paragraph(
    "cd backend<br/>uv run python -m pytest ../AI_Test_Plan/test_ai_layer.py -v",
    ParagraphStyle("R", parent=st["Normal"], fontName="Courier", fontSize=9,
                   backColor=colors.HexColor("#F3F4F6"), borderPadding=6, leading=13)))

doc.build(s)
print("wrote StockPilot_AI_Test_Plan.pdf")
