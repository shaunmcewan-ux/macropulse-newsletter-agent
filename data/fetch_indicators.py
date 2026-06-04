"""
Fetch macro indicators: BTC Dominance, ETH/BTC ratio, TOTAL/TOTAL2/TOTAL3 market caps.
Uses CoinGecko /global endpoint (free, no key).
Outputs JSON to stdout when run directly.
"""

import json
import sys
import requests

COINGECKO_BASE = "https://api.coingecko.com/api/v3"


def fetch_global_indicators() -> dict:
    """
    Returns:
      BTC_D      - BTC dominance %
      ETH_BTC    - ETH/BTC price ratio
      TOTAL      - Total crypto market cap (USD)
      TOTAL2     - Total minus BTC (USD)
      TOTAL3     - Total minus BTC and ETH (USD)
      TOTAL_7D   - 7-day change in total market cap %
    """
    try:
        resp = requests.get(f"{COINGECKO_BASE}/global", timeout=15)
        resp.raise_for_status()
        data = resp.json()["data"]
    except Exception as e:
        print(f"[fetch_indicators] CoinGecko global error: {e}", file=sys.stderr)
        return {}

    total_mcap = data["total_market_cap"].get("usd", 0)
    pct        = data["market_cap_percentage"]

    btc_pct = pct.get("btc", 0)
    eth_pct = pct.get("eth", 0)

    btc_mcap = total_mcap * (btc_pct / 100)
    eth_mcap = total_mcap * (eth_pct / 100)

    # ETH/BTC price ratio requires separate price call
    eth_btc_ratio = None
    try:
        price_resp = requests.get(
            f"{COINGECKO_BASE}/simple/price?ids=ethereum,bitcoin&vs_currencies=usd",
            timeout=10
        )
        price_data = price_resp.json()
        eth_price = price_data.get("ethereum", {}).get("usd", 0)
        btc_price = price_data.get("bitcoin", {}).get("usd", 1)
        if btc_price > 0:
            eth_btc_ratio = eth_price / btc_price
    except Exception:
        pass

    return {
        "BTC_D":       round(btc_pct, 2),
        "ETH_BTC":     round(eth_btc_ratio, 6) if eth_btc_ratio else None,
        "TOTAL":       total_mcap,
        "TOTAL2":      total_mcap - btc_mcap,
        "TOTAL3":      total_mcap - btc_mcap - eth_mcap,
        "total_mcap_change_24h": data.get("market_cap_change_percentage_24h_usd", 0),
    }


def format_market_cap(value: float) -> str:
    """Format a market cap value to human-readable string, e.g. $2.4T"""
    if value >= 1e12:
        return f"${value / 1e12:.2f}T"
    if value >= 1e9:
        return f"${value / 1e9:.1f}B"
    return f"${value:,.0f}"


if __name__ == "__main__":
    indicators = fetch_global_indicators()
    # Add formatted values for display
    for key in ["TOTAL", "TOTAL2", "TOTAL3"]:
        if key in indicators:
            indicators[f"{key}_fmt"] = format_market_cap(indicators[key])
    print(json.dumps(indicators, indent=2))
