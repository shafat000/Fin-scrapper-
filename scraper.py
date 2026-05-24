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
from stochastic import run_stochastic_analysis
from portfolio_optimizer import run_portfolio_optimization
from information_theory import run_information_theory
from world_model import run_world_model
from market_simulator import run_market_simulation
from autonomous_research import run_autonomous_research
from analyst import analyze_all
from signals import generate_all
from insights import generate_all_insights
from ai_analyst import run_ai_analysis
from backtest import run_backtest, print_backtest_results
from validation import validate_signals, print_validation_results
from export import (
    print_stocks, print_crypto, print_forex,
    print_commodities, print_indices, print_news,
    print_insights, print_analysis, print_signals,
    print_regime, print_stochastic, print_portfolio_opt,
    print_world_model, print_information_theory,
    print_simulation, print_research,
    print_ai_analysis, save_json, save_csv,
)

BANNER = r"""
 _____ _             _____                                 
|_   _| |           /  ___|                                
  | | | |__   ___   \ `--.  ___ _ __ __ _ _ __   ___ _ __ 
  | | | '_ \ / _ \   `--. \/ __| '__/ _` | '_ \ / _ \ '__|
  | | | | | |  __/  /\__/ / (__| | | (_| | |_) |  __/ |   
  \_/ |_| |_|\___|  \____/ \___|_|  \__,_| .__/ \___|_|   
                                          | |              
  Autonomous Financial Intelligence Civilization  v6.0     
"""


def _filter_symbol(data: list[dict], symbol: str) -> list[dict]:
    """Return only the entry whose symbol matches (case-insensitive, partial ok)."""
    sym = symbol.upper()
    return [d for d in data if sym in d.get("symbol", "").upper()]


