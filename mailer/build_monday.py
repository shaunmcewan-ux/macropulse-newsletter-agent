"""
Build the Monday "Week Ahead" newsletter HTML using the macropulse.uk-styled template.
"""

from __future__ import annotations

import json
import os
from typing import Mapping

from mailer.render import (
    coming_up_rows,
    dial_svg,
    feature_body,
    portfolio_rows,
    portfolio_totals_row,
    render,
    snapshot_rows,
)

ROOT = os.path.dirname(os.path.dirname(__file__))
DIAL_FILE = os.path.join(ROOT, "config", "dial.json")


def _snapshot_label() -> str:
    """Day-aware label for the market snapshot card subhead.

    - On Monday: 'Mon DD MMM close' (overnight + weekend session)
    - On Friday: 'Fri DD MMM close'
    - Any other day: '<Day> DD MMM' (no 'close' since intraday)
    """
    from datetime import date as _date
    d = _date.today()
    weekday = d.strftime("%A")        # Monday, Tuesday...
    short   = d.strftime("%a")        # Mon, Tue, Wed...
    daynum  = d.strftime("%d").lstrip("0")
    mon     = d.strftime("%b")        # Jun
    if weekday == "Friday":
        return f"{short} {daynum} {mon} close"
    return f"{short} {daynum} {mon}"


def _load_dial() -> dict:
    try:
        with open(DIAL_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "phase": "BTC Accumulation",
            "phase_summary": "Macro pressure is easing at the margin while crypto breadth still needs confirmation.",
            "active_zone": "BTC Accumulation",
        }


def _spotlight_svg_or_fallback(charts: Mapping[str, str], symbol: str) -> str:
    svg = charts.get(symbol)
    if svg:
        return svg
    return (
        '<svg width="100%" height="210" viewBox="0 0 560 210" '
        'preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">'
        '<rect width="560" height="210" fill="#111a23"/>'
        f'<text x="280" y="105" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" '
        f'font-size="13" fill="#7c8a95">Chart unavailable &mdash; {symbol}</text>'
        '</svg>'
    )


def _default_analysis(symbol: str, prices: Mapping[str, dict]) -> str:
    """A minimal fallback when no analysis is provided in the article file."""
    data = prices.get(symbol, {}) or {}
    price = data.get("price")
    c24 = data.get("change_24h")
    c7d = data.get("change_7d")
    parts = []
    if isinstance(price, (int, float)):
        parts.append(f"{symbol} last: {price:,.2f}.")
    if isinstance(c7d, (int, float)):
        parts.append(f"7-day move: {c7d:+.1f}%.")
    if isinstance(c24, (int, float)):
        parts.append(f"24h: {c24:+.1f}%.")
    parts.append(
        "Detailed technical context (support / resistance / MA structure / RSI) "
        "should be written into the article file as ##spot1 / ##spot2 sections."
    )
    return " ".join(parts)


def _parse_article_sections(article: str) -> dict:
    """
    Parse the article file. Supported section markers (each on its own line):

        Headline (first non-blank line)

        Paragraph 1...
        Paragraph 2...

        ##spot1
        Multi-paragraph chart analysis for spotlight 1.

        ##spot2
        Multi-paragraph chart analysis for spotlight 2.

        ##comingup_intro
        2-3 sentence intro for the Coming Up section.

        ##note: ISM Services PMI (May 2026)
        Optional tightened editorial note for this event.
        (Falls back to the calendar feed's note if absent.)

        ##note: NFP (May 2026)
        ...

    Returns:
      {
        'main': str,                # everything before any ## marker
        'spot1': str | None,
        'spot2': str | None,
        'comingup_intro': str | None,
        'event_notes': {title: note, ...}
      }
    """
    import re

    text = article or ""
    out = {"main": text, "spot1": None, "spot2": None, "spot3": None,
           "comingup_intro": None, "event_notes": {}}

    # Split on lines starting with ## (preserving the marker line itself).
    parts = re.split(r"(?m)^##(?=\S)", text)
    out["main"] = parts[0].rstrip()
    for chunk in parts[1:]:
        # chunk starts with the marker word (e.g. "spot1", "note: ISM ...")
        first_nl = chunk.find("\n")
        marker = chunk[:first_nl].strip() if first_nl > -1 else chunk.strip()
        body   = chunk[first_nl + 1:].strip() if first_nl > -1 else ""

        if marker == "spot1":
            out["spot1"] = body
        elif marker == "spot2":
            out["spot2"] = body
        elif marker == "spot3":
            out["spot3"] = body
        elif marker == "comingup_intro":
            out["comingup_intro"] = body
        elif marker.startswith("note:"):
            title = marker[len("note:"):].strip()
            if title:
                out["event_notes"][title] = body
    return out


