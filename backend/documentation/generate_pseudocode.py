"""StockPilot — Pseudo Code document (Chapter 03 deliverable).

Structured-English pseudocode for every significant algorithm in the system,
written from the verified implementation.
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
GREY = HexColor("#5a5a64"); LIGHTB = HexColor("#eef2f9"); LIGHTGOLD = HexColor("#fbf6e9")
CODEBG = HexColor("#f5f5f7"); BORDER = HexColor("#c9d3e6"); TEXT = HexColor("#16161a")

PAGE_W, PAGE_H = A4
MARGIN = 46
CW = PAGE_W - 2 * MARGIN
OUT = os.path.join(os.path.dirname(__file__), "StockPilot_Pseudocode.pdf")

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                        topMargin=MARGIN, bottomMargin=MARGIN,
                        title="StockPilot - Pseudo Code", author="Group 13 - CSE5015")

S = getSampleStyleSheet()
S.add(ParagraphStyle("T1", fontName="Helvetica-Bold", fontSize=23, leading=27, textColor=NAVY, spaceAfter=3))
S.add(ParagraphStyle("T2", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=ACCENT, spaceAfter=9))
S.add(ParagraphStyle("Sub", fontName="Helvetica-Oblique", fontSize=10, leading=14, textColor=GREY, spaceAfter=12))
S.add(ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=NAVY, spaceBefore=15, spaceAfter=6))
S.add(ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=11, leading=14.5, textColor=BLUE, spaceBefore=11, spaceAfter=4))
S.add(ParagraphStyle("Body", fontName="Helvetica", fontSize=9.3, leading=13.2, textColor=TEXT, alignment=TA_JUSTIFY, spaceAfter=5))
S.add(ParagraphStyle("PCode", fontName="Courier", fontSize=7.7, leading=10.4, textColor=HexColor("#101014"),
                     backColor=CODEBG, borderPadding=8, spaceBefore=3, spaceAfter=8, leftIndent=3, rightIndent=3))
S.add(ParagraphStyle("Cell", fontName="Helvetica", fontSize=8.2, leading=10.8, textColor=TEXT))
S.add(ParagraphStyle("CellC", fontName="Courier", fontSize=7.6, leading=10.2, textColor=HexColor("#101014")))
S.add(ParagraphStyle("Head", fontName="Helvetica-Bold", fontSize=8.2, leading=10.8, textColor=white))
S.add(ParagraphStyle("CoTitle", fontName="Helvetica-Bold", fontSize=9.3, leading=12, textColor=TEXT))
S.add(ParagraphStyle("CoBody", fontName="Helvetica", fontSize=8.8, leading=12.4, textColor=TEXT, alignment=TA_JUSTIFY))

def P(t, s="Body"): return Paragraph(t, S[s])
def _p(t): return Paragraph(str(t), S["Cell"])
def _pc(t): return Paragraph(str(t), S["CellC"])
def _ph(t): return Paragraph(str(t), S["Head"])

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
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),3.5),("BOTTOMPADDING",(0,0),(-1,-1),3.5)]))
    return t

def code(txt):
    """Render pseudocode preserving indentation.

    ReportLab collapses runs of whitespace inside a Paragraph, which would destroy
    the nesting that pseudocode relies on, so leading spaces become &nbsp;.
    """
    out = []
    for line in txt.split("\n"):
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        esc = stripped.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        out.append("&nbsp;" * indent + esc)
    return Paragraph("<br/>".join(out), S["PCode"])

def algo(num, title, purpose, body, keep=False):
    els = [P(f"{num} &nbsp; {title}", "H2"),
           P(f"<i>Purpose:</i> {purpose}"),
           code(body)]
    return KeepTogether(els) if keep else els

st = []

# ─────────── COVER ───────────
st.append(P("StockPilot", "T1"))
st.append(P("Pseudo Code", "T2"))
st.append(P("Structured-English algorithms for every significant computation in the system: the six-factor "
            "scoring engine, the XGBoost prediction model, the backtesting engine, sentiment analysis, "
            "authentication, the marketplace approval workflow, and the supporting application logic. "
            "Written directly from the implemented code.", "Sub"))
st.append(rule())
st.append(callout("Notation",
    "<font face='Courier'>ALGORITHM / BEGIN / END</font> delimit a routine. <font face='Courier'>INPUT</font> and "
    "<font face='Courier'>OUTPUT</font> declare parameters and results. Control flow uses "
    "<font face='Courier'>IF / THEN / ELSE / ENDIF</font>, <font face='Courier'>FOR EACH / ENDFOR</font>, "
    "<font face='Courier'>WHILE / ENDWHILE</font>. <font face='Courier'>&larr;</font> denotes assignment and "
    "<font face='Courier'>//</font> introduces a comment. <font face='Courier'>CLAMP(x, lo, hi)</font> restricts "
    "x to the range [lo, hi]. Indentation shows nesting.", LIGHTGOLD, ACCENT))
st.append(Spacer(1,8))

st.append(table(["Section","Algorithms"], [
 ["1. Core AI engine","Six-factor scoring, factor computation, verdict derivation, sentiment"],
 ["2. Machine learning","Feature engineering, dataset preparation, training, walk-forward evaluation, live prediction"],
 ["3. Backtesting","Signal generation, portfolio simulation, metric calculation"],
 ["4. Marketplace","Threshold validation, publish request, administrator approval"],
 ["5. Security","Registration, login, request authentication, role checks, token refresh"],
 ["6. Application logic","Portfolio valuation, journal statistics, sector breakdown, notifications"],
], [1.35*inch, CW-1.35*inch]))

# ═══════════ 1. CORE AI ═══════════
st.append(P("1. Core AI Engine", "H1"))

st.extend(algo("1.1", "Generate an investment verdict (main entry point)",
  "Produce an explainable BUY / HOLD / SELL recommendation for a ticker using the user's factor weights.",
"""ALGORITHM GenerateVerdict
INPUT   ticker      : stock symbol
        weights     : map of six factor names to numeric weights
