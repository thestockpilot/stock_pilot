"""Generate the StockPilot site map as SVG.

The structure is taken from the actual application:
    routes            Frontend/src/routes/AppRouter.jsx
    navigation        Frontend/src/components/layout/Header.jsx
    in-page sections  the card / tab titles inside each screen component

StockPilot is a single-page application, so "pages" are client-side routes and
"sub-pages" are tabs or panels within a route rather than separate URLs. Tabs
that are addressable by query string are shown with their parameter.
"""
import os
from html import escape

OUT_DIR = os.path.dirname(__file__)
FONT = "Helvetica, Arial, sans-serif"
INK = "#111111"
MUTED = "#555555"
RULE = "#111111"

LH = 15.5           # line height inside a card
PAD_TOP = 52        # first body line, relative to the card top
CARD_W = 402
COL_X = [46, 486, 926, 1366]


def esc(s):
    return escape(s, quote=False)


# ────────────────────────────────────────────────────────────────
# primitives
# ────────────────────────────────────────────────────────────────
def card_height(lines, roles=None):
    return PAD_TOP + len(lines) * LH + 12 + (12 if roles else 0)


def card(x, y, title, path, lines, roles=None, w=CARD_W, accent=True):
    """A route card. `lines` entries starting with '#' are sub-headings."""
    h = card_height(lines, roles)
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="white" '
           f'stroke="{RULE}" stroke-width="1.8"/>']
    if accent:
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="30" rx="4" fill="#eeeeee"/>')
        out.append(f'<rect x="{x}" y="{y+22}" width="{w}" height="8" fill="#eeeeee"/>')
        out.append(f'<line x1="{x}" y1="{y+30}" x2="{x+w}" y2="{y+30}" '
                   f'stroke="{RULE}" stroke-width="1.8"/>')
    out.append(f'<text x="{x+11}" y="{y+20}" font-size="12.5" font-weight="bold" '
               f'fill="{INK}">{esc(title)}</text>')
    if path:
        out.append(f'<text x="{x+w-11}" y="{y+20}" font-size="11" text-anchor="end" '
                   f'font-family="Consolas, monospace" fill="{MUTED}">{esc(path)}</text>')
    if roles:
        out += role_chips(x + 11, y + 47, roles)

    body_y = y + PAD_TOP + (12 if roles else 0)
    for i, ln in enumerate(lines):
        ty = body_y + i * LH
        if ln.startswith("#"):
            out.append(f'<text x="{x+11}" y="{ty}" font-size="10" font-weight="bold" '
                       f'fill="{INK}">{esc(ln[1:].strip())}</text>')
        elif ln.strip() == "":
            continue
        else:
            out.append(f'<text x="{x+17}" y="{ty}" font-size="10" fill="#222">'
                       f'•  {esc(ln)}</text>')
    return out, h + (4 if roles else 0)


ROLE_LABEL = {"I": "Investor", "A": "Analyst", "D": "Admin"}


def role_chips(x, y, roles):
    out = []
    for i, r in enumerate(roles):
        cx = x + i * 30
        out.append(f'<rect x="{cx}" y="{y-11}" width="26" height="15" rx="7.5" '
                   f'fill="white" stroke="{RULE}" stroke-width="1.1"/>')
        out.append(f'<text x="{cx+13}" y="{y}" font-size="9.5" text-anchor="middle" '
                   f'font-weight="bold" fill="{INK}">{r}</text>')
    return out


def band(x, y, w, h, label, dashed=True):
    dash = ' stroke-dasharray="8,5"' if dashed else ""
    return [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="none" '
            f'stroke="{RULE}" stroke-width="1.6"{dash}/>',
            f'<rect x="{x+16}" y="{y-9}" width="{9.2*len(label)+16}" height="18" fill="white"/>',
            f'<text x="{x+24}" y="{y+4}" font-size="12.5" font-weight="bold" '
            f'fill="{INK}">{esc(label)}</text>']


