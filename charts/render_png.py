"""
PNG renderers for the newsletter — dial + spotlight charts.

Why PNG and not SVG: Gmail (web + mobile) strips inline <svg> wrappers but
keeps the text content inside, so SVG axis labels and tick labels leak as
raw text in the email body. PNGs are universally rendered by every major
email client.

Output: each function returns a complete <img ...> tag with a base64-encoded
data URI, ready to drop into a template token slot.
"""

from __future__ import annotations

import base64
import io
import math
from datetime import datetime
from typing import Iterable, Optional

import matplotlib
matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle
from matplotlib.lines import Line2D


# ── shared palette (matches macropulse.uk + Dial Handoff §3) ─────────────────
BG_PAGE   = "#0c141b"
BG_CARD   = "#111a23"
INK       = "#edf3f7"
INK_2     = "#b9c4cc"
INK_3     = "#7c8a95"
LINE      = "#1c2935"

# Per-phase colours (literal hex, Dial Handoff §3/§8)
PHASE = [
    {"id": "risk-off", "label": "Risk Off",         "abbr": "RO",  "color": "#ef5a6b"},
    {"id": "btc",      "label": "BTC Accumulation", "abbr": "BTC", "color": "#ff9d2f"},
    {"id": "alt",      "label": "Alt Rotation",     "abbr": "ALT", "color": "#4ec38a"},
    {"id": "profit",   "label": "Take Profit",      "abbr": "TP",  "color": "#b794f6"},
]
PHASE_BY_ID    = {p["id"]: p for p in PHASE}
PHASE_BY_LABEL = {p["label"]: p for p in PHASE}


# ── helpers ──────────────────────────────────────────────────────────────────
def _to_data_uri(png_bytes: bytes) -> str:
    b64 = base64.b64encode(png_bytes).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _img_tag(png_bytes: bytes, alt: str, width: int, height: int) -> str:
    src = _to_data_uri(png_bytes)
    return (
        f'<img src="{src}" alt="{alt}" '
        f'width="{width}" height="{height}" '
        f'style="display:block;width:100%;max-width:{width}px;height:auto;'
        f'border:0;outline:none;text-decoration:none;" />'
    )


def _resolve_phase(state: str) -> dict:
    if state in PHASE_BY_ID:
        return PHASE_BY_ID[state]
    if state in PHASE_BY_LABEL:
        return PHASE_BY_LABEL[state]
    key = state.strip().lower()
    for p in PHASE:
        if p["id"] == key or p["label"].lower() == key:
            return p
    return PHASE_BY_ID["btc"]