OUTPUT  verdict, confidence, compositeScore, factorScores

BEGIN
    // 1. Acquire and prepare market data
    rawData  <- FetchHistoricalData(ticker, period = "6 months")
    IF rawData is empty THEN
        RETURN error "insufficient data"
    ENDIF
    indicators <- CalculateAllIndicators(rawData)      // Algorithm 2.1
    latest     <- last row of indicators

    // 2. Score each of the six factors on a 0-100 scale
    factorScores <- ComputeSixFactors(latest, indicators, ticker)   // Algorithm 1.2

    // 3. Combine the factor scores using the user's weights
    totalWeight <- SUM of all values in weights
    IF totalWeight = 0 THEN totalWeight <- 1 ENDIF     // guard against divide-by-zero

    compositeScore <- 0
    FOR EACH factor IN factorScores DO
        w <- weights[factor.name]  (0 if absent)
        compositeScore <- compositeScore + factor.score * (w / totalWeight)
    ENDFOR

    // 4. Map the composite score onto a verdict
    IF compositeScore >= BUY_THRESHOLD THEN
        verdict <- "BUY"
    ELSE IF compositeScore <= SELL_THRESHOLD THEN
        verdict <- "SELL"
    ELSE
        verdict <- "HOLD"
    ENDIF

    // 5. Confidence reflects how strongly the factors agree
    confidence <- ComputeConsensusStrength(factorScores)

    RETURN verdict, confidence, compositeScore, factorScores
END"""))

st.extend(algo("1.2", "Compute the six factor scores",
  "Convert raw technical indicators into six comparable 0-100 scores.",
"""ALGORITHM ComputeSixFactors
INPUT   latest      : most recent row of indicator values
        indicators  : full indicator history (needed for the sentiment fallback)
        ticker      : stock symbol
OUTPUT  factorScores : map of six factor names to scores in [0, 100]

BEGIN
    // ---- MOMENTUM : trend strength ----
    rsiPart   <- (latest.RSI_14 / 100) * 0.4
    macdPart  <- (0.5 + CLAMP(latest.MACD_Histogram / 2, -0.5, 0.5)) * 0.3
    posPart   <- latest.Price_Position * 0.3
    momentum  <- CLAMP((rsiPart + macdPart + posPart) * 100, 0, 100)

    // ---- VOLATILITY : lower volatility scores higher (safety) ----
    volScore  <- 1 - CLAMP((latest.Volatility_20 * 100) / 5, 0, 1)
    atrPct    <- latest.ATR_14 / latest.Close
    atrScore  <- 1 - CLAMP(atrPct / 0.05, 0, 1)
    volatility<- CLAMP(((volScore + atrScore) / 2) * 100, 0, 100)

    // ---- VOLUME : participation and money flow ----
    ratioPart <- CLAMP(latest.Volume_Ratio / 2, 0, 1) * 0.5
    mfiPart   <- (latest.MFI_14 / 100) * 0.5
    volume    <- CLAMP((ratioPart + mfiPart) * 100, 0, 100)

    // ---- VALUATION : mean-reversion opportunity ----
    bbScore   <- 1 - latest.BB_Position          // low in the band scores higher
    smaSpread <- (latest.Price_to_SMA_20 + latest.Price_to_SMA_50 - 2) / 0.2
    smaScore  <- 1 - CLAMP(smaSpread, -1, 1) * 0.5
    valuation <- CLAMP(((bbScore + smaScore) / 2) * 100, 0, 100)

    // ---- GROWTH : rate of change plus trend confirmation ----
    rocPart   <- CLAMP(latest.ROC_10 / 20, -1, 1) * 0.5
    trendBonus<- latest.Price_Above_SMA_20 * 0.3
    growth    <- CLAMP(((rocPart + 0.5 + trendBonus) * 100) / 1.8, 0, 100)

    // ---- SENTIMENT : news analysis, with a technical fallback ----
    sentiment <- ComputeSentimentScore(ticker, indicators)          // Algorithm 1.3

    RETURN { momentum, volatility, volume, valuation, growth, sentiment }
