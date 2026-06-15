"""
Monday newsletter orchestrator.

This script is called by the Claude Code scheduled agent.
It fetches all data, generates charts, saves the draft HTML,
and uploads to Mailchimp (sending a test to the owner for approval).

Claude (the agent) calls this after writing the feature article
and passes it via --article argument.

Usage:
  python run_monday.py --article article.txt [--dry-run]
  python run_monday.py --article article.txt --chart-analysis "BTC testing $95k resistance..."
"""

import argparse
import json
import os
import sys
import time
from datetime import date

# Add project root to path
ROOT = os.path.dirname(__file__)
sys.path.insert(0, ROOT)

from data.fetch_prices     import fetch_all_prices, fetch_price_history
from data.fetch_events     import fetch_week_events
from data.fetch_calendar   import fetch_calendar, save_week_snapshot
from charts.render_png     import render_chart_png
from charts.freshness      import archive_stale_charts
from mailer.build_monday    import build_monday_email
from mailer.send_mailchimp  import draft_and_test, upload_image

CONFIG_DIR  = os.path.join(ROOT, "config")
ASSETS_FILE = os.path.join(CONFIG_DIR, "assets.json")
DRAFTS_DIR  = os.path.join(ROOT, "drafts")


def run(article: str, chart_analysis: str = "", dry_run: bool = False):
    today = date.today()
    print(f"\n[run_monday] Starting Monday run for {today.isoformat()}")

    # ── Load config ────────────────────────────────────────────────────────────
    with open(ASSETS_FILE) as f:
        assets = json.load(f)

    monday_cfg    = assets["monday"]
    asset_colors  = assets["asset_colors"]
    chart_symbols = monday_cfg["feature_charts"]

    # ── Fetch prices ────────────────────────────────────────────────────────────
    print("[run_monday] Fetching prices...")
    prices = fetch_all_prices()
    print(f"[run_monday] Got prices for: {list(prices.keys())}")

    # ── Fetch events (legacy chip data — retained for compatibility) ─────────
    print("[run_monday] Fetching week events...")
    events_data = fetch_week_events(today)
    print(f"[run_monday] Got {len(events_data.get('events', []))} events")

    # ── Fetch the editorial calendar (macropulse.uk/data/calendar.json) ──────
    print("[run_monday] Fetching editorial calendar (next 14 days)...")
    try:
        calendar_data = fetch_calendar(today, window_days=14)
        fresh = calendar_data["freshness"]
        flag  = " !!" if fresh["flag"] else ""
        print(f"[run_monday] calendar lastUpdated={fresh['last_updated']} "
              f"({fresh['status']}, age={fresh['age_days']}d){flag}")
        print(f"[run_monday] {len(calendar_data['events'])} events in window "
              f"({calendar_data['window_start']} -> {calendar_data['window_end']})")

        # Snapshot the FULL window for Friday's look-back (all importances).
        snapshot_path = save_week_snapshot(
            calendar_data["events"], today, DRAFTS_DIR,
        )
        print(f"[run_monday] Week snapshot saved: {snapshot_path}")

        # For the email body, show only HIGH-importance events to keep the
        # Coming Up section focused and under the 250-word cap.
        all_events = calendar_data["events"]
        high_only  = [e for e in all_events if (e.get("importance") or "").lower() == "high"]
        calendar_data = {**calendar_data, "events": high_only}
        print(f"[run_monday] Filtering Coming Up to HIGH-importance: "
              f"{len(high_only)}/{len(all_events)} events")
    except Exception as e:
        print(f"[run_monday] !! calendar fetch failed: {e}")
        calendar_data = None

    # ── Charts ────────────────────────────────────────────────────────────────
    # Preference order per symbol:
    #   1. A hand-annotated chart you exported from TradingView, dropped into
    #      drafts/charts/<symbol>.png (e.g. drafts/charts/btc.png). This is the
    #      intended weekly workflow — your support/resistance lines are the value.
    #   2. Fallback: an auto-generated 30-day matplotlib chart, so a scheduled
    #      run never ends up with an empty chart slot if no image was provided.
    # Either way the PNG is uploaded to Mailchimp's file manager and embedded as
    # a hosted image (Mailchimp strips data:image base64 URIs from campaign HTML).
    charts_dir = os.path.join(DRAFTS_DIR, "charts")
    # A new issue must not reuse last issue's screenshots. Archive any image
    # older than today; this issue's freshly-saved screenshots (mtime == today)
    # are kept so re-runs still embed them.
    stale = archive_stale_charts(charts_dir, today)
    if stale:
        print(f"[run_monday] Archived {len(stale)} stale chart image(s) from a previous issue: {stale}")
        print(f"[run_monday] Save THIS week's TradingView screenshots into {charts_dir} and re-run for the final.")
    print(f"[run_monday] Building charts for: {chart_symbols} (provided images dir: {charts_dir})")
    charts = {}
    for sym in chart_symbols:
        print(f"  -> {sym}...")

        # 1. Look for a provided TradingView image
        png_bytes = None
        source = None
        for ext in (".png", ".jpg", ".jpeg"):
            candidate = os.path.join(charts_dir, f"{sym.lower()}{ext}")
            if os.path.exists(candidate):
                with open(candidate, "rb") as f:
                    png_bytes = f.read()
                source = os.path.basename(candidate)
                print(f"     using provided chart: {source}")
                break

        # 2. Fallback to an auto-generated chart
        if png_bytes is None:
            history = fetch_price_history(sym, days=30)
            if not history:
                print(f"  X No provided image and no history data for {sym} — skipping")
                continue
            color = asset_colors.get(sym, "#ff9d2f")
            png_bytes = render_chart_png(history, symbol=sym, color=color)
            source = "auto-generated"
            print(f"     no provided image — auto-generated 30-day chart")
            time.sleep(0.5)  # CoinGecko rate limit

        alt = f"{sym} chart"
        ext = (source or "").lower()
        upload_name = f"chart-{sym.lower()}-{today.isoformat()}.png"

        if not dry_run:
            try:
                url = upload_image(png_bytes, upload_name)
                charts[sym] = (
                    f'<img src="{url}" alt="{alt}" '
                    f'width="560" style="display:block;width:100%;max-width:560px;'
                    f'height:auto;border:0;border-radius:12px;" />'
                )
            except Exception as e:
                print(f"  ! Upload failed for {sym}: {e} — embedding as data URI")
                import base64
                b64 = base64.b64encode(png_bytes).decode("ascii")
                charts[sym] = (
                    f'<img src="data:image/png;base64,{b64}" alt="{alt}" '
                    f'width="560" style="display:block;width:100%;max-width:560px;height:auto;border:0;border-radius:12px;" />'
                )
        else:
            import base64
            b64 = base64.b64encode(png_bytes).decode("ascii")
            charts[sym] = (
                f'<img src="data:image/png;base64,{b64}" alt="{alt}" '
                f'width="560" style="display:block;width:100%;max-width:560px;height:auto;border:0;border-radius:12px;" />'
            )

    # ── Build HTML ────────────────────────────────────────────────────────────
    print("[run_monday] Building HTML...")
    issue_date = today.strftime("%d %B %Y").lstrip("0")

    html = build_monday_email(
        prices=prices,
        events_data=events_data,
        charts=charts,
        article=article,
        chart_symbols=chart_symbols,
        issue_date=issue_date,
        calendar_data=calendar_data,
    )

    # ── Save draft ─────────────────────────────────────────────────────────
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    draft_path = os.path.join(DRAFTS_DIR, f"{today.isoformat()}-monday.html")
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[run_monday] Draft saved: {draft_path} ({len(html):,} chars)")

    if dry_run:
        print("[run_monday] Dry run — skipping Mailchimp upload.")
        return draft_path

    # ── Upload to Mailchimp + send test for review ────────────────────────────
    print("[run_monday] Uploading to Mailchimp and sending test email for review...")
    subject      = f"MacroPulse | Week Ahead | {issue_date}"
    preview_text = f"Key events and market setup for the week of {events_data.get('week_start', today.isoformat())}"

    try:
        # send_test=True (default): owner gets a test email to review.
        # Mailchimp prefixes the test's subject with [TEST]; the live send
        # via --send re-PATCHes the clean subject so subscribers never see it.
        campaign_id = draft_and_test(draft_path, subject, preview_text)
        print(f"\n[run_monday] OK Test sent. Campaign ID: {campaign_id}")
        print(f"[run_monday] Review the test email in your inbox.")
        print(f"[run_monday] After edits, re-send a test:")
        print(f"  python mailer/send_mailchimp.py --campaign-id {campaign_id} --test")
        print(f"[run_monday] When approved, publish to the list:")
        print(f"  python mailer/send_mailchimp.py --campaign-id {campaign_id} --send")
    except Exception as e:
        print(f"[run_monday] Mailchimp error: {e}")
        print(f"[run_monday] Draft is saved locally at: {draft_path}")

    return draft_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Monday MacroPulse email")
    parser.add_argument("--article",        default="",
                        help="Path to feature article text file, or inline text")
    parser.add_argument("--chart-analysis", default="",
                        help="2-3 sentence chart analysis written by Claude")
    parser.add_argument("--dry-run",        action="store_true",
                        help="Generate HTML but don't send to Mailchimp")
    args = parser.parse_args()

    article_text = ""
    if args.article:
        if os.path.exists(args.article):
            with open(args.article, encoding="utf-8") as f:
                article_text = f.read()
        else:
            article_text = args.article  # inline text

    run(
        article=article_text,
        chart_analysis=args.chart_analysis,
        dry_run=args.dry_run,
    )
