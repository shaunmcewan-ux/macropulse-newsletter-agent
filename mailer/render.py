"""
Render helpers for the new MacroPulse newsletter templates.
Produces the inline HTML fragments that get substituted into the design-pack templates.
"""

from __future__ import annotations

import os
from typing import Iterable, Mapping

HERE      = os.path.dirname(__file__)
TPL_DIR   = os.path.join(HERE, "templates")

# Cycle order matches the D1 Phase Arc handoff: defensive → bullish → euphoric → top
# Label casing matches the website's phase-arc.js exactly so the two surfaces agree.
ZONE_LIST = ["Risk Off", "BTC Accumulation", "Alt Rotation", "Take Profit"]

# Per-state colours from the Dial Handoff §3 (literal hex for email safety)
ZONE_COLORS = {
    "Risk Off":         "#ef5a6b",   # --phase-risk-off (red)
    "BTC Accumulation": "#ff9d2f",   # --phase-btc (orange)
    "Alt Rotation":     "#4ec38a",   # --phase-alt (green)
    "Take Profit":      "#b794f6",   # --phase-profit (purple, NEW)
}

# ── colour tokens (matched to live macropulse.uk) ────────────────────────────
TXT_PRIMARY      = "#edf3f7"
TXT_SECONDARY    = "#b9c4cc"
TXT_MUTED        = "#7c8a95"
ROW_DIVIDER      = "rgba(237,243,247,0.08)"
ROW_DIVIDER_TOP  = "rgba(237,243,247,0.15)"
PILL_POS_BG      = "#163024"
PILL_POS_TEXT    = "#4ec38a"
PILL_NEG_BG      = "#3a1d22"
PILL_NEG_TEXT    = "#ef5a6b"

CHIP_COLORS = {
    "fomc":        ("#3a2748", "#c4a8f5"),
    "cpi":         ("#1d2a4d", "#93b8f7"),
    "nfp":         ("#2a2218", "#f9b27a"),
    "macro":       ("#2a2218", "#f9b27a"),
    "earnings":    ("#1c3326", "#7bd4a0"),
    "geopolitics": ("#3a1a1a", "#f08c8c"),
    "default":     ("#1a1a1a", TXT_SECONDARY),
}


# ── small fragment builders ──────────────────────────────────────────────────
def pill(value: str, positive: bool | None = None) -> str:
    """Green/red rounded pill for a percent change. `positive=None` keeps a neutral pill."""
    if positive is None:
        bg, txt = "#1a1a1a", TXT_SECONDARY
    elif positive:
        bg, txt = PILL_POS_BG, PILL_POS_TEXT
    else:
        bg, txt = PILL_NEG_BG, PILL_NEG_TEXT
    return (
        f'<span style="display:inline-block;padding:5px 10px;background:{bg};'
        f'color:{txt};font-size:12px;font-weight:600;border-radius:999px;line-height:1;">'
        f'{value}</span>'
    )


def chip(label: str, kind: str = "default") -> str:
    bg, txt = CHIP_COLORS.get(kind, CHIP_COLORS["default"])
    return (
        f'<span style="display:inline-block;padding:6px 12px;background:{bg};'
        f'color:{txt};font-size:11px;font-weight:600;border-radius:999px;'
        f'line-height:1;margin:0 4px 4px 0;">{label}</span>'
    )


def fmt_pct(v: float | None) -> tuple[str, bool | None]:
    """Format a percent change as a label and return its sign. None → 'n/a'."""
    if v is None:
        return "n/a", None
    sign_char = "&#8722;" if v < 0 else "+"
    return f"{sign_char}{abs(v):.1f}%", v >= 0


def fmt_price(symbol: str, price: float | None) -> str:
    if price is None:
        return "n/a"
    if symbol in ("BTC", "ETH"):
        return f"${price:,.0f}"
    if symbol in ("SUI", "DOGE"):
        return f"${price:,.3f}" if price < 1 else f"${price:,.2f}"
    if symbol == "SP500":
        return f"{price:,.0f}"
    if symbol in ("GOLD", "OIL"):
        return f"${price:,.2f}"
    return f"{price:,.2f}"


# Zone → pointer% mapping (matches macropulse.uk dialStates)
_ZONE_POINTER = {
    "Risk Off":         8,
    "BTC Accumulation": 58,
    "ALT Rotation":     82,
    "Take Profit":      95,
}

