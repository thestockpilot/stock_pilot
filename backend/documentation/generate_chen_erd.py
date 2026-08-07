"""Generate Chen-notation ERD and normalisation diagrams for StockPilot.

Chen notation:
    rectangle       entity
    diamond         relationship
    ellipse         attribute (primary-key attributes are underlined)
    double ellipse  multivalued attribute
    line label      cardinality (1, N, M)

Rendered as plain SVG so no Graphviz/Java toolchain is required.
"""
import math
import os
from html import escape

OUT_DIR = os.path.dirname(__file__)

FONT = "Helvetica, Arial, sans-serif"
INK = "#111111"
LINE = "#111111"


# ────────────────────────────────────────────────────────────────
# primitives
# ────────────────────────────────────────────────────────────────
def svg_open(w, h, title):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="{FONT}">',
        f'<rect width="{w}" height="{h}" fill="white"/>',
        f'<text x="{w/2}" y="34" font-size="19" font-weight="bold" '
        f'text-anchor="middle" fill="{INK}">{escape(title)}</text>',
    ]


def svg_close(parts):
    parts.append("</svg>")
    return "\n".join(parts)


def entity(x, y, label, w=132, h=44, weak=False):
    """Rectangle. A weak entity gets a double border."""
    out = [f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" '
           f'fill="white" stroke="{LINE}" stroke-width="2"/>']
    if weak:
        out.append(f'<rect x="{x-w/2+5}" y="{y-h/2+5}" width="{w-10}" height="{h-10}" '
                   f'fill="none" stroke="{LINE}" stroke-width="1.4"/>')
    out.append(f'<text x="{x}" y="{y+5}" font-size="13" font-weight="bold" '
               f'text-anchor="middle" fill="{INK}">{escape(label)}</text>')
    return out


def relationship(x, y, label, w=112, h=58, identifying=False):
    """Diamond."""
    pts = f"{x},{y-h/2} {x+w/2},{y} {x},{y+h/2} {x-w/2},{y}"
    out = [f'<polygon points="{pts}" fill="white" stroke="{LINE}" stroke-width="2"/>']
    if identifying:
        iw, ih = w - 14, h - 14
        ipts = f"{x},{y-ih/2} {x+iw/2},{y} {x},{y+ih/2} {x-iw/2},{y}"
        out.append(f'<polygon points="{ipts}" fill="none" stroke="{LINE}" stroke-width="1.3"/>')
    out.append(f'<text x="{x}" y="{y+4}" font-size="11.5" text-anchor="middle" '
               f'fill="{INK}">{escape(label)}</text>')
    return out


def attribute(x, y, label, pk=False, rx=54, ry=19, multivalued=False, derived=False):
    """Ellipse. Primary-key attributes are underlined."""
    dash = ' stroke-dasharray="4,3"' if derived else ""
    out = [f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="white" '
           f'stroke="{LINE}" stroke-width="1.5"{dash}/>']
    if multivalued:
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx-5}" ry="{ry-4}" fill="none" '
                   f'stroke="{LINE}" stroke-width="1.1"/>')
    out.append(f'<text x="{x}" y="{y+4}" font-size="10.5" text-anchor="middle" '
               f'fill="{INK}">{escape(label)}</text>')
    if pk:
        # Drawn as an explicit line rather than text-decoration, which some SVG
        # renderers ignore.
        half = len(label) * 2.75
        out.append(f'<line x1="{x-half}" y1="{y+6.5}" x2="{x+half}" y2="{y+6.5}" '
                   f'stroke="{INK}" stroke-width="1.1"/>')
    return out


def line(x1, y1, x2, y2, label=None, lw=1.5, offset=0.5, dx=0, dy=-5):
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{LINE}" stroke-width="{lw}"/>']
    if label:
        mx = x1 + (x2 - x1) * offset + dx
        my = y1 + (y2 - y1) * offset + dy
        out.append(f'<rect x="{mx-11}" y="{my-11}" width="22" height="16" fill="white" stroke="none"/>')
        out.append(f'<text x="{mx}" y="{my+1}" font-size="12" font-weight="bold" '
                   f'text-anchor="middle" fill="{INK}">{escape(label)}</text>')
    return out


