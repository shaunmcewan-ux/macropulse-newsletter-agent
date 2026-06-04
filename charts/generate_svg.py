"""
Generate dark-themed SVG price/indicator charts for MacroPulse emails.
Matches the Issue #0 visual style: dark background, minimal grid, colored lines.

Usage:
    chart = generate_price_chart(history, symbol="BTC", color="#f7931a")
    # history is a list of [unix_timestamp_seconds, price]
"""

from datetime import datetime
from typing import Optional


# ── Design constants ──────────────────────────────────────────────────────────

BG_COLOR       = "#0d1f2d"
GRID_COLOR     = "#1a2f40"
AXIS_COLOR     = "#2a4050"
LABEL_COLOR    = "#5a7a8a"
MA20_COLOR     = "#d4a853"   # amber — matches brand accent
MA50_COLOR     = "#4a6080"   # muted blue
CURRENT_COLOR  = "#e8eef2"   # near-white

SVG_W = 560
SVG_H = 210
PAD_L = 10
PAD_R = 68   # room for y-axis labels on right
PAD_T = 32   # room for title
PAD_B = 28   # room for x-axis labels

CHART_W = SVG_W - PAD_L - PAD_R
CHART_H = SVG_H - PAD_T - PAD_B


# ── Math helpers ──────────────────────────────────────────────────────────────

def moving_average(prices: list, window: int) -> list:
    result = [None] * len(prices)
    for i in range(window - 1, len(prices)):
        result[i] = sum(prices[i - window + 1 : i + 1]) / window
    return result


def scale_x(ts: float, ts_min: float, ts_max: float) -> float:
    if ts_max == ts_min:
        return PAD_L
    return PAD_L + ((ts - ts_min) / (ts_max - ts_min)) * CHART_W


def scale_y(price: float, p_min: float, p_max: float) -> float:
    if p_max == p_min:
        return PAD_T + CHART_H / 2
    return PAD_T + CHART_H - ((price - p_min) / (p_max - p_min)) * CHART_H


def format_price(price: float) -> str:
    if price >= 1_000:
        return f"${price:,.0f}"
    if price >= 1:
        return f"${price:.2f}"
    if price >= 0.01:
        return f"${price:.4f}"
    return f"${price:.8f}"


def format_mcap(value: float) -> str:
    if value >= 1e12:
        return f"${value/1e12:.2f}T"
    if value >= 1e9:
        return f"${value/1e9:.1f}B"
    return f"${value:,.0f}"


# ── SVG path builder ──────────────────────────────────────────────────────────

def build_path(points: list) -> str:
    """Build SVG path d attribute from list of (x, y) tuples."""
    if not points:
        return ""
    cmds = [f"M {points[0][0]:.1f} {points[0][1]:.1f}"]
    for x, y in points[1:]:
        cmds.append(f"L {x:.1f} {y:.1f}")
    return " ".join(cmds)


# ── Main chart generator ──────────────────────────────────────────────────────