# ── D1 Phase Arc dial — hosted at /api/dial.svg (single source of truth) ─────
def dial_svg(active_zone: str, score: float | None = None, size: int = 400) -> str:
    """
    Return an <img> tag referencing the website's server-rendered dial.

    `/api/dial.svg` reads the same ledger.json the dashboard reads, so the
    image is guaranteed to match the live state. Per the handoff, never
    hand-render the dial — always reference this endpoint.

    `active_zone` and `score` are accepted for backward compatibility but
    NOT passed to the endpoint by default: the endpoint reads state from
    ledger.json. Pass them only as query params for a one-off preview
    (e.g. a Friday look-back rendering an earlier state):

        ?size=640  ?state=Risk%20Off  ?bg=transparent  ?score=42

    Email clients render hosted SVGs reliably (Gmail web/iOS/Android,
    Apple Mail, Outlook 365). Outlook Windows desktop falls back to the
    SVG's alt text; we accept that for now.
    """
    url = f"https://www.macropulse.uk/api/dial.svg?size={size}"
    return (
        f'<img src="{url}" alt="MacroPulse cycle dial — current state" '
        f'width="{size}" '
        f'style="display:block;width:100%;max-width:{size}px;height:auto;'
        f'border:0;outline:none;text-decoration:none;" />'
    )


# Legacy 4-dot rail — retained for reference; no longer wired into templates.
def pulse_rail_row(active_zone: str) -> str:
    """
    Render the 4-cell row of dots + labels under the dial headline.
    Matches `.db-cycle-rail` on the live site:
      - 4 dots in cycle order (Risk Off → BTC Accumulation → Alt Rotation → Take Profit)
      - Active dot uses the zone's accent color with a soft halo
      - Inactive dots are transparent with a thin border
      - Labels are uppercase mono-style, dimmed except the active one (which uses orange-light)
    """
    if active_zone not in ZONE_COLORS:
        active_zone = "BTC Accumulation"

    cells = []
    for zone in ZONE_LIST:
        is_active = (zone == active_zone)
        zone_color = ZONE_COLORS[zone]

        if is_active:
            dot = (
                f'<span style="display:inline-block;width:9px;height:9px;'
                f'background:{zone_color};border-radius:50%;'
                f'border:1px solid {zone_color};'
                f'box-shadow:0 0 10px {zone_color};vertical-align:middle;"></span>'
            )
            label_color = "#ffbd69"  # --orange-1 from site
        else:
            dot = (
                f'<span style="display:inline-block;width:9px;height:9px;'
                f'background:transparent;border-radius:50%;'
                f'border:1px solid rgba(237,243,247,0.25);vertical-align:middle;"></span>'
            )
            label_color = "rgba(237,243,247,0.5)"

        label_html = (
            f'<span style="font-family:Consolas,\'JetBrains Mono\',Menlo,monospace;'
            f'font-size:10px;text-transform:uppercase;letter-spacing:0.14em;'
            f'color:{label_color};margin-left:8px;vertical-align:middle;">{zone}</span>'
        )

        cells.append(
            f'                  <td valign="middle" width="25%" '
            f'style="padding:8px 4px;text-align:left;white-space:nowrap;">'
            f'{dot}{label_html}</td>'
        )

    return "\n".join(cells)


# ── market snapshot rows ─────────────────────────────────────────────────────
SNAPSHOT_ORDER = [
    ("BTC",   "BTC"),
    ("ETH",   "ETH"),
    ("SUI",   "SUI"),
    ("DOGE",  "DOGE"),
    ("SP500", "S&amp;P 500"),
    ("GOLD",  "Gold"),
    ("OIL",   "Oil (WTI)"),
]


def snapshot_rows(prices: Mapping[str, dict]) -> str:
    """
    Render the 7 asset rows. `prices` is the dict from fetch_all_prices() —
    keys are asset symbols; values have at least 'price', 'change_24h' (pct),
    and 'change_7d' (pct, may be None).
    """
    out = []
    for i, (key, label) in enumerate(SNAPSHOT_ORDER):
        is_last = (i == len(SNAPSHOT_ORDER) - 1)
        border  = "" if is_last else f"border-bottom:1px solid {ROW_DIVIDER};"
        pad     = "14px 0 0" if is_last else "14px 0"
        data    = prices.get(key, {}) or {}
        price   = data.get("price")
        c24     = data.get("change_24h")
        c7d     = data.get("change_7d")
        lbl24, sgn24 = fmt_pct(c24)
        lbl7d, sgn7d = fmt_pct(c7d)
        out.append(
            f'                <tr>\n'
            f'                  <td align="left" style="padding:{pad};font-size:15px;font-weight:600;color:#ffffff;{border}">{label}</td>\n'
            f'                  <td align="right" style="padding:{pad};font-size:15px;font-weight:500;color:#ffffff;{border}">{fmt_price(key, price)}</td>\n'
            f'                  <td align="right" style="padding:{pad};{border}">{pill(lbl24, sgn24)}</td>\n'
            f'                  <td align="right" style="padding:{pad};{border}">{pill(lbl7d, sgn7d)}</td>\n'
            f'                </tr>'
        )
    return "\n".join(out)


# ── Scorecard (indicators.json) — mirrors dashboard scorecard table ──────────
SCORECARD_LABELS = {
    "Global Liquidity (Global M2)":   "Global M2",
    "ISM Manufacturing PMI":          "ISM PMI",
    "DXY (US Dollar Index)":          "DXY",
    "Real Yields (US10Y - CPI)":      "Real 10y",
    "2s10s Yield Curve":              "2s10s curve",
    "Fed Balance Sheet":              "Fed sheet",
    "BTC Funding Rates (perps avg)":  "BTC funding",
    "Stablecoin Dominance":           "Stables %",
}

