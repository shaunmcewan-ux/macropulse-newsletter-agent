"""
Build the Friday "Week in Review" newsletter HTML using the macropulse.uk-styled template.
"""

from __future__ import annotations

import json
import os
from typing import Mapping

from mailer.render import (
    dial_svg,
    feature_body,
    indicator_tiles,
    portfolio_rows,
    render,
    scorecard_rows,
)


def _fetch_indicators_json() -> dict | None:
    import json as _json, urllib.request as _u
    try:
        with _u.urlopen("https://www.macropulse.uk/data/indicators.json",
                        timeout=15) as r:
            return _json.load(r)
    except Exception as e:
        print(f"[build_friday] !! indicators.json fetch failed: {e}")
        return None


def _scorecard_tally(indicators_json: dict | None) -> str:
    if not indicators_json:
        return "Scorecard unavailable &mdash; indicators.json fetch failed."
    inds = indicators_json.get("indicators", []) or []
    sup = sum(1 for i in inds if (i.get("status") or "").lower() == "supportive")
    neu = sum(1 for i in inds if (i.get("status") or "").lower() == "neutral")
    hw  = sum(1 for i in inds if (i.get("status") or "").lower() == "headwind")
    return f"{sup} supportive &middot; {neu} neutral &middot; {hw} headwind"

ROOT = os.path.dirname(os.path.dirname(__file__))
DIAL_FILE = os.path.join(ROOT, "config", "dial.json")


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


def _parse_article_sections(article: str) -> dict:
    """See build_monday._parse_article_sections — same format."""
    text = article or ""
    parts = {"main": text, "spot1": None, "spot2": None}
    if "##spot1" in text:
        main, rest = text.split("##spot1", 1)
        parts["main"] = main.rstrip()
        if "##spot2" in rest:
            s1, s2 = rest.split("##spot2", 1)
            parts["spot1"] = s1.strip()
            parts["spot2"] = s2.strip()
        else:
            parts["spot1"] = rest.strip()
    return parts


def _format_paragraphs(text: str) -> str:
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


def _default_analysis(symbol: str) -> str:
    return (
        f"This week&rsquo;s {symbol} reading. Add detailed technical context "
        "(structure, key levels, MAs, momentum, trade implication) under "
        f"##spot1 / ##spot2 in the article file."
    )


def build_friday_email(
    prices: Mapping[str, dict],
    indicators: Mapping[str, object],
    portfolio_config: dict,
    charts: Mapping[str, str],
    article: str,
    chart_symbols: list[str],
    issue_date: str,
    issue_number: str = "&mdash;",
    preview_text: str | None = None,
    indicators_data: dict | None = None,
) -> str:
    dial = _load_dial()
    sections = _parse_article_sections(article)
    headline, body_html = feature_body(sections["main"])

    # Scorecard data — fetch indicators.json if not supplied
    if indicators_data is None:
        indicators_data = _fetch_indicators_json()

    holdings = portfolio_config.get("holdings", [])
    start_total = portfolio_config.get("start_value_gbp", 0.0)
    port_rows, book_pnl_pct = portfolio_rows(holdings, prices, start_total)

    sym1 = chart_symbols[0] if len(chart_symbols) > 0 else "BTC_D"
    sym2 = chart_symbols[1] if len(chart_symbols) > 1 else "TOTAL3"

    spot1_title    = f"{sym1} &mdash; the cycle tell"
    spot2_title    = f"{sym2} &mdash; alt market structure"
    spot1_analysis = _format_paragraphs(sections["spot1"]) or _default_analysis(sym1)
    spot2_analysis = _format_paragraphs(sections["spot2"]) or _default_analysis(sym2)

    if not preview_text:
        sign = "&#8722;" if book_pnl_pct < 0 else "+"
        preview_text = f"Book {sign}{abs(book_pnl_pct):.1f}% &middot; {dial.get('phase','')}"

    sign_pnl = "&#8722;" if book_pnl_pct < 0 else "+"
    book_pnl_str = f"{sign_pnl}{abs(book_pnl_pct):.1f}%"

    tokens = {
        "ISSUE_DATE":          issue_date,
        "ISSUE_NUMBER":        issue_number,
        "PREVIEW_TEXT":        preview_text,

        "DIAL_PHASE":          dial.get("phase", "BTC Accumulation"),
        "DIAL_SUMMARY":        dial.get("phase_summary", ""),
        # See build_monday.py: score is intentionally not passed; needle sits
        # at the active-zone midpoint to match the website.
        "DIAL_SVG":            dial_svg(
                                   dial.get("active_zone", "BTC Accumulation"),
                                   score=None,
                                   size=400,
                               ),

        "SCORECARD_TALLY":     _scorecard_tally(indicators_data),
        "SCORECARD_ROWS":      scorecard_rows(indicators_data) if indicators_data else "",
        "INDICATOR_TILES":     indicator_tiles(indicators),

        "SPOT1_TITLE":         spot1_title,
        "SPOT1_CHART_SVG":     _spotlight_svg_or_fallback(charts, sym1),
        "SPOT1_ANALYSIS":      spot1_analysis,
        "SPOT2_TITLE":         spot2_title,
        "SPOT2_CHART_SVG":     _spotlight_svg_or_fallback(charts, sym2),
        "SPOT2_ANALYSIS":      spot2_analysis,

        "PORTFOLIO_ROWS":      port_rows,
        "BOOK_PNL":            book_pnl_str,
        "ALLOCATION_HEADLINE": "Stay weighted to held positions",
        "ALLOCATION_BODY":     "The book is positioned for the regime that&rsquo;s playing out &mdash; no changes this issue.",

        "FEATURE_EYEBROW":     "Last Week",
        "FEATURE_HEADLINE":    headline,
        "FEATURE_BODY":        body_html,
        "FEATURE_CTA_URL":     "https://www.macropulse.uk/newsletter/",
        "FEATURE_CTA_LABEL":   "Read the full review &rarr;",
    }

    return render("friday", tokens)