def generate_price_chart(
    history: list,
    symbol:  str   = "ASSET",
    color:   str   = "#00b4d8",
    title:   Optional[str] = None,
    is_mcap: bool  = False,
    show_ma: bool  = True,
) -> str:
    """
    Generate a dark-themed SVG line chart.

    Args:
        history:  [[unix_ts, price], ...] — sorted ascending
        symbol:   asset name for label
        color:    line color hex
        title:    override label (default: symbol)
        is_mcap:  use market cap formatting for y-axis labels
        show_ma:  show 20-day and 50-day moving average lines

    Returns:
        SVG string (no <html> wrapper — embed directly in email)
    """
    if not history or len(history) < 2:
        return _empty_chart(symbol, color)

    timestamps = [h[0] for h in history]
    prices     = [h[1] for h in history]

    p_min_raw = min(prices)
    p_max_raw = max(prices)
    padding   = (p_max_raw - p_min_raw) * 0.08
    p_min     = p_min_raw - padding
    p_max     = p_max_raw + padding

    ts_min = timestamps[0]
    ts_max = timestamps[-1]

    current_price = prices[-1]
    change_pct    = ((current_price - prices[0]) / prices[0]) * 100
    change_color  = "#4ade80" if change_pct >= 0 else "#f87171"
    change_sign   = "+" if change_pct >= 0 else ""

    # Coordinates for price line
    coords = [
        (scale_x(t, ts_min, ts_max), scale_y(p, p_min, p_max))
        for t, p in zip(timestamps, prices)
    ]
    price_path = build_path(coords)

    # Moving averages
    ma20_path = ""
    ma50_path = ""
    if show_ma and len(prices) >= 20:
        ma20 = moving_average(prices, 20)
        ma20_pts = [
            (scale_x(t, ts_min, ts_max), scale_y(p, p_min, p_max))
            for t, p in zip(timestamps, ma20) if p is not None
        ]
        if ma20_pts:
            ma20_path = build_path(ma20_pts)

    if show_ma and len(prices) >= 50:
        ma50 = moving_average(prices, 50)
        ma50_pts = [
            (scale_x(t, ts_min, ts_max), scale_y(p, p_min, p_max))
            for t, p in zip(timestamps, ma50) if p is not None
        ]
        if ma50_pts:
            ma50_path = build_path(ma50_pts)

    # Grid lines (4 horizontal)
    grid_lines = ""
    for i in range(1, 5):
        y = PAD_T + (CHART_H / 4) * i
        grid_lines += f'<line x1="{PAD_L}" y1="{y:.1f}" x2="{SVG_W - PAD_R}" y2="{y:.1f}" stroke="{GRID_COLOR}" stroke-width="1"/>\n'

    # Y-axis labels (right side)
    y_labels = ""
    fmt = format_mcap if is_mcap else format_price
    for i in range(5):
        price_val = p_max - ((p_max - p_min) / 4) * i
        y = PAD_T + (CHART_H / 4) * i
        y_labels += (
            f'<text x="{SVG_W - PAD_R + 6}" y="{y + 4:.1f}" '
            f'font-family="Arial,sans-serif" font-size="10" fill="{LABEL_COLOR}" '
            f'dominant-baseline="middle">{fmt(price_val)}</text>\n'
        )

    # X-axis labels (3 dates: start, mid, end)
    x_labels = ""
    label_indices = [0, len(timestamps) // 2, len(timestamps) - 1]
    for idx in label_indices:
        ts = timestamps[idx]
        x  = scale_x(ts, ts_min, ts_max)
        dt = datetime.fromtimestamp(ts).strftime("%d %b").lstrip("0")
        x_labels += (
            f'<text x="{x:.1f}" y="{SVG_H - 6}" '
            f'font-family="Arial,sans-serif" font-size="10" fill="{LABEL_COLOR}" '
            f'text-anchor="middle">{dt}</text>\n'
        )

    # Current price line (horizontal dashed)
    current_y   = scale_y(current_price, p_min, p_max)
    current_x   = scale_x(ts_max, ts_min, ts_max)
    price_label = fmt(current_price)

    # Title
    display_title = title or symbol
    period_days   = max(1, round((ts_max - ts_min) / 86400))

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}" viewBox="0 0 {SVG_W} {SVG_H}">
  <!-- Background -->
  <rect width="{SVG_W}" height="{SVG_H}" rx="8" fill="{BG_COLOR}"/>

  <!-- Grid -->
  {grid_lines}
  <!-- Chart border -->
  <line x1="{PAD_L}" y1="{PAD_T}" x2="{PAD_L}" y2="{PAD_T + CHART_H}" stroke="{AXIS_COLOR}" stroke-width="1"/>
  <line x1="{PAD_L}" y1="{PAD_T + CHART_H}" x2="{SVG_W - PAD_R}" y2="{PAD_T + CHART_H}" stroke="{AXIS_COLOR}" stroke-width="1"/>

  <!-- MA lines -->
  {"" if not ma50_path else f'<path d="{ma50_path}" fill="none" stroke="{MA50_COLOR}" stroke-width="1" stroke-dasharray="3,3" opacity="0.7"/>'}
  {"" if not ma20_path else f'<path d="{ma20_path}" fill="none" stroke="{MA20_COLOR}" stroke-width="1.2" stroke-dasharray="4,3" opacity="0.85"/>'}

  <!-- Area fill under price line -->
  <defs>
    <linearGradient id="areaGrad_{symbol}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{color}" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="{color}" stop-opacity="0.01"/>
    </linearGradient>
  </defs>
  <path d="{price_path} L {coords[-1][0]:.1f} {PAD_T + CHART_H} L {PAD_L} {PAD_T + CHART_H} Z"
        fill="url(#areaGrad_{symbol})"/>

  <!-- Price line -->
  <path d="{price_path}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>

  <!-- Current price dot -->
  <circle cx="{current_x:.1f}" cy="{current_y:.1f}" r="3.5" fill="{color}"/>

  <!-- Current price horizontal dashed guide -->
  <line x1="{PAD_L}" y1="{current_y:.1f}" x2="{current_x:.1f}" y2="{current_y:.1f}"
        stroke="{color}" stroke-width="0.5" stroke-dasharray="3,4" opacity="0.4"/>

  <!-- Y-axis labels -->
  {y_labels}

  <!-- X-axis labels -->
  {x_labels}

  <!-- Title bar -->
  <text x="{PAD_L + 8}" y="18" font-family="Arial,sans-serif" font-size="12" font-weight="700"
        fill="{CURRENT_COLOR}">{display_title}</text>
  <text x="{PAD_L + 8 + len(display_title) * 7 + 6}" y="18"
        font-family="Arial,sans-serif" font-size="11" fill="{change_color}">
        {change_sign}{change_pct:.1f}% ({period_days}d)</text>
  <text x="{SVG_W - PAD_R - 4}" y="18" font-family="Arial,sans-serif" font-size="11"
        fill="{CURRENT_COLOR}" text-anchor="end">{price_label}</text>

  <!-- MA legend -->
  {"" if not ma20_path else f'<line x1="{PAD_L+8}" y1="{SVG_H-8}" x2="{PAD_L+20}" y2="{SVG_H-8}" stroke="{MA20_COLOR}" stroke-width="1.2" stroke-dasharray="4,3"/><text x="{PAD_L+24}" y="{SVG_H-4}" font-family="Arial,sans-serif" font-size="9" fill="{LABEL_COLOR}">MA20</text>'}
  {"" if not ma50_path else f'<line x1="{PAD_L+56}" y1="{SVG_H-8}" x2="{PAD_L+68}" y2="{SVG_H-8}" stroke="{MA50_COLOR}" stroke-width="1" stroke-dasharray="3,3"/><text x="{PAD_L+72}" y="{SVG_H-4}" font-family="Arial,sans-serif" font-size="9" fill="{LABEL_COLOR}">MA50</text>'}