SCORECARD_TV_LINKS = {
    "Global Liquidity (Global M2)":   "https://www.tradingview.com/symbols/ECONOMICS-USM2/",
    "ISM Manufacturing PMI":          "https://www.tradingview.com/symbols/ECONOMICS-USBCOI/",
    "DXY (US Dollar Index)":          "https://www.tradingview.com/symbols/TVC-DXY/",
    "Real Yields (US10Y - CPI)":      "https://www.tradingview.com/symbols/FRED-DFII10/",
    "2s10s Yield Curve":              "https://www.tradingview.com/symbols/FRED-T10Y2Y/",
    "Fed Balance Sheet":              "https://www.tradingview.com/symbols/FRED-WALCL/",
    "BTC Funding Rates (perps avg)":  "https://www.coinglass.com/FundingRate",
    "Stablecoin Dominance":           "https://www.tradingview.com/symbols/CRYPTOCAP-USDT.D/",
}

SCORECARD_GLOSSARY = {
    "Global Liquidity (Global M2)":   "https://www.macropulse.uk/methodology/glossary/#m2",
    "ISM Manufacturing PMI":          "https://www.macropulse.uk/methodology/glossary/#ism",
    "DXY (US Dollar Index)":          "https://www.macropulse.uk/methodology/glossary/#dxy",
    "Real Yields (US10Y - CPI)":      "https://www.macropulse.uk/methodology/glossary/#real-yields",
    "2s10s Yield Curve":              "https://www.macropulse.uk/methodology/glossary/#curve",
    "Fed Balance Sheet":              "https://www.macropulse.uk/methodology/glossary/#fed-sheet",
    "BTC Funding Rates (perps avg)":  "https://www.macropulse.uk/methodology/glossary/#funding",
    "Stablecoin Dominance":           "https://www.macropulse.uk/methodology/glossary/#stables",
}


def _status_pill(status: str) -> str:
    """Coloured-dot status pill matching the dashboard."""
    s = (status or "").lower()
    if s == "supportive":
        bg, dot, txt = "rgba(78,195,138,0.12)", "#4ec38a", "#4ec38a"
    elif s == "headwind":
        bg, dot, txt = "rgba(239,90,107,0.12)", "#ef5a6b", "#ef5a6b"
    else:
        bg, dot, txt = "rgba(255,255,255,0.06)", TXT_SECONDARY, TXT_SECONDARY
    label = (status or "neutral").capitalize()
    return (
        f'<span style="display:inline-block;padding:5px 11px 5px 9px;'
        f'background:{bg};border-radius:999px;'
        f'font-size:11px;font-weight:600;letter-spacing:0.08em;'
        f'text-transform:uppercase;color:{txt};line-height:1;white-space:nowrap;">'
        f'<span style="display:inline-block;width:6px;height:6px;border-radius:50%;'
        f'background:{dot};margin-right:6px;vertical-align:1px;"></span>'
        f'{label}</span>'
    )


def _trend_arrow(trend: str) -> str:
    """Coloured directional arrow."""
    t = (trend or "").lower()
    if t == "up":
        return '<span style="color:#4ec38a;font-size:16px;font-weight:600;">↑</span>'
    if t == "down":
        return '<span style="color:#ef5a6b;font-size:16px;font-weight:600;">↓</span>'
    return f'<span style="color:{TXT_MUTED};font-size:16px;font-weight:600;">→</span>'


def _tighten_note(note: str, target_words: int = 22) -> str:
    """Trim the bot's note to ~22 words, preserving numbers and catalysts."""
    if not note:
        return ""
    # Strip noisy boilerplate phrases that don't help the reader
    drop_phrases = [
        "released at 8:30 a.m. ET",
        "released at 10:00 a.m. ET",
        "released at 2:00 p.m. ET",
        "(released ",
    ]
    cleaned = note
    for p in drop_phrases:
        cleaned = cleaned.replace(p, "")
    # Cut at the first semicolon or sentence end
    for sep in ("; ", ". ", " — ", " - "):
        i = cleaned.find(sep)
        if 30 < i < 240:
            cleaned = cleaned[:i].rstrip(" -—;.")
            break
    words = cleaned.split()
    if len(words) > target_words + 8:
        cleaned = " ".join(words[: target_words + 4]).rstrip(",;: ")
        cleaned = cleaned + "…"
    return cleaned.strip()