async def main():
    print(BANNER)

    # ── Symbol filter prompt ──────────────────────────────────────────────────
    raw = input("  Enter symbol to analyze (or press Enter for full scan): ").strip()
    target = raw.upper() if raw else None
    if target:
        print(f"  >> Single-symbol mode: {target}\n")
    else:
        print("  >> Full scan mode\n")

    t0 = datetime.now()
    print(f"  Started at: {t0.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # ── Layer 1: Market Data ──────────────────────────────────────────────────
    print("  [1] Fetching all market data concurrently...")
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

    # ── Apply symbol filter ───────────────────────────────────────────────────
    if target:
        stocks      = _filter_symbol(stocks,      target) or stocks
        crypto      = _filter_symbol(crypto,       target) or crypto
        forex       = _filter_symbol(forex,        target) or forex
        commodities = _filter_symbol(commodities,  target) or commodities
        indices     = _filter_symbol(indices,       target) or indices
        # keep at least one list non-empty so pipeline doesn't crash
        if not any([stocks, crypto, forex, commodities, indices]):
            print(f"  [!] Symbol '{target}' not found in any market. Running full scan.\n")

    print_stocks(stocks)
    print_crypto(crypto)
    print_forex(forex)
    print_commodities(commodities)
    print_indices(indices)
    print_news(news)

    # ── Performance Backtest ──────────────────────────────────────────────────
    backtest_results = run_backtest({"stocks": stocks, "crypto": crypto})
    print_backtest_results(backtest_results)

    # ── Layer 2: Microstructure Engine ────────────────────────────────────────
    print("  [2] Microstructure Engine (OFI, Microprice, Queue Model, Spread)...")
    microstructure = run_microstructure(stocks, crypto, forex, commodities, indices)

    # ── Layer 3: Feature Extraction ───────────────────────────────────────────
    print("  [3] Feature Extraction (cross-asset signals, feature vectors)...")
    features = run_feature_extraction(stocks, crypto, forex, commodities, indices, microstructure)

    # ── Layer 4: Regime Detection (HMM + Bayesian) ────────────────────────────
    print("  [4] Regime Detection (HMM + Bayesian Switching)...")
    regime = detect_regime(features, microstructure, features["cross_asset"], news)
    print_regime(regime)

    # ── Layer 5: Stochastic Mathematics ──────────────────────────────────────
    print("  [5] Stochastic Models (GBM, OU, Heston, Monte Carlo, Black-Scholes)...")
    vix        = regime.get("vix")
    stochastic = run_stochastic_analysis(stocks[:8], vix=vix)
    print_stochastic(stochastic)

    # ── Layer 6: Portfolio Optimization ──────────────────────────────────────
    print("  [6] Portfolio Optimization (Markowitz, Risk Parity, HRP, Kelly)...")
    analysis      = analyze_all(stocks, crypto, news)
    portfolio_opt = run_portfolio_optimization(stocks, crypto, analysis)
    print_portfolio_opt(portfolio_opt)

    # ── Layer 7: Information Theory ───────────────────────────────────────────
    print("  [7] Information Theory (Entropy, KL Divergence, Mutual Information)...")
    info_theory = run_information_theory(stocks, crypto, indices)
    print_information_theory(info_theory)

    # ── Layer 8: World Model (Economic Digital Twin) ──────────────────────────
    print("  [8] World Model (Central Bank, Geopolitics, Supply Chain, Inst Flows)...")
    world_model = run_world_model(stocks, crypto, forex, commodities,
                                   indices, news, microstructure)
    print_world_model(world_model)

    # ── Layer 9: Multi-Agent Market Simulation ────────────────────────────────
    print("  [9] Market Simulation (HF + Retail + Market Maker + Central Bank)...")
    simulation = run_market_simulation(stocks, regime, world_model, microstructure)
    print_simulation(simulation)

    # ── Layer 10: Autonomous Research Scientist ───────────────────────────────
    print("  [10] Autonomous Research (Anomaly Detection, Hypothesis, Validation)...")
    research = run_autonomous_research(stocks, crypto, regime, world_model, info_theory)
    print_research(research)

    # ── Rule-Based Analysis ───────────────────────────────────────────────────
    insights = generate_all_insights(stocks, crypto, news)
    print_insights(insights)
    print_analysis(analysis)
    signals = generate_all(analysis, stocks, crypto)
    print_signals(signals)

    # ── Signal Confluence Validation ──────────────────────────────────────────
    validated_stocks = validate_signals(stocks, microstructure["stocks"])
    validated_crypto = validate_signals(crypto, microstructure["crypto"])
    print_validation_results(validated_stocks + validated_crypto)

    # ── Layers 11+: Full AI Pipeline ──────────────────────────────────────────
    print("\n  [AI] Running highest-level multi-agent civilization AI...")
    ai_analysis = run_ai_analysis(
        stocks, crypto, analysis, news,
        features=features,
        microstructure=microstructure,
        regime=regime,
        stochastic=stochastic,
        portfolio_opt=portfolio_opt,
        world_model=world_model,
        info_theory=info_theory,
        simulation=simulation,
        research=research,
    )
    print_ai_analysis(ai_analysis)

    # ── Summary ───────────────────────────────────────────────────────────────
    bullish   = sum(1 for n in news if n.get("sentiment") == "bullish")
    bearish   = sum(1 for n in news if n.get("sentiment") == "bearish")
    buy_sigs  = sum(1 for s in stocks + crypto if s.get("signal") in ("BUY", "STRONG BUY"))
    sell_sigs = sum(1 for s in stocks + crypto if s.get("signal") in ("SELL", "STRONG SELL"))
    print(f"\n  News Sentiment  -> Bullish: {bullish}  Bearish: {bearish}  Neutral: {len(news)-bullish-bearish}")
    print(f"  Market Signals  -> Buy: {buy_sigs}  Sell: {sell_sigs}")
    print(f"  Regime          -> {regime.get('composite_regime')}  |  HMM: {regime.get('hmm_state')}  |  VIX: {regime.get('vix','N/A')}")
    print(f"  World State     -> {world_model.get('world_state')}  |  Geo Risk: {world_model.get('geopolitical',{}).get('risk_level')}")
    print(f"  Market Sim      -> {simulation.get('market_direction')}  |  Nash: {simulation.get('market_equilibrium',{}).get('equilibrium_state')}")
    print(f"  Info Regime     -> {info_theory.get('info_regime')}  |  KL Signal: {info_theory.get('kl_divergence',{}).get('regime_change_signal')}")
    print(f"  Research        -> {research.get('ai_research',{}).get('research_verdict')}  |  Deployable: {research.get('deployable_count')}")

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
        "stochastic":      stochastic,
        "portfolio_opt":   portfolio_opt,
        "information_theory": info_theory,
        "world_model":     world_model,
        "simulation":      simulation,
        "research":        research,
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
            "hmm_state":         regime.get("hmm_state"),
            "world_state":       world_model.get("world_state"),
            "market_direction":  simulation.get("market_direction"),
            "info_regime":       info_theory.get("info_regime"),
            "research_verdict":  research.get("ai_research",{}).get("research_verdict"),
        },
    }

    save_json(output)
    save_csv(output)
    elapsed = (datetime.now() - t0).seconds
    print(f"\n  Done in {elapsed}s. {output['summary']['total_instruments']} instruments + {len(news)} articles.\n")


if __name__ == "__main__":
    asyncio.run(main())