def attrs_around(parts, ex, ey, specs, radius_x=150, radius_y=95,
                 start=180, end=360, ew=132, eh=44):
    """Fan attributes on an arc around an entity and connect each with a line."""
    n = len(specs)
    for i, spec in enumerate(specs):
        name = spec["name"]
        ang = math.radians(start + (end - start) * (i / max(n - 1, 1)))
        ax = ex + radius_x * math.cos(ang)
        ay = ey + radius_y * math.sin(ang)
        # anchor on the entity border, roughly toward the attribute
        bx = ex + (ew / 2) * (1 if ax > ex else -1) * 0.55
        by = ey + (eh / 2) * (1 if ay > ey else -1) * 0.85
        parts += line(bx, by, ax, ay, lw=1.2)
        parts += attribute(ax, ay, name, pk=spec.get("pk", False),
                           rx=spec.get("rx", 52), ry=17,
                           multivalued=spec.get("mv", False),
                           derived=spec.get("derived", False))


def write(name, content):
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", os.path.basename(path))
    return path


# ════════════════════════════════════════════════════════════════
# 1. OVERVIEW ERD — every entity and relationship, no attributes
# ════════════════════════════════════════════════════════════════
def erd_overview():
    W, H = 1560, 990
    p = svg_open(W, H, "StockPilot — Entity Relationship Diagram (Chen Notation) — Overview")
    p.append(f'<text x="{W/2}" y="56" font-size="12" text-anchor="middle" fill="#555">'
             f'Attributes are shown in the detailed diagrams. '
             f'Dashed links denote a logical association by ticker string (no foreign key).</text>')

    UX, UY = 470, 450          # USER at the centre-left
    p += entity(UX, UY, "USER", w=150, h=52)

    # user-owned entities in a single left-hand column, with the relationship
    # diamonds in their own column so nothing overlaps a box
    EX, DX = 150, 320
    owned = [
        ("HOLDING",      130, "owns"),
        ("WATCHLIST",    290, "monitors"),
        ("TRADE",        450, "logs"),
        ("NOTIFICATION", 610, "receives"),
        ("STRATEGY",     770, "creates"),
    ]
    for name, ey, rel in owned:
        ry = (UY + ey) / 2
        p += relationship(DX, ry, rel, w=104, h=52)
        p += line(UX - 75, UY, DX + 52, ry, "1", offset=0.72, dy=-9)
        # STRATEGY also carries the "published as" link off its right edge, so
        # "creates" attaches to its top edge instead
        end = (EX + 40, ey - 24) if name == "STRATEGY" else (EX + 66, ey)
        p += line(DX - 52, ry, end[0], end[1], "N", offset=0.45, dy=-9)
        p += entity(EX, ey, name)

    # marketplace chain along the bottom, from the same STRATEGY entity
    LX, LY = 1250, 770
    p += relationship(760, LY, "published as", w=132, h=56)
    p += line(EX + 66, LY, 694, LY, "1", offset=0.55, dy=-9)
    p += line(826, LY, LX - 80, LY, "1", offset=0.5, dy=-9)
    p += entity(LX, LY, "MARKETPLACE LISTING", w=160, h=52)
    p[-1] = (f'<text x="{LX}" y="{LY-2}" font-size="12.5" font-weight="bold" '
             f'text-anchor="middle" fill="{INK}">MARKETPLACE</text>'
             f'<text x="{LX}" y="{LY+13}" font-size="12.5" font-weight="bold" '
             f'text-anchor="middle" fill="{INK}">LISTING</text>')

    RX, RY = 1250, 450
    p += relationship(LX, 610, "receives", w=104, h=52)
    p += line(LX, LY - 26, LX, 636, "1", offset=0.5, dx=14)
    p += line(LX, 584, RX, RY + 26, "N", offset=0.5, dx=14)
    p += entity(RX, RY, "MARKETPLACE RATING", w=160, h=52)
    p[-1] = (f'<text x="{RX}" y="{RY-2}" font-size="12.5" font-weight="bold" '
             f'text-anchor="middle" fill="{INK}">MARKETPLACE</text>'
             f'<text x="{RX}" y="{RY+13}" font-size="12.5" font-weight="bold" '
             f'text-anchor="middle" fill="{INK}">RATING</text>')

    # user writes ratings
    p += relationship(860, RY, "writes", w=104, h=52)
    p += line(UX + 75, UY, 808, RY, "1", offset=0.5, dy=-9)
    p += line(912, RY, RX - 80, RY, "N", offset=0.5, dy=-9)

    # independent market-data entities (linked logically by ticker)
    p += entity(900, 150, "STOCK", w=140, h=48)
    p += entity(1250, 100, "PRICE HISTORY", w=170, h=48, weak=True)
    p += entity(1250, 240, "PREDICTION", w=150, h=48)
    for tx, ty in [(1250, 100), (1250, 240)]:
        p.append(f'<line x1="970" y1="150" x2="{tx-85}" y2="{ty}" stroke="{LINE}" '
                 f'stroke-width="1.3" stroke-dasharray="6,4"/>')
        my = (150 + ty) / 2
        p.append(f'<rect x="1040" y="{my-19}" width="52" height="14" fill="white"/>')
        p.append(f'<text x="1066" y="{my-8}" font-size="10" text-anchor="middle" '
                 f'fill="#555">by ticker</text>')

    p += entity(900, 320, "PLATFORM SETTINGS", w=200, h=48)
    p.append(f'<text x="900" y="356" font-size="10" text-anchor="middle" fill="#555">'
             f'singleton — no relationships</text>')

    # legend
    lx, ly = 60, 928
    p.append(f'<rect x="{lx-20}" y="{ly-30}" width="1100" height="52" fill="none" '
             f'stroke="#999" stroke-width="1"/>')
    p += entity(lx + 30, ly - 4, "Entity", w=76, h=26)
    p += relationship(lx + 190, ly - 4, "Relationship", w=118, h=32)
    p += attribute(lx + 360, ly - 4, "attribute", rx=48, ry=15)
    p += attribute(lx + 500, ly - 4, "primary key", pk=True, rx=52, ry=15)
    p += entity(lx + 660, ly - 4, "Weak entity", w=104, h=26, weak=True)
    p.append(f'<line x1="{lx+760}" y1="{ly-4}" x2="{lx+830}" y2="{ly-4}" stroke="{LINE}" '
             f'stroke-width="1.3" stroke-dasharray="6,4"/>')
    p.append(f'<text x="{lx+900}" y="{ly}" font-size="10.5" fill="#333">logical link (no FK)</text>')

    return write("StockPilot_ERD_Chen_Overview.svg", svg_close(p))


