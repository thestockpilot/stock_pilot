"""Generate the StockPilot data flow diagrams.

Yourdon / DeMarco notation:
    rectangle              external entity (source or sink)
    circle                 process, numbered
    open-ended rectangle   data store, numbered D1..Dn
    labelled arrow         data flow

Note: Chen notation is an ERD notation (entity / relationship / attribute) and
has no process or data-store symbol, so it cannot express a DFD. Yourdon is the
standard pairing with a Chen ERD.

Three sheets:
    Context (Level 0)  the system as a single process
    Level 1            the eight major processes and every data store
    Level 2            explosion of process 3.0, Generate Investment Advice
"""
import math
import os
from html import escape

OUT_DIR = os.path.dirname(__file__)
FONT = "Helvetica, Arial, sans-serif"
INK = "#111111"
RULE = "#111111"
MUTED = "#555555"


def esc(s):
    return escape(s, quote=False)


# ────────────────────────────────────────────────────────────────
# notation primitives
# ────────────────────────────────────────────────────────────────
def svg_open(w, h, title, subtitle=None):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
           f'viewBox="0 0 {w} {h}" font-family="{FONT}">',
           f'<rect width="{w}" height="{h}" fill="white"/>',
           f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" '
           f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
           f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{RULE}"/></marker></defs>',
           f'<text x="{w/2}" y="36" font-size="19" font-weight="bold" '
           f'text-anchor="middle" fill="{INK}">{esc(title)}</text>']
    if subtitle:
        out.append(f'<text x="{w/2}" y="58" font-size="11.5" text-anchor="middle" '
                   f'fill="{MUTED}">{esc(subtitle)}</text>')
    return out


def entity(x, y, lines, w=190, h=62, duplicate=False):
    """External entity — plain rectangle.

    A repeated entity carries a diagonal stroke in the top-left corner, the
    standard mark for 'this box appears elsewhere on the same diagram'.
    """
    out = [f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" fill="white" '
           f'stroke="{RULE}" stroke-width="2.2"/>']
    if duplicate:
        out.append(f'<line x1="{x-w/2}" y1="{y-h/2+16}" x2="{x-w/2+16}" y2="{y-h/2}" '
                   f'stroke="{RULE}" stroke-width="2.2"/>')
    start = y - (len(lines) - 1) * 7 + 4
    for i, ln in enumerate(lines):
        out.append(f'<text x="{x}" y="{start+i*14}" font-size="12" font-weight="bold" '
                   f'text-anchor="middle" fill="{INK}">{esc(ln)}</text>')
    return out


def process(x, y, num, lines, r=62):
    """Process — circle with its number above the name."""
    out = [f'<circle cx="{x}" cy="{y}" r="{r}" fill="white" stroke="{RULE}" '
           f'stroke-width="2.2"/>',
           f'<line x1="{x-r*0.86}" y1="{y-r*0.5}" x2="{x+r*0.86}" y2="{y-r*0.5}" '
           f'stroke="{RULE}" stroke-width="1.2"/>',
           f'<text x="{x}" y="{y-r*0.5-7}" font-size="12.5" font-weight="bold" '
           f'text-anchor="middle" fill="{INK}">{esc(num)}</text>']
    start = y - (len(lines) - 1) * 6.5 + 8
    for i, ln in enumerate(lines):
        out.append(f'<text x="{x}" y="{start+i*13}" font-size="10" '
                   f'text-anchor="middle" fill="{INK}">{esc(ln)}</text>')
    return out