END"""))

st.extend(algo("1.3", "Compute the sentiment score",
  "Score recent news with FinBERT, falling back to an on-balance-volume trend when no news is available.",
"""ALGORITHM ComputeSentimentScore
INPUT   ticker, indicators
OUTPUT  score in [0, 100]      // 100 = strongly positive, 50 = neutral

BEGIN
    TRY
        headlines <- FetchNewsHeadlines(ticker, maximum = 10)
        IF headlines is empty THEN
            RAISE "no headlines"
        ENDIF

        totalScore <- 0
        FOR EACH headline IN headlines DO
            probabilities <- FinBERTClassify(headline)   // positive / negative / neutral
            totalScore <- totalScore + (probabilities.positive - probabilities.negative)
        ENDFOR
        averageScore <- totalScore / COUNT(headlines)    // range -1 .. +1
        score <- (averageScore + 1) / 2 * 100            // rescale to 0 .. 100

    CATCH any error
        // FALLBACK: use the on-balance-volume trend as a sentiment proxy
        obvWindow <- last 20 values of indicators.OBV
        IF COUNT(obvWindow) >= 2 THEN
            trend <- (obvWindow.last - obvWindow.first) / (ABS(obvWindow.first) + 1)
            score <- CLAMP(0.5 + trend * 5, 0, 1) * 100
        ELSE
            score <- 50                                  // neutral default
        ENDIF
    ENDTRY

    RETURN CLAMP(score, 0, 100)
END"""))

# ═══════════ 2. ML ═══════════
st.append(PageBreak())
st.append(P("2. Machine Learning Pipeline", "H1"))

st.extend(algo("2.1", "Calculate all technical indicators",
  "Derive 23 indicator columns from raw OHLCV price data.",
"""ALGORITHM CalculateAllIndicators
INPUT   data : table of Open, High, Low, Close, Volume indexed by date
OUTPUT  enriched table with 23 additional indicator columns

BEGIN
    VALIDATE that data contains the required OHLCV columns and is non-empty

    // Trend
    FOR EACH period IN {5, 10, 20, 50} DO
        data.SMA_period <- simple moving average of Close over `period` days
        data.EMA_period <- exponential moving average of Close over `period` days
    ENDFOR
    data.Price_to_SMA_20    <- Close / SMA_20
    data.Price_to_SMA_50    <- Close / SMA_50
    data.Price_Above_SMA_20 <- 1 IF Close > SMA_20 ELSE 0

    // Momentum
    data.RSI_14          <- relative strength index over 14 days
    data.MACD            <- EMA_12(Close) - EMA_26(Close)
    data.MACD_Signal     <- EMA_9(MACD)
    data.MACD_Histogram  <- MACD - MACD_Signal
    data.ROC_10          <- percentage rate of change over 10 days

    // Volatility
    data.BB_Mid      <- SMA_20
    data.BB_High     <- BB_Mid + 2 * standard deviation of Close over 20 days
    data.BB_Low      <- BB_Mid - 2 * standard deviation of Close over 20 days
    data.BB_Width    <- (BB_High - BB_Low) / BB_Mid
    data.BB_Position <- (Close - BB_Low) / (BB_High - BB_Low)
    data.ATR_14      <- average true range over 14 days
    data.Volatility_20 <- standard deviation of daily returns over 20 days

    // Volume
    data.OBV          <- on-balance volume (cumulative signed volume)
    data.MFI_14       <- money flow index over 14 days
    data.VWAP_20      <- volume-weighted average price over 20 days
    data.Volume_Ratio <- Volume / 20-day average Volume

    // Derived price relationships
    data.Daily_Return     <- percentage change of Close
    data.High_Low_Ratio   <- High / Low
    data.Close_Open_Ratio <- Close / Open
    data.Price_Position   <- (Close - 20-day low) / (20-day high - 20-day low)

    HANDLE missing values: forward-fill, then drop any remaining incomplete rows
    RETURN data
END"""))

st.extend(algo("2.2", "Prepare the labelled training dataset",
  "Build the supervised learning problem: features X and binary target y.",
"""ALGORITHM PrepareTrainingData
INPUT   ticker, period (default "5y")
OUTPUT  X : feature matrix,  y : binary target vector

