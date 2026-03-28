import asyncio
import httpx
from datetime import datetime

from scanner import (
    fetch,
    STOCK_SYMBOLS, CRYPTO_SYMBOLS,
    FOREX_SYMBOLS, COMMODITY_SYMBOLS, INDEX_SYMBOLS,
)
from news import scrape_news
from export import (
    print_stocks, print_crypto, print_forex,
    print_commodities, print_indices, print_news,
    save_json, save_csv,
)

BANNER = r"""
 _____ _             _____                                 
|_   _| |           /  ___|                                
  | | | |__   ___   \ `--.  ___ _ __ __ _ _ __   ___ _ __ 
  | | | '_ \ / _ \   `--. \/ __| '__/ _` | '_ \ / _ \ '__|
  | | | | | |  __/  /\__/ / (__| | | (_| | |_) |  __/ |   
  \_/ |_| |_|\___|  \____/ \___|_|  \__,_| .__/ \___|_|   
                                          | |              
  TradingView Real-Time Financial Scraper |_|  v2.0        
"""


async def main():
    print(BANNER)
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    print("  Fetching: Stocks | Crypto | Forex | Commodities | Indices | News\n")

    async with httpx.AsyncClient(timeout=30) as client:
        (
            stocks, crypto, forex, commodities, indices, news
        ) = await asyncio.gather(
            fetch("america", STOCK_SYMBOLS,    client),
            fetch("crypto",  CRYPTO_SYMBOLS,   client),
            fetch("forex",   FOREX_SYMBOLS,    client),
            fetch("america", COMMODITY_SYMBOLS, client),
            fetch("america", INDEX_SYMBOLS,    client),
            scrape_news(max_scrolls=6),
        )

    # ── Print ──────────────────────────────────────────────
    print_stocks(stocks)
    print_crypto(crypto)
    print_forex(forex)
    print_commodities(commodities)
    print_indices(indices)
    print_news(news)

    # ── Summary stats ──────────────────────────────────────
    bullish = sum(1 for n in news if n.get("sentiment") == "bullish")
    bearish = sum(1 for n in news if n.get("sentiment") == "bearish")
    print(f"\n  News Sentiment → Bullish: {bullish}  Bearish: {bearish}  Neutral: {len(news)-bullish-bearish}")

    buy_signals    = sum(1 for s in stocks + crypto if s.get("signal") in ("BUY", "STRONG BUY"))
    sell_signals   = sum(1 for s in stocks + crypto if s.get("signal") in ("SELL", "STRONG SELL"))
    print(f"  Market Signals → Buy: {buy_signals}  Sell: {sell_signals}")

    # ── Export ─────────────────────────────────────────────
    output = {
        "fetched_at":   datetime.utcnow().isoformat() + "Z",
        "stocks":       stocks,
        "crypto":       crypto,
        "forex":        forex,
        "commodities":  commodities,
        "indices":      indices,
        "news":         news,
        "summary": {
            "total_instruments": len(stocks) + len(crypto) + len(forex) + len(commodities) + len(indices),
            "total_news":        len(news),
            "bullish_news":      bullish,
            "bearish_news":      bearish,
            "buy_signals":       buy_signals,
            "sell_signals":      sell_signals,
        },
    }

    save_json(output)
    save_csv(output)
    print(f"\n  Done in one shot. {output['summary']['total_instruments']} instruments + {len(news)} news articles.\n")


if __name__ == "__main__":
    asyncio.run(main())