def datastore(x, y, ident, label, w=232, h=44):
    """Data store — open-ended rectangle with the identifier in a closed cell."""
    x0, y0 = x - w / 2, y - h / 2
    return [f'<line x1="{x0}" y1="{y0}" x2="{x0+w}" y2="{y0}" stroke="{RULE}" stroke-width="2.2"/>',
            f'<line x1="{x0}" y1="{y0+h}" x2="{x0+w}" y2="{y0+h}" stroke="{RULE}" stroke-width="2.2"/>',
            f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+h}" stroke="{RULE}" stroke-width="2.2"/>',
            f'<line x1="{x0+44}" y1="{y0}" x2="{x0+44}" y2="{y0+h}" stroke="{RULE}" stroke-width="2.2"/>',
            f'<text x="{x0+22}" y="{y+5}" font-size="12" font-weight="bold" '
            f'text-anchor="middle" fill="{INK}">{esc(ident)}</text>',
            f'<text x="{x0+56}" y="{y+5}" font-size="11" fill="{INK}">{esc(label)}</text>']


def on_circle(cx, cy, r, tx, ty):
    """Point on a process circle's edge, facing (tx, ty).

    Every flow must physically touch the symbol it connects; computing the
    attachment point removes the guesswork that let earlier revisions leave
    arrows floating in white space.
    """
    ang = math.atan2(ty - cy, tx - cx)
    return (cx + r * math.cos(ang), cy + r * math.sin(ang))


def _head(x1, y1, x2, y2, size=11):
    """Solid arrow head at (x2, y2), pointing away from (x1, y1).

    Drawn as a polygon rather than an SVG marker, which several rasterisers
    ignore — and a DFD without direction on its flows is unreadable.
    """
    ang = math.atan2(y2 - y1, x2 - x1)
    spread = math.radians(21)
    ax = x2 - size * math.cos(ang - spread)
    ay = y2 - size * math.sin(ang - spread)
    bx = x2 - size * math.cos(ang + spread)
    by = y2 - size * math.sin(ang + spread)
    return [f'<polygon points="{x2:.1f},{y2:.1f} {ax:.1f},{ay:.1f} {bx:.1f},{by:.1f}" '
            f'fill="{RULE}"/>']


def flow(points, label=None, at=0.5, dx=0, dy=-7, anchor="middle", both=False, fs=10):
    """Data flow — polyline with an arrow head; `points` is [(x, y), ...]."""
    d = " ".join(f"{px},{py}" for px, py in points)
    out = [f'<polyline points="{d}" fill="none" stroke="{RULE}" stroke-width="1.6"/>']
    out += _head(*points[-2], *points[-1])
    if both:
        out += _head(*points[1], *points[0])
    if label:
        # position along the longest segment
        best, bl = 0, -1
        for i in range(len(points) - 1):
            seg = math.dist(points[i], points[i + 1])
            if seg > bl:
                bl, best = seg, i
        (x1, y1), (x2, y2) = points[best], points[best + 1]
        lx = x1 + (x2 - x1) * at + dx
        ly = y1 + (y2 - y1) * at + dy
        for i, ln in enumerate(label.split("\n")):
            ty = ly + i * 12
            out.append(f'<rect x="{lx - (4.6*len(ln) if anchor=="middle" else 0) - 3}" '
                       f'y="{ty-9}" width="{9.2*len(ln)+6}" height="12" fill="white"/>')
            out.append(f'<text x="{lx}" y="{ty}" font-size="{fs}" text-anchor="{anchor}" '
                       f'fill="{INK}">{esc(ln)}</text>')
    return out


def write(name, parts):
    parts.append("</svg>")
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print("wrote", name)
    return path


def legend(p, x, y, w):
    p.append(f'<rect x="{x}" y="{y}" width="{w}" height="52" fill="none" '
             f'stroke="#999" stroke-width="1"/>')
    p += entity(x + 90, y + 26, ["External entity"], w=140, h=30)
    p += process(x + 250, y + 26, "n", ["Process"], r=22)
    p += datastore(x + 470, y + 26, "Dn", "Data store", w=190, h=30)
    p += flow([(x + 620, y + 26), (x + 690, y + 26)])
    p.append(f'<text x="{x+700}" y="{y+30}" font-size="11" fill="#333">Data flow</text>')
    p.append(f'<text x="{x+800}" y="{y+30}" font-size="10.5" fill="{MUTED}">'
             f'Yourdon / DeMarco notation. A double-headed arrow is a read and a write '
             f'on the same store.</text>')