BEGIN
    raw        <- FetchHistoricalData(ticker, period)
    indicators <- CalculateAllIndicators(raw)

    // Forward return over the prediction horizon (default 5 trading days)
    horizon    <- config.target_horizon
    fwdReturn  <- percentage change of Close over `horizon` days, SHIFTED BACKWARD
                  by `horizon` so each row is labelled with its own future outcome

    // Three-way labelling with a neutral dead-band (default 1%)
    deadband <- config.target_deadband
    FOR EACH row DO
        IF   fwdReturn[row] >  deadband THEN target[row] <- 1      // up move
        ELSE IF fwdReturn[row] < -deadband THEN target[row] <- 0   // down move
        ELSE target[row] <- UNDEFINED                              // too small: noise
        ENDIF
    ENDFOR
    DROP every row whose target is UNDEFINED   // keeps the two classes distinct

    // Build the feature matrix
    X <- indicators WITHOUT the columns {Target, Close}
         // Close is excluded because the label is derived from it (leakage)

    IF config.stationary_only THEN
        // Keep only scale-free columns. Absolute price levels such as SMA_20
        // are not comparable across tickers or across time, so a split like
        // "SMA_20 > 187.5" carries no transferable information.
        X <- X restricted to:
             RSI_14, MFI_14, BB_Position, Price_Position,
             Price_to_SMA_20, Price_to_SMA_50, BB_Width, Volume_Ratio,
             High_Low_Ratio, Close_Open_Ratio, Daily_Return, ROC_10,
             Volatility_20, MACD_Histogram, Price_Above_SMA_20
    ENDIF

    y <- target column
    RECORD feature column names for use at prediction time
    RETURN X, y
END"""))

st.extend(algo("2.3", "Train the model",
  "Fit an XGBoost classifier using a chronological split and early stopping.",
"""ALGORITHM TrainModel
INPUT   ticker, period, testSize (default 0.2)
OUTPUT  trained classifier

BEGIN
    X, y <- PrepareTrainingData(ticker, period)

    // Chronological split - never shuffle time-series data
    splitIndex <- FLOOR(COUNT(X) * (1 - testSize))
    XTrain, XTest <- X[0 .. splitIndex-1], X[splitIndex .. end]
    yTrain, yTest <- y[0 .. splitIndex-1], y[splitIndex .. end]

    // Carve a validation slice from the END of the training window
    validationIndex <- FLOOR(COUNT(XTrain) * 0.80)
    XFit, yFit <- XTrain[0 .. validationIndex-1], yTrain[0 .. validationIndex-1]
    XVal, yVal <- XTrain[validationIndex .. end], yTrain[validationIndex .. end]

    // Correct for class imbalance
    scalePosWeight <- COUNT(yFit = 0) / COUNT(yFit = 1)

    model <- NEW XGBoostClassifier WITH
                 n_estimators     = config.max_estimators      (300)
                 max_depth        = config.max_depth           (4)
                 learning_rate    = config.learning_rate       (0.03)
                 subsample        = 0.8
                 colsample_bytree = 0.8
                 scale_pos_weight = scalePosWeight

    FIT model ON (XFit, yFit)
        WATCHING (XVal, yVal)
        STOPPING EARLY after config.early_stopping_rounds without improvement

    metrics <- Evaluate(model, XTest, yTest)   // accuracy, log-loss, confusion matrix
    LOG metrics

    SAVE model, feature column names, configuration and library versions
         as a single bundle to disk
    RETURN model
END"""))

st.extend(algo("2.4", "Walk-forward evaluation",
  "Honestly estimate performance using expanding-window time-series cross-validation.",
"""ALGORITHM WalkForwardEvaluate
INPUT   ticker, numberOfSplits (default 5)
OUTPUT  mean accuracy, standard deviation, mean log-loss

BEGIN
    X, y <- PrepareTrainingData(ticker)
    accuracies <- empty list
    logLosses  <- empty list

    // Each fold trains on all data BEFORE its test window, never after
    FOR EACH (trainIndices, testIndices) IN TimeSeriesSplit(X, numberOfSplits) DO
        model <- NEW XGBoostClassifier WITH the configured hyper-parameters
        FIT model ON X[trainIndices], y[trainIndices]

        predictions <- model.PredictProbability(X[testIndices])
        APPEND Accuracy(y[testIndices], predictions >= 0.5) TO accuracies
        APPEND LogLoss(y[testIndices], predictions)          TO logLosses
    ENDFOR

    RETURN MEAN(accuracies), STDDEV(accuracies), MEAN(logLosses)
END"""))

st.extend(algo("2.5", "Generate a live prediction",
  "Run the trained model on the most recent market data and persist the result.",
"""ALGORITHM PredictLive
INPUT   ticker
OUTPUT  signal, confidence, probabilityUp, probabilityDown

