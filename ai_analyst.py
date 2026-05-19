"""
ai_analyst.py — Multi-Agent Investment Pipeline (NVIDIA LLaMA)

Architecture:
  Market Data
      ↓
  Analyst Agents  (Fundamental / Technical / Sentiment / News)  [parallel]
      ↓
  Bull vs Bear Debate
      ↓
  Trader Agent
      ↓
  Risk Manager
      ↓
  Portfolio Manager
      ↓
  Final Trade Decision
"""
from __future__ import annotations
import json
from openai import OpenAI

_CLIENT = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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",
)
MODEL = "meta/llama-3.3-70b-instruct"


# ── Shared helpers ─────────────────────────────────────────────────────────────

def _call(system: str, user: str, max_tokens: int = 1200) -> dict:
    """Single LLM call. Returns parsed JSON or error dict."""
    try:
        resp = _CLIENT.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            temperature=0.2,
            max_tokens=max_tokens,
        )
        raw = resp.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        return {"error": "JSON parse failed", "raw": raw}
    except Exception as e:
        return {"error": str(e)}


def _slim_stocks(stocks: list[dict], n: int = 12) -> list[dict]:
    keys = ("symbol", "price", "change_%", "rsi", "macd", "macd_signal",
            "ema20", "ema50", "ema200", "vwap", "atr", "bb_upper", "bb_lower",
            "pe_ratio", "eps", "market_cap", "sector", "beta",
            "volume", "avg_vol_10d", "signal")
    return [{k: v for k, v in d.items() if k in keys} for d in stocks[:n]]


def _slim_crypto(crypto: list[dict], n: int = 8) -> list[dict]:
    keys = ("symbol", "price", "change_%", "rsi", "macd", "macd_signal",
            "ema20", "ema50", "ema200", "vwap", "atr", "volume", "avg_vol_10d", "signal")
    return [{k: v for k, v in d.items() if k in keys} for d in crypto[:n]]


def _slim_analysis(analysis: dict, n: int = 10) -> dict:
    def _trim(items):
        return [{k: v for k, v in a.items() if k in
                 ("symbol", "price", "composite", "verdict", "scores")} for a in items[:n]]
    return {"stocks": _trim(analysis.get("stocks", [])),
            "crypto": _trim(analysis.get("crypto", []))}


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 1 — Four Analyst Agents (independent, focused)
# ══════════════════════════════════════════════════════════════════════════════

def _fundamental_agent(stocks: list[dict], crypto: list[dict]) -> dict:
    print("    [Agent 1/4] Fundamental Analyst...")
    data = {"stocks": _slim_stocks(stocks), "crypto": _slim_crypto(crypto)}
    system = (
        "You are a Fundamental Analyst. Evaluate stocks using P/E ratio, EPS, market cap, "
        "beta, dividend yield, and sector positioning. Crypto has no fundamentals — skip it. "
        "Respond ONLY with valid JSON, no markdown."
    )
    user = f"""Analyze this market data and return JSON:
{{
  "top_fundamental_stocks": [
    {{"symbol": "X", "pe_ratio": 0, "eps": 0, "verdict": "UNDERVALUED|FAIR|OVERVALUED", "note": "reason"}}
  ],
  "weak_fundamental_stocks": [
    {{"symbol": "X", "reason": "why weak"}}
  ],
  "macro_fundamental_bias": "BULLISH|BEARISH|NEUTRAL",
  "summary": "2 sentence fundamental market assessment"
}}

DATA: {json.dumps(data)}"""
    return _call(system, user)