# ════════════════════════════════════════════════════════════════
# 2. DETAILED ERD — user & trading subject area
# ════════════════════════════════════════════════════════════════
def erd_user_trading():
    W, H = 1500, 1020
    p = svg_open(W, H, "StockPilot — Chen ERD (1 of 2): User, Portfolio, Watchlist, Trade, Notification")

    UX, UY = 420, 300
    p += entity(UX, UY, "USER", w=150, h=52)
    # Arc stops short of the right-hand side, which is where the relationship
    # lines to HOLDING and WATCHLIST leave the entity.
    attrs_around(p, UX, UY, [
        {"name": "user_id", "pk": True},
        {"name": "email"}, {"name": "password_hash", "rx": 60},
        {"name": "full_name"}, {"name": "role"},
        {"name": "phone"}, {"name": "is_active"},
        {"name": "created_at"},
    ], radius_x=310, radius_y=250, start=172, end=300, ew=150, eh=52)

    # HOLDING
    HX, HY = 1150, 175
    p += relationship(780, 175, "owns", w=104, h=52)
    p += line(UX + 75, UY - 20, 728, 175, "1", offset=0.55, dy=-9)
    p += line(832, 175, HX - 70, HY, "N", offset=0.45, dy=-9)
    p += entity(HX, HY, "HOLDING", w=140, h=48)
    attrs_around(p, HX, HY, [
        {"name": "holding_id", "pk": True}, {"name": "ticker"},
        {"name": "quantity"}, {"name": "avg_cost"},
        {"name": "current_price", "rx": 60}, {"name": "closed_at"},
    ], radius_x=185, radius_y=120, start=-95, end=95, ew=140, eh=48)

    # WATCHLIST
    WX, WY = 1150, 460
    p += relationship(780, 400, "monitors", w=112, h=52)
    p += line(UX + 75, UY + 5, 724, 400, "1", offset=0.55, dy=-9)
    p += line(836, 400, WX - 70, WY, "N", offset=0.45, dy=-9)
    p += entity(WX, WY, "WATCHLIST", w=150, h=48)
    attrs_around(p, WX, WY, [
        {"name": "watch_id", "pk": True}, {"name": "ticker"}, {"name": "added_at"},
    ], radius_x=175, radius_y=88, start=-80, end=80, ew=150, eh=48)

    # TRADE
    TX, TY = 750, 780
    p += relationship(500, 560, "logs", w=100, h=50)
    p += line(UX + 30, UY + 26, 490, 535, "1", offset=0.5, dx=16)
    p += line(510, 585, TX - 60, TY - 26, "N", offset=0.5, dx=16)
    p += entity(TX, TY, "TRADE", w=140, h=48)
    # Arc leaves the upper-left clear for the incoming 'logs' relationship.
    attrs_around(p, TX, TY, [
        {"name": "trade_id", "pk": True}, {"name": "ticker"}, {"name": "side"},
        {"name": "entry_price"}, {"name": "exit_price"}, {"name": "quantity"},
        {"name": "opened_at"}, {"name": "closed_at"}, {"name": "notes"},
    ], radius_x=300, radius_y=170, start=-82, end=168, ew=140, eh=48)

    # NOTIFICATION
    NX, NY = 190, 780
    p += relationship(300, 560, "receives", w=112, h=50)
    p += line(UX - 40, UY + 26, 320, 535, "1", offset=0.5, dx=-18)
    p += line(288, 585, NX + 60, NY - 26, "N", offset=0.5, dx=-18)
    p += entity(NX, NY, "NOTIFICATION", w=160, h=48)
    attrs_around(p, NX, NY, [
        {"name": "notif_id", "pk": True}, {"name": "kind"},
        {"name": "title"}, {"name": "is_read"},
    ], radius_x=170, radius_y=110, start=100, end=260, ew=160, eh=48)

    p.append(f'<text x="{W/2}" y="{H-18}" font-size="11" text-anchor="middle" fill="#555">'
             f'All five relationships are 1:N from USER with mandatory participation on the child side; '
             f'deleting a user cascades to every owned record.</text>')
    return write("StockPilot_ERD_Chen_User.svg", svg_close(p))