BEGIN
    IF model is not loaded IN MEMORY THEN
        LOAD model bundle FROM disk           // once per process, then cached
        IF the bundle is missing THEN
            RETURN error "model unavailable"  // HTTP 503
        ENDIF
    ENDIF

    raw        <- FetchHistoricalData(ticker, period = "6 months")
    indicators <- CalculateAllIndicators(raw)
    IF indicators is empty THEN
        RETURN error "no usable data for ticker"
    ENDIF

    latestRow <- last row of indicators, excluding Close

    // Fail loudly rather than silently substituting zeros
    missing <- feature columns recorded at training time BUT absent from latestRow
    IF missing is not empty THEN
        RETURN error "live features do not match training features"
    ENDIF
    latestRow <- latestRow restricted to the recorded feature columns
    IF latestRow contains any missing value THEN
        RETURN error "live features contain missing values"
    ENDIF

    probabilities  <- model.PredictProbability(latestRow)
    probabilityUp   <- probabilities[class = 1]
    probabilityDown <- probabilities[class = 0]

    // Map the probability onto a signal using the neutral HOLD band
    IF probabilityUp >= config.hold_upper THEN          // default 0.57
        signal <- "BUY"   ; confidence <- probabilityUp
    ELSE IF probabilityUp <= config.hold_lower THEN     // default 0.43
        signal <- "SELL"  ; confidence <- probabilityDown
    ELSE
        signal <- "HOLD"  ; confidence <- MAX(probabilityUp, probabilityDown)
    ENDIF

    PERSIST a prediction record (ticker, signal, confidence,
            probabilityUp, probabilityDown, modelVersion, timestamp)

    RETURN signal, confidence * 100, probabilityUp * 100, probabilityDown * 100
END"""))

# ═══════════ 3. BACKTEST ═══════════
st.append(PageBreak())
st.append(P("3. Backtesting Engine", "H1"))

st.extend(algo("3.1", "Run a backtest",
  "Simulate the strategy over historical data and report risk-adjusted performance.",
"""ALGORITHM RunBacktest
INPUT   ticker, period, weights, riskTolerance, timeHorizon
OUTPUT  performance metrics, equity curve, trade ledger

BEGIN
    // 1. Translate the investor profile into simulation parameters
    riskConfig    <- RISK_TABLE[riskTolerance]      // Conservative | Moderate | Aggressive
    horizonConfig <- HORIZON_TABLE[timeHorizon]     // Short | Medium | Long

    buyThreshold  <- riskConfig.buy                          // entry conviction
    sellThreshold <- riskConfig.buy - horizonConfig.band     // exit band
    stopLoss      <- horizonConfig.stopLoss   * riskConfig.stopMultiplier
    takeProfit    <- horizonConfig.takeProfit * riskConfig.profitMultiplier

    // 2. Prepare the data
    raw        <- FetchHistoricalData(ticker, period)
    indicators <- CalculateAllIndicators(raw)
    IF COUNT(indicators) < 60 THEN
        RETURN error "insufficient data for backtest"     // HTTP 400
    ENDIF

    // 3. Score EVERY historical day, not just the latest
    compositeSeries <- empty series
    FOR EACH day IN indicators DO
        scores <- ComputeSixFactors(day, indicators, ticker)
                  // NOTE: for historical days the sentiment factor uses the OBV
                  // proxy, because per-day news sentiment is not stored
        compositeSeries[day] <- weighted sum of scores USING weights
    ENDFOR

    // 4. Derive entry and exit signals
    FOR EACH day DO
        entrySignal[day] <- TRUE IF compositeSeries[day] >= buyThreshold
        exitSignal[day]  <- TRUE IF compositeSeries[day] <= sellThreshold
    ENDFOR

    // 5. Simulate the portfolio (delegated to the vectorbt engine)
    portfolio <- SimulatePortfolio(
                     prices          = indicators.Close,
                     entries         = entrySignal,
                     exits           = exitSignal,
                     trailingStop    = stopLoss,
                     takeProfit      = takeProfit,
                     onOppositeEntry = "close then allow re-entry",
                     fees            = 0.1%,
                     slippage        = 0.05%,
                     initialCash     = 10000)

    // 6. Extract metrics, guarding against undefined values
    totalReturn   <- portfolio.TotalReturn * 100
    buyHoldReturn <- (last Close / first Close - 1) * 100
    edgeVsHold    <- totalReturn - buyHoldReturn
    tradeCount    <- portfolio.Trades.Count

    IF tradeCount > 0 THEN
        winRate      <- portfolio.Trades.WinRate
        profitFactor <- portfolio.Trades.ProfitFactor
    ELSE
        winRate <- 0 ; profitFactor <- 0
    ENDIF

    IF profitFactor is infinite OR undefined THEN profitFactor <- 99.99 ENDIF
    IF sharpeRatio is undefined THEN sharpeRatio <- 0 ENDIF

    sharpeRatio  <- portfolio.SharpeRatio
    maxDrawdown  <- ABS(portfolio.MaxDrawdown) * 100

    // 7. Build the outputs
    equityCurve <- portfolio.Value normalised so the first point equals 1.0,
                   down-sampled to approximately 100 points
    tradeLedger <- FOR EACH completed trade RECORD
                   { entryDate, entryPrice, exitDate, exitPrice,
                     size, profitOrLoss, returnPercent, status }

    RETURN totalReturn, buyHoldReturn, edgeVsHold, winRate, sharpeRatio,
           maxDrawdown, profitFactor, tradeCount, equityCurve, tradeLedger