def scorecard_rows(indicators_json: dict) -> str:
    """
    Render the 8-indicator scorecard table body as <tr> rows. Matches the
    macropulse.uk/dashboard/ scorecard column order and styling.
    """
    inds = indicators_json.get("indicators", [])
    rows = []
    last_idx = len(inds) - 1

    for idx, ind in enumerate(inds):
        is_last = (idx == last_idx)
        bottom_border = "" if is_last else f"border-bottom:1px solid {ROW_DIVIDER};"
        name      = ind.get("name", "")
        value     = ind.get("value", "")
        status    = ind.get("status", "neutral")
        trend     = ind.get("trend", "flat")
        note      = _tighten_note(ind.get("note", ""))

        short     = SCORECARD_LABELS.get(name, name)
        glossary  = SCORECARD_GLOSSARY.get(name, "https://www.macropulse.uk/methodology/")
        tv_link   = SCORECARD_TV_LINKS.get(name, "")

        # Indicator cell: short label (linked) + TV ↗ + value below
        indicator_html = (
            f'<a href="{glossary}" style="color:{TXT_PRIMARY};text-decoration:none;'
            f'font-weight:600;font-size:14px;letter-spacing:-0.005em;">{short}</a>'
            + (
                f' <a href="{tv_link}" title="Chart on TradingView" '
                f'style="color:{TXT_MUTED};text-decoration:none;font-size:11px;'
                f'margin-left:2px;">↗</a>'
                if tv_link else ""
            )
            + f'<div style="font-size:13px;color:{TXT_MUTED};margin-top:3px;'
              f'font-variant-numeric:tabular-nums;">{value}</div>'
        )

        rows.append(
            f'                <tr>\n'
            f'                  <td valign="top" style="padding:14px 12px 14px 0;{bottom_border}'
            f'font-family:Arial,Helvetica,sans-serif;">{indicator_html}</td>\n'
            f'                  <td valign="top" style="padding:14px 12px;{bottom_border}'
            f'text-align:left;white-space:nowrap;">{_status_pill(status)}</td>\n'
            f'                  <td valign="top" style="padding:14px 12px;{bottom_border}'
            f'text-align:center;">{_trend_arrow(trend)}</td>\n'
            f'                  <td valign="top" style="padding:14px 0 14px 12px;{bottom_border}'
            f'font-family:Arial,Helvetica,sans-serif;font-size:13px;line-height:1.55;'
            f'color:{TXT_SECONDARY};">{note}</td>\n'
            f'                </tr>'
        )
    return "\n".join(rows)


# ── "Coming up" editorial block (calendar.json-driven) ──────────────────────
def _importance_pill(level: str) -> str:
    level = (level or "medium").lower()
    bg, txt = {
        "high":   ("#3a1d22", "#ef5a6b"),
        "medium": ("#2a2218", "#f9b27a"),
        "low":    ("#1c2935", TXT_MUTED),
    }.get(level, ("#1c2935", TXT_MUTED))
    return (
        f'<span style="display:inline-block;padding:3px 9px;background:{bg};'
        f'color:{txt};font-size:10px;font-weight:600;letter-spacing:0.16em;'
        f'text-transform:uppercase;border-radius:999px;line-height:1.4;">{level}</span>'
    )


def coming_up_rows(events: list[dict], notes_override: dict[str, str] | None = None) -> str:
    """
    Render the calendar.json events as calendar-style rows. Each event:

        | Wed |  ISM Services PMI (May 2026)        [HIGH]
        | 03  |  Determines whether the expansion is broadening
        | Jun |  - one-line headline takeaway, not a paragraph
        |-----+----------------------------------------------|

    Args:
      events: list from fetch_calendar()['events'] (already sorted asc).
      notes_override: optional dict keyed by event title that supplies a
                      tightened editorial line for a specific event. Falls
                      back to the feed's note (first sentence only).
    """
    from datetime import datetime as _dt

    if not events:
        return (
            f'                <tr><td style="padding:18px 0;text-align:center;'
            f'font-family:Arial,Helvetica,sans-serif;font-size:14px;color:{TXT_MUTED};">'
            f'No high-importance events in the next 14 days.</td></tr>'
        )

    def _first_sentence(s: str, max_chars: int = 180) -> str:
        """Take the first sentence of a bot note, truncated if extremely long."""
        if not s:
            return ""
        # Cut at first period+space (most natural sentence end)
        for sep in (". ", "; ", " — ", " - "):
            i = s.find(sep)
            if 0 < i < max_chars:
                return s[: i + 1 if sep.startswith(".") else i].rstrip(" -—;") + "."
        # Otherwise just truncate
        if len(s) > max_chars:
            return s[: max_chars].rstrip() + "…"
        return s

    rows = []
    last_idx = len(events) - 1
    for idx, ev in enumerate(events):
        is_last = (idx == last_idx)
        bottom_border = "" if is_last else f"border-bottom:1px solid {ROW_DIVIDER};"

        try:
            d = _dt.strptime(ev["date"], "%Y-%m-%d").date()
            dow   = d.strftime("%a").upper()      # MON, TUE...
            dnum  = d.strftime("%d").lstrip("0")  # 3, 10, 16
            mon   = d.strftime("%b").upper()      # JUN
        except Exception:
            dow, dnum, mon = "—", "—", ""

        title      = ev.get("title", "Event")
        importance = ev.get("importance", "medium")
        raw_note   = (notes_override or {}).get(title) or ev.get("note", "")
        takeaway   = _first_sentence(raw_note)

        pill_html = _importance_pill(importance)

        # Calendar-card row: 64px date block + flexible event block.
        rows.append(
            f'                <tr>\n'
            f'                  <td valign="top" width="64" style="padding:18px 14px 18px 0;{bottom_border}'
            f'font-family:Arial,Helvetica,sans-serif;text-align:center;">\n'
            f'                    <div style="font-size:10px;font-weight:600;letter-spacing:0.18em;color:{TXT_MUTED};line-height:1;">{dow}</div>\n'
            f'                    <div style="font-size:26px;font-weight:600;color:{TXT_PRIMARY};line-height:1;margin-top:6px;letter-spacing:-0.02em;">{dnum}</div>\n'
            f'                    <div style="font-size:10px;font-weight:600;letter-spacing:0.18em;color:{TXT_MUTED};line-height:1;margin-top:6px;">{mon}</div>\n'
            f'                  </td>\n'
            f'                  <td valign="top" style="padding:18px 0;{bottom_border}font-family:Arial,Helvetica,sans-serif;">\n'
            f'                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>\n'
            f'                      <td align="left" valign="top" style="font-size:16px;font-weight:600;color:{TXT_PRIMARY};letter-spacing:-0.01em;line-height:1.3;padding-right:8px;">{title}</td>\n'
            f'                      <td align="right" valign="top" style="line-height:1;white-space:nowrap;">{pill_html}</td>\n'
            f'                    </tr></table>\n'
            f'                    <div style="font-size:13px;line-height:1.5;color:{TXT_SECONDARY};margin-top:6px;">{takeaway}</div>\n'
            f'                  </td>\n'
            f'                </tr>'
        )
    return "\n".join(rows)