# ════════════════════════════════════════════════════════════════
# 3. DETAILED ERD — strategy & marketplace subject area
# ════════════════════════════════════════════════════════════════
def erd_marketplace():
    W, H = 1600, 1000
    p = svg_open(W, H, "StockPilot — Chen ERD (2 of 2): Strategy, Marketplace Listing, Rating")

    # STRATEGY
    SX, SY = 300, 300
    p += entity(SX, SY, "STRATEGY", w=155, h=52)
    attrs_around(p, SX, SY, [
        {"name": "strategy_id", "pk": True}, {"name": "name"},
        {"name": "description"}, {"name": "weights"},
        {"name": "is_preset"}, {"name": "is_published", "rx": 58},
    ], radius_x=210, radius_y=175, start=168, end=340, ew=155, eh=52)

    # USER creates STRATEGY
    UX, UY = 300, 760
    p += entity(UX, UY, "USER", w=140, h=48)
    p += relationship(SX, 530, "creates", w=110, h=52)
    p += line(SX, SY + 26, SX, 504, "1", offset=0.5, dx=16)
    p += line(SX, 556, UX, UY - 24, "N", offset=0.5, dx=16)
    p.append(f'<text x="{SX+120}" y="534" font-size="10" fill="#555">'
             f'owner may be NULL (system preset)</text>')

    # LISTING (1:1)
    LX, LY = 900, 300
    p += relationship(600, 300, "published as", w=140, h=58)
    p += line(SX + 78, SY, 530, 300, "1", offset=0.5, dy=-9)
    p += line(670, 300, LX - 85, LY, "1", offset=0.5, dy=-9)
    p += entity(LX, LY, "MARKETPLACE LISTING", w=215, h=52)
    attrs_around(p, LX, LY, [
        {"name": "listing_id", "pk": True}, {"name": "price_cents"},
        {"name": "status"}, {"name": "sales_count"},
        {"name": "avg_rating", "derived": True}, {"name": "rating_count"},
        {"name": "listed_at"},
    ], radius_x=250, radius_y=175, start=210, end=345, ew=215, eh=52)

    # backtest attributes grouped below the listing
    bt = ["backtest_return", "backtest_sharpe", "backtest_winrate",
          "backtest_trades", "backtest_max_drawdown", "backtest_profit_factor"]
    for i, name in enumerate(bt):
        bx = 600 + i * 126
        by = 575
        p += line(LX, LY + 26, bx, by - 17, lw=1.0)
        p += attribute(bx, by, name, rx=60, ry=17)

    # RATING — kept to the right of the backtest attribute row so the
    # "receives" connector never crosses an ellipse.
    RX, RY = 1310, 800
    p += relationship(1430, 480, "receives", w=112, h=52)
    p += line(LX + 107, LY + 15, 1374, 480, "1", offset=0.55, dx=20)
    p += line(1430, 506, 1390, RY - 26, "N", offset=0.5, dx=20)
    p += entity(RX, RY, "MARKETPLACE RATING", w=210, h=52)
    attrs_around(p, RX, RY, [
        {"name": "rating_id", "pk": True}, {"name": "rating"},
        {"name": "review"}, {"name": "created_at"},
    ], radius_x=175, radius_y=110, start=-85, end=85, ew=210, eh=52)

    # USER writes RATING
    p += relationship(760, 800, "writes", w=104, h=52)
    p += line(UX + 70, UY, 708, 800, "1", offset=0.5, dy=-9)
    p += line(812, 800, RX - 105, RY, "N", offset=0.5, dy=-9)

    p.append(f'<text x="{W/2}" y="{H-18}" font-size="11" text-anchor="middle" fill="#555">'
             f'STRATEGY : LISTING is 1:1 (enforced by a UNIQUE constraint on strategy_id); '
             f'participation is optional on the strategy side. avg_rating is a derived attribute.</text>')
    return write("StockPilot_ERD_Chen_Marketplace.svg", svg_close(p))