END"""))

# ═══════════ 4. MARKETPLACE ═══════════
st.append(P("4. Marketplace Workflow", "H1"))

st.extend(algo("4.1", "Request publication of a strategy",
  "Validate a strategy's backtest against the live thresholds and submit it for review.",
"""ALGORITHM RequestPublication
INPUT   strategyId, priceInCents, backtestMetrics, currentUser
OUTPUT  listing status

BEGIN
    // 1. Role check - runs BEFORE any other work
    REQUIRE currentUser.role IN {analyst, admin}
        ELSE RETURN error 403 "insufficient permissions"

    // 2. Ownership check - the WHERE clause includes the owner, so another
    //    user's strategy simply returns nothing (404, never revealing existence)
    strategy <- SELECT strategy WHERE id = strategyId AND ownerId = currentUser.id
    IF strategy is NULL THEN
        RETURN error 404 "strategy not found"
    ENDIF

    // 2. Load the thresholds as configured by the administrator
    thresholds <- LoadPlatformSettings()      // creates defaults if absent

    // 3. Re-validate on the SERVER. The client-side check is convenience only
    //    and must never be trusted.
    failures <- empty list
    IF backtestMetrics.trades       < thresholds.minTrades       THEN
        APPEND "min trades not met" TO failures
    ENDIF
    IF backtestMetrics.winRate      < thresholds.minWinRate      THEN
        APPEND "win rate not met" TO failures
    ENDIF
    IF backtestMetrics.sharpe       < thresholds.minSharpe       THEN
        APPEND "sharpe ratio not met" TO failures
    ENDIF
    IF backtestMetrics.maxDrawdown  > thresholds.maxDrawdown     THEN
        APPEND "drawdown too large" TO failures
    ENDIF
    IF backtestMetrics.profitFactor < thresholds.minProfitFactor THEN
        APPEND "profit factor not met" TO failures
    ENDIF

    IF failures is not empty THEN
        RETURN error 400 WITH the per-metric breakdown     // nothing is stored
    ENDIF

    // 4. Create or update the listing
    listing <- SELECT listing WHERE strategyId = strategyId
    IF listing EXISTS THEN
        IF listing.status = "review"   THEN RETURN error "already pending review" ENDIF
        IF listing.status = "verified" THEN RETURN error "already published"      ENDIF
        UPDATE listing SET status = "review", price and all six metrics
    ELSE
        INSERT listing WITH status = "review", price and all six metrics
    ENDIF

    COMMIT
    RETURN { status: "review", listingId: listing.id }
END"""))

st.extend(algo("4.2", "Administrator reviews a listing",
  "Approve, reject or remove a submitted listing.",
"""ALGORITHM ReviewListing
INPUT   listingId, action IN {approve, reject, remove, delete}, administrator
OUTPUT  resulting status

BEGIN
    REQUIRE administrator.role = "admin"      // else 403 Insufficient permissions

    listing <- SELECT listing WITH its strategy WHERE id = listingId
    IF listing is NULL THEN RETURN error 404 ENDIF

    CASE action OF

        approve:
            IF listing.status <> "review" THEN
                RETURN error 400 "only listings in review can be approved"
            ENDIF
            listing.status            <- "verified"
            listing.listedAt          <- CURRENT TIMESTAMP
            listing.strategy.isPublished <- TRUE          // now publicly visible

        reject:
            IF listing.status <> "review" THEN
                RETURN error 400 "only listings in review can be rejected"
            ENDIF
            listing.status            <- "removed"
            listing.strategy.isPublished <- FALSE

        remove:
            // No status guard - this may delist an already-active listing
            listing.status            <- "removed"
            listing.strategy.isPublished <- FALSE

        delete:
            listing.strategy.isPublished <- FALSE
            DELETE listing permanently
    ENDCASE

    COMMIT
    RETURN listing.status