def _technical_agent(stocks: list[dict], crypto: list[dict]) -> dict:
    print("    [Agent 2/4] Technical Analyst...")
    data = {"stocks": _slim_stocks(stocks), "crypto": _slim_crypto(crypto)}
    system = (
        "You are a Technical Analyst. Evaluate RSI, MACD crossovers, EMA alignment "
        "(golden/death cross), VWAP position, Bollinger Bands, and ATR volatility. "
        "Respond ONLY with valid JSON, no markdown."
    )
    user = f"""Analyze this market data and return JSON:
{{
  "bullish_setups": [
    {{"symbol": "X", "signals": ["signal1", "signal2"], "strength": "STRONG|MODERATE|WEAK"}}
  ],
  "bearish_setups": [
    {{"symbol": "X", "signals": ["signal1"], "strength": "STRONG|MODERATE|WEAK"}}
  ],
  "macro_technical_bias": "BULLISH|BEARISH|NEUTRAL",
  "summary": "2 sentence technical market assessment"
}}

DATA: {json.dumps(data)}"""
    return _call(system, user)


def _sentiment_agent(stocks: list[dict], crypto: list[dict], analysis: dict) -> dict:
    print("    [Agent 3/4] Sentiment Analyst...")
    data = {
        "analysis_scores": _slim_analysis(analysis),
        "stock_signals":   [{"symbol": s.get("symbol"), "signal": s.get("signal"),
                             "change_%": s.get("change_%"), "relative_volume": s.get("relative_volume")}
                            for s in stocks[:12]],
        "crypto_signals":  [{"symbol": c.get("symbol"), "signal": c.get("signal"),
                             "change_%": c.get("change_%")} for c in crypto[:8]],
    }
    system = (
        "You are a Market Sentiment Analyst. Evaluate momentum, volume patterns, "
        "relative strength, and composite scores to gauge market sentiment. "
        "Respond ONLY with valid JSON, no markdown."
    )
    user = f"""Analyze this data and return JSON:
{{
  "fear_greed_index": 0,
  "fear_greed_label": "EXTREME FEAR|FEAR|NEUTRAL|GREED|EXTREME GREED",
  "momentum_leaders": [{{"symbol": "X", "momentum": "reason"}}],
  "momentum_laggards": [{{"symbol": "X", "weakness": "reason"}}],
  "overall_sentiment": "RISK-ON|RISK-OFF|NEUTRAL",
  "summary": "2 sentence sentiment assessment"
}}

DATA: {json.dumps(data)}"""
    return _call(system, user)


def _news_agent(news: list[dict]) -> dict:
    print("    [Agent 4/4] News Analyst...")
    headlines = [{"title": n["title"], "sentiment": n["sentiment"],
                  "categories": n.get("categories", [])} for n in news[:40]]
    system = (
        "You are a Financial News Analyst. Identify market-moving themes, macro catalysts, "
        "geopolitical risks, and sector-specific news. Respond ONLY with valid JSON, no markdown."
    )
    user = f"""Analyze these headlines and return JSON:
{{
  "dominant_themes": ["theme1", "theme2", "theme3"],
  "macro_catalysts": [{{"event": "X", "impact": "BULLISH|BEARISH|NEUTRAL", "affected_sectors": ["X"]}}],
  "key_risks_from_news": ["risk1", "risk2"],
  "news_macro_bias": "BULLISH|BEARISH|NEUTRAL",
  "summary": "2 sentence news-driven market assessment"
}}

HEADLINES: {json.dumps(headlines)}"""
    return _call(system, user)


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 2 — Bull vs Bear Debate
# ══════════════════════════════════════════════════════════════════════════════

