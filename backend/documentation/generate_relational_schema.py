"""Render StockPilot's 1NF, 2NF and 3NF relational schemas as boxed diagrams.

Style mirrors a standard relational-schema drawing: each relation is a row of
attribute cells; the primary key is underlined, foreign keys are dashed-underlined.
Emits three SVGs, one per normal form.
"""
import os
from html import escape

OUT_DIR = os.path.dirname(__file__)
FONT = "Helvetica, Arial, sans-serif"
INK = "#111827"
RULE = "#111827"
MUTED = "#6B7280"
TITLE_BLUE = "#1D4ED8"
CELL_H = 34
CHARW = 7.4          # approx width per character at 12px
PADX = 14


def esc(s):
    return escape(s, quote=False)


def cell_w(text):
    return max(72, len(text) * CHARW + PADX * 2)


def relation(x, y, name, attrs):
    """attrs: list of (label, kind, target). kind in {'pk','fk','pfk',''}.
    Returns (svg_parts, total_width, cells) where cells carries per-attribute
    geometry so referential arrows can be routed afterwards."""
    out = [f'<text x="{x}" y="{y-8}" font-size="12.5" font-weight="bold" '
           f'fill="{TITLE_BLUE}">{esc(name)}</text>']
    cells = []
    cx = x
    for label, kind, target in attrs:
        w = cell_w(label)
        out.append(f'<rect x="{cx}" y="{y}" width="{w}" height="{CELL_H}" '
                   f'fill="white" stroke="{RULE}" stroke-width="1.4"/>')
        out.append(f'<text x="{cx+w/2}" y="{y+21}" font-size="12" '
                   f'text-anchor="middle" fill="{INK}">{esc(label)}</text>')
        tw = len(label) * CHARW
        ux1, ux2, uy = cx + w/2 - tw/2, cx + w/2 + tw/2, y + 25
        if kind in ("pk", "pfk"):
            out.append(f'<line x1="{ux1}" y1="{uy}" x2="{ux2}" y2="{uy}" '
                       f'stroke="{INK}" stroke-width="1.3"/>')
        if kind in ("fk", "pfk"):
            yo = uy + (2.5 if kind == "pfk" else 0)
            out.append(f'<line x1="{ux1}" y1="{yo}" x2="{ux2}" y2="{yo}" '
                       f'stroke="{INK}" stroke-width="1.1" stroke-dasharray="3,2"/>')
        cells.append({"label": label, "kind": kind, "target": target,
                      "cx": cx + w / 2, "left": cx, "right": cx + w,
                      "top": y, "bottom": y + CELL_H})
        cx += w
    return out, cx - x, cells


def _arrow_head_right(x, y):
    """Solid arrowhead at (x, y) pointing RIGHT (into a PK cell's left edge)."""
    return [f'<polygon points="{x},{y} {x-9},{y-5} {x-9},{y+5}" fill="{RULE}"/>']


def referential_arrows(tables, x_left, lane_step):
    """Route FK -> PK connectors through the LEFT gutter.

    Each foreign-key cell drops into the gap below its row, runs left to its own
    vertical lane in the margin, travels to the referenced table, and enters that
    table's primary-key cell from the LEFT edge (a short approach, since every PK
    is the leftmost cell). The arrowhead marks the 'one' side of the relationship.
    """
    pk_anchor = {}
    fks = []
    for name, cells in tables.items():
        for c in cells:
            if c["kind"] in ("pk", "pfk") and name not in pk_anchor:
                pk_anchor[name] = c
            if c["kind"] in ("fk", "pfk") and c["target"]:
                fks.append((name, c))

    seen = {}
    out = []
    for i, (src, c) in enumerate(fks):
        tgt = pk_anchor.get(c["target"])
        if not tgt:
            continue
        lane = x_left - 26 - i * lane_step
        sx, sy = c["cx"], c["bottom"]
        gy = c["bottom"] + 14
        total = sum(1 for _, cc in fks if cc["target"] == c["target"])
        k = seen.get(c["target"], 0)
        seen[c["target"]] = k + 1
        ty = tgt["top"] + (k + 1) * CELL_H / (total + 1)
        tx = tgt["left"]
        pts = [(sx, sy), (sx, gy), (lane, gy), (lane, ty), (tx - 1, ty)]
        d = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
        out.append(f'<polyline points="{d}" fill="none" stroke="{MUTED}" '
                   f'stroke-width="1.2"/>')
        out += _arrow_head_right(tx - 1, ty)
    return out