def _format_paragraphs(text: str) -> str:
    """Convert plain-text paragraphs (blank-line separated) into <p> blocks for spotlight analysis."""
    if not text:
        return ""
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    out = []
    for i, p in enumerate(paras):
        margin = "18px 0 0" if i == 0 else "14px 0 0"
        out.append(
            f'<p style="font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#b9c4cc;margin:{margin};">{p}</p>'
        )
    return "\n              ".join(out)


def _fetch_indicators_json() -> dict | None:
    """Pull the 8-indicator scorecard data. Returns None if the fetch fails."""
    import json, urllib.request
    try:
        with urllib.request.urlopen(
            "https://www.macropulse.uk/data/indicators.json", timeout=15
        ) as r:
            return json.load(r)
    except Exception as e:
        print(f"[build_monday] !! indicators.json fetch failed: {e}")
        return None


def _scorecard_tally(indicators_json: dict | None) -> str:
    """Plain tally line — '3 supportive · 4 neutral · 1 headwind'."""
    if not indicators_json:
        return "Scorecard unavailable &mdash; indicators.json fetch failed."
    inds = indicators_json.get("indicators", []) or []
    sup = sum(1 for i in inds if (i.get("status") or "").lower() == "supportive")
    neu = sum(1 for i in inds if (i.get("status") or "").lower() == "neutral")
    hw  = sum(1 for i in inds if (i.get("status") or "").lower() == "headwind")
    return f"{sup} supportive &middot; {neu} neutral &middot; {hw} headwind"


