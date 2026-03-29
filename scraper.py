import asyncio
import httpx
from datetime import datetime

from scanner import (
    fetch,
    STOCK_SYMBOLS, CRYPTO_SYMBOLS,
    FOREX_SYMBOLS, COMMODITY_SYMBOLS, INDEX_SYMBOLS,
)
from news import scrape_news
from analyst import analyze_all
from signals import generate_all
from insights import generate_all_insights
from export import (
    print_stocks, print_crypto, print_forex,
    print_commodities, print_indices, print_news,
    print_insights, print_analysis, print_signals,
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
  TradingView Real-Time Financial Scraper |_|  v3.0        
"""


async def main():
    print(BANNER)
    t0 = datetime.now()
    print(f"  Started at: {t0.strftime('%Y-%m-%d %H:%M:%S')}\n")

    print("  [1/2] Fetching market data + news concurrently...")
    async with httpx.AsyncClient(timeout=20) as client:
        (
            stocks, crypto, forex, commodities, indices, news
        ) = await asyncio.gather(
            fetch("america", STOCK_SYMBOLS,     client),
            fetch("crypto",  CRYPTO_SYMBOLS,    client),
            fetch("forex",   FOREX_SYMBOLS,     client),
            fetch("global",  COMMODITY_SYMBOLS, client),
            fetch("global",  INDEX_SYMBOLS,     client),
            scrape_news(max_scrolls=3),
        )
    print(f"  [2/2] Done in {(datetime.now()-t0).seconds}s - printing results...")

    # -- Market data tables ----------------------------------------------------
    print_stocks(stocks)
    print_crypto(crypto)
    print_forex(forex)
    print_commodities(commodities)
    print_indices(indices)
    print_news(news)

    # -- AI-Powered Insights ---------------------------------------------------
    insights = generate_all_insights(stocks, crypto, news)
    print_insights(insights)

    # -- Investment Analysis ---------------------------------------------------
    analysis = analyze_all(stocks, crypto, news)
    print_analysis(analysis)

    # -- Real-Time Trading Signals ---------------------------------------------
    signals = generate_all(analysis, stocks, crypto)
    print_signals(signals)

    # -- Summary ---------------------------------------------------------------
    bullish    = sum(1 for n in news if n.get("sentiment") == "bullish")
    bearish    = sum(1 for n in news if n.get("sentiment") == "bearish")
    buy_sigs   = sum(1 for s in stocks + crypto if s.get("signal") in ("BUY", "STRONG BUY"))
    sell_sigs  = sum(1 for s in stocks + crypto if s.get("signal") in ("SELL", "STRONG SELL"))
    print(f"\n  News Sentiment -> Bullish: {bullish}  Bearish: {bearish}  Neutral: {len(news)-bullish-bearish}")
    print(f"  Market Signals -> Buy: {buy_sigs}  Sell: {sell_sigs}")

    # -- Export ----------------------------------------------------------------
    output = {
        "fetched_at":  datetime.utcnow().isoformat() + "Z",
        "stocks":      stocks,
        "crypto":      crypto,
        "forex":       forex,
        "commodities": commodities,
        "indices":     indices,
        "news":        news,
        "insights":    insights,
        "analysis":    analysis,
        "signals":     signals,
        "summary": {
            "total_instruments": len(stocks) + len(crypto) + len(forex) + len(commodities) + len(indices),
            "total_news":        len(news),
            "bullish_news":      bullish,
            "bearish_news":      bearish,
            "buy_signals":       buy_sigs,
            "sell_signals":      sell_sigs,
            "macro_regime":      insights.get("macro_regime", "N/A"),
        },
    }

    save_json(output)
    save_csv(output)
    print(f"\n  Done. {output['summary']['total_instruments']} instruments + {len(news)} articles.\n")


if __name__ == "__main__":
    asyncio.run(main())
