# HANDOFF — MacroPulse scorecard (newsletter)

Render the 8-indicator scorecard in the same shape the dashboard
shows it, so the newsletter and the website agree row-for-row.

═══════════════════════════════════════════════════════════════════
STEP 1 — FETCH
═══════════════════════════════════════════════════════════════════

  https://www.macropulse.uk/data/indicators.json

═══════════════════════════════════════════════════════════════════
STEP 2 — DATA SHAPE
═══════════════════════════════════════════════════════════════════

{
  "lastUpdated": "YYYY-MM-DD",
  "dial": { "state": "BTC Accumulation", "summary": "..." },
  "indicators": [
    {
      "name": "Global Liquidity (Global M2)",
      "value": "$108.4T",
      "trend": "up" | "down" | "flat",
      "status": "supportive" | "neutral" | "headwind",
      "note": "30–60 word editorial note from the bot"
    },
    ...                            // exactly 8 indicators in this order
  ]
}

═══════════════════════════════════════════════════════════════════
STEP 3 — SANITY CHECKS
═══════════════════════════════════════════════════════════════════

  A) lastUpdated should be today or yesterday (UTC). Older than 2
     days → STOP and flag.

  B) Exactly 8 indicators, in this order, with these `name` values
     (verbatim):
       1. Global Liquidity (Global M2)
       2. ISM Manufacturing PMI
       3. DXY (US Dollar Index)
       4. Real Yields (US10Y - CPI)
       5. 2s10s Yield Curve
       6. Fed Balance Sheet
       7. BTC Funding Rates (perps avg)
       8. Stablecoin Dominance

  C) Each indicator has status ∈ {supportive, neutral, headwind}
     and trend ∈ {up, down, flat}. If anything is missing or
     unrecognised, flag.

═══════════════════════════════════════════════════════════════════
STEP 4 — REFERENCE TABLES (use these exact labels and links)
═══════════════════════════════════════════════════════════════════

Short labels — same as dashboard column 1:
  Global Liquidity (Global M2)      → Global M2
  ISM Manufacturing PMI             → ISM PMI
  DXY (US Dollar Index)             → DXY
  Real Yields (US10Y - CPI)         → Real 10y
  2s10s Yield Curve                 → 2s10s curve
  Fed Balance Sheet                 → Fed sheet
  BTC Funding Rates (perps avg)     → BTC funding
  Stablecoin Dominance              → Stables %

TradingView chart links — same as the ↗ icon on the dashboard:
  Global Liquidity (Global M2)      → https://www.tradingview.com/symbols/ECONOMICS-USM2/
  ISM Manufacturing PMI             → https://www.tradingview.com/symbols/ECONOMICS-USBCOI/
  DXY (US Dollar Index)             → https://www.tradingview.com/symbols/TVC-DXY/
  Real Yields (US10Y - CPI)         → https://www.tradingview.com/symbols/FRED-DFII10/
  2s10s Yield Curve                 → https://www.tradingview.com/symbols/FRED-T10Y2Y/
  Fed Balance Sheet                 → https://www.tradingview.com/symbols/FRED-WALCL/
  BTC Funding Rates (perps avg)     → https://www.coinglass.com/FundingRate
  Stablecoin Dominance              → https://www.tradingview.com/symbols/CRYPTOCAP-USDT.D/

Glossary anchor links — the indicator name in each row should link
to its definition on the website:
  Global Liquidity (Global M2)      → https://www.macropulse.uk/methodology/glossary/#m2
  ISM Manufacturing PMI             → https://www.macropulse.uk/methodology/glossary/#ism
  DXY (US Dollar Index)             → https://www.macropulse.uk/methodology/glossary/#dxy
  Real Yields (US10Y - CPI)         → https://www.macropulse.uk/methodology/glossary/#real-yields
  2s10s Yield Curve                 → https://www.macropulse.uk/methodology/glossary/#curve
  Fed Balance Sheet                 → https://www.macropulse.uk/methodology/glossary/#fed-sheet
  BTC Funding Rates (perps avg)     → https://www.macropulse.uk/methodology/glossary/#funding
  Stablecoin Dominance              → https://www.macropulse.uk/methodology/glossary/#stables