# ════════════════════════════════════════════════════════════════
# 4. NORMALISATION — UNF → 1NF → 2NF → 3NF
# ════════════════════════════════════════════════════════════════
def normalisation():
    W, H = 1500, 1180
    p = svg_open(W, H, "StockPilot — Normalisation of the Marketplace Listing Record (UNF → 3NF)")

    def box(x, y, w, h, title, rows, note=None, note_color="#555"):
        out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" '
               f'stroke="{LINE}" stroke-width="1.8"/>',
               f'<rect x="{x}" y="{y}" width="{w}" height="26" fill="#eeeeee" '
               f'stroke="{LINE}" stroke-width="1.8"/>',
               f'<text x="{x+10}" y="{y+18}" font-size="12" font-weight="bold" '
               f'fill="{INK}">{escape(title)}</text>']
        # "*" marks the identifier that follows it as a key attribute. Underlines
        # are drawn as explicit lines because text-decoration is ignored by some
        # SVG rasterisers.
        cw = 5.35  # approximate advance width of 10.5px Helvetica
        for i, r in enumerate(rows):
            ry_ = y + 45 + i * 17
            out.append(f'<text x="{x+10}" y="{ry_}" font-size="10.5" '
                       f'fill="{INK}">{escape(r.replace("*", ""))}</text>')
            pos = 0
            while True:
                j = r.find("*", pos)
                if j < 0:
                    break
                pre = len(r[:j].replace("*", ""))
                rest = r[j + 1:]
                k = 0
                while k < len(rest) and (rest[k].isalnum() or rest[k] == "_"):
                    k += 1
                x1 = x + 10 + pre * cw
                out.append(f'<line x1="{x1:.1f}" y1="{ry_+3}" x2="{x1+k*cw:.1f}" '
                           f'y2="{ry_+3}" stroke="{INK}" stroke-width="1"/>')
                pos = j + 1
        if note:
            out.append(f'<text x="{x}" y="{y+h+15}" font-size="10" fill="{note_color}">{escape(note)}</text>')
        return out

    def stage(x, y, label):
        return [f'<text x="{x}" y="{y}" font-size="14" font-weight="bold" fill="{INK}">{escape(label)}</text>']

    def arrow(x, y, text):
        return [f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+30}" stroke="{LINE}" stroke-width="1.6"/>',
                f'<polygon points="{x},{y+38} {x-5},{y+28} {x+5},{y+28}" fill="{LINE}"/>',
                f'<text x="{x+12}" y="{y+24}" font-size="10.5" fill="#333">{escape(text)}</text>']

    # ---- UNF ----
    p += stage(60, 78, "Unnormalised (UNF)")
    p += box(60, 90, 640, 150, "STRATEGY_LISTING (repeating groups present)", [
        "*strategy_id", "name, description, weights",
        "owner_id, owner_name, owner_email",
        "price_cents, status, listed_at",
        "backtest_return, backtest_sharpe, backtest_winrate",
        "ratings  =  { user_id, rating, review }   <-- repeating group",
    ], note="Violates 1NF: 'ratings' holds multiple values in a single attribute.")

    p += arrow(380, 262, "Remove the repeating group into its own relation")

    # ---- 1NF ----
    p += stage(60, 330, "First Normal Form (1NF)")
    p += box(60, 342, 640, 132, "STRATEGY_LISTING", [
        "*strategy_id", "name, description, weights",
        "owner_id, owner_name, owner_email",
        "price_cents, status, listed_at",
        "backtest_return, backtest_sharpe, backtest_winrate",
    ])
    p += box(740, 342, 440, 132, "LISTING_RATING", [
        "*listing_id, *user_id   (composite key)",
        "rating", "review", "created_at",
    ], note="All attributes are now atomic.")

    p += arrow(380, 496, "Remove partial dependency on part of the composite key")

    # ---- 2NF ----
    p += stage(60, 564, "Second Normal Form (2NF)")
    p += box(60, 576, 640, 132, "STRATEGY_LISTING", [
        "*strategy_id", "name, description, weights",
        "owner_id, owner_name, owner_email",
        "price_cents, status, listed_at",
        "backtest_return, backtest_sharpe, backtest_winrate",
    ])
    p += box(740, 576, 440, 132, "MARKETPLACE_RATING", [
        "*rating_id   (surrogate key)",
        "listing_id  (FK)", "user_id  (FK)",
        "rating, review, created_at",
    ], note="A surrogate key removes the partial dependency.")

    p += arrow(380, 730, "Remove transitive dependency: owner_name/email depend on owner_id, not the key")

    # ---- 3NF ----
    p += stage(60, 800, "Third Normal Form (3NF) — the implemented schema")
    p += box(60, 812, 400, 152, "STRATEGY", [
        "*strategy_id", "owner_id  (FK -> USER)",
        "name", "description", "weights (JSONB)",
        "is_preset, is_published",
    ])
    p += box(500, 812, 400, 152, "MARKETPLACE_LISTING", [
        "*listing_id", "strategy_id  (FK, UNIQUE)",
        "price_cents, status, listed_at",
        "avg_rating, rating_count, sales_count",
        "backtest_return / sharpe / winrate /",
        "  trades / max_drawdown / profit_factor",
    ])
    p += box(940, 812, 240, 152, "USER", [
        "*user_id", "email", "full_name", "role", "is_active",
    ])
    p += box(1220, 812, 240, 152, "MARKETPLACE_RATING", [
        "*rating_id", "listing_id (FK)", "user_id (FK)",
        "rating", "review",
    ])

    p.append(f'<text x="60" y="985" font-size="11.5" font-weight="bold" fill="{INK}">'
             f'Result</text>')
    for i, ln in enumerate([
        "Every non-key attribute depends on the key, the whole key, and nothing but the key.",
        "owner_name and owner_email were transitively dependent on owner_id; they now live only in USER.",
        "avg_rating and rating_count are retained on the listing as derived (denormalised) values, maintained by the",
        "application to avoid recomputing an aggregate over MARKETPLACE_RATING on every marketplace page load.",
    ]):
        p.append(f'<text x="60" y="{1006+i*18}" font-size="10.5" fill="#333">{escape(ln)}</text>')

    return write("StockPilot_Normalisation.svg", svg_close(p))


if __name__ == "__main__":
    erd_overview()
    erd_user_trading()
    erd_marketplace()
    normalisation()
    print("done")