# ── week-ahead calendar (legacy chips block, retained for reference) ─────────
DAY_LABELS = [("Mon", 0), ("Tue", 1), ("Wed", 2), ("Thu", 3), ("Fri", 4)]


def _event_kind(event_type: str | None) -> str:
    if not event_type:
        return "default"
    t = event_type.lower()
    if "fomc" in t or "fed" in t: return "fomc"
    if "cpi"  in t or "ppi" in t: return "cpi"
    if "nfp"  in t or "claims" in t or "pmi" in t or "macro" in t: return "nfp"
    if "earn" in t: return "earnings"
    if "geo"  in t or "war" in t or "summit" in t: return "geopolitics"
    return "default"


def calendar_rows(events_data: dict) -> str:
    """
    Render 5 weekday rows. events_data['events'] is a list of dicts with at least
    'date' (ISO yyyy-mm-dd or '2026-05-18'), 'day' (Mon/Tue/...), 'label', 'type'.
    Falls back to empty rows if no events for a day.
    """
    from datetime import date, timedelta

    events = events_data.get("events", []) or []
    week_start_iso = events_data.get("week_start")
    if week_start_iso:
        from datetime import datetime as _dt
        try:
            week_start = _dt.fromisoformat(week_start_iso).date()
        except Exception:
            week_start = date.today()
    else:
        week_start = date.today()

    by_day: dict[int, list[dict]] = {0: [], 1: [], 2: [], 3: [], 4: []}
    for ev in events:
        d = ev.get("date")
        if d:
            try:
                from datetime import datetime as _dt
                ed = _dt.fromisoformat(d).date()
                idx = (ed - week_start).days
                if 0 <= idx <= 4:
                    by_day[idx].append(ev)
                continue
            except Exception:
                pass
        # fall back on 'day' name
        day_name = (ev.get("day") or "").strip()[:3].title()
        for i, (lbl, _) in enumerate(DAY_LABELS):
            if lbl == day_name:
                by_day[i].append(ev)
                break

    out = []
    for i, (lbl, _) in enumerate(DAY_LABELS):
        dnum = (week_start + timedelta(days=i)).day
        top_border = ROW_DIVIDER_TOP if i == 0 else ROW_DIVIDER
        extra_bottom = (
            f"border-bottom:1px solid {ROW_DIVIDER_TOP};" if i == 4 else ""
        )

        chips_html = "".join(chip(e.get("label", "—"), _event_kind(e.get("type"))) for e in by_day[i])
        if not chips_html:
            chips_html = f'<span style="font-size:13px;color:{TXT_MUTED};">no scheduled events</span>'

        out.append(
            f'                <tr>\n'
            f'                  <td valign="top" width="72" style="padding:14px 0;border-top:1px solid {top_border};{extra_bottom}">\n'
            f'                    <div style="font-size:10px;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;color:{TXT_MUTED};">{lbl}</div>\n'
            f'                    <div style="font-size:18px;font-weight:600;color:#ffffff;line-height:1;margin-top:6px;">{dnum}</div>\n'
            f'                  </td>\n'
            f'                  <td valign="middle" style="padding:14px 0;border-top:1px solid {top_border};{extra_bottom}">\n'
            f'                    {chips_html}\n'
            f'                  </td>\n'
            f'                </tr>'
        )
    return "\n".join(out)


