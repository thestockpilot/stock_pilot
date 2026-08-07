"""Generate the StockPilot frontend site map as a classic top-down tree.

Level 0  entry point (black)      /auth
Level 1  primary navigation (blue)  the routes in Header.jsx
Level 2  screen sections (green)     panels and tabs within each route

Structure taken from Frontend/src/routes/AppRouter.jsx and the section titles
inside each screen component.
"""
import os
from html import escape

OUT_DIR = os.path.dirname(__file__)
FONT = "Helvetica, Arial, sans-serif"

BLACK = "#111827"
BLUE = "#2F6BEA"
GREEN = "#16A34A"
GREEN_DIM = "#4B9E6B"     # admin-only branch, visually distinct but same family
LINE = "#2F6BEA"
LINE_G = "#16A34A"

COL_PITCH = 252
ROOT_Y = 92
L1_Y = 210
L1_W, L1_H = 196, 56
L2_W, L2_H = 188, 50
L2_GAP = 14
L2_TOP = 320


def esc(s):
    return escape(s, quote=False)


def box(x, y, w, h, label, fill, sub=None, fs=13.5):
    """Filled rectangle with centred white label; `label` may contain a newline."""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>']
    lines = label.split("\n")
    if sub:
        total = len(lines) * (fs + 2) + 12
        start = y + (h - total) / 2 + fs
    else:
        start = y + (h - len(lines) * (fs + 2)) / 2 + fs
    for i, ln in enumerate(lines):
        out.append(f'<text x="{x+w/2}" y="{start + i*(fs+2)}" font-size="{fs}" '
                   f'font-weight="bold" text-anchor="middle" fill="white">{esc(ln)}</text>')
    if sub:
        out.append(f'<text x="{x+w/2}" y="{start + len(lines)*(fs+2) + 3}" font-size="10" '
                   f'text-anchor="middle" fill="#FFFFFF" opacity="0.78" '
                   f'font-family="Consolas, monospace">{esc(sub)}</text>')
    return out


# ────────────────────────────────────────────────────────────────
# content
# ────────────────────────────────────────────────────────────────
COLUMNS = [
    ("Dashboard", "/", [
        "Investor View", "Analyst View", "Admin View",
        "Market Indices", "Watchlist", "Featured\nStrategy",
    ], False),
    ("Advisor", "/advisor", [
        "Analysis Config", "AI Verdict", "Trading Chart",
        "Factor\nBreakdown", "News Sentiment", "Backtest",
        "Fundamentals", "Save Strategy",
    ], False),
    ("Marketplace", "/marketplace", [
        "Browse\nStrategies", "My Strategies", "Strategy Detail",
        "Buy & Rate", ("Request\nPublish", "analyst role only"),
    ], False),
    ("Portfolio", "/portfolio", [
        "Holdings", "Add Holding", "Performance",
        "Allocation", "Sector\nExposure", "Watchlist",
    ], False),
    ("Journal", "/journal", [
        "Log Trade", "Trade History", "Equity Curve",
        "Monthly\nProfit / Loss", "By Strategy", "Drawdown",
    ], False),
    ("Settings", "/settings", [
        "Profile", "Security", "Notifications",
    ], False),
    ("Admin", "/admin", [
        "Revenue", "Pending\nReviews", "Listings",
        "Strategies", "Users", "Thresholds",
    ], True),
]


def build():
    n = len(COLUMNS)
    W = n * COL_PITCH + 96
    max_children = max(len(c[2]) for c in COLUMNS)
    H = L2_TOP + max_children * (L2_H + L2_GAP) + 78

    centres = [48 + COL_PITCH / 2 + i * COL_PITCH for i in range(n)]

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="{FONT}">',
         f'<rect width="{W}" height="{H}" fill="white"/>',
         f'<text x="40" y="44" font-size="20" font-weight="bold" fill="{BLACK}">'
         f'STOCKPILOT — FRONTEND SITE MAP</text>',
         f'<text x="40" y="66" font-size="11.5" fill="#6B7280">'
         f'Entry point, primary navigation and the sections within each screen.</text>']

    # ── root ─────────────────────────────────────────────────────
    root_x = W / 2 - 118
    p += box(root_x, ROOT_Y, 236, 60, "Login / Sign Up", BLACK, sub="/auth")

    # bus from the root down to every level-1 box
    bus_y = ROOT_Y + 60 + 32
    p.append(f'<line x1="{W/2}" y1="{ROOT_Y+60}" x2="{W/2}" y2="{bus_y}" '
             f'stroke="{LINE}" stroke-width="2.2"/>')
    p.append(f'<line x1="{centres[0]}" y1="{bus_y}" x2="{centres[-1]}" y2="{bus_y}" '
             f'stroke="{LINE}" stroke-width="2.2"/>')

    for i, (label, path, children, restricted) in enumerate(COLUMNS):
        cx = centres[i]
        p.append(f'<line x1="{cx}" y1="{bus_y}" x2="{cx}" y2="{L1_Y}" '
                 f'stroke="{LINE}" stroke-width="2.2"/>')
        p += box(cx - L1_W / 2, L1_Y, L1_W, L1_H, label, BLUE, sub=path)
        if restricted:
            p.append(f'<text x="{cx}" y="{L1_Y+L1_H+15}" font-size="9.5" '
                     f'text-anchor="middle" fill="#B91C1C" font-weight="bold">'
                     f'admin role only</text>')

        # elbow spine down the left of the child column
        colour = GREEN_DIM if restricted else GREEN
        spine_x = cx - L1_W / 2 + 22
        last_y = L2_TOP + (len(children) - 1) * (L2_H + L2_GAP) + L2_H / 2
        p.append(f'<line x1="{spine_x}" y1="{L1_Y+L1_H}" x2="{spine_x}" y2="{last_y}" '
                 f'stroke="{colour}" stroke-width="2.2"/>')

        for j, ch in enumerate(children):
            note = None
            if isinstance(ch, tuple):
                ch, note = ch
            y = L2_TOP + j * (L2_H + L2_GAP)
            mid = y + L2_H / 2
            bx = cx - L2_W / 2 + 26
            p.append(f'<line x1="{spine_x}" y1="{mid}" x2="{bx}" y2="{mid}" '
                     f'stroke="{colour}" stroke-width="2.2"/>')
            p += box(bx, y, L2_W, L2_H, ch, colour, fs=12)
            if note:
                p.append(f'<text x="{bx+L2_W/2}" y="{y+L2_H+13}" font-size="9.5" '
                         f'text-anchor="middle" fill="#B91C1C" font-weight="bold">'
                         f'{esc(note)}</text>')

    # ── legend ───────────────────────────────────────────────────
    ly = H - 34
    items = [("Entry point", BLACK), ("Primary navigation", BLUE), ("Screen section", GREEN)]
    x = 44
    for label, colour in items:
        p.append(f'<rect x="{x}" y="{ly-13}" width="22" height="16" fill="{colour}"/>')
        p.append(f'<text x="{x+31}" y="{ly}" font-size="11.5" fill="#374151">{esc(label)}</text>')
        x += 42 + len(label) * 7.2
    p.append(f'<text x="{x+30}" y="{ly}" font-size="11.5" fill="#6B7280">'
             f'All navigation below the entry point requires a valid session; '
             f'the API authorises every request independently.</text>')

    p.append("</svg>")
    path = os.path.join(OUT_DIR, "StockPilot_SiteMap_Tree.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(p))
    print("wrote", os.path.basename(path))
    return path


if __name__ == "__main__":
    build()
    print("done")
