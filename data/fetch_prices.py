"""
Fetch current prices and 7-day / week-on-week changes for all dashboard assets.
Outputs JSON to stdout when run directly.

Sources:
  - CoinGecko free API (no key) for crypto
  - yfinance for SP500, Gold, Oil
"""

import json
import sys
import time
import requests

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SUI": "sui",
    "DOGE": "dogecoin",
}

YAHOO_TICKERS = {
    "SP500": "^GSPC",
    "GOLD":  "GC=F",
    "OIL":   "CL=F",
}

COINGECKO_BASE = "https://api.coingecko.com/api/v3"


def fetch_crypto_prices() -> dict:
    """Returns {SYMBOL: {price, change_24h, change_7d}} for all crypto assets."""
    ids = ",".join(COINGECKO_IDS.values())
    # /coins/markets returns price_change_percentage_7d_in_currency when requested;
    # /simple/price has no 7d field — that endpoint only supports 24h change.
    url = (
        f"{COINGECKO_BASE}/coins/markets"
        f"?vs_currency=usd&ids={ids}"
        f"&price_change_percentage=7d"
    )
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        items = resp.json()  # list of coin objects
    except Exception as e:
        print(f"[fetch_prices] CoinGecko error: {e}", file=sys.stderr)
        return {}

    by_id = {item["id"]: item for item in items if "id" in item}
    result = {}
    for symbol, cg_id in COINGECKO_IDS.items():
        item = by_id.get(cg_id)
        if item:
            result[symbol] = {
                "price":      item.get("current_price", 0),
                "change_24h": item.get("price_change_percentage_24h", 0),
                "change_7d":  item.get("price_change_percentage_7d_in_currency", 0),
            }
    return result


def fetch_trad_prices() -> dict:
    """Returns {SYMBOL: {price, change_7d}} for SP500, Gold, Oil."""
    if not HAS_YFINANCE:
        print("[fetch_prices] yfinance not installed, skipping trad assets", file=sys.stderr)
        return {}

    result = {}
    for symbol, ticker in YAHOO_TICKERS.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="10d")
            if len(hist) >= 2:
                current  = float(hist["Close"].iloc[-1])
                week_ago = float(hist["Close"].iloc[0])
                change_7d = ((current - week_ago) / week_ago) * 100
                result[symbol] = {
                    "price":      current,
                    "change_7d":  change_7d,
                    "change_24h": ((current - float(hist["Close"].iloc[-2])) / float(hist["Close"].iloc[-2])) * 100,
                }
        except Exception as e:
            print(f"[fetch_prices] yfinance error for {symbol}: {e}", file=sys.stderr)

    return result


def fetch_price_history(symbol: str, days: int = 30) -> list:
    """
    Returns list of [unix_timestamp_seconds, price] for chart generation.
    Works for both crypto (CoinGecko) and trad assets (yfinance).
    """
    if symbol in COINGECKO_IDS:
        cg_id = COINGECKO_IDS[symbol]
        url = (
            f"{COINGECKO_BASE}/coins/{cg_id}/market_chart"
            f"?vs_currency=usd&days={days}&interval=daily"
        )
        try:
            time.sleep(0.5)  # CoinGecko free tier rate limit
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            prices = resp.json().get("prices", [])
            return [[p[0] / 1000, p[1]] for p in prices]
        except Exception as e:
            print(f"[fetch_prices] History error for {symbol}: {e}", file=sys.stderr)
            return []

    if symbol in YAHOO_TICKERS and HAS_YFINANCE:
        ticker = YAHOO_TICKERS[symbol]
        try:
            t    = yf.Ticker(ticker)
            hist = t.history(period=f"{days + 5}d")
            return [
                [int(row.name.timestamp()), float(row["Close"])]
                for _, row in hist.iterrows()
            ][-days:]
        except Exception as e:
            print(f"[fetch_prices] History error for {symbol}: {e}", file=sys.stderr)
            return []

    return []


def fetch_all_prices() -> dict:
    crypto = fetch_crypto_prices()
    trad   = fetch_trad_prices()
    return {**crypto, **trad}


if __name__ == "__main__":
    prices = fetch_all_prices()
    print(json.dumps(prices, indent=2))