# ── indicator pulse tiles (Friday) ───────────────────────────────────────────
def _tile(label: str, value: str, delta_label: str, positive: bool | None) -> str:
    return (
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
        'bgcolor="#1a1a1a" style="background:#1a1a1a;border:1px solid rgba(255,255,255,0.1);border-radius:20px;">'
        '<tr><td style="padding:20px;">'
        f'<div style="font-size:10px;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;color:{TXT_MUTED};">{label}</div>'
        f'<div style="font-size:28px;font-weight:600;color:#ffffff;line-height:1;margin-top:10px;letter-spacing:-0.015em;">{value}</div>'
        f'<div style="margin-top:14px;">{pill(delta_label, positive)}</div>'
        '</td></tr></table>'
    )


def indicator_tiles(indicators: Mapping[str, object]) -> str:
    """
    Render the 2×2 indicator tile grid. `indicators` provides:
      BTC_D, ETH_BTC, TOTAL2_fmt, TOTAL3_fmt, plus *_wow keys for weekly delta.
    """
    btcd      = indicators.get("BTC_D")
    btcd_wow  = indicators.get("BTC_D_wow")
    ethbtc    = indicators.get("ETH_BTC")
    ethbtc_wow= indicators.get("ETH_BTC_wow")
    t2_fmt    = indicators.get("TOTAL2_fmt") or "n/a"
    t2_wow    = indicators.get("TOTAL2_wow")
    t3_fmt    = indicators.get("TOTAL3_fmt") or "n/a"
    t3_wow    = indicators.get("TOTAL3_wow")

    btcd_val   = f"{btcd:.1f}%" if isinstance(btcd, (int, float)) else "n/a"
    ethbtc_val = f"{ethbtc:.4f}" if isinstance(ethbtc, (int, float)) else "n/a"

    def _delta(v, suffix="% w/w"):
        if v is None or not isinstance(v, (int, float)):
            return "—", None
        sign = "&#8722;" if v < 0 else "+"
        return f"{sign}{abs(v):.1f}{suffix}", v >= 0

    btcd_d   = _delta(btcd_wow, "pp w/w") if btcd_wow is not None else ("—", None)
    ethbtc_d = _delta(ethbtc_wow) if ethbtc_wow is not None else ("—", None)
    t2_d     = _delta(t2_wow) if t2_wow is not None else ("—", None)
    t3_d     = _delta(t3_wow) if t3_wow is not None else ("—", None)

    tiles = [
        _tile("BTC.D",  btcd_val,  *btcd_d),
        _tile("ETH / BTC", ethbtc_val, *ethbtc_d),
        _tile("TOTAL2", t2_fmt,    *t2_d),
        _tile("TOTAL3", t3_fmt,    *t3_d),
    ]

    return (
        f'                <tr>\n'
        f'                  <td valign="top" width="50%" style="padding:0 6px 12px 0;">{tiles[0]}</td>\n'
        f'                  <td valign="top" width="50%" style="padding:0 0 12px 6px;">{tiles[1]}</td>\n'
        f'                </tr>\n'
        f'                <tr>\n'
        f'                  <td valign="top" width="50%" style="padding:0 6px 0 0;">{tiles[2]}</td>\n'
        f'                  <td valign="top" width="50%" style="padding:0 0 0 6px;">{tiles[3]}</td>\n'
        f'                </tr>'
    )


# ── Monday "Opening position" sample portfolio (forward-looking variant) ─────
def portfolio_opening_rows(holdings: Iterable[dict],
                           prices: Mapping[str, dict]) -> str:
    """
    Render the Monday "Opening position" sample portfolio as a 3-row table.

    Columns: Asset · Allocation % · Entry $ · Current $ · Position £
    No green/red pills, no week-change column — this is a calm positional
    view of how the sample book is allocated heading INTO the week.
    """
    rows = []
    items = list(holdings)
    last_idx = len(items) - 1

    def _fmt_usd(v):
        if v is None: return "&mdash;"
        if abs(v) >= 1000: return f"${v:,.0f}"
        if abs(v) >= 1:    return f"${v:,.2f}"
        return f"${v:,.4f}"

    def _fmt_gbp(v):
        if v is None: return "&mdash;"
        if abs(v) >= 1000: return f"&pound;{v:,.0f}"
        return f"&pound;{v:,.2f}"

    for idx, h in enumerate(items):
        is_last = (idx == last_idx)
        border  = "" if is_last else f"border-bottom:1px solid {ROW_DIVIDER};"
        pad     = "14px 0 0" if is_last else "14px 0"

        sym       = h["symbol"]
        alloc_pct = h.get("allocation_pct", 0)
        entry_usd = h.get("entry_price_usd", 0.0)
        start_gbp = h.get("start_value_gbp", 0.0)
        cur_usd   = (prices.get(sym, {}) or {}).get("price")

        if cur_usd and entry_usd:
            cur_gbp = start_gbp * (cur_usd / entry_usd)
        else:
            cur_gbp = start_gbp

        rows.append(
            f'                <tr>\n'
            f'                  <td align="left"  style="padding:{pad};font-size:15px;font-weight:600;color:#edf3f7;{border}">{sym}</td>\n'
            f'                  <td align="right" style="padding:{pad};font-size:14px;color:{TXT_SECONDARY};{border}">{alloc_pct}%</td>\n'
            f'                  <td align="right" style="padding:{pad};font-size:14px;color:{TXT_SECONDARY};{border}">{_fmt_usd(entry_usd)}</td>\n'
            f'                  <td align="right" style="padding:{pad};font-size:14px;font-weight:500;color:#edf3f7;{border}">{_fmt_usd(cur_usd)}</td>\n'
            f'                  <td align="right" style="padding:{pad};font-size:14px;font-weight:600;color:#edf3f7;{border}">{_fmt_gbp(cur_gbp)}</td>\n'
            f'                </tr>'
        )
    return "\n".join(rows)