# ── D1 Phase Arc dial as PNG ────────────────────────────────────────────────
def render_dial_png(state: str = "btc", score: Optional[float] = None,
                    size: int = 400) -> bytes:
    """
    Render the half-dial speedometer as a PNG. Geometry matches the React
    component (4 zones × 45° on a 180° arc, opacity 0.95 active / 0.18 idle,
    needle pointing to zone midpoint or interpolated score).
    """
    active = _resolve_phase(state)
    i_active = PHASE.index(active)

    w = size
    h = int(size * 0.72)
    dpi = 100

    fig = plt.figure(figsize=(w / dpi, h / dpi), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  # screen coords (y grows down) to match SVG
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(BG_CARD)
    ax.set_facecolor(BG_CARD)

    cx = w / 2
    cy = h - 28
    r  = w / 2 - 24

    # Each zone spans 45° on the upper half. matplotlib Wedge angles are CCW
    # from the +x axis. The React code uses degrees from -180° (left) sweeping
    # CW to 0° (right) along the TOP half. In matplotlib (with axis flipped),
    # we draw from 180° (left, top) CCW to 0° (right, top), so theta1=180-i*45-45,
    # theta2=180-i*45. Phase order in cycle (left → right): risk-off, btc, alt, profit.
    # Convert: phase i sits between angles (180 - (i+1)*45) and (180 - i*45) when
    # drawn CCW. With ax.invert_yaxis(), CCW in matplotlib renders as CW visually
    # on screen, which is what we want.
    for i, p in enumerate(PHASE):
        # CCW theta1 < theta2; phase i on the dial occupies left-to-right slot i
        theta1 = 180 - (i + 1) * 45 + 1.2
        theta2 = 180 - i * 45 - 1.2
        wedge = Wedge(
            (cx, cy), r, theta1, theta2, width=22,
            facecolor=p["color"],
            alpha=0.95 if i == i_active else 0.18,
            edgecolor="none",
            linewidth=0,
        )
        ax.add_patch(wedge)

    # Tick labels (RO / BTC / ALT / TP) outside the arc — offset matches website
    for i, p in enumerate(PHASE):
        mid_deg = 180 - (i + 0.5) * 45
        tx = cx + (r + 16) * math.cos(math.radians(mid_deg))
        ty = cy - (r + 16) * math.sin(math.radians(mid_deg))
        is_active_label = (i == i_active)
        ax.text(
            tx, ty, p["abbr"],
            ha="center", va="center",
            fontsize=max(9, size // 32),
            color=p["color"] if is_active_label else INK_3,
            fontweight=("bold" if is_active_label else "regular"),
            family="monospace",
        )

    # Needle angle: midpoint, or interpolated from score (0–100 -> left to right)
    if isinstance(score, (int, float)):
        s = max(0.0, min(100.0, float(score)))
        needle_deg = 180 - (s / 100) * 180
    else:
        needle_deg = 180 - (i_active + 0.5) * 45

    # Outlined arrow polygon — taper shaft + arrowhead, mirroring phase-arc.js.
    # Geometry is computed in a "needle-local" frame (tip up = +y), then rotated
    # into screen coords. Length r-8, shaft half-width 1.3, head half-width 6,
    # head height 16.
    needle_length = r - 8
    shaft_half = 1.3
    head_half  = 6
    head_height = 16
    L = needle_length

    # Polygon points in needle-local coords (origin = hub, +y = toward tip).
    local_pts = [
        (-shaft_half, 0),
        (-shaft_half, -(L - head_height)),
        (-head_half,  -(L - head_height)),
        (0, -L),
        (head_half,   -(L - head_height)),
        (shaft_half,  -(L - head_height)),
        (shaft_half, 0),
    ]
    # Rotation: phase-arc.js uses transform="translate(cx cy) rotate(angle+90)"
    # In SVG, rotate(θ) is clockwise. In our matplotlib coords (y-inverted), the
    # equivalent screen rotation has the same sign. Build the rotated points.
    theta = math.radians(needle_deg + 90)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    # SVG rotate(θ) clockwise on y-down screen == matplotlib rotation by -θ on
    # standard axes; here y is INVERTED back to screen-style, so apply directly:
    rotated = []
    for (lx, ly) in local_pts:
        rx = lx * cos_t - ly * sin_t
        ry = lx * sin_t + ly * cos_t
        rotated.append((cx + rx, cy + ry))

    from matplotlib.patches import Polygon as MplPolygon
    ax.add_patch(MplPolygon(
        rotated, closed=True,
        facecolor=active["color"],
        edgecolor="#080e13",
        linewidth=1.6,
        joinstyle="round",
        capstyle="round",
    ))

    # Hub — matches website: r=9 light stroke + r=3.5 inner dot.
    ax.add_patch(Circle((cx, cy), 9,   facecolor=BG_PAGE,
                        edgecolor=(237/255, 243/255, 247/255, 0.18), linewidth=1))
    ax.add_patch(Circle((cx, cy), 3.5, facecolor=active["color"], edgecolor="none"))

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=BG_CARD, dpi=dpi,
                bbox_inches=None, pad_inches=0)
    plt.close(fig)
    return buf.getvalue()


def dial_img_tag(state: str = "btc", score: Optional[float] = None,
                 size: int = 400) -> str:
    """Return a complete <img> tag for the dial with a PNG data URI src."""
    png = render_dial_png(state, score, size)
    label = _resolve_phase(state)["label"]
    alt = f"MacroPulse dial: {label}"
    if isinstance(score, (int, float)):
        alt += f" (score {int(score)}/100)"
    h = int(size * 0.72)
    return _img_tag(png, alt, size, h)


# ── Price/indicator chart as PNG ────────────────────────────────────────────
def _format_money(v: float, is_mcap: bool) -> str:
    if is_mcap:
        if v >= 1e12: return f"${v/1e12:.2f}T"
        if v >= 1e9:  return f"${v/1e9:.1f}B"
        return f"${v/1e6:.0f}M"
    if v >= 1000: return f"${v:,.0f}"
    if v >= 1:    return f"${v:,.2f}"
    return f"${v:,.4f}"


def render_chart_png(
    history: Iterable[Iterable],
    symbol: str,
    color: str = "#ff9d2f",
    is_mcap: bool = False,
    show_ma: bool = True,
    width: int = 560,
    height: int = 240,
) -> bytes:
    """
    Render a price-history line chart as PNG.

    history: iterable of [timestamp_ms_or_s, price] pairs.
    """
    pts = list(history)
    if not pts:
        # Empty placeholder
        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        ax.set_facecolor(BG_CARD)
        fig.patch.set_facecolor(BG_CARD)
        ax.text(0.5, 0.5, f"No data — {symbol}", ha="center", va="center",
                color=INK_3, transform=ax.transAxes, fontsize=12)
        ax.axis("off")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", facecolor=BG_CARD)
        plt.close(fig)
        return buf.getvalue()

    # Build x/y arrays
    xs_ts = [p[0] for p in pts]
    ys    = [p[1] for p in pts]
    # Auto-detect ms vs s
    if xs_ts and xs_ts[0] > 1e12:
        xs = [datetime.fromtimestamp(t / 1000) for t in xs_ts]
    else:
        xs = [datetime.fromtimestamp(t) for t in xs_ts]

    dpi = 100
    fig, ax = plt.subplots(figsize=(width/dpi, height/dpi), dpi=dpi)
    fig.patch.set_facecolor(BG_CARD)
    ax.set_facecolor(BG_CARD)

    # Main line + area fill
    ax.plot(xs, ys, color=color, linewidth=2, solid_capstyle="round")
    ax.fill_between(xs, ys, min(ys), color=color, alpha=0.15)

    # MA20 if asked and we have enough points
    if show_ma and len(ys) >= 20:
        ma20 = []
        for i in range(len(ys)):
            window = ys[max(0, i - 19): i + 1]
            ma20.append(sum(window) / len(window))
        ax.plot(xs, ma20, color="#d4a853", linewidth=1.2,
                linestyle=(0, (4, 3)), alpha=0.85, label="MA20")

    # MA50 if we have enough points
    if show_ma and len(ys) >= 50:
        ma50 = []
        for i in range(len(ys)):
            window = ys[max(0, i - 49): i + 1]
            ma50.append(sum(window) / len(window))
        ax.plot(xs, ma50, color="#7896b8", linewidth=1.2,
                linestyle=(0, (4, 3)), alpha=0.65, label="MA50")

    # Styling
    ax.tick_params(colors=INK_3, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(LINE)
        spine.set_linewidth(0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, color=LINE, linewidth=0.6, alpha=0.5)

    # Y-axis label positioning
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")

    # Title strip
    last = ys[-1]
    first = ys[0]
    pct = ((last / first) - 1) * 100 if first else 0
    pct_str = f"{pct:+.1f}% (30d)"
    title_color = "#4ec38a" if pct >= 0 else "#ef5a6b"
    ax.set_title(
        f"{symbol}    {_format_money(last, is_mcap)}    {pct_str}",
        color=INK, fontsize=11, fontweight="600", loc="left", pad=10,
    )
    # Tint the percentage manually by adding a second-line text — title is
    # one colour. So we keep the title plain (INK) but redo via text:
    ax.title.set_color(INK)
    # add the % colour as a corner annotation
    ax.text(
        0.99, 1.04, pct_str,
        transform=ax.transAxes, ha="right", va="bottom",
        color=title_color, fontsize=10, fontweight="600",
    )

    # Date formatter
    import matplotlib.dates as mdates
    locator = mdates.AutoDateLocator(maxticks=5)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))

    fig.tight_layout(pad=1.1)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=BG_CARD, dpi=dpi)
    plt.close(fig)
    return buf.getvalue()


def chart_img_tag(
    history: Iterable[Iterable],
    symbol: str,
    color: str = "#ff9d2f",
    is_mcap: bool = False,
    show_ma: bool = True,
    width: int = 560,
    height: int = 240,
) -> str:
    png = render_chart_png(history, symbol, color, is_mcap, show_ma, width, height)
    return _img_tag(png, f"{symbol} 30-day chart", width, height)


if __name__ == "__main__":
    # quick smoke test
    import os
    out = os.path.join(os.path.dirname(__file__), "..", "drafts")
    os.makedirs(out, exist_ok=True)
    for s in ("risk-off", "btc", "alt", "profit"):
        with open(os.path.join(out, f"dial-{s}.png"), "wb") as f:
            f.write(render_dial_png(s, score=None, size=400))
        print(f"wrote dial-{s}.png")

    # fake history
    import random, time
    now = time.time()
    hist = [[now - (30 - i) * 86400, 60000 + i * 200 + random.randint(-300, 300)] for i in range(30)]
    with open(os.path.join(out, "chart-btc.png"), "wb") as f:
        f.write(render_chart_png(hist, "BTC", "#ff9d2f"))
    print("wrote chart-btc.png")
