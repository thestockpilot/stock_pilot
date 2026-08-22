"""Visual: how a stock time-series becomes a spreadsheet XGBoost can learn from."""
import os, math
from html import escape

OUT = os.path.dirname(__file__)
FONT = "Helvetica, Arial, sans-serif"
INK = "#1F2937"; MUT = "#6B7280"
BLUE = "#3B82F6"; GREEN = "#10B981"; RED = "#EF4444"; PURP = "#8B5CF6"; AMBER = "#F59E0B"


def esc(s): return escape(s, quote=False)


def arrow(x1, y1, x2, y2, col="#374151", w=2.6):
    o = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{w}"/>']
    ang = math.atan2(y2 - y1, x2 - x1)
    for s in (-0.4, 0.4):
        o.append(f'<line x1="{x2}" y1="{y2}" x2="{x2-14*math.cos(ang-s)}" y2="{y2-14*math.sin(ang-s)}" stroke="{col}" stroke-width="{w}"/>')
    return o


def build():
    W, H = 1560, 710
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">',
         f'<rect width="{W}" height="{H}" fill="white"/>',
         f'<text x="{W/2}" y="44" font-size="24" font-weight="bold" text-anchor="middle" fill="{INK}">How XGBoost Works on Time-Series Stock Data</text>',
         f'<text x="{W/2}" y="72" font-size="13.5" text-anchor="middle" fill="{MUT}">The trick: reshape the price history into a spreadsheet — features look BACK, the label looks FORWARD</text>']

    # ---------- PANEL 1: price time-series with chart ----------
    x0, y0, cw, ch = 50, 150, 430, 300
    p.append(f'<text x="{x0}" y="{y0-14}" font-size="15" font-weight="bold" fill="{INK}">1.  Price history (a time-series)</text>')
    p.append(f'<rect x="{x0}" y="{y0}" width="{cw}" height="{ch}" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5"/>')
    # jagged price line
    ys = [230, 220, 235, 210, 205, 190, 200, 180, 170, 185, 165, 150, 160, 140, 130, 145, 125, 120, 135, 128]
    n = len(ys); pad = 24
    pts = []
    for i, v in enumerate(ys):
        px = x0 + pad + i * (cw - 2 * pad) / (n - 1)
        py = y0 + (v - 110) * (ch - 40) / 140 + 12
        pts.append((px, py))
    p.append('<polyline points="' + " ".join(f"{a:.0f},{b:.0f}" for a, b in pts) + f'" fill="none" stroke="{BLUE}" stroke-width="2.4"/>')
    # "today" marker
    ti = 12
    tx, ty = pts[ti]
    p.append(f'<circle cx="{tx:.0f}" cy="{ty:.0f}" r="6" fill="{AMBER}" stroke="white" stroke-width="2"/>')
    p.append(f'<text x="{tx:.0f}" y="{y0+ch-8}" font-size="10.5" text-anchor="middle" fill="{AMBER}" font-weight="bold">one day</text>')
    # lookback bracket (features)
    bx1, bx2 = pts[5][0], pts[ti][0]
    p.append(f'<line x1="{bx1:.0f}" y1="{y0+18}" x2="{bx2:.0f}" y2="{y0+18}" stroke="{GREEN}" stroke-width="2"/>')
    p.append(f'<text x="{(bx1+bx2)/2:.0f}" y="{y0+13}" font-size="10.5" text-anchor="middle" fill="{GREEN}" font-weight="bold">FEATURES = recent past</text>')
    # lookahead bracket (label)
    fx1, fx2 = pts[ti][0], pts[17][0]
    p.append(f'<line x1="{fx1:.0f}" y1="{y0+ch-26}" x2="{fx2:.0f}" y2="{y0+ch-26}" stroke="{RED}" stroke-width="2"/>')
    p.append(f'<text x="{(fx1+fx2)/2:.0f}" y="{y0+ch-30}" font-size="10.5" text-anchor="middle" fill="{RED}" font-weight="bold">LABEL = future move</text>')
    p.append(f'<text x="{x0+cw/2}" y="{y0+ch+24}" font-size="10.5" text-anchor="middle" fill="{MUT}">price goes up and down over days &rarr; time matters</text>')

    p += arrow(x0 + cw + 8, y0 + ch/2, x0 + cw + 58, y0 + ch/2)
    p.append(f'<text x="{x0+cw+33}" y="{y0+ch/2-12}" font-size="10" text-anchor="middle" fill="{MUT}" font-style="italic">reshape</text>')

    # ---------- PANEL 2: the spreadsheet ----------
    sx, sy = 560, 150
    sw = 620
    p.append(f'<text x="{sx}" y="{sy-14}" font-size="15" font-weight="bold" fill="{INK}">2.  Reshaped into a spreadsheet (what XGBoost sees)</text>')
    headers = ["Day", "RSI", "MACD", "Volatility", "…", "LABEL (5 days later)"]
    colw = [70, 62, 66, 88, 44, 180]
    rows = [
        (["Jan 02", "32", "-0.5", "1.2", "…", "UP"], GREEN),
        (["Jan 03", "45", "0.2", "1.1", "…", "DOWN"], RED),
        (["Jan 04", "58", "0.6", "0.9", "…", "(dropped: <1%)"], "#9CA3AF"),
        (["Jan 05", "40", "-0.1", "1.0", "…", "UP"], GREEN),
        (["… today", "61", "0.3", "1.3", "…", "??? (predict this)"], AMBER),
    ]
    rh = 34
    # header
    cx = sx
    for j, hh in enumerate(headers):
        fill = "#DBEAFE" if j < 5 else "#FEE2E2"
        p.append(f'<rect x="{cx}" y="{sy}" width="{colw[j]}" height="{rh}" fill="{fill}" stroke="#94A3B8" stroke-width="1"/>')
        p.append(f'<text x="{cx+colw[j]/2}" y="{sy+21}" font-size="10" font-weight="bold" text-anchor="middle" fill="{INK}">{esc(hh)}</text>')
        cx += colw[j]
    # rows
    for ri, (cells, lcol) in enumerate(rows):
        ry = sy + rh + ri * rh
        cx = sx
        for j, val in enumerate(cells):
            if j == 5:
                fill = lcol if lcol != "#9CA3AF" else "#F3F4F6"
                tcol = "white" if lcol in (GREEN, RED, AMBER) else "#6B7280"
                p.append(f'<rect x="{cx}" y="{ry}" width="{colw[j]}" height="{rh}" fill="{fill}" stroke="#94A3B8" stroke-width="1"/>')
                p.append(f'<text x="{cx+colw[j]/2}" y="{ry+21}" font-size="10" font-weight="bold" text-anchor="middle" fill="{tcol}">{esc(val)}</text>')
            else:
                p.append(f'<rect x="{cx}" y="{ry}" width="{colw[j]}" height="{rh}" fill="white" stroke="#CBD5E1" stroke-width="1"/>')
                p.append(f'<text x="{cx+colw[j]/2}" y="{ry+21}" font-size="10" text-anchor="middle" fill="{INK}">{esc(val)}</text>')
            cx += colw[j]
    # annotations under the table
    p.append(f'<text x="{sx+140}" y="{sy+rh*6+26}" font-size="11" text-anchor="middle" fill="{GREEN}" font-weight="bold">&#8593; these columns come from the PAST</text>')
    p.append(f'<text x="{sx+sw-90}" y="{sy+rh*6+26}" font-size="11" text-anchor="middle" fill="{RED}" font-weight="bold">&#8593; this comes from the FUTURE</text>')
    p.append(f'<text x="{sx+sw/2}" y="{sy+rh*6+48}" font-size="10.5" text-anchor="middle" fill="{MUT}">'
             f'Each row is independent. XGBoost no longer sees "time" — just numbers &rarr; an answer.</text>')

    p += arrow(sx + sw + 6, sy + 120, sx + sw + 52, sy + 120)

    # ---------- PANEL 3: XGBoost ----------
    gx, gy = 1225, 150
    gw = 285
    p.append(f'<text x="{gx}" y="{gy-14}" font-size="15" font-weight="bold" fill="{INK}">3.  XGBoost</text>')
    p.append(f'<rect x="{gx}" y="{gy}" width="{gw}" height="150" rx="10" fill="#F5F3FF" stroke="{PURP}" stroke-width="2"/>')
    p.append(f'<text x="{gx+gw/2}" y="{gy+28}" font-size="12.5" font-weight="bold" text-anchor="middle" fill="#6D28D9">Learns the table</text>')
    for i, ln in enumerate(['"low RSI + rising MACD', '   → usually UP"', '"high volatility + high RSI', '   → usually DOWN"']):
        p.append(f'<text x="{gx+18}" y="{gy+54+i*20}" font-size="10.5" fill="{INK}">{esc(ln)}</text>')
    p.append(f'<text x="{gx+gw/2}" y="{gy+146}" font-size="9.5" text-anchor="middle" fill="{MUT}">team of small decision trees</text>')

    p += arrow(gx + gw/2, gy + 150, gx + gw/2, gy + 190)
    p.append(f'<rect x="{gx}" y="{gy+192}" width="{gw}" height="96" rx="10" fill="#111827"/>')
    p.append(f'<text x="{gx+gw/2}" y="{gy+218}" font-size="12" font-weight="bold" text-anchor="middle" fill="white">Predict today\'s row</text>')
    p.append(f'<text x="{gx+gw/2}" y="{gy+244}" font-size="15" font-weight="bold" text-anchor="middle" fill="{AMBER}">62% DOWN</text>')
    p.append(f'<text x="{gx+gw/2}" y="{gy+270}" font-size="13" font-weight="bold" text-anchor="middle" fill="{RED}">&rarr;  SELL signal</text>')

    # ---------- bottom banner: honest testing ----------
    by = 512
    p.append(f'<rect x="50" y="{by}" width="{W-100}" height="130" rx="10" fill="#FFFBEB" stroke="{AMBER}" stroke-width="1.6"/>')
    p.append(f'<text x="74" y="{by+30}" font-size="15" font-weight="bold" fill="#92400E">&#9888;  The catch: the model ignores time, but WE must not</text>')
    for i, ln in enumerate([
        "XGBoost treats every row as independent — it has no idea which day came first. That is fine for LEARNING.",
        "But when we TEST it, we must keep the rows in time order: train on OLDER rows, test on NEWER rows.",
        "If we shuffled them, future days would leak into training and the model would “cheat” — giving a fake-high score (look-ahead leakage).",
        "That is why StockPilot uses a chronological 80:20 split and walk-forward validation, never a random shuffle.",
    ]):
        p.append(f'<text x="74" y="{by+56+i*20}" font-size="11.5" fill="{INK}">&#8226;  {esc(ln)}</text>')

    # one-line takeaway
    p.append(f'<text x="{W/2}" y="{H-24}" font-size="13" text-anchor="middle" fill="{INK}" font-weight="bold">'
             f'Features summarise the PAST · the label is the FUTURE · XGBoost learns "numbers &rarr; up/down" · we split by time so we never peek ahead.</text>')

    p.append("</svg>")
    path = os.path.join(OUT, "StockPilot_XGBoost_TimeSeries.svg")
    open(path, "w", encoding="utf-8").write("\n".join(p))
    print("wrote", os.path.basename(path))
    return path


if __name__ == "__main__":
    build()
