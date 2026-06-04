"""
Static SVG renderer for the D1 Phase Arc dial (MacroPulse Dial Handoff §4 + §8).

Pure Python — no JS, no animations, no external deps. Produces an inline SVG
string ready to drop into the email templates. All colours are literal hex
(no CSS vars) so Gmail / Apple Mail / Outlook 365 render identically.

Geometry mirrors the React `DialPhaseArc` in dials/dials.jsx so the dashboard
and email surfaces look the same.
"""

from __future__ import annotations

import math
from typing import Optional

# ── Phases in cycle order (Dial Handoff §2) ──────────────────────────────────
PHASES = [
    {"id": "risk-off", "label": "Risk Off",         "abbr": "RO",  "color": "#ef5a6b"},
    {"id": "btc",      "label": "BTC Accumulation", "abbr": "BTC", "color": "#ff9d2f"},
    {"id": "alt",      "label": "Alt Rotation",     "abbr": "ALT", "color": "#4ec38a"},
    {"id": "profit",   "label": "Take Profit",      "abbr": "TP",  "color": "#b794f6"},
]
PHASE_BY_ID    = {p["id"]: p for p in PHASES}
PHASE_BY_LABEL = {p["label"]: p for p in PHASES}

INK_3       = "#7c8a95"
LINE_STRONG = "#34404b"
HUB_FILL    = "#0c141b"


def _resolve_phase_id(state: str) -> str:
    """Accept either canonical id ('risk-off') or display label ('Risk Off')."""
    if state in PHASE_BY_ID:
        return state
    if state in PHASE_BY_LABEL:
        return PHASE_BY_LABEL[state]["id"]
    # case-insensitive fallback
    key = state.strip().lower()
    for p in PHASES:
        if p["id"] == key or p["label"].lower() == key:
            return p["id"]
    return "btc"  # safe default


def _polar(cx: float, cy: float, r: float, deg: float) -> tuple[float, float]:
    rad = deg * math.pi / 180.0
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


def _arc_path(cx: float, cy: float, r_outer: float, r_inner: float,
              a0: float, a1: float) -> str:
    x0o, y0o = _polar(cx, cy, r_outer, a0)
    x1o, y1o = _polar(cx, cy, r_outer, a1)
    x1i, y1i = _polar(cx, cy, r_inner, a1)
    x0i, y0i = _polar(cx, cy, r_inner, a0)
    return (
        f"M {x0o:.2f} {y0o:.2f} "
        f"A {r_outer:.2f} {r_outer:.2f} 0 0 1 {x1o:.2f} {y1o:.2f} "
        f"L {x1i:.2f} {y1i:.2f} "
        f"A {r_inner:.2f} {r_inner:.2f} 0 0 0 {x0i:.2f} {y0i:.2f} Z"
    )


def render_dial_svg(
    state: str = "btc",
    score: Optional[float] = None,
    size: int = 400,
) -> str:
    """
    Render the D1 Phase Arc dial as a static inline SVG string.

    Args:
      state:  phase id ('risk-off' | 'btc' | 'alt' | 'profit') or display
              label ('Risk Off', 'BTC Accumulation', 'ALT Rotation',
              'Take Profit').
      score:  Optional 0-100. When provided, needle interpolates linearly
              across the 180° arc; otherwise it points at the zone midpoint.
      size:   Outer width in pixels. Height auto-derives to size * 0.72.

    Returns: <svg ...>...</svg> string, ready to inline.
    """
    phase_id = _resolve_phase_id(state)
    i = next(idx for idx, p in enumerate(PHASES) if p["id"] == phase_id)
    active_color = PHASES[i]["color"]
    active_label = PHASES[i]["label"]

    w = size
    h = size * 0.72
    cx = w / 2
    cy = h - 28
    r  = w / 2 - 24

    # Needle angle — same logic as React component
    if isinstance(score, (int, float)):
        s = max(0.0, min(100.0, float(score)))
        needle_angle = -180 + (s / 100) * 180
    else:
        needle_angle = -180 + i * 45 + 22.5

    # Zone arcs (45° each, with 1.2° gaps between them)
    zone_paths = []
    for idx, p in enumerate(PHASES):
        active   = idx == i
        a0 = -180 + idx * 45 + 1.2
        a1 = -180 + (idx + 1) * 45 - 1.2
        path_d = _arc_path(cx, cy, r, r - 22, a0, a1)
        opacity = 0.95 if active else 0.18
        zone_paths.append(
            f'<path d="{path_d}" fill="{p["color"]}" fill-opacity="{opacity}"/>'
        )

    # Tick labels (zone abbreviations just outside the arc)
    tick_labels = []
    for idx, p in enumerate(PHASES):
        tx, ty = _polar(cx, cy, r + 14, -180 + idx * 45 + 22.5)
        active = idx == i
        fill   = p["color"] if active else INK_3
        weight = 600 if active else 500
        font_size = max(9, size // 32)
        tick_labels.append(
            f'<text x="{tx:.2f}" y="{ty + 4:.2f}" '
            f'text-anchor="middle" '
            f'font-family="Consolas,\'JetBrains Mono\',Menlo,monospace" '
            f'font-size="{font_size}" letter-spacing="0.18em" '
            f'fill="{fill}" font-weight="{weight}" '
            f'style="text-transform:uppercase;">{p["abbr"]}</text>'
        )

    # Needle — rotated about (cx, cy). The +90° matches the React component.
    rot   = needle_angle + 90
    n_len = r - 12
    needle = (
        f'<g transform="translate({cx:.2f} {cy:.2f}) rotate({rot:.2f})">'
        f'<line x1="0" y1="0" x2="0" y2="{-n_len:.2f}" '
        f'stroke="{active_color}" stroke-width="2.5" stroke-linecap="round"/>'
        f'<circle cx="0" cy="{-n_len:.2f}" r="4" fill="{active_color}"/>'
        f'</g>'
    )

    # Hub (centred at cx, cy)
    hub = (
        f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="8" '
        f'fill="{HUB_FILL}" stroke="{LINE_STRONG}"/>'
        f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="3" fill="{active_color}"/>'
    )

    title = (
        f"MacroPulse dial: {active_label}"
        + (f" (score {int(score)}/100)" if isinstance(score, (int, float)) else "")
    )

    return (
        f'<svg width="{w}" height="{h:.0f}" viewBox="0 0 {w} {h:.0f}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{title}">'
        f'<title>{title}</title>'
        + "".join(zone_paths)
        + "".join(tick_labels)
        + needle
        + hub
        + '</svg>'
    )


if __name__ == "__main__":
    # quick smoke test — emit one of each phase
    import os
    out_dir = os.path.join(os.path.dirname(__file__), "..", "drafts")
    os.makedirs(out_dir, exist_ok=True)
    for state in ("risk-off", "btc", "alt", "profit"):
        svg = render_dial_svg(state, score=None, size=400)
        path = os.path.join(out_dir, f"dial-{state}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"wrote {path}")