def _bull_bear_debate(
    fundamental: dict, technical: dict, sentiment: dict, news_analysis: dict,
    stocks: list[dict], crypto: list[dict],
) -> dict:
    print("    [Debate] Bull vs Bear...")
    context = {
        "fundamental_bias":  fundamental.get("macro_fundamental_bias"),
        "fundamental_summary": fundamental.get("summary"),
        "technical_bias":    technical.get("macro_technical_bias"),
        "technical_summary": technical.get("summary"),
        "sentiment":         sentiment.get("overall_sentiment"),
        "fear_greed":        f"{sentiment.get('fear_greed_index')} — {sentiment.get('fear_greed_label')}",
        "news_bias":         news_analysis.get("news_macro_bias"),
        "news_summary":      news_analysis.get("summary"),
        "top_fundamental":   fundamental.get("top_fundamental_stocks", [])[:5],
        "bullish_setups":    technical.get("bullish_setups", [])[:5],
        "bearish_setups":    technical.get("bearish_setups", [])[:5],
        "momentum_leaders":  sentiment.get("momentum_leaders", [])[:4],
        "macro_catalysts":   news_analysis.get("macro_catalysts", [])[:3],
    }
    system = (
        "You are a debate moderator between a Bull and a Bear analyst. "
        "Given all analyst inputs, construct the strongest bull case AND bear case, "
        "then determine which side wins based on the weight of evidence. "
        "Respond ONLY with valid JSON, no markdown."
    )
    user = f"""Given these analyst reports, run the bull vs bear debate and return JSON:
{{
  "bull_case": {{
    "arguments": ["arg1", "arg2", "arg3"],
    "strongest_point": "single best bull argument",
    "top_long_candidates": ["SYM1", "SYM2", "SYM3"]
  }},
  "bear_case": {{
    "arguments": ["arg1", "arg2", "arg3"],
    "strongest_point": "single best bear argument",
    "top_short_candidates": ["SYM1", "SYM2"]
  }},
  "debate_winner": "BULL|BEAR|DRAW",
  "conviction": "HIGH|MEDIUM|LOW",
  "market_regime": "TRENDING-UP|TRENDING-DOWN|RANGING|VOLATILE",
  "verdict": "2 sentence debate conclusion"
}}

ANALYST REPORTS: {json.dumps(context)}"""
    return _call(system, user, max_tokens=1000)


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 3 — Trader Agent
# ══════════════════════════════════════════════════════════════════════════════

def _trader_agent(
    debate: dict, technical: dict, sentiment: dict,
    stocks: list[dict], crypto: list[dict],
) -> dict:
    print("    [Trader] Generating trade setups...")
    context = {
        "debate_winner":     debate.get("debate_winner"),
        "market_regime":     debate.get("market_regime"),
        "conviction":        debate.get("conviction"),
        "top_longs":         debate.get("bull_case", {}).get("top_long_candidates", []),
        "top_shorts":        debate.get("bear_case", {}).get("top_short_candidates", []),
        "bullish_setups":    technical.get("bullish_setups", [])[:6],
        "bearish_setups":    technical.get("bearish_setups", [])[:4],
        "momentum_leaders":  sentiment.get("momentum_leaders", [])[:4],
        "prices":            {s["symbol"]: s.get("price") for s in stocks[:12]
                              if s.get("symbol")},
    }
    system = (
        "You are an aggressive but disciplined Trader. Based on the debate outcome and "
        "technical setups, generate specific trade ideas with entry, stop, and target levels. "
        "Respond ONLY with valid JSON, no markdown."
    )
    user = f"""Generate trade setups and return JSON:
{{
  "trade_ideas": [
    {{
      "symbol": "X",
      "direction": "LONG|SHORT",
      "entry_zone": "price or range as string",
      "stop_loss": "price as string",
      "target1": "price as string",
      "target2": "price as string",
      "timeframe": "intraday|swing|position",
      "rationale": "1 sentence"
    }}
  ],
  "best_trade": "symbol of highest conviction trade",
  "trades_to_avoid": ["SYM1", "SYM2"],
  "trader_bias": "AGGRESSIVE-LONG|CAUTIOUS-LONG|NEUTRAL|CAUTIOUS-SHORT|AGGRESSIVE-SHORT"
}}

Include up to 5 trade ideas. CONTEXT: {json.dumps(context)}"""
    return _call(system, user, max_tokens=1200)


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 4 — Risk Manager
# ══════════════════════════════════════════════════════════════════════════════