END"""))

# ═══════════ 5. SECURITY ═══════════
st.append(PageBreak())
st.append(P("5. Security and Authentication", "H1"))

st.extend(algo("5.1", "Register and log in",
  "Create an account with a hashed password, and issue tokens on successful login.",
"""ALGORITHM RegisterUser
INPUT   fullName, email, password
OUTPUT  access token, refresh token, user profile
BEGIN
    existing <- SELECT user WHERE email = email
    IF existing EXISTS THEN
        RETURN error 409 "email already registered"
    ENDIF
    passwordHash <- BcryptHash(password)        // never store the plain password
    user <- INSERT user (email, passwordHash, fullName, role = "investor")
    RETURN CreateAccessToken(user.id), CreateRefreshToken(user.id), user
END


ALGORITHM LoginUser
INPUT   email, password
OUTPUT  access token, refresh token, user profile
BEGIN
    user <- SELECT user WHERE email = email

    // Identical response for both failure modes, so the API does not reveal
    // whether an email address is registered
    IF user is NULL OR NOT BcryptVerify(password, user.passwordHash) THEN
        RETURN error 401 "invalid email or password"
    ENDIF

    RETURN CreateAccessToken(user.id), CreateRefreshToken(user.id), user
END"""))

st.extend(algo("5.2", "Authenticate an incoming request",
  "Validate the bearer token on every protected endpoint and enforce role permissions.",
"""ALGORITHM AuthenticateRequest
INPUT   Authorization header
OUTPUT  the authenticated user, or an error

BEGIN
    token   <- extract the bearer credential FROM the Authorization header
    payload <- DecodeAndVerifyJWT(token)        // checks signature and expiry
    IF payload is INVALID THEN
        RETURN error 401 "invalid token"
    ENDIF

    userId <- payload.subject
    IF userId is not a valid identifier THEN
        RETURN error 401 "invalid token"
    ENDIF

    user <- SELECT user WHERE id = userId
    IF user is NULL OR user.isActive = FALSE THEN
        RETURN error 401 "user not found"       // suspended accounts fail here
    ENDIF

    RETURN user
END


ALGORITHM RequireRole
INPUT   allowedRoles
OUTPUT  the authenticated user, or an error
BEGIN
    user <- AuthenticateRequest()               // runs first
    IF user.role NOT IN allowedRoles THEN
        RETURN error 403 "insufficient permissions"
    ENDIF
    RETURN user
END"""))

st.extend(algo("5.3", "Refresh an expired token (client side)",
  "Transparently renew the access token and retry the failed request exactly once.",
"""ALGORITHM HandleUnauthorisedResponse
INPUT   the failed request, the error response
OUTPUT  the retried response, or a redirect to the login page

BEGIN
    IF error.status <> 401 THEN
        PROPAGATE the error                       // not an auth problem
    ENDIF

    IF request was already retried THEN
        PROPAGATE the error                       // prevent an infinite loop
    ENDIF

    IF a refresh is already in progress THEN
        ENQUEUE this request and WAIT for the new token
        RETRY the request with that token WHEN it arrives
        RETURN
    ENDIF

    MARK request as retried
    SET refreshInProgress <- TRUE

    refreshToken <- READ from local storage
    IF refreshToken is absent THEN
        CLEAR stored tokens
        REDIRECT to the login page
        RETURN
    ENDIF

    TRY
        response <- POST /auth/refresh WITH refreshToken
        STORE the new access token (and refresh token if returned)
        RELEASE every queued request WITH the new token
        RETRY the original request WITH the new token
    CATCH
        REJECT all queued requests
        CLEAR stored tokens
        REDIRECT to the login page
    FINALLY
        SET refreshInProgress <- FALSE
    ENDTRY
END"""))

# ═══════════ 6. APPLICATION ═══════════
st.append(P("6. Application Logic", "H1"))

st.extend(algo("6.1", "Value the portfolio",
  "List open holdings with live prices and derived profit or loss.",
"""ALGORITHM ValuePortfolio
INPUT   currentUser
OUTPUT  holdings enriched with live prices and totals

BEGIN
    holdings <- SELECT holdings
                WHERE userId = currentUser.id AND closedAt IS NULL
                ORDER BY openedAt DESCENDING

    tickers  <- distinct ticker symbols among the holdings
    stockMap <- SELECT stocks WHERE ticker IN tickers    // for names and sectors

    // Fetch live prices CONCURRENTLY (bounded pool), tolerating failures
    livePrices <- empty map
    FOR EACH ticker IN tickers IN PARALLEL (at most 4 at a time) DO
        TRY
            livePrices[ticker] <- LookupCurrentPrice(ticker)
        CATCH
            // leave unset; the stored price will be used instead
        ENDTRY
    ENDFOR

    FOR EACH holding IN holdings DO
        holding.name <- stockMap[holding.ticker].name IF present ELSE holding.ticker
        IF livePrices CONTAINS holding.ticker THEN
            holding.currentPrice <- livePrices[holding.ticker]
        ENDIF
    ENDFOR

    // Derived figures (computed for display)
    marketValue  <- SUM over holdings OF quantity * (currentPrice OR avgCost)
    costBasis    <- SUM over holdings OF quantity * avgCost
    unrealisedPL <- marketValue - costBasis
    returnPct    <- (unrealisedPL / costBasis) * 100   IF costBasis > 0 ELSE 0

    RETURN holdings, marketValue, costBasis, unrealisedPL, returnPct