def portfolio_opening_totals(holdings: Iterable[dict],
                             prices: Mapping[str, dict],
                             start_total_gbp: float) -> tuple[str, str]:
    """
    Compute the book's current £ value and a short summary line for the
    'opening position' card footer.

    Returns (book_value_str, summary_line) — both pre-formatted HTML-safe.
    """
    current = 0.0
    start   = 0.0
    for h in holdings:
        sym = h["symbol"]
        entry_usd = h.get("entry_price_usd", 0.0)
        start_gbp = h.get("start_value_gbp", 0.0)
        cur_usd   = (prices.get(sym, {}) or {}).get("price")
        start += start_gbp
        if cur_usd and entry_usd:
            current += start_gbp * (cur_usd / entry_usd)
        else:
            current += start_gbp

    if start <= 0:
        start = start_total_gbp or 9000.0
    delta_pct = ((current / start) - 1) * 100
    sign = "+" if delta_pct >= 0 else "&#8722;"
    book_value = f"&pound;{current:,.0f}"
    summary = (
        f"Baseline &pound;{start:,.0f} since 1 April 2026 &middot; "
        f"book value {book_value} ({sign}{abs(delta_pct):.1f}%)"
    )
    return book_value, summary


# ── portfolio (Friday) ───────────────────────────────────────────────────────
def portfolio_totals_row(holdings: Iterable[dict],
                         prices: Mapping[str, dict],
                         start_total_gbp: float) -> str:
    """
    Render a TOTALS row to append below the per-asset rows. Shows total
    Entry £, total Now £, blank 7d cell, and since-inception % coloured
    green/red. Lives inside the same <table> as portfolio_rows().
    """
    start_sum = 0.0
    current   = 0.0
    for h in holdings:
        sym = h["symbol"]
        entry_usd = h.get("entry_price_usd", 0.0)
        start_gbp = h.get("start_value_gbp", 0.0)
        cur_usd   = (prices.get(sym, {}) or {}).get("price")
        start_sum += start_gbp
        if cur_usd and entry_usd:
            current += start_gbp * (cur_usd / entry_usd)
        else:
            current += start_gbp

    base = start_total_gbp or start_sum or 9000.0
    since = ((current / base) - 1) * 100 if base else 0.0
    sign  = "&#8722;" if since < 0 else "+"
    since_color = PILL_POS_TEXT if since >= 0 else PILL_NEG_TEXT

    def _fmt_gbp(v):
        return f"&pound;{v:,.0f}" if abs(v) >= 1000 else f"&pound;{v:,.2f}"

    return (
        f'                <tr>\n'
        f'                  <td align="left"  style="padding:14px 0 0;font-size:15px;font-weight:700;color:{TXT_PRIMARY};border-top:1px solid {ROW_DIVIDER_TOP};letter-spacing:0.04em;text-transform:uppercase;">Total</td>\n'
        f'                  <td align="right" style="padding:14px 0 0;font-size:14px;color:{TXT_SECONDARY};border-top:1px solid {ROW_DIVIDER_TOP};">{_fmt_gbp(start_sum)}</td>\n'
        f'                  <td align="right" style="padding:14px 0 0;font-size:14px;font-weight:700;color:{TXT_PRIMARY};border-top:1px solid {ROW_DIVIDER_TOP};">{_fmt_gbp(current)}</td>\n'
        f'                  <td align="right" style="padding:14px 0 0;border-top:1px solid {ROW_DIVIDER_TOP};">&mdash;</td>\n'
        f'                  <td align="right" style="padding:14px 0 0;font-size:14px;font-weight:700;color:{since_color};border-top:1px solid {ROW_DIVIDER_TOP};">{sign}{abs(since):.1f}%</td>\n'
        f'                </tr>'
    )