def _risk_manager(
    trader: dict, debate: dict, news_analysis: dict, stocks: list[dict],
) -> dict:
    print("    [Risk Manager] Assessing risk...")
    context = {
        "trade_ideas":       trader.get("trade_ideas", []),
        "trader_bias":       trader.get("trader_bias"),
        "market_regime":     debate.get("market_regime"),
        "debate_conviction": debate.get("conviction"),
        "key_risks":         news_analysis.get("key_risks_from_news", []),
        "macro_catalysts":   news_analysis.get("macro_catalysts", []),
        "vix_signal":        next((s.get("signal") for s in stocks
                                   if "VIX" in str(s.get("symbol", ""))), "N/A"),
    }
    system = (
        "You are a Risk Manager. Your job is to stress-test trade ideas, flag excessive risk, "
        "set position sizing rules, and identify tail risks. Be conservative and protect capital. "
        "Respond ONLY with valid JSON, no markdown."
    )
    user = f"""Review these trades and return a risk assessment JSON:
{{
  "approved_trades": ["SYM1", "SYM2"],
  "rejected_trades": [{{"symbol": "X", "reason": "why rejected"}}],
  "risk_adjustments": [{{"symbol": "X", "adjustment": "tighten stop / reduce size / etc"}}],
  "max_position_size_%": 0,
  "portfolio_heat": "LOW|MEDIUM|HIGH|EXTREME",
  "tail_risks": ["risk1", "risk2"],
  "risk_verdict": "2 sentence overall risk assessment"
}}

CONTEXT: {json.dumps(context)}"""
    return _call(system, user, max_tokens=1000)


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 5 — Portfolio Manager
# ══════════════════════════════════════════════════════════════════════════════

def _portfolio_manager(
    trader: dict, risk: dict, debate: dict,
    fundamental: dict, sentiment: dict,
) -> dict:
    print("    [Portfolio Manager] Building portfolio...")
    context = {
        "approved_trades":      risk.get("approved_trades", []),
        "rejected_trades":      risk.get("rejected_trades", []),
        "risk_adjustments":     risk.get("risk_adjustments", []),
        "portfolio_heat":       risk.get("portfolio_heat"),
        "max_position_size_%":  risk.get("max_position_size_%"),
        "trade_ideas":          trader.get("trade_ideas", []),
        "best_trade":           trader.get("best_trade"),
        "debate_winner":        debate.get("debate_winner"),
        "market_regime":        debate.get("market_regime"),
        "fear_greed":           sentiment.get("fear_greed_label"),
        "top_fundamental":      fundamental.get("top_fundamental_stocks", [])[:4],
    }
    system = (
        "You are a Portfolio Manager. Construct an optimal portfolio allocation from approved "
        "trades, balancing risk/reward, diversification, and market regime. "
        "Respond ONLY with valid JSON, no markdown."
    )
    user = f"""Build the portfolio and return JSON:
{{
  "allocations": [
    {{
      "symbol": "X",
      "direction": "LONG|SHORT|HOLD",
      "allocation_%": 0,
      "priority": "CORE|TACTICAL|SPECULATIVE"
    }}
  ],
  "cash_reserve_%": 0,
  "portfolio_bias": "BULLISH|BEARISH|BALANCED",
  "rebalance_trigger": "condition that would cause rebalancing",
  "portfolio_summary": "2 sentence portfolio strategy"
}}

CONTEXT: {json.dumps(context)}"""
    return _call(system, user, max_tokens=1000)


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 6 — Final Trade Decision
# ══════════════════════════════════════════════════════════════════════════════

