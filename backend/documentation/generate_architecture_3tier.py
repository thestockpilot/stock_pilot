"""Generate the standard three-tier architecture diagram for StockPilot.

This is the conventional textbook form — presentation / application / data
tier, with one external service — intended for the main body of the report.
The detailed annotated version lives in generate_architecture.py and is better
suited to an appendix.
"""
import os
from html import escape

OUT_DIR = os.path.dirname(__file__)
FONT = "Helvetica, Arial, sans-serif"

INK = "#111827"
RULE = "#111827"
MUTED = "#6B7280"
TIER = "#F5F6F8"


def esc(s):
    return escape(s, quote=False)


def box(x, y, w, h, title, lines=(), fs=13, fill="white", lw=1.8, ink=INK):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" '
           f'stroke="{RULE}" stroke-width="{lw}"/>']
    n = len(lines)
    ty = y + (h - (n * 14)) / 2 + fs - 2 if n else y + h / 2 + fs / 2 - 1
    out.append(f'<text x="{x+w/2}" y="{ty}" font-size="{fs}" font-weight="bold" '
               f'text-anchor="middle" fill="{ink}">{esc(title)}</text>')
    for i, ln in enumerate(lines):
        out.append(f'<text x="{x+w/2}" y="{ty+18+i*14}" font-size="10.5" '
                   f'text-anchor="middle" fill="{ink}" opacity="0.85">{esc(ln)}</text>')
    return out


def tier(x, y, w, h, label):
    return [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{TIER}" '
            f'stroke="#B6BCC6" stroke-width="1.4" stroke-dasharray="9,6"/>',
            f'<text x="{x+18}" y="{y+24}" font-size="12.5" font-weight="bold" '
            f'fill="{MUTED}" letter-spacing="1.2">{esc(label)}</text>']


def link(x1, y1, x2, y2, label=None, both=True, gap=0):
    """Straight connector with an arrow head at one or both ends."""
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{RULE}" stroke-width="2"/>']
    vertical = abs(x2 - x1) < abs(y2 - y1)
    if vertical:
        d = 1 if y2 > y1 else -1
        out.append(f'<polygon points="{x2},{y2} {x2-7},{y2-11*d} {x2+7},{y2-11*d}" fill="{RULE}"/>')
        if both:
            out.append(f'<polygon points="{x1},{y1} {x1-7},{y1+11*d} {x1+7},{y1+11*d}" fill="{RULE}"/>')
    else:
        d = 1 if x2 > x1 else -1
        out.append(f'<polygon points="{x2},{y2} {x2-11*d},{y2-7} {x2-11*d},{y2+7}" fill="{RULE}"/>')
        if both:
            out.append(f'<polygon points="{x1},{y1} {x1+11*d},{y1-7} {x1+11*d},{y1+7}" fill="{RULE}"/>')
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        for i, ln in enumerate(label.split("\n")):
            if vertical:
                out.append(f'<rect x="{mx+10}" y="{my-14+i*14}" width="{7.4*len(ln)+10}" '
                           f'height="15" fill="white"/>')
                out.append(f'<text x="{mx+16}" y="{my-2+i*14}" font-size="10.5" '
                           f'fill="{INK}">{esc(ln)}</text>')
            else:
                out.append(f'<rect x="{mx-3.9*len(ln)-4}" y="{my-26+i*14}" '
                           f'width="{7.8*len(ln)+8}" height="15" fill="white"/>')
                out.append(f'<text x="{mx}" y="{my-14+i*14}" font-size="10.5" '
                           f'text-anchor="middle" fill="{INK}">{esc(ln)}</text>')
    return out


