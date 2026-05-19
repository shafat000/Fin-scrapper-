import asyncio
import httpx
from datetime import datetime

from scanner import (
    fetch,
    STOCK_SYMBOLS, CRYPTO_SYMBOLS,
    FOREX_SYMBOLS, COMMODITY_SYMBOLS, INDEX_SYMBOLS,
)
from news import scrape_news
from microstructure import run_microstructure
from features import run_feature_extraction
from regime import detect_regime
from analyst import analyze_all
from signals import generate_all
from insights import generate_all_insights
from ai_analyst import run_ai_analysis
from export import (
    print_stocks, print_crypto, print_forex,
    print_commodities, print_indices, print_news,
    print_insights, print_analysis, print_signals,
    print_regime, print_ai_analysis,
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
  TradingView Real-Time Financial Scraper |_|  v4.0        
"""


async def main():
    print(BANNER)
    t0 = datetime.now()
    print(f"  Started at: {t0.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # ── Layer 1: Market Data ──────────────────────────────────────────────────
    print("  [Market Data] Fetching all sources concurrently...")
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
    print(f"  Done in {(datetime.now()-t0).seconds}s\n")

    # Print market data tables
    print_stocks(stocks)
    print_crypto(crypto)
    print_forex(forex)
    print_commodities(commodities)
    print_indices(indices)
    print_news(news)

    # ── Layer 2: Microstructure Engine ────────────────────────────────────────
    print("  [Microstructure] Analyzing market structure...")
    microstructure = run_microstructure(stocks, crypto, forex, commodities, indices)

    # ── Layer 3: Feature Extraction ───────────────────────────────────────────
    print("  [Features] Extracting feature vectors...")
    features = run_feature_extraction(stocks, crypto, forex, commodities, indices, microstructure)

    # ── Layer 4: Regime Detection ─────────────────────────────────────────────
    print("  [Regime] Detecting market regime...")
    regime = detect_regime(features, microstructure, features["cross_asset"], news)
    print_regime(regime)

    # ── Rule-Based Analysis (feeds into AI agents) ────────────────────────────
    insights = generate_all_insights(stocks, crypto, news)
    print_insights(insights)

    analysis = analyze_all(stocks, crypto, news)
    print_analysis(analysis)

    signals = generate_all(analysis, stocks, crypto)
    print_signals(signals)

    # ── Layers 5-11: Full AI Pipeline ─────────────────────────────────────────
    print("\n  [AI Pipeline] Running highest-level multi-agent system...")
    ai_analysis = run_ai_analysis(
        stocks, crypto, analysis, news,
        features=features,
        microstructure=microstructure,
        regime=regime,
    )
    print_ai_analysis(ai_analysis)

    # ── Summary ───────────────────────────────────────────────────────────────
    bullish   = sum(1 for n in news if n.get("sentiment") == "bullish")
    bearish   = sum(1 for n in news if n.get("sentiment") == "bearish")
    buy_sigs  = sum(1 for s in stocks + crypto if s.get("signal") in ("BUY", "STRONG BUY"))
    sell_sigs = sum(1 for s in stocks + crypto if s.get("signal") in ("SELL", "STRONG SELL"))
    print(f"\n  News Sentiment -> Bullish: {bullish}  Bearish: {bearish}  Neutral: {len(news)-bullish-bearish}")
    print(f"  Market Signals -> Buy: {buy_sigs}  Sell: {sell_sigs}")
    print(f"  Regime         -> {regime.get('composite_regime')}  |  {regime.get('trend_regime')}  |  VIX: {regime.get('vix','N/A')}")

    # ── Export ────────────────────────────────────────────────────────────────
    output = {
        "fetched_at":      datetime.utcnow().isoformat() + "Z",
        "stocks":          stocks,
        "crypto":          crypto,
        "forex":           forex,
        "commodities":     commodities,
        "indices":         indices,
        "news":            news,
        "microstructure":  microstructure,
        "features":        features,
        "regime":          regime,
        "insights":        insights,
        "analysis":        analysis,
        "signals":         signals,
        "ai_analysis":     ai_analysis,
        "summary": {
            "total_instruments": len(stocks)+len(crypto)+len(forex)+len(commodities)+len(indices),
            "total_news":        len(news),
            "bullish_news":      bullish,
            "bearish_news":      bearish,
            "buy_signals":       buy_sigs,
            "sell_signals":      sell_sigs,
            "composite_regime":  regime.get("composite_regime"),
            "trend_regime":      regime.get("trend_regime"),
            "volatility_regime": regime.get("volatility_regime"),
            "macro_regime":      regime.get("macro_regime"),
        },
    }

    save_json(output)
    save_csv(output)
    elapsed = (datetime.now() - t0).seconds
    print(f"\n  Done in {elapsed}s. {output['summary']['total_instruments']} instruments + {len(news)} articles.\n")


if __name__ == "__main__":
    asyncio.run(main())