def _final_decision(
    fundamental: dict, technical: dict, sentiment: dict, news_analysis: dict,
    debate: dict, trader: dict, risk: dict, portfolio: dict,
) -> dict:
    print("    [Final Decision] Synthesizing...")
    context = {
        "macro_bias": {
            "fundamental": fundamental.get("macro_fundamental_bias"),
            "technical":   technical.get("macro_technical_bias"),
            "sentiment":   sentiment.get("overall_sentiment"),
            "news":        news_analysis.get("news_macro_bias"),
        },
        "debate_winner":    debate.get("debate_winner"),
        "market_regime":    debate.get("market_regime"),
        "best_trade":       trader.get("best_trade"),
        "trader_bias":      trader.get("trader_bias"),
        "portfolio_heat":   risk.get("portfolio_heat"),
        "tail_risks":       risk.get("tail_risks", []),
        "allocations":      portfolio.get("allocations", []),
        "cash_reserve_%":   portfolio.get("cash_reserve_%"),
        "portfolio_bias":   portfolio.get("portfolio_bias"),
        "approved_trades":  risk.get("approved_trades", []),
    }
    system = (
        "You are the Chief Investment Officer. Synthesize all agent outputs into a final, "
        "definitive investment decision. Be specific, actionable, and decisive. "
        "Respond ONLY with valid JSON, no markdown."
    )
    user = f"""Synthesize all agent outputs into the final decision JSON:
{{
  "overall_market_bias": "STRONG BULL|BULL|NEUTRAL|BEAR|STRONG BEAR",
  "market_regime": "description",
  "final_trades": [
    {{
      "symbol": "X",
      "action": "BUY NOW|BUY|HOLD|SELL|SELL NOW|AVOID",
      "conviction": "HIGH|MEDIUM|LOW",
      "allocation_%": 0,
      "entry_zone": "price or range",
      "stop_loss": "price",
      "target": "price",
      "timeframe": "intraday|swing|position",
      "rationale": "1-2 sentences combining all agent insights"
    }}
  ],
  "top_opportunity": "single best trade right now with full rationale",
  "biggest_risk": "single biggest threat to the portfolio",
  "cash_reserve_%": 0,
  "do_not_touch": ["SYM1", "SYM2"],
  "executive_summary": "4-5 sentence definitive market outlook and action plan"
}}

ALL AGENT OUTPUTS: {json.dumps(context)}"""
    return _call(system, user, max_tokens=1500)


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def run_ai_analysis(
    stocks: list[dict],
    crypto: list[dict],
    analysis: dict,
    news: list[dict],
) -> dict:
    """
    Run the full multi-agent pipeline and return all agent outputs + final decision.
    """
    print("\n  -- Multi-Agent Pipeline ------------------------------------------")

    # Layer 1 — Analyst Agents
    print("  [Layer 1] Analyst Agents")
    fundamental   = _fundamental_agent(stocks, crypto)
    technical     = _technical_agent(stocks, crypto)
    sentiment     = _sentiment_agent(stocks, crypto, analysis)
    news_analysis = _news_agent(news)

    # Layer 2 — Bull vs Bear Debate
    print("  [Layer 2] Bull vs Bear Debate")
    debate = _bull_bear_debate(fundamental, technical, sentiment, news_analysis, stocks, crypto)

    # Layer 3 — Trader
    print("  [Layer 3] Trader Agent")
    trader = _trader_agent(debate, technical, sentiment, stocks, crypto)

    # Layer 4 — Risk Manager
    print("  [Layer 4] Risk Manager")
    risk = _risk_manager(trader, debate, news_analysis, stocks)

    # Layer 5 — Portfolio Manager
    print("  [Layer 5] Portfolio Manager")
    portfolio = _portfolio_manager(trader, risk, debate, fundamental, sentiment)

    # Layer 6 — Final Decision
    print("  [Layer 6] Final Trade Decision")
    final = _final_decision(fundamental, technical, sentiment, news_analysis,
                            debate, trader, risk, portfolio)

    print("  -- Pipeline complete ---------------------------------------------\n")

    return {
        "agents": {
            "fundamental":   fundamental,
            "technical":     technical,
            "sentiment":     sentiment,
            "news":          news_analysis,
        },
        "debate":     debate,
        "trader":     trader,
        "risk":       risk,
        "portfolio":  portfolio,
        "final":      final,
    }
