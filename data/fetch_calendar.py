"""
Fetch macropulse.uk/data/calendar.json — the same feed the website dashboard uses.

Provides:
- fetch_calendar(reference_date) -> dict with events filtered to the upcoming 14
  days, freshness status, and the raw feed for debugging.
- save_week_snapshot(events, path) -> persist a Monday issue's event list to
  disk so the Friday look-back can read it back and write actuals against it.
"""

from __future__ import annotations

import json
import os
import urllib.request
from datetime import date, datetime, timedelta

CALENDAR_URL = "https://www.macropulse.uk/data/calendar.json"

# Bytes / characters that survive the bot's UTF-8 round-trip as replacement
# characters. We map them back to en/em dashes and curly apostrophes.
_REPLACEMENT_FIXUPS = [
    ("�", "–"),   # U+FFFD replacement char → en-dash (most common context)
]


def _clean(s: str) -> str:
    """Strip the UTF-8 mojibake the bot occasionally introduces."""
    if not s:
        return s
    for bad, good in _REPLACEMENT_FIXUPS:
        s = s.replace(bad, good)
    return s


def _freshness(last_updated: str, today: date) -> dict:
    """
    Classify feed freshness. The user's preference is to flag both directions:
      stale  if lastUpdated is more than 2 days BEHIND today
      future if lastUpdated is more than 14 days AHEAD of today
    """
    try:
        lu = datetime.strptime(last_updated, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return {"status": "unknown", "age_days": None, "last_updated": last_updated, "flag": True}

    age = (today - lu).days  # positive = behind, negative = ahead
    if age > 2:
        return {"status": "stale",  "age_days": age, "last_updated": last_updated, "flag": True}
    if age < -14:
        return {"status": "future", "age_days": age, "last_updated": last_updated, "flag": True}
    return {"status": "ok", "age_days": age, "last_updated": last_updated, "flag": False}


def fetch_calendar(
    reference_date: date | None = None,
    window_days: int = 14,
    url: str = CALENDAR_URL,
) -> dict:
    """
    Fetch the calendar.json feed and filter it to events between
    `reference_date` and `reference_date + window_days` inclusive.

    Returns:
      {
        "freshness":   {"status": "ok|stale|future|unknown", "age_days": int, "last_updated": str, "flag": bool},
        "window_start": "YYYY-MM-DD",
        "window_end":   "YYYY-MM-DD",
        "events":       [ {date, title, category, importance, note}, ... ]  (sorted ascending)
        "raw_count":    int  (total events in feed before filtering)
      }
    """
    if reference_date is None:
        reference_date = date.today()
    window_end = reference_date + timedelta(days=window_days)

    with urllib.request.urlopen(url, timeout=20) as r:
        data = json.load(r)

    fresh = _freshness(data.get("lastUpdated", ""), reference_date)

    filtered = []
    for ev in data.get("events", []):
        try:
            ed = datetime.strptime(ev["date"], "%Y-%m-%d").date()
        except (KeyError, ValueError):
            continue
        if reference_date <= ed <= window_end:
            filtered.append({
                "date":        ev["date"],
                "date_obj":    ed,
                "title":       _clean(ev.get("title", "")),
                "category":    ev.get("category", ""),
                "importance":  (ev.get("importance") or "medium").lower(),
                "note":        _clean(ev.get("note", "")),
            })
    filtered.sort(key=lambda e: e["date"])

    return {
        "freshness":    fresh,
        "window_start": reference_date.isoformat(),
        "window_end":   window_end.isoformat(),
        "events":       filtered,
        "raw_count":    len(data.get("events", [])),
    }


def save_week_snapshot(
    events: list[dict],
    issue_date: date,
    snapshot_dir: str,
) -> str:
    """
    Persist a Monday issue's event list to disk so the following Friday can
    read it back and write actuals. Returns the absolute snapshot path.

    File naming: weekly snapshots are keyed by the Monday's ISO date, so
    Friday can find them with `(friday_date - timedelta(days=4))`.
    """
    os.makedirs(snapshot_dir, exist_ok=True)
    path = os.path.join(snapshot_dir, f"calendar-{issue_date.isoformat()}.json")

    # Strip date_obj before serialising (datetime objects aren't JSON-native)
    payload = {
        "issue_date": issue_date.isoformat(),
        "events": [
            {k: v for k, v in ev.items() if k != "date_obj"}
            for ev in events
        ],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return path


def load_week_snapshot(monday_date: date, snapshot_dir: str) -> dict | None:
    """Friday helper: load the Monday snapshot for the issue's week, if it exists."""
    path = os.path.join(snapshot_dir, f"calendar-{monday_date.isoformat()}.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    # smoke test
    today = date.today()
    result = fetch_calendar(today)
    print(f"freshness: {result['freshness']}")
    print(f"window: {result['window_start']} -> {result['window_end']}")
    print(f"events in window: {len(result['events'])} / {result['raw_count']} total")
    for ev in result["events"]:
        print(f"  {ev['date']}  [{ev['importance']:6}] {ev['category']:14} {ev['title']}")