END"""))

st.extend(algo("6.2", "Compute trading journal statistics",
  "Derive win rate, net profit, profit factor and the equity curve from logged trades.",
"""ALGORITHM ComputeJournalStatistics
INPUT   trades : list of completed trades
OUTPUT  tradeCount, winRate, netProfitLoss, profitFactor, equityCurve

BEGIN
    wins <- empty list ; losses <- empty list ; equityCurve <- empty list
    runningTotal <- 0

    FOR EACH trade IN trades ORDERED BY closedAt ASCENDING DO
        direction <- +1 IF trade.side = "buy" ELSE -1
        profit    <- direction * (trade.exitPrice - trade.entryPrice) * trade.quantity

        IF profit > 0 THEN APPEND profit TO wins
        ELSE IF profit < 0 THEN APPEND profit TO losses
        ENDIF

        runningTotal <- runningTotal + profit
        APPEND runningTotal TO equityCurve
    ENDFOR

    tradeCount    <- COUNT(trades)
    decided       <- COUNT(wins) + COUNT(losses)      // exclude break-even trades
    winRate       <- COUNT(wins) / decided            IF decided > 0 ELSE 0
    netProfitLoss <- SUM(wins) + SUM(losses)

    grossProfit <- SUM(wins)
    grossLoss   <- ABS(SUM(losses))
    profitFactor<- grossProfit / grossLoss            IF grossLoss > 0
                   ELSE (99.99 IF grossProfit > 0 ELSE 0)

    RETURN tradeCount, winRate, netProfitLoss, profitFactor, equityCurve
END"""))

st.extend(algo("6.3", "Compute the sector breakdown",
  "Group portfolio value by market sector for the allocation chart.",
"""ALGORITHM ComputeSectorBreakdown
INPUT   currentUser
OUTPUT  list of { sector, value, weightPercent } ordered by value

BEGIN
    holdings <- SELECT holdings WHERE userId = currentUser.id AND closedAt IS NULL
    IF holdings is empty THEN RETURN empty list ENDIF

    stockMap     <- SELECT stocks WHERE ticker IN holdings.tickers
    sectorTotals <- empty map

    FOR EACH holding IN holdings DO
        sector <- stockMap[holding.ticker].sector IF present ELSE "Unknown"
        value  <- holding.quantity * (holding.currentPrice OR holding.avgCost)
        sectorTotals[sector] <- sectorTotals[sector] + value
    ENDFOR

    grandTotal <- SUM of all values in sectorTotals
    result <- empty list
    FOR EACH (sector, value) IN sectorTotals ORDERED BY value DESCENDING DO
        APPEND { sector, value, weightPercent: value / grandTotal * 100 } TO result
    ENDFOR

    RETURN result
END"""))

st.extend(algo("6.4", "Manage notifications",
  "Retrieve recent notifications and mark them as read.",
"""ALGORITHM ListNotifications
INPUT   currentUser
OUTPUT  notifications and the unread count
BEGIN
    notifications <- SELECT notifications
                     WHERE userId = currentUser.id
                     ORDER BY createdAt DESCENDING
                     LIMIT 50
    unreadCount <- COUNT of notifications WHERE isRead = FALSE
    RETURN notifications, unreadCount
END


ALGORITHM MarkAllNotificationsRead
INPUT   currentUser
BEGIN
    // A single set-based update; rows are never loaded into memory
    UPDATE notifications
       SET isRead = TRUE
     WHERE userId = currentUser.id AND isRead = FALSE
    COMMIT
END"""))

st.extend(algo("6.5", "Transaction handling (applies to every request)",
  "Guarantee that a request either commits all of its changes or none of them.",
"""ALGORITHM HandleRequestTransaction
INPUT   the request handler to execute
OUTPUT  the handler's response

BEGIN
    session <- OPEN a new database session

    TRY
        response <- EXECUTE the request handler USING session
        COMMIT session              // all changes are applied together
        RETURN response
    CATCH any error
        ROLLBACK session            // no partial writes survive
        PROPAGATE the error
    FINALLY
        CLOSE session               // always release the connection
    ENDTRY
END"""))

def footer(canvas, d):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.4)
    canvas.setFillColor(GREY)
    canvas.drawCentredString(PAGE_W/2, 25,
        f"StockPilot - Pseudo Code  |  Group 13, CSE5015  |  Page {d.page}")
    canvas.restoreState()

doc.build(st, onFirstPage=footer, onLaterPages=footer)
print("Generated:", OUT)