# ════════════════════════════════════════════════════════════════
# 1. CONTEXT DIAGRAM (LEVEL 0)
# ════════════════════════════════════════════════════════════════
def context():
    W, H = 1540, 900
    p = svg_open(W, H, "StockPilot — Context Diagram (Level 0 DFD)",
                 "The whole system as a single process, with its four external entities.")

    CX, CY = W / 2, 430
    p += process(CX, CY, "0", ["StockPilot", "AI Investment", "Advisory System"], r=132)

    # external entities
    p += entity(190, 220, ["Investor"])
    p += entity(190, 640, ["Financial Analyst"])
    p += entity(1350, 220, ["Administrator"])
    p += entity(1350, 640, ["Yahoo Finance", "(market data & news)"])

    # Each flow is anchored on the circle edge facing its entity, so nothing
    # starts or ends in white space.
    def into(src, label, **kw):
        return flow([src, on_circle(CX, CY, 132, *src)], label, **kw)

    def outof(dst, label, **kw):
        return flow([on_circle(CX, CY, 132, *dst), dst], label, **kw)

    # Investor  (box x 95–285, y 189–251)
    p += into((285, 200),
              "login credentials, ticker,\nrisk profile, holdings,\ntrades, purchases, ratings",
              at=0.42, dy=-24)
    p += outof((285, 242),
               "verdict & confidence,\nfactor explanation, portfolio\nvaluation, notifications",
               at=0.58, dy=30)

    # Financial Analyst  (y 609–671)
    p += into((285, 660),
              "factor weights,\nstrategy definition,\npublication request",
              at=0.42, dy=34)
    p += outof((285, 618),
               "backtest metrics,\nthreshold checklist,\nreview status, earnings",
               at=0.58, dy=-26)

    # Administrator  (box x 1255–1445, y 189–251)
    p += into((1255, 200),
              "approval decision,\nrole & account change,\nthreshold configuration",
              at=0.42, dy=-24)
    p += outof((1255, 242),
               "platform statistics,\npending review queue,\nrevenue report",
               at=0.58, dy=30)

    # Yahoo Finance  (y 609–671)
    p += outof((1255, 660), "ticker, period\nand interval request", at=0.7, dy=32)
    p += into((1255, 618),
              "OHLCV history, live quote,\nnews headlines, fundamentals",
              at=0.38, dy=-22)

    p.append(f'<text x="{W/2}" y="{H-92}" font-size="10.5" text-anchor="middle" fill="{MUTED}">'
             f'FinBERT and the XGBoost predictor are libraries running inside the system, '
             f'not external entities. Yahoo Finance is the only external data source.</text>')
    legend(p, 60, H - 74, W - 120)
    return write("StockPilot_DFD_Context.svg", p)