Trend arrows:
  up   → ↑   (use green styling if rendered in HTML)
  down → ↓   (red)
  flat → →   (grey)

Status labels (capitalised in table cells, lower-case in prose):
  supportive → Supportive
  neutral    → Neutral
  headwind   → Headwind

═══════════════════════════════════════════════════════════════════
STEP 5 — RENDER. Beehiiv-friendly Markdown. Two formats; produce
both unless I tell you otherwise.
═══════════════════════════════════════════════════════════════════

▸ Format A — compact Markdown table (the canonical render, mirrors
  the dashboard's column order):

  ## The scorecard

  | Indicator | Status | Trend | Latest |
  |---|---|---|---|
  | **[Global M2](glossary url)** &nbsp;[↗](TV url)<br>$108.4T | Supportive | ↑ | Marginal expansion; oxygen continuing to reach risk. |
  | **[ISM PMI](glossary url)** &nbsp;[↗](TV url)<br>52.7 | Supportive | → | Fourth straight month of expansion; June 1 print is the catalyst. |
  | ... (six more rows in the JSON order) |

  Notes for the table:
   - Indicator cell: bold short-label linked to glossary, then a
     small [↗](TradingView) link, then a line break, then the value
     in plain text.
   - Latest cell: tighten the bot's `note` to ≈ 22 words. Keep
     numbers (52.7%, $108.4T, +0.43%, +115K), keep catalyst
     references ("June 10 CPI", "June 16–17 FOMC"), drop boilerplate
     ("released at 8:30 a.m. ET").
   - Cap rows at one short paragraph each.

▸ Format B — fallback bullet list (if the table renders poorly in
  Beehiiv preview):

  ## The scorecard

  • **[Global M2](glossary url)** — $108.4T, Supportive. ↑ Marginal
    expansion; oxygen continuing to reach risk. [Chart →](TV url)
  • **[ISM PMI](glossary url)** — 52.7, Supportive. → Fourth straight
    month of expansion; June 1 print is the catalyst. [Chart →](TV url)
  • ... (six more bullets in the JSON order)

═══════════════════════════════════════════════════════════════════
VOICE
═══════════════════════════════════════════════════════════════════

  - Calm, research-led, editorial. Buy-side morning-note register.
  - Numbers tabular: 3.8% YoY, +115K, $6.71T, +0.43%.
  - Status words lower-case in prose: "supportive", "neutral",
    "headwind". Capitalised inside the table cells.
  - Arrows: ↑ up, ↓ down, → flat.
  - No exclamation marks, no emojis (the arrows are not emojis).
  - One italic per paragraph at most; reserve italics for state
    names or proper-noun emphasis.

═══════════════════════════════════════════════════════════════════
HARD RULES
═══════════════════════════════════════════════════════════════════

  1. Never re-judge an indicator. The JSON's status and trend are
     authoritative.
  2. Never invent values or change a label. If the JSON disagrees
     with what you "expected", surface the disagreement — the JSON
     wins.
  3. Indicators always render in the order they appear in
     indicators.json. That order matches the dashboard.
  4. Short labels exactly as listed in Step 4. No variants.
  5. Don't reproduce the bot's full `note` — clamp to ≈ 22 words for
     the Latest cell. The full note is on the website if a reader
     wants the long form (the row indicator links to glossary, not
     to the note).

Start by fetching indicators.json and reporting back:
  - lastUpdated
  - the full scorecard tally (X supportive · Y neutral · Z headwind)
  - any indicator with missing/unrecognised fields
Then render both Format A and Format B unless instructed otherwise.
