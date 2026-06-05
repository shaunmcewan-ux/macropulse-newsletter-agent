"""
Friday newsletter orchestrator.
Fetches prices, indicators, generates charts, assembles HTML, uploads to Mailchimp.
"""

import argparse
import json
import os
import sys
import time
from datetime import date

ROOT = os.path.dirname(__file__)
sys.path.insert(0, ROOT)

from data.fetch_prices      import fetch_all_prices, fetch_price_history
from data.fetch_indicators  import fetch_global_indicators
from charts.render_png      import render_chart_png
from mailer.build_friday     import build_friday_email
from mailer.send_mailchimp   import draft_and_test, upload_image

CONFIG_DIR    = os.path.join(ROOT, "config")
ASSETS_FILE   = os.path.join(CONFIG_DIR, "assets.json")
PORTFOLIO_FILE = os.path.join(CONFIG_DIR, "portfolio.json")
DRAFTS_DIR    = os.path.join(ROOT, "drafts")


def run(article: str, dry_run: bool = False):
    today = date.today()
    print(f"\n[run_friday] Starting Friday run for {today.isoformat()}")

    with open(ASSETS_FILE)    as f: assets    = json.load(f)
    with open(PORTFOLIO_FILE) as f: portfolio = json.load(f)

    friday_cfg    = assets["friday"]
    asset_colors  = assets["asset_colors"]
    chart_symbols = friday_cfg["feature_charts"]

    # ── Fetch prices ──────────────────────────────────────────────────────────
    print("[run_friday] Fetching prices...")
    prices = fetch_all_prices()

    # ── Fetch indicators ──────────────────────────────────────────────────────
    print("[run_friday] Fetching global indicators...")
    indicators = fetch_global_indicators()
    print(f"[run_friday] BTC.D: {indicators.get('BTC_D')}%  TOTAL: {indicators.get('TOTAL_fmt')}")

    # ── Generate feature charts (indicators) ──────────────────────────────────
    print(f"[run_friday] Generating charts for: {chart_symbols}")
    # Chart loading mirrors run_monday: provided TradingView export first
    # (drafts/charts/<sym.lower()>.{png,jpg,jpeg}), auto-gen fallback only for
    # symbols our price feeds support; everything else is skipped (the email
    # builder will render a "Chart unavailable" placeholder for that slot).
    charts_dir = os.path.join(DRAFTS_DIR, "charts")
    charts = {}
    for sym in chart_symbols:
        print(f"  -> {sym}...")

        # 1. Provided image takes priority
        png_bytes = None
        for ext in (".png", ".jpg", ".jpeg"):
            candidate = os.path.join(charts_dir, f"{sym.lower()}{ext}")
            if os.path.exists(candidate):
                with open(candidate, "rb") as f:
                    png_bytes = f.read()
                print(f"     using provided chart: {os.path.basename(candidate)}")
                break

        # 2. Fallback: auto-generate from our price feed (only for known symbols)
        if png_bytes is None:
            if sym in ("BTC", "ETH", "SUI", "DOGE", "SP500", "GOLD", "OIL"):
                history = fetch_price_history(sym, days=30)
            else:
                # Indicator symbols (ISM, 10Y2Y, BTC_D, TOTAL3, etc.) have no
                # auto-gen path — they need a hand-exported chart in drafts/charts/.
                print(f"     no provided image and no auto-gen path for {sym} - skipping")
                continue
            if not history:
                print(f"     no price history for {sym} - skipping")
                continue
            color = asset_colors.get(sym, "#ff9d2f")
            is_mc = sym in ("TOTAL", "TOTAL2", "TOTAL3")
            png_bytes = render_chart_png(history, symbol=sym, color=color, is_mcap=is_mc)
            print(f"     no provided image - auto-generated 30-day chart")
        if not dry_run:
            try:
                url = upload_image(png_bytes, f"chart-{sym.lower()}-{today.isoformat()}.png")
                charts[sym] = (
                    f'<img src="{url}" alt="{sym} 30-day chart" '
                    f'width="560" style="display:block;width:100%;max-width:560px;'
                    f'height:auto;border:0;" />'
                )
            except Exception as e:
                print(f"  ! Upload failed for {sym}: {e} — embedding as data URI")
                import base64
                b64 = base64.b64encode(png_bytes).decode("ascii")
                charts[sym] = (
                    f'<img src="data:image/png;base64,{b64}" alt="{sym} 30-day chart" '
                    f'width="560" style="display:block;width:100%;max-width:560px;height:auto;border:0;" />'
                )
        else:
            import base64
            b64 = base64.b64encode(png_bytes).decode("ascii")
            charts[sym] = (
                f'<img src="data:image/png;base64,{b64}" alt="{sym} 30-day chart" '
                f'width="560" style="display:block;width:100%;max-width:560px;height:auto;border:0;" />'
            )
        time.sleep(0.5)

    # ── Build HTML ────────────────────────────────────────────────────────────
    print("[run_friday] Building HTML...")
    issue_date = today.strftime("%d %B %Y").lstrip("0")

    html = build_friday_email(
        prices=prices,
        indicators=indicators,
        portfolio_config=portfolio,
        charts=charts,
        article=article,
        chart_symbols=chart_symbols,
        issue_date=issue_date,
    )

    # ── Save draft ────────────────────────────────────────────────────────────
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    draft_path = os.path.join(DRAFTS_DIR, f"{today.isoformat()}-friday.html")
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[run_friday] Draft saved: {draft_path} ({len(html):,} chars)")

    if dry_run:
        print("[run_friday] Dry run — skipping Mailchimp upload.")
        return draft_path

    # ── Upload to Mailchimp + send test for review ────────────────────────────
    print("[run_friday] Uploading to Mailchimp and sending test email for review...")
    subject      = f"MacroPulse | Week in Review | {issue_date}"
    preview_text = "This week's market recap, indicator pulse, and portfolio performance."

    try:
        # send_test=True (default): owner gets a test email; live send re-PATCHes
        # the clean subject so subscribers never see [TEST]. See run_monday.py.
        campaign_id = draft_and_test(draft_path, subject, preview_text)
        print(f"\n[run_friday] OK Test sent. Campaign ID: {campaign_id}")
        print(f"[run_friday] Review the test email in your inbox.")
        print(f"[run_friday] After edits, re-send a test:")
        print(f"  python mailer/send_mailchimp.py --campaign-id {campaign_id} --test")
        print(f"[run_friday] When approved, publish to the list:")
        print(f"  python mailer/send_mailchimp.py --campaign-id {campaign_id} --send")
    except Exception as e:
        print(f"[run_friday] Mailchimp error: {e}")
        print(f"[run_friday] Draft saved at: {draft_path}")

    return draft_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--article",  default="")
    parser.add_argument("--dry-run",  action="store_true")
    args = parser.parse_args()

    article_text = ""
    if args.article:
        if os.path.exists(args.article):
            with open(args.article, encoding="utf-8") as f:
                article_text = f.read()
        else:
            article_text = args.article

    run(article=article_text, dry_run=args.dry_run)