def connector(x1, y1, x2, y2, label=None):
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{RULE}" stroke-width="1.5"/>']
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        out.append(f'<rect x="{mx - 4.2*len(label)}" y="{my-17}" '
                   f'width="{8.4*len(label)}" height="14" fill="white"/>')
        out.append(f'<text x="{mx}" y="{my-6}" font-size="9.5" text-anchor="middle" '
                   f'fill="{MUTED}">{esc(label)}</text>')
    return out


def arrow_head(x, y, direction="right"):
    if direction == "right":
        pts = f"{x},{y} {x-9},{y-5} {x-9},{y+5}"
    else:
        pts = f"{x},{y} {x-5},{y-9} {x+5},{y-9}"
    return [f'<polygon points="{pts}" fill="{RULE}"/>']


# ────────────────────────────────────────────────────────────────
# content — mirrors the shipped application
# ────────────────────────────────────────────────────────────────
DASHBOARD = [
    "#Common to every role",
    "Market indices strip (S&P 500, Nasdaq, Dow, VIX)",
    "Watchlist panel — click through to Advisor",
    "Featured strategy — click through to Marketplace",
    "",
    "#Investor view  (InvestorDashboard)",
    "Stats: total value, today P/L, unrealised P/L,",
    "open positions, AI says BUY",
    "Portfolio performance (line)",
    "Allocation (doughnut) · Sector breakdown",
    "Recent activity — latest journal trades",
    "",
    "#Analyst view  (AnalystDashboard)",
    "Stats: total earnings, published, awaiting review,",
    "strategies created, average rating",
    "My strategies — status of every authored strategy",
    "Best performer",
    "",
    "#Admin view  (AdminDashboard)",
    "Platform stats: users, strategies, listings, revenue",
    "Awaiting review queue",
    "Quick actions → /admin tabs",
]

ADVISOR = [
    "Analysis configuration — ticker, risk tolerance,",
    "time horizon, preset or custom factor weights",
    "Verdict hero — BUY / HOLD / SELL + confidence",
    "  live XGBoost result, MODEL LIVE badge",
    "Trading chart — candle / line, 1D…1Y timeframes",
    "52-week range · Action plan",
    "Factor contribution (bars) · Factor radar",
    "News sentiment (FinBERT)",
    "Backtest performance — period tabs, vectorbt run,",
    "  metrics, equity curve, Download log (CSV)",
    "Fundamentals · Signal comparison",
    "Save as strategy → /marketplace",
]

MARKETPLACE = [
    "Filter tabs — all / verified / listed / mine",
    "Sort — rating, price, sales",
    "My strategies",
    "Available strategies — cards with backtest report",
    "Strategy detail — weights, metrics, ratings",
    "Buy · Rate and review",
    "",
    "#For analysts only",
    "Request to publish — dialog with live backtest,",
    "  price, per-threshold pass/fail checklist",
    "  POST /strategies/{id}/publish  → status 'review'",
]

PORTFOLIO = [
    "Stats: total value, cost basis, P/L, watchlist size",
    "Holdings table — sortable by symbol, price,",
    "  market value, P/L, %",
    "Add holding · Edit holding · Delete holding",
    "Portfolio value (line)",
    "Sector exposure · Allocation",
    "Verdict summary — AI signal per holding",
    "Watchlist — add and remove tickers",
]

JOURNAL = [
    "Stats: win rate, total P/L, trade count, best trade",
    "Equity curve",
    "Monthly profit / loss",
    "Outcomes — win / loss distribution",
    "By strategy",
    "Drawdown",
    "Trade history table",
    "Log trade · Edit trade · Delete trade",
]

SETTINGS = [
    "#Profile          ?tab=profile",
    "Name, email, phone, bio",
    "",
    "#Security         ?tab=security",
    "Change password",
    "",
    "#Notifications    ?tab=notifications",
    "Verdict changes, news sentiment, price alerts,",
    "marketplace updates, weekly report, product news",
]