# ════════════════════════════════════════════════════════════════
# 2. LEVEL 1 DFD
# ════════════════════════════════════════════════════════════════
def level1():
    """Level 1.

    Three columns — external entities, processes, data stores — with each
    entity placed beside the processes it actually talks to. Every flow is
    anchored to a computed point on the shape's perimeter, and each data-store
    access carries its true direction: read (store to process), write (process
    to store) or both.
    """
    W, H = 1660, 1580
    p = svg_open(W, H, "StockPilot — Level 1 Data Flow Diagram",
                 "Process 0 exploded into its eight major processes and eleven data stores.")

    PX, EX, DX = 700, 150, 1310
    R = 62
    EW, EH = 190, 62                   # entity box
    ER = EX + EW / 2                   # entity right edge  = 245
    DL, DR = DX - 116, DX + 116        # data store left / right edge
    BUS = 1540                         # right-hand routing bus for long flows

    procs = [
        (180, "1.0", ["Authenticate", "& Authorise"]),
        (330, "2.0", ["Manage User", "Account"]),
        (500, "3.0", ["Generate", "Investment", "Advice"]),
        (680, "4.0", ["Manage Portfolio,", "Watchlist", "& Journal"]),
        (860, "5.0", ["Evaluate", "Strategy", "(Backtest)"]),
        (1030, "6.0", ["Operate", "Strategy", "Marketplace"]),
        (1230, "7.0", ["Administer", "Platform"]),
        (1400, "8.0", ["Notify User"]),
    ]
    PY = {num: y for y, num, _ in procs}
    for y, num, lines in procs:
        p += process(PX, y, num, lines, r=R)

    stores = [
        (180, "D1", "USER"),
        (440, "D11", "STOCK / PRICE HISTORY"),
        (520, "D8", "PREDICTION"),
        (620, "D2", "HOLDING"),
        (690, "D3", "WATCHLIST"),
        (760, "D4", "TRADE"),
        (860, "D5", "STRATEGY"),
        (1000, "D6", "MARKETPLACE LISTING"),
        (1070, "D7", "MARKETPLACE RATING"),
        (1150, "D10", "PLATFORM SETTINGS"),
        (1400, "D9", "NOTIFICATION"),
    ]
    SY = {ident: y for y, ident, _ in stores}
    for y, ident, label in stores:
        p += datastore(DX, y, ident, label)

    # ── external entities, each beside the processes it uses ─────
    p += entity(EX, 300, ["Investor"])
    p += entity(EX, 600, ["Yahoo Finance"], h=54)
    p += entity(EX, 880, ["Financial Analyst"])
    p += entity(EX, 1120, ["Investor"], duplicate=True)
    p += entity(EX, 1320, ["Administrator"])

    # ── helpers: every endpoint lands on a real perimeter point ──
    def to_proc(src, num, label, **kw):
        """External entity → process."""
        dst = on_circle(PX, PY[num], R, *src)
        return flow([src, dst], label, **kw)

    def from_proc(num, dst, label, **kw):
        """Process → external entity."""
        src = on_circle(PX, PY[num], R, *dst)
        return flow([src, dst], label, **kw)

    def store(num, ident, label, direction="rw", bus=None, **kw):
        """Process ↔ data store. direction is 'read', 'write' or 'rw'."""
        sy_ = SY[ident]
        if bus:
            pe = on_circle(PX, PY[num], R, PX + R, PY[num])
            pts = [pe, (bus, PY[num]), (bus, sy_), (DR, sy_)]
            if direction == "read":
                pts = list(reversed(pts))
            return flow(pts, label, both=(direction == "rw"), **kw)
        pe = on_circle(PX, PY[num], R, DL, sy_)
        pts = [pe, (DL, sy_)]
        if direction == "read":
            pts = [(DL, sy_), pe]
        return flow(pts, label, both=(direction == "rw"), **kw)

    # ── Investor (box spans x 55–245, y 269–331) ─────────────────
    p += to_proc((ER, 280), "1.0", "login credentials", at=0.5, dy=-8)
    p += from_proc("1.0", (ER, 294), "session token & role", at=0.5, dy=13)
    p += to_proc((ER, 308), "2.0", "profile & password change", at=0.5, dy=-8)
    p += from_proc("2.0", (ER, 322), "updated profile", at=0.5, dy=14)
    p += to_proc((205, 331), "3.0", "ticker, risk profile,\nfactor weights", at=0.74, dy=-14)
    p += from_proc("3.0", (170, 331), "verdict, confidence,\nfactor breakdown",
                   at=0.30, dy=20)
    p += to_proc((125, 331), "4.0", "holdings, watchlist,\ntrades", at=0.84, dy=-13)
    p += from_proc("4.0", (85, 331), "valuation, profit / loss,\njournal analytics",
                   at=0.20, dy=22)

    # ── Yahoo Finance (y 573–627) ────────────────────────────────
    p += to_proc((ER, 586), "3.0", "OHLCV, quotes,\nheadlines, fundamentals",
                 at=0.78, dy=-10)
    p += to_proc((ER, 618), "5.0", "price history for the\nbacktest window",
                 at=0.44, dy=-10)

    # ── Financial Analyst (y 849–911) ────────────────────────────
    p += to_proc((ER, 858), "5.0", "backtest request\n(weights, period)", at=0.5, dy=-11)
    p += from_proc("5.0", (ER, 880), "metrics, equity curve,\ntrade ledger", at=0.5, dy=16)
    p += to_proc((ER, 900), "6.0", "strategy definition,\npublication request",
                 at=0.46, dy=-11)
    p += from_proc("6.0", (ER, 910), "threshold checklist,\nreview status, earnings",
                   at=0.54, dy=26)

    # ── Investor, repeated (y 1089–1151) ─────────────────────────
    p += to_proc((ER, 1100), "6.0", "purchase, rating\n& review", at=0.5, dy=-11)
    p += from_proc("6.0", (ER, 1130), "strategy catalogue", at=0.5, dy=15)
    p += flow([on_circle(PX, PY["8.0"], R, EX + 60, 1440), (EX + 60, 1440),
               (EX + 60, 1151)], "alerts", at=0.5, dy=-8)

    # ── Administrator (y 1289–1351) ──────────────────────────────
    p += to_proc((ER, 1298), "6.0", "approve / reject / remove", at=0.42, dy=-8)
    p += to_proc((ER, 1318), "7.0", "role & status change,\nthreshold values",
                 at=0.5, dy=-11)
    p += from_proc("7.0", (ER, 1342), "statistics, review\nqueue, revenue", at=0.5, dy=17)

    # ── process ↔ data store, with the real access direction ─────
    p += store("1.0", "D1", "credentials, role hash", "read")
    p += store("2.0", "D1", "profile, password hash", "rw", at=0.42, dy=15)
    p += store("3.0", "D11", "price & indicator cache", "rw", at=0.5, dy=-8)
    p += store("3.0", "D8", "prediction record", "write", at=0.5, dy=14)
    p += store("4.0", "D2", "holding", "rw", at=0.5, dy=-8)
    p += store("4.0", "D3", "watchlist entry", "rw", at=0.5, dy=-8)
    p += store("4.0", "D4", "trade record", "rw", at=0.5, dy=14)
    p += store("5.0", "D5", "factor weights", "read", at=0.5, dy=-8)
    p += store("6.0", "D5", "strategy", "rw", at=0.44, dy=-8)
    p += store("6.0", "D6", "listing & status", "rw", at=0.5, dy=-8)
    p += store("6.0", "D7", "rating & review", "rw", at=0.5, dy=14)
    p += store("6.0", "D10", "thresholds", "read", at=0.66, dy=16)
    p += store("7.0", "D6", "approve / reject /\nremove", "rw", at=0.66, dy=-14)
    p += store("7.0", "D10", "threshold values", "rw", at=0.5, dy=15)
    p += store("7.0", "D1", "role & account status", "rw", bus=BUS, at=0.5, dy=-8)
    p += store("8.0", "D9", "notification, read flag", "rw")

    # the administrator's decision is what raises a notification
    p += flow([on_circle(PX, PY["7.0"], R, PX, PY["8.0"]),
               on_circle(PX, PY["8.0"], R, PX, PY["7.0"])],
              "approval outcome", at=0.5, dx=12, anchor="start")

    legend(p, 60, H - 62, W - 120)
    return write("StockPilot_DFD_Level1.svg", p)