def portfolio_rows(holdings: Iterable[dict], prices: Mapping[str, dict],
                   start_value_gbp_total: float) -> tuple[str, float]:
    """
    Render the 3-row portfolio table. `holdings` items have:
      symbol, entry_price_usd, start_value_gbp.
    `prices[symbol].price` is current USD price.

    Returns (rows_html, total_book_pnl_pct).
    """
    rows = []
    items = list(holdings)
    total_start = 0.0
    total_now   = 0.0

    for i, h in enumerate(items):
        is_last = (i == len(items) - 1)
        border  = "" if is_last else f"border-bottom:1px solid {ROW_DIVIDER};"
        pad     = "14px 0 0" if is_last else "14px 0"

        sym       = h["symbol"]
        entry_usd = h.get("entry_price_usd", 0.0)
        start_gbp = h.get("start_value_gbp", 0.0)
        cur_usd   = (prices.get(sym, {}) or {}).get("price")
        c7d       = (prices.get(sym, {}) or {}).get("change_7d")

        if cur_usd and entry_usd:
            cur_gbp = start_gbp * (cur_usd / entry_usd)
            since   = ((cur_usd / entry_usd) - 1) * 100
        else:
            cur_gbp = start_gbp
            since   = 0.0

        total_start += start_gbp
        total_now   += cur_gbp

        # Entry / Now: show small values to 3dp, large to 0dp
        def fmt_gbp(v):
            if abs(v) >= 1000:
                return f"&pound;{v:,.0f}"
            if abs(v) >= 1:
                return f"&pound;{v:,.2f}"
            return f"&pound;{v:,.3f}"

        lbl7d, sgn7d = fmt_pct(c7d)
        sign_since = "&#8722;" if since < 0 else "+"
        since_color = PILL_POS_TEXT if since >= 0 else PILL_NEG_TEXT

        rows.append(
            f'                <tr>\n'
            f'                  <td align="left"  style="padding:{pad};font-size:15px;font-weight:600;color:#ffffff;{border}">{sym}</td>\n'
            f'                  <td align="right" style="padding:{pad};font-size:14px;color:{TXT_SECONDARY};{border}">{fmt_gbp(entry_usd)}</td>\n'
            f'                  <td align="right" style="padding:{pad};font-size:14px;font-weight:500;color:#ffffff;{border}">{fmt_gbp(cur_usd or 0)}</td>\n'
            f'                  <td align="right" style="padding:{pad};{border}">{pill(lbl7d, sgn7d)}</td>\n'
            f'                  <td align="right" style="padding:{pad};font-size:14px;font-weight:600;color:{since_color};{border}">{sign_since}{abs(since):.1f}%</td>\n'
            f'                </tr>'
        )

    book_pnl_pct = ((total_now / total_start) - 1) * 100 if total_start else 0.0
    return "\n".join(rows), book_pnl_pct


# ── feature article body ────────────────────────────────────────────────────
def feature_body(article: str) -> tuple[str, str]:
    """
    Parse a plain-text article. Returns (headline, body_html).

    Conventions:
      - First non-empty line is the headline.
      - Blank line separates paragraphs.
      - A paragraph that starts with '>' becomes a pull-quote.
    """
    lines = [l.rstrip() for l in (article or "").splitlines()]
    # drop leading blanks
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines:
        return "Issue note", '<p style="font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.7;color:rgba(255,255,255,0.68);margin:22px 0 0;">No article this issue.</p>'

    headline = lines.pop(0).strip()
    # consume blank line
    while lines and not lines[0].strip():
        lines.pop(0)

    # group into paragraphs
    paras = []
    buf = []
    for line in lines:
        if not line.strip():
            if buf:
                paras.append(" ".join(buf).strip())
                buf = []
        else:
            buf.append(line.strip())
    if buf:
        paras.append(" ".join(buf).strip())

    body_parts = []
    first = True
    for p in paras:
        if p.startswith(">"):
            quote = p.lstrip(">").strip()
            body_parts.append(
                '              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:24px 0;">\n'
                '                <tr>\n'
                '                  <td style="border-left:3px solid #ff9d2f;padding:4px 0 4px 18px;">\n'
                f'                    <div style="font-family:Arial,Helvetica,sans-serif;font-style:italic;font-size:19px;line-height:1.45;color:#ffffff;font-weight:400;">&ldquo;{quote}&rdquo;</div>\n'
                '                  </td>\n'
                '                </tr>\n'
                '              </table>'
            )
        else:
            margin = "22px 0 0" if first else "18px 0 0"
            body_parts.append(
                f'              <p style="font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.7;color:rgba(255,255,255,0.68);margin:{margin};">{p}</p>'
            )
            first = False

    return headline, "\n".join(body_parts)


# ── template loader ────────────────────────────────────────────────────────
def load_template(name: str) -> str:
    path = os.path.join(TPL_DIR, f"{name}.html")
    with open(path, encoding="utf-8") as f:
        return f.read()


def render(template_name: str, tokens: Mapping[str, str]) -> str:
    """Render a template by substituting {{TOKEN}} placeholders."""
    html = load_template(template_name)
    for k, v in tokens.items():
        html = html.replace(f"{{{{{k}}}}}", str(v))
    return html
