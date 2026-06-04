"""
Fetch upcoming economic events for the current week (Mon–Fri).
Combines:
  - Hardcoded events from config/events_2026.json (FOMC, CPI, NFP, BoE)
  - yfinance earnings calendar for major tickers
Outputs JSON to stdout when run directly.
"""

import json
import os
import sys
from datetime import date, timedelta

import requests

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", "config")

# Single source of truth: the live website's published events file, so the
# newsletter shows exactly what macropulse.uk serves and the two never drift.
# Resolution order (each is a fallback for the previous, so a scheduled run
# never hard-fails):
#   1. Live published URL  — the real source of truth once deployed
#   2. Website repo's local public/data copy — if this machine has the site repo
#   3. Newsletter's bundled config/events_2026.json — last resort
EVENTS_URL = os.environ.get(
    "MACROPULSE_EVENTS_URL",
    "https://www.macropulse.uk/data/events_2026.json",
)
_WEBSITE_EVENTS = os.path.join(
    os.path.expanduser("~"),
    "OneDrive", "MacroPulse", "macropulse-site", "public", "data", "events_2026.json",
)
_LOCAL_EVENTS = os.path.join(CONFIG_DIR, "events_2026.json")
EVENTS_FILE = _WEBSITE_EVENTS if os.path.exists(_WEBSITE_EVENTS) else _LOCAL_EVENTS


def load_calendar() -> dict:
    """Load the raw events calendar from the single source of truth.

    Tries the live published URL first, then the local site/bundled files.
    Prints the source used to stderr so each run's provenance is obvious.
    """
    # 1. Live published URL
    try:
        resp = requests.get(EVENTS_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and data:
            print(f"[fetch_events] events source: live URL {EVENTS_URL}", file=sys.stderr)
            return data
    except Exception as e:
        print(f"[fetch_events] live URL unavailable ({e}); using local file", file=sys.stderr)

    # 2/3. Local file (website copy if present, else bundled fallback)
    try:
        with open(EVENTS_FILE, "r", encoding="utf-8") as f:
            print(f"[fetch_events] events source: local file {EVENTS_FILE}", file=sys.stderr)
            return json.load(f)
    except Exception as e:
        print(f"[fetch_events] Could not load any events source: {e}", file=sys.stderr)
        return {}

# Major tickers to check for earnings
EARNINGS_WATCHLIST = [
    "NVDA", "AAPL", "MSFT", "GOOGL", "META", "AMZN", "TSLA",
    "JPM", "GS", "BAC", "COIN", "MSTR", "MARA",
]

EVENT_TYPE_EMOJI = {
    "rate_decision": "🏦",
    "inflation":     "📊",
    "employment":    "👷",
    "gdp":           "📈",
    "crypto":        "₿",
    "earnings":      "💰",
    "other":         "📅",
}


def get_week_range(reference_date: date = None) -> tuple:
    """Returns (monday, friday) for the week containing reference_date."""
    if reference_date is None:
        reference_date = date.today()
    monday = reference_date - timedelta(days=reference_date.weekday())
    friday = monday + timedelta(days=4)
    return monday, friday


def fetch_scheduled_events(week_start: date, week_end: date) -> list:
    """Load events from the shared JSON calendar that fall within the week."""
    events = []
    calendar = load_calendar()
    if not calendar:
        return []

    all_events = []
    for category in calendar.values():
        all_events.extend(category)

    for event in all_events:
        try:
            event_date = date.fromisoformat(event["date"])
            if week_start <= event_date <= week_end:
                events.append({
                    "date":  event["date"],
                    "day":   event_date.strftime("%A"),
                    "label": event["label"],
                    "type":  event.get("type", "other"),
                    "emoji": EVENT_TYPE_EMOJI.get(event.get("type", "other"), "📅"),
                })
        except (ValueError, KeyError):
            continue

    return sorted(events, key=lambda x: x["date"])


def fetch_earnings_events(week_start: date, week_end: date) -> list:
    """Fetch upcoming earnings for major tickers that fall within the week."""
    if not HAS_YFINANCE:
        return []

    events = []
    for ticker in EARNINGS_WATCHLIST:
        try:
            t = yf.Ticker(ticker)
            cal = t.calendar
            if cal is None:
                continue
            # earnings_date can be a single date or a list
            earnings_date = None
            if hasattr(cal, "get"):
                ed = cal.get("Earnings Date")
                if ed is not None:
                    if hasattr(ed, "__len__") and len(ed) > 0:
                        earnings_date = ed[0].date() if hasattr(ed[0], "date") else ed[0]
                    elif hasattr(ed, "date"):
                        earnings_date = ed.date()

            if earnings_date and week_start <= earnings_date <= week_end:
                events.append({
                    "date":  earnings_date.isoformat(),
                    "day":   earnings_date.strftime("%A"),
                    "label": f"{ticker} Earnings",
                    "type":  "earnings",
                    "emoji": "💰",
                })
        except Exception:
            continue

    return sorted(events, key=lambda x: x["date"])


def fetch_week_events(reference_date: date = None) -> dict:
    """
    Returns all events for the week containing reference_date.
    {
      "week_start": "YYYY-MM-DD",
      "week_end":   "YYYY-MM-DD",
      "events":     [{date, day, label, type, emoji}, ...]
    }
    """
    week_start, week_end = get_week_range(reference_date)
    scheduled = fetch_scheduled_events(week_start, week_end)
    earnings  = fetch_earnings_events(week_start, week_end)

    # Merge and deduplicate
    all_events = scheduled + earnings
    seen = set()
    unique = []
    for e in all_events:
        key = (e["date"], e["label"])
        if key not in seen:
            seen.add(key)
            unique.append(e)

    return {
        "week_start": week_start.isoformat(),
        "week_end":   week_end.isoformat(),
        "events":     sorted(unique, key=lambda x: x["date"]),
    }


if __name__ == "__main__":
    result = fetch_week_events()
    print(json.dumps(result, indent=2))