</svg>"""

    return svg


def _empty_chart(symbol: str, color: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}">'
        f'<rect width="{SVG_W}" height="{SVG_H}" rx="8" fill="{BG_COLOR}"/>'
        f'<text x="{SVG_W//2}" y="{SVG_H//2}" text-anchor="middle" '
        f'font-family="Arial,sans-serif" font-size="13" fill="{LABEL_COLOR}">'
        f'{symbol} — data unavailable</text></svg>'
    )


def charts_for_email(symbols: list, histories: dict, asset_colors: dict) -> dict:
    """
    Generate multiple charts from a dict of histories.

    Args:
        symbols:       list of symbol strings to generate
        histories:     {symbol: [[ts, price], ...]}
        asset_colors:  {symbol: hex_color}

    Returns:
        {symbol: svg_string}
    """
    result = {}
    for sym in symbols:
        hist  = histories.get(sym, [])
        color = asset_colors.get(sym, "#00b4d8")
        is_mc = sym in ("TOTAL", "TOTAL2", "TOTAL3")
        result[sym] = generate_price_chart(
            history=hist,
            symbol=sym,
            color=color,
            is_mcap=is_mc,
        )
    return result


if __name__ == "__main__":
    # Quick test with synthetic data
    import math
    import time as _time

    now = int(_time.time())
    fake = [[now - (29 - i) * 86400, 65000 + 8000 * math.sin(i / 4)] for i in range(30)]
    svg = generate_price_chart(fake, symbol="BTC", color="#f7931a")
    print(svg[:500] + "...")
    print(f"\nGenerated chart: {len(svg)} chars")