def build():
    W, H = 1500, 1000
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="{FONT}">',
         f'<rect width="{W}" height="{H}" fill="white"/>',
         f'<text x="{W/2}" y="42" font-size="21" font-weight="bold" text-anchor="middle" '
         f'fill="{INK}">StockPilot — Three-Tier System Architecture</text>',
         f'<text x="{W/2}" y="65" font-size="11.5" text-anchor="middle" fill="{MUTED}">'
         f'Thin client, application server, relational database, and one external '
         f'market-data service.</text>']

    CX = 700

    # ── Tier 1: presentation ─────────────────────────────────────
    p += tier(300, 92, 800, 244, "PRESENTATION TIER")
    for i, (name, role) in enumerate([("Investor", "browser"),
                                      ("Financial Analyst", "browser"),
                                      ("Administrator", "browser")]):
        p += box(330 + i * 250, 122, 200, 52, name, fs=12.5)
        p += link(430 + i * 250, 174, 430 + i * 250, 226, None, both=False)

    # spans the full width of the actor row so every connector lands on it
    p += box(400, 226, 600, 92, "Web Browser  —  Client Application",
             ["React 18 single-page application (Vite build)",
              "React Router · Chart.js · lightweight-charts · axios"])

    # ── Tier 2: application ──────────────────────────────────────
    p += tier(300, 376, 800, 320, "APPLICATION TIER")
    p.append(f'<rect x="392" y="404" width="616" height="272" rx="5" fill="white" '
             f'stroke="{RULE}" stroke-width="2.2"/>')
    p.append(f'<text x="700" y="430" font-size="13.5" font-weight="bold" '
             f'text-anchor="middle" fill="{INK}">'
             f'Application Server  —  FastAPI on Uvicorn (ASGI)</text>')
    inner = [
        ("REST API Layer", ["15 routers under /api/v1", "Pydantic request / response models"]),
        ("Security & Access Control", ["JWT access and refresh tokens",
                                       "bcrypt hashing · role-based access"]),
        ("Business Logic Layer", ["market data · technical indicators",
                                  "scoring · backtesting · marketplace"]),
        ("Machine Learning Layer", ["XGBoost prediction model",
                                    "FinBERT sentiment model"]),
    ]
    for i, (t, s) in enumerate(inner):
        ix = 412 + (i % 2) * 298
        iy = 444 + (i // 2) * 114
        p += box(ix, iy, 278, 98, t, s, fs=12)

    # ── Tier 3: data ─────────────────────────────────────────────
    p += tier(300, 736, 800, 186, "DATA TIER")
    p += box(460, 766, 480, 126, "PostgreSQL 16  —  Relational Database",
             ["Accessed through SQLAlchemy 2.0 async ORM over asyncpg",
              "Schema in third normal form · 11 tables",
              "Migrations version-controlled with Alembic"])

    # ── external service ─────────────────────────────────────────
    p += box(1160, 486, 280, 110, "Yahoo Finance API",
             ["Accessed with the yfinance client", "Price history, live quotes,",
              "news headlines and fundamentals"], fill="white")
    p.append(f'<text x="1300" y="620" font-size="10.5" text-anchor="middle" fill="{MUTED}">'
             f'External service — outside the system boundary</text>')

    # ── connectors ───────────────────────────────────────────────
    p += link(CX, 318, CX, 404, "HTTPS  ·  JSON  ·  REST")
    p += link(CX, 676, CX, 766, "SQL  ·  asyncpg driver")
    p += link(1008, 541, 1160, 541, "HTTPS")

    # ── notes ────────────────────────────────────────────────────
    p.append(f'<text x="300" y="{H-52}" font-size="10.5" fill="{MUTED}">'
             f'The browser holds no business logic and never contacts the database or the '
             f'external service directly; every request passes through the application server,</text>')
    p.append(f'<text x="300" y="{H-36}" font-size="10.5" fill="{MUTED}">'
             f'which authenticates it and authorises it against the caller\'s role before any '
             f'data is read or written.</text>')

    p.append("</svg>")
    path = os.path.join(OUT_DIR, "StockPilot_Architecture_3Tier.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(p))
    print("wrote", os.path.basename(path))
    return path


if __name__ == "__main__":
    build()
    print("done")