ADMIN = [
    "Platform stats: users, strategies, listings, revenue",
    "",
    "#Revenue",
    "Sales and earnings per listing",
    "",
    "#Pending Reviews  (badge = queue size)",
    "Backtest report, factor weights, Approve / Reject",
    "",
    "#Listings",
    "All listings, Remove from any state",
    "",
    "#Strategies",
    "Every strategy on the platform, Delete",
    "",
    "#Users",
    "Change role, Suspend / reactivate account",
    "",
    "#Thresholds",
    "Min trades, win rate, Sharpe, max drawdown,",
    "min profit factor — applies platform-wide",
]

AUTH = [
    "#Sign in",
    "Email + password → access and refresh JWT",
    "",
    "#Sign up",
    "Name, email, password → role defaults to investor",
    "",
    "Authenticated visitor is redirected to /",
]


def build():
    rows = [
        [("Dashboard", "/", DASHBOARD, ["I", "A", "D"]),
         ("Stock Analysis", "/advisor", ADVISOR, ["I", "A", "D"]),
         ("Strategy Marketplace", "/marketplace", MARKETPLACE, ["I", "A", "D"]),
         ("Portfolio", "/portfolio", PORTFOLIO, ["I", "A", "D"])],
        [("Trading Journal", "/journal", JOURNAL, ["I", "A", "D"]),
         ("Settings", "/settings", SETTINGS, ["I", "A", "D"]),
         ("Admin Console", "/admin", ADMIN, ["D"]),
         (None, None, None, None)],
    ]

    # geometry derived from the content so there is no dead space
    PUB_Y, PUB_H = 104, 214
    BAND_Y = PUB_Y + PUB_H + 26
    ROW_Y = BAND_Y + 36
    row_h = [max(card_height(l, r) for _, _, l, r in row if l) for row in rows]
    BAND_H = 36 + row_h[0] + 34 + row_h[1] + 30
    W = 1815
    H = BAND_Y + BAND_H + 72

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="{FONT}">',
         f'<rect width="{W}" height="{H}" fill="white"/>',
         f'<text x="{W/2}" y="36" font-size="21" font-weight="bold" text-anchor="middle" '
         f'fill="{INK}">StockPilot — Site Map</text>',
         f'<text x="{W/2}" y="58" font-size="11.5" text-anchor="middle" fill="{MUTED}">'
         f'Single-page application. Boxes are client-side routes; bullets are panels or '
         f'tabs within a route. Role chips show who sees the route in the navigation — '
         f'the API authorises every request independently.</text>']

    # ── entry ────────────────────────────────────────────────────
    p += band(46, PUB_Y, 866, PUB_H, "PUBLIC — no token")
    auth_parts, _ = card(70, 126, "Authentication", "/auth", AUTH, w=380)
    p += auth_parts

    p.append(f'<rect x="486" y="126" width="402" height="128" rx="4" fill="white" '
             f'stroke="{RULE}" stroke-width="1.4"/>')
    p.append(f'<text x="497" y="146" font-size="12" font-weight="bold" fill="{INK}">'
             f'Route guards</text>')
    for i, ln in enumerate([
        "AuthRoute      token present    → redirect /",
        "ProtectedRoute no token         → redirect /auth",
        "AdminRoute     role ≠ admin      → redirect /",
        "*              unknown path     → redirect /",
    ]):
        p.append(f'<text x="497" y="{170+i*17}" font-size="9.8" '
                 f'font-family="Consolas, monospace" fill="#222">{esc(ln)}</text>')

    p += connector(912, 190, 1090, 190)
    p += arrow_head(1090, 190)
    p.append(f'<rect x="946" y="168" width="110" height="14" fill="white"/>')
    p.append(f'<text x="1001" y="179" font-size="9.5" text-anchor="middle" fill="{MUTED}">'
             f'valid session</text>')

    # ── persistent shell ─────────────────────────────────────────
    p.append(f'<rect x="1110" y="126" width="660" height="128" rx="4" fill="white" '
             f'stroke="{RULE}" stroke-width="1.8"/>')
    p.append(f'<rect x="1110" y="126" width="660" height="30" rx="4" fill="#eeeeee"/>')
    p.append(f'<rect x="1110" y="148" width="660" height="8" fill="#eeeeee"/>')
    p.append(f'<line x1="1110" y1="156" x2="1770" y2="156" stroke="{RULE}" stroke-width="1.8"/>')
    p.append(f'<text x="1121" y="146" font-size="12.5" font-weight="bold" fill="{INK}">'
             f'Persistent shell — Layout + Header</text>')
    p.append(f'<text x="1759" y="146" font-size="11" text-anchor="end" '
             f'font-family="Consolas, monospace" fill="{MUTED}">every route below</text>')
    for i, ln in enumerate([
        "Logo → /   ·   Nav tabs (filtered by role)",
        "Notifications dropdown — mark read, mark all read,",
        "   Notification settings → /settings?tab=notifications",
        "User menu — My profile, Settings, Sign out",
    ]):
        p.append(f'<text x="1127" y="{178+i*17}" font-size="10" fill="#222">'
                 f'{"•  " if not ln.startswith("   ") else "   "}{esc(ln.strip())}</text>')

    # ── authenticated band ───────────────────────────────────────
    p += band(46, BAND_Y, 1724, BAND_H, "AUTHENTICATED — ProtectedRoute + Layout")

    y = ROW_Y
    for ri, row in enumerate(rows):
        for col, (title, path, lines, roles) in enumerate(row):
            if title is None:
                continue
            parts, _ = card(COL_X[col], y, title, path, lines, roles=roles)
            p += parts
        if ri == 0:
            y += row_h[0] + 34

    # notes fill the empty fourth slot of the second row
    ny = y
    p.append(f'<rect x="{COL_X[3]}" y="{ny}" width="{CARD_W}" height="152" rx="4" '
             f'fill="white" stroke="{RULE}" stroke-width="1.4" stroke-dasharray="6,4"/>')
    p.append(f'<text x="{COL_X[3]+13}" y="{ny+24}" font-size="12" font-weight="bold" '
             f'fill="{INK}">Notes</text>')
    for i, ln in enumerate([
        "One route, three dashboards: RoleDashboard reads",
        "user.role and lazy-loads the matching component.",
        "An unknown role falls back to the investor view.",
        "",
        "The Admin tab is hidden for non-admins and the",
        "route additionally redirects; the API rejects the",
        "call with 403 even if the guard is bypassed.",
    ]):
        p.append(f'<text x="{COL_X[3]+13}" y="{y-34-216+i*16}" font-size="9.8" fill="#333">'
                 f'{esc(ln)}</text>')

    # ── legend ───────────────────────────────────────────────────
    ly = H - 34
    p.append(f'<rect x="46" y="{ly-26}" width="1724" height="40" rx="4" fill="none" '
             f'stroke="#999" stroke-width="1"/>')
    p.append(f'<text x="66" y="{ly-1}" font-size="10.5" font-weight="bold" fill="{INK}">'
             f'Role chips</text>')
    x = 150
    for k, v in ROLE_LABEL.items():
        p += role_chips(x, ly - 1, [k])
        p.append(f'<text x="{x+32}" y="{ly-1}" font-size="10.5" fill="#333">{esc(v)}</text>')
        x += 150
    p.append(f'<text x="{x+40}" y="{ly-1}" font-size="10.5" fill="#333">'
             f'Solid box = client-side route  ·  bullet = panel or tab within that route  '
             f'·  ?tab= = deep-linkable</text>')

    p.append("</svg>")
    path = os.path.join(OUT_DIR, "StockPilot_SiteMap.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(p))
    print("wrote", os.path.basename(path))
    return path


if __name__ == "__main__":
    build()
    print("done")