def svg(title, subtitle, rows, note=None):
    """rows: list of relation dicts, stacked one per row in a single column."""
    # size the left gutter from the number of FK connectors
    n_fk = sum(1 for r in rows for (_, k, t) in r["attrs"]
               if k in ("fk", "pfk") and t)
    lane_step = 15
    x_left = 60 + n_fk * lane_step

    body = []
    y = 128
    row_gap = 66
    max_right = 0
    tables = {}
    for r in rows:
        p, w, cells = relation(x_left, y, r["name"], r["attrs"])
        body += p
        tables[r["name"]] = cells
        max_right = max(max_right, x_left + w)
        y += CELL_H + row_gap

    arrows = referential_arrows(tables, x_left, lane_step)
    body = arrows + body            # connectors drawn under the boxes

    W = int(max(1400, max_right + 40))
    H = y + 20
    if note:
        H += 20 + len(note) * 15

    head = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" font-family="{FONT}">',
            f'<rect width="{W}" height="{H}" fill="white"/>',
            f'<text x="{W/2}" y="40" font-size="20" font-weight="bold" '
            f'text-anchor="middle" fill="{INK}">{esc(title)}</text>',
            f'<text x="{W/2}" y="62" font-size="11.5" text-anchor="middle" '
            f'fill="{MUTED}">{esc(subtitle)}</text>',
            # legend
            f'<text x="46" y="92" font-size="10.5" fill="{MUTED}">'
            f'Underline = primary key      Dashed underline = foreign key</text>']
    parts = head + body
    if note:
        base = H - len(note) * 15 - 10
        for i, ln in enumerate(note):
            parts.append(f'<text x="46" y="{base+i*15}" font-size="10.5" '
                         f'fill="#333">{esc(ln)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def write(name, content):
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", os.path.basename(path))
    return path


# ────────────────────────────────────────────────────────────────
# attribute helper: "attr" plain, "attr!" pk, "attr*" fk, "attr#" pk+fk
# ────────────────────────────────────────────────────────────────
def A(spec):
    """Mini-language per attribute, comma-separated:
        name           plain attribute
        name!          primary key
        name#          part of a composite primary key (no FK)
        name*TARGET     foreign key -> TARGET table
        name#TARGET     part of PK AND a foreign key -> TARGET table
    """
    out = []
    for tok in spec.split(","):
        t = tok.strip()
        if "#" in t:
            base, _, target = t.partition("#")
            out.append((base, "pfk" if target else "pk", target or None))
        elif "*" in t:
            base, _, target = t.partition("*")
            out.append((base, "fk", target or None))
        elif t.endswith("!"):
            out.append((t[:-1], "pk", None))
        else:
            out.append((t, "", None))
    return out


# ════════════════════════════════════════════════════════════════
# 1NF
# ════════════════════════════════════════════════════════════════
def nf1():
    rows = [
        {"name": "USER", "attrs": A("user_id!, email, password_hash, full_name, role, phone, bio, is_active")},
        {"name": "HOLDING_USER_STOCK  (partial deps)",
         "attrs": A("user_id#, ticker#, quantity, avg_cost, current_price, user_full_name, user_email, stock_name, stock_sector")},
        {"name": "WATCHLIST", "attrs": A("user_id#, ticker#, added_at")},
        {"name": "TRADE", "attrs": A("trade_id!, user_id*USER, ticker, side, quantity, entry_price, exit_price, strategy_label, notes")},
        {"name": "STRATEGY_LISTING  (transitive deps)",
         "attrs": A("listing_id!, strategy_id, owner_id*USER, name, price_cents, status, sales_count, owner_full_name, owner_email")},
        {"name": "LISTING_RATING  (partial deps)",
         "attrs": A("listing_id#, user_id#, rating, review, created_at, price_cents, status")},
        {"name": "PREDICTION", "attrs": A("prediction_id!, ticker, signal, confidence, probability_up, probability_down, composite_score, model_version")},
        {"name": "NOTIFICATION", "attrs": A("notif_id!, user_id*USER, title, body, kind, is_read, created_at")},
        {"name": "PLATFORM_SETTINGS", "attrs": A("id!, min_trades, min_winrate, min_sharpe, max_drawdown, min_profit_factor")},
    ]
    note = [
        "Atomic values only, no repeating groups, every relation has a key. But composite-key relations "
        "(HOLDING_USER_STOCK, LISTING_RATING) hold attributes that depend on only PART of the key -> 2NF violation;",
        "STRATEGY_LISTING holds owner_full_name / owner_email that depend on owner_id, a non-key attribute -> 3NF violation.",
    ]
    return write("StockPilot_Schema_1NF.svg",
                 svg("StockPilot — Relational Schema (1NF)",
                     "First Normal Form: atomic attributes, keys defined, redundancy still present.",
                     rows, note))


# ════════════════════════════════════════════════════════════════
# 2NF
# ════════════════════════════════════════════════════════════════
def nf2():
    rows = [
        {"name": "USER", "attrs": A("user_id!, email, password_hash, full_name, role, phone, bio, is_active")},
        {"name": "STOCK", "attrs": A("ticker!, stock_name, stock_sector")},
        {"name": "HOLDING", "attrs": A("holding_id!, user_id*USER, ticker*STOCK, quantity, avg_cost, current_price, opened_at")},
        {"name": "WATCHLIST", "attrs": A("watch_id!, user_id*USER, ticker*STOCK, added_at")},
        {"name": "TRADE", "attrs": A("trade_id!, user_id*USER, ticker*STOCK, side, quantity, entry_price, exit_price, strategy_label")},
        {"name": "STRATEGY_LISTING  (still transitive)",
         "attrs": A("listing_id!, strategy_id, owner_id*USER, name, price_cents, status, sales_count, owner_full_name, owner_email")},
        {"name": "MARKETPLACE_RATING  (surrogate key)",
         "attrs": A("rating_id!, listing_id*STRATEGY_LISTING, user_id*USER, rating, review, created_at")},
        {"name": "PREDICTION", "attrs": A("prediction_id!, ticker*STOCK, signal, confidence, probability_up, probability_down, composite_score")},
        {"name": "NOTIFICATION", "attrs": A("notif_id!, user_id*USER, title, body, kind, is_read, created_at")},
        {"name": "PLATFORM_SETTINGS", "attrs": A("id!, min_trades, min_winrate, min_sharpe, max_drawdown, min_profit_factor")},
    ]
    note = [
        "Partial dependencies removed: STOCK split out; HOLDING / WATCHLIST / TRADE given surrogate keys; RATING given a surrogate key.",
        "Remaining problem: STRATEGY_LISTING mixes strategy and listing data, and owner_full_name / owner_email still depend "
        "transitively on owner_id -> resolved in 3NF.",
    ]
    return write("StockPilot_Schema_2NF.svg",
                 svg("StockPilot — Relational Schema (2NF)",
                     "Second Normal Form: no partial dependencies on part of a composite key.",
                     rows, note))


# ════════════════════════════════════════════════════════════════
# 3NF
# ════════════════════════════════════════════════════════════════
def nf3():
    rows = [
        {"name": "USER", "attrs": A("user_id!, email, password_hash, full_name, role, phone, bio, avatar_url, is_active, created_at, updated_at")},
        {"name": "STOCK", "attrs": A("ticker!, name, sector")},
        {"name": "PRICE_HISTORY", "attrs": A("ticker#STOCK, date#, open, high, low, close, volume")},
        {"name": "HOLDING", "attrs": A("holding_id!, user_id*USER, ticker*STOCK, quantity, avg_cost, current_price, opened_at, closed_at")},
        {"name": "WATCHLIST", "attrs": A("watch_id!, user_id*USER, ticker*STOCK, added_at")},
        {"name": "TRADE", "attrs": A("trade_id!, user_id*USER, ticker*STOCK, side, quantity, entry_price, exit_price, stop_loss, take_profit, strategy_label, notes")},
        {"name": "STRATEGY", "attrs": A("strategy_id!, owner_id*USER, name, description, weights, is_preset, is_published, created_at, updated_at")},
        {"name": "MARKETPLACE_LISTING", "attrs": A("listing_id!, strategy_id*STRATEGY, price_cents, status, sales_count, avg_rating, rating_count, listed_at, backtest_return, backtest_sharpe, backtest_winrate")},
        {"name": "MARKETPLACE_RATING", "attrs": A("rating_id!, listing_id*MARKETPLACE_LISTING, user_id*USER, rating, review, created_at")},
        {"name": "PREDICTION", "attrs": A("prediction_id!, ticker*STOCK, signal, confidence, probability_up, probability_down, composite_score, model_version, created_at")},
        {"name": "NOTIFICATION", "attrs": A("notif_id!, user_id*USER, title, body, kind, is_read, created_at")},
        {"name": "PLATFORM_SETTINGS", "attrs": A("id!, min_trades, min_winrate, min_sharpe, max_drawdown, min_profit_factor")},
    ]
    note = [
        "Transitive dependencies removed: STRATEGY (authoring) separated from MARKETPLACE_LISTING (sale); owner details live only in USER.",
        "Every non-key attribute now depends on the key, the whole key, and nothing but the key. This is the implemented schema.",
        "avg_rating / rating_count are kept on the listing as a deliberate derived cache (controlled denormalisation).",
    ]
    return write("StockPilot_Schema_3NF.svg",
                 svg("StockPilot — Relational Schema (3NF) — Implemented",
                     "Third Normal Form: no transitive dependencies. Final database schema.",
                     rows, note))


if __name__ == "__main__":
    nf1()
    nf2()
    nf3()
    print("done")
