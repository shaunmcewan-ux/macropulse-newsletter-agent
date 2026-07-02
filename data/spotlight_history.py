"""
Spotlight rotation memory.

Each scheduled newsletter run is a cold start — the agent has no built-in
recollection of which charts it featured in previous issues. Left unmanaged,
that risks running the same spotlight (e.g. BTC daily) week after week.

This module gives the agent a persistent record. After every build the
orchestrator calls `record()`, which upserts a compact entry per issue into
`config/spotlight-history.json`:

    {
      "date": "2026-06-22", "type": "monday",
      "spotlights": [
        {"slot": 1, "symbol": "DXY",      "theme": "Dollar reclaims 100, headwind flip"},
        {"slot": 2, "symbol": "BTC",      "theme": "Range consolidation on trendline support"},
        {"slot": 3, "symbol": "ETFFLOWS", "theme": "ETF inflow bid thinning through Q2"}
      ]
    }

At the start of the next issue the agent reads `recent()` and deliberately
rotates: pick spotlights that differ from the last few issues, UNLESS a
significant development in a previously-featured chart justifies a follow-up
(in which case re-feature it with a fresh chart and an updated write-up that
references what changed).

The theme for each slot is extracted from the article file's ``##spotN``
sections so the record captures the *angle*, not just the ticker — BTC in two
consecutive weeks is fine if the story genuinely moved; the theme text is how
the agent tells the difference.
"""

from __future__ import annotations

import json
import os
import re
from datetime import date

HISTORY_FILENAME = "spotlight-history.json"
MAX_ISSUES_KEPT = 26  # ~3 months of twice-weekly issues


def _history_path(root: str) -> str:
    return os.path.join(root, "config", HISTORY_FILENAME)


def _load(root: str) -> dict:
    path = _history_path(root)
    if not os.path.exists(path):
        return {
            "_note": (
                "Rotation memory for newsletter spotlights. The orchestrator "
                "upserts one entry per issue after each build. The agent reads "
                "this before choosing spotlights so it does not repeat last "
                "week's charts unless a significant development warrants a "
                "follow-up. Newest issue last."
            ),
            "issues": [],
        }
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _theme_from_article(article_text: str, slot: int, max_words: int = 16) -> str:
    """Pull a short theme for spotlight `slot` from the article's ##spotN block."""
    if not article_text:
        return ""
    marker = f"##spot{slot}"
    idx = article_text.find(marker)
    if idx == -1:
        return ""
    body = article_text[idx + len(marker):]
    # Stop at the next ## marker.
    nxt = body.find("\n##")
    if nxt != -1:
        body = body[:nxt]
    # First non-empty line/sentence, trimmed to max_words.
    body = body.strip()
    # Prefer the first sentence.
    first = re.split(r"(?<=[.;])\s", body, maxsplit=1)[0] if body else ""
    words = first.split()
    theme = " ".join(words[:max_words]).rstrip(",;:.—- ")
    if len(words) > max_words:
        theme += "…"
    return theme


def record(root: str, issue_date: date, issue_type: str,
           symbols: list[str], article_text: str) -> str:
    """
    Upsert the spotlight record for one issue (keyed by date + type).

    Safe to call on every build — a re-run of the same issue replaces the
    prior entry rather than duplicating it. Returns the history file path.
    """
    hist = _load(root)
    issues = hist.setdefault("issues", [])

    spotlights = []
    for i, sym in enumerate(symbols, start=1):
        spotlights.append({
            "slot": i,
            "symbol": sym,
            "theme": _theme_from_article(article_text, i),
        })

    entry = {
        "date": issue_date.isoformat(),
        "type": issue_type,
        "spotlights": spotlights,
    }

    # Upsert by (date, type).
    issues = [e for e in issues
              if not (e.get("date") == entry["date"] and e.get("type") == entry["type"])]
    issues.append(entry)
    issues.sort(key=lambda e: (e.get("date", ""), e.get("type", "")))
    hist["issues"] = issues[-MAX_ISSUES_KEPT:]

    path = _history_path(root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(hist, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return path


def recent(root: str, n: int = 6, exclude_date: str | None = None) -> list[dict]:
    """Return the most recent `n` issue records, newest last."""
    issues = _load(root).get("issues", [])
    if exclude_date:
        issues = [e for e in issues if e.get("date") != exclude_date]
    return issues[-n:]


def format_recent(root: str, n: int = 6, exclude_date: str | None = None) -> str:
    """A human-readable block of recent spotlights for the snapshot report."""
    rows = recent(root, n=n, exclude_date=exclude_date)
    if not rows:
        return "(no prior spotlights on record)"
    lines = []
    for e in rows:
        spots = ", ".join(
            f"{s.get('symbol', '?')}"
            + (f" [{s['theme']}]" if s.get("theme") else "")
            for s in e.get("spotlights", [])
        )
        lines.append(f"  {e.get('date')} {e.get('type'):7} -> {spots}")
    return "\n".join(lines)


if __name__ == "__main__":
    # quick self-test
    import tempfile
    root = tempfile.mkdtemp()
    os.makedirs(os.path.join(root, "config"), exist_ok=True)
    art = (
        "Headline\n\nbody\n\n##spot1\nDXY reclaimed 100 on the FOMC bid; headwind flip is live.\n"
        "##spot2\nBTC holds the trendline in a $63k-68k range consolidation.\n"
        "##spot3\nETF inflows have thinned through the second quarter.\n"
    )
    record(root, date(2026, 6, 22), "monday", ["DXY", "BTC", "ETFFLOWS"], art)
    print(format_recent(root))