def build_monday_email(
    prices: Mapping[str, dict],
    events_data: dict,
    charts: Mapping[str, str],
    article: str,
    chart_symbols: list[str],
    issue_date: str,
    issue_number: str = "&mdash;",
    preview_text: str | None = None,
    calendar_data: dict | None = None,
    indicators_data: dict | None = None,
    portfolio_config: dict | None = None,
) -> str:
    dial = _load_dial()
    sections = _parse_article_sections(article)
    # feature_body is still called so the article kicker can flow into the
    # dial card subhead via dial.json's phase_summary if the user wants —
    # but the body and headline are no longer rendered as their own section.
    headline, body_html = feature_body(sections["main"])

    # Sample-portfolio data — load from config/portfolio.json if not supplied
    if portfolio_config is None:
        try:
            import json as _json
            with open(os.path.join(ROOT, "config", "portfolio.json"),
                      encoding="utf-8") as _f:
                portfolio_config = _json.load(_f)
        except Exception as _e:
            print(f"[build_monday] !! portfolio.json load failed: {_e}")
            portfolio_config = {"holdings": [], "start_value_gbp": 9000}
    _holdings    = portfolio_config.get("holdings", []) or []
    _start_total = portfolio_config.get("start_value_gbp", 9000.0)
    _port_rows, _book_pnl_pct = portfolio_rows(_holdings, prices, _start_total)

    # ── Coming Up section (calendar.json) ────────────────────────────────────
    cal_events = (calendar_data or {}).get("events", []) or []
    cal_fresh  = (calendar_data or {}).get("freshness", {}) or {}
    cu_intro_text = sections["comingup_intro"]
    if not cu_intro_text:
        # Fallback: name the highest-importance event in the window
        high = [e for e in cal_events if (e.get("importance") or "").lower() == "high"]
        anchor = high[0] if high else (cal_events[0] if cal_events else None)
        cu_intro_text = (
            f"Five data points matter in the next fortnight. The headline is "
            f"{anchor['title']} — write a sharper intro in <code>##comingup_intro</code>."
            if anchor else
            "No scheduled events in the next fortnight."
        )
    coming_up_html = coming_up_rows(cal_events, notes_override=sections["event_notes"])
    last_updated_str = cal_fresh.get("last_updated") or "—"
    if cal_fresh.get("flag"):
        last_updated_str += f" ({cal_fresh.get('status')})"

    sym1 = chart_symbols[0] if len(chart_symbols) > 0 else "BTC"
    sym2 = chart_symbols[1] if len(chart_symbols) > 1 else "SP500"
    sym3 = chart_symbols[2] if len(chart_symbols) > 2 else None

    _spotlight_titles = {
        "BTC":    "BTC",
        "BTC2":   "BTC",
        "ETHBTC": "ETHBTC",
        "ETH":    "ETH",
        "SP500":  "S&amp;P 500",
        "BTC.D":  "BTC.D",
        "GOLD":   "Gold",
        "DXY":    "US Dollar Index",
        "RAINBOW": "Bitcoin Rainbow Chart",
    }
    spot1_title    = _spotlight_titles.get(sym1, f"{sym1} &mdash; this week&rsquo;s setup")
    spot2_title    = _spotlight_titles.get(sym2, f"{sym2} &mdash; cross-asset context")
    spot1_analysis = _format_paragraphs(sections["spot1"]) or _default_analysis(sym1, prices)
    spot2_analysis = _format_paragraphs(sections["spot2"]) or _default_analysis(sym2, prices)

    # Optional third spotlight — a thematic, current-news section (e.g. the
    # Bitcoin Rainbow band, a SpaceX IPO read, corporate BTC treasuries).
    # Rendered whenever a third feature chart is configured AND there is either
    # an image OR written ##spot3 analysis. On a test draft with no screenshot
    # yet, it shows a "Chart unavailable" placeholder beside the analysis so the
    # user can see the section and capture the chart for the final.
    spot3_section = ""
    if sym3 and (charts.get(sym3) or sections["spot3"]):
        spot3_title    = _spotlight_titles.get(sym3, f"{sym3} &mdash; long-term context")
        spot3_analysis = (_format_paragraphs(sections["spot3"])
                          or _default_analysis(sym3, prices))
        spot3_chart    = _spotlight_svg_or_fallback(charts, sym3)
        spot3_section = (
            '<tr><td class="gutter" style="padding:12px 32px;">\n'
            '  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#111a23" style="background:#111a23;border:1px solid #1c2935;border-radius:32px;">\n'
            '    <tr><td class="card-pad" style="padding:32px;">\n'
            '      <div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:0;line-height:0;color:#111a23;" aria-hidden="true">mp-card-spot3</div>\n'
            '      <div style="font-family:Arial,Helvetica,sans-serif;font-size:11px;font-weight:600;letter-spacing:0.28em;text-transform:uppercase;color:#7c8a95;">Chart Spotlight &middot; 03</div>\n'
            f'      <div style="font-family:Arial,Helvetica,sans-serif;font-size:22px;font-weight:600;letter-spacing:-0.015em;color:#edf3f7;margin-top:8px;line-height:1.25;">{spot3_title}</div>\n'
            f'      <div style="margin-top:18px;line-height:0;">{spot3_chart}</div>\n'
            f'      <p style="font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.7;color:#b9c4cc;margin:18px 0 0;">{spot3_analysis}</p>\n'
            '    </td></tr>\n'
            '  </table>\n'
            '</td></tr>'
        )

    if not preview_text:
        preview_text = f"{dial.get('phase','')} &middot; {dial.get('phase_summary','')[:80]}"

    tokens = {
        "ISSUE_DATE":        issue_date,
        "ISSUE_NUMBER":      issue_number,
        "PREVIEW_TEXT":      preview_text,

        "DIAL_PHASE":        dial.get("phase", "BTC Accumulation"),
        "DIAL_SUMMARY":      dial.get("phase_summary", ""),
        # Score is intentionally NOT passed: the dial.json "score" values were
        # designed for the old 5-state gradient bar (Sell/Hold/Buy BTC/Alt/Top).
        # On the new 4-state arc, those values misplace the needle into the
        # wrong zone. Letting the renderer use the active-zone midpoint matches
        # the website's phase-arc.js exactly. To override, pass dial.get("score").
        "DIAL_SVG":          dial_svg(
                                 dial.get("active_zone", "BTC Accumulation"),
                                 score=None,
                                 size=400,
                             ),

        "PORTFOLIO_ROWS":          _port_rows,
        "PORTFOLIO_TOTALS_ROW":    portfolio_totals_row(_holdings, prices, _start_total),

        "SNAPSHOT_LABEL":    _snapshot_label(),
        "SNAPSHOT_ROWS":     snapshot_rows(prices),
        "COMINGUP_INTRO":    cu_intro_text,
        "COMINGUP_ROWS":     coming_up_html,
        "COMINGUP_LAST_UPDATED": last_updated_str,

        "SPOT1_TITLE":       spot1_title,
        "SPOT1_CHART_SVG":   _spotlight_svg_or_fallback(charts, sym1),
        "SPOT1_ANALYSIS":    spot1_analysis,
        "SPOT2_TITLE":       spot2_title,
        "SPOT2_CHART_SVG":   _spotlight_svg_or_fallback(charts, sym2),
        "SPOT2_ANALYSIS":    spot2_analysis,
        "SPOT3_SECTION":     spot3_section,
    }

    return render("monday", tokens)