# ════════════════════════════════════════════════════════════════
# 3. LEVEL 2 DFD — explosion of process 3.0
# ════════════════════════════════════════════════════════════════
def level2():
    W, H = 1640, 1180
    p = svg_open(W, H, "StockPilot — Level 2 DFD: Process 3.0, Generate Investment Advice",
                 "The six-factor engine and the live XGBoost predictor, decomposed.")

    R = 58
    P = {                                    # process centres
        "3.1": (430, 250), "3.2": (430, 620), "3.3": (720, 780), "3.4": (720, 470),
        "3.5": (1010, 620), "3.6": (1290, 400), "3.7": (1010, 250), "3.8": (1290, 830),
    }
    labels = {
        "3.1": ["Authorise", "request"],
        "3.2": ["Retrieve", "market data"],
        "3.3": ["Compute 23", "technical", "indicators"],
        "3.4": ["Analyse news", "sentiment", "(FinBERT)"],
        "3.5": ["Score six", "factors,", "apply weights"],
        "3.6": ["Derive", "composite", "verdict"],
        "3.7": ["Produce model", "prediction", "(XGBoost)"],
        "3.8": ["Record", "prediction"],
    }

    p += entity(140, 250, ["Investor /", "Financial Analyst"], h=62)
    p += entity(140, 780, ["Yahoo Finance"], h=54)
    for k, (x, y) in P.items():
        p += process(x, y, k, labels[k], r=R)
    p += datastore(430, 90, "D1", "USER", w=210)
    p += datastore(760, 990, "D11", "STOCK / PRICE HISTORY", w=250)
    p += datastore(1290, 990, "D8", "PREDICTION", w=210)

    def pp(a, b, label, **kw):
        """Process → process, both ends anchored on the circle edges."""
        return flow([on_circle(*P[a], R, *P[b]), on_circle(*P[b], R, *P[a])],
                    label, **kw)

    def ep(src, b, label, **kw):
        return flow([src, on_circle(*P[b], R, *src)], label, **kw)

    def pe(a, dst, label, **kw):
        return flow([on_circle(*P[a], R, *dst), dst], label, **kw)

    # request path
    p += ep((235, 250), "3.1", "ticker, weights,\nJWT", at=0.5, dy=-12)
    p += flow([(430, 112), on_circle(*P["3.1"], R, 430, 112)], "role check", at=0.5,
              dx=8, anchor="start")
    p += pp("3.1", "3.2", "authorised\nrequest", at=0.5, dx=8, anchor="start")

    # market data
    p += ep((235, 766), "3.2", "OHLCV,\nheadlines", at=0.5, dy=-10)
    p += pp("3.2", "3.3", "price series", at=0.5, dy=-8)
    p += pp("3.2", "3.4", "6-month\nOHLCV", at=0.5, dy=-10)
    p += flow([on_circle(*P["3.3"], R, 760, 968), (760, 968)], "cache", at=0.5,
              dx=8, anchor="start", both=True)

    # scoring
    p += pp("3.3", "3.5", "momentum, volatility,\nvolume, valuation", at=0.5, dy=16)
    p += pp("3.4", "3.5", "sentiment score\n0–100", at=0.5, dy=-12)
    p += pp("3.5", "3.6", "weighted\ncomposite score", at=0.5, dy=-10)

    # model branch
    p += pp("3.1", "3.7", "ticker (live prediction path)", at=0.5, dy=-9)
    p += pp("3.7", "3.6", "signal, confidence,\nclass probabilities", at=0.5, dy=-10)

    # verdict out
    p += pp("3.6", "3.8", "BUY / HOLD / SELL\n+ confidence", at=0.45, dx=10, anchor="start")
    p += flow([on_circle(*P["3.8"], R, 1290, 968), (1290, 968)], "persist", at=0.5,
              dx=10, anchor="start")
    p += flow([on_circle(*P["3.6"], R, 140, 400), (140, 400), (140, 281)],
              "verdict, confidence and per-factor breakdown", at=0.55, dy=-9)

    p.append(f'<text x="{W/2}" y="{H-88}" font-size="10.5" text-anchor="middle" fill="{MUTED}">'
             f'Process 3.4 falls back to an on-balance-volume trend proxy when no headlines '
             f'are available. Process 3.7 loads model.pkl once per worker process.</text>')
    legend(p, 60, H - 70, W - 120)
    return write("StockPilot_DFD_Level2_Advice.svg", p)


if __name__ == "__main__":
    context()
    level1()
    level2()
    print("done")
