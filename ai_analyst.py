"""
ai_analyst.py - Highest-Level Multi-Agent AI Investment System
NVIDIA LLaMA 3.3-70B

Architecture:
  Market Data Layer
       |
  Microstructure Engine        [microstructure.py]
       |
  Feature Extraction           [features.py]
       |
  Regime Detection             [regime.py]
       |
  Specialized AI Agents        [Layer 1: Fundamental / Technical / Sentiment / News]
       |
  Debate & Coordination        [Layer 2: Bull vs Bear]
       |
  Risk Optimization            [Layer 3: Trader + Layer 4: Risk Manager]
       |
  Portfolio Optimization       [Layer 5: Portfolio Manager]
       |
  Execution Optimization       [Layer 6: Execution Strategist]
       |
  Learning & Reflection        [Layer 7: Post-Analysis Reflector]
       |
  Continuous Adaptation        [Layer 8: Final CIO Decision]
"""
from __future__ import annotations
import json
from openai import OpenAI
from memory import get_memory_context, store_reflection, store_episode

_CLIENT = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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",
)
MODEL = "meta/llama-3.3-70b-instruct"


# ── Core LLM call ─────────────────────────────────────────────────────────────

def _call(system: str, user: str, max_tokens: int = 1200) -> dict:
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


# ── Data slimmers ─────────────────────────────────────────────────────────────

def _slim(items: list[dict], keys: tuple, n: int = 12) -> list[dict]:
    return [{k: v for k, v in d.items() if k in keys} for d in items[:n]]

def _slim_stocks(s, n=12):
    return _slim(s, ("symbol","price","change_%","rsi","macd","macd_signal",
                     "ema20","ema50","ema200","vwap","atr","bb_upper","bb_lower",
                     "pe_ratio","eps","market_cap","sector","beta","volume","avg_vol_10d","signal"), n)

def _slim_crypto(c, n=8):
    return _slim(c, ("symbol","price","change_%","rsi","macd","macd_signal",
                     "ema20","ema50","ema200","vwap","atr","volume","avg_vol_10d","signal"), n)

def _slim_analysis(analysis: dict, n=10) -> dict:
    keys = ("symbol","price","composite","verdict","scores")
    return {
        "stocks": [{k: v for k, v in a.items() if k in keys} for a in analysis.get("stocks",[])[:n]],
        "crypto": [{k: v for k, v in a.items() if k in keys} for a in analysis.get("crypto",[])[:n]],
    }

def _slim_features(features: dict, n=8) -> dict:
    keys = ("symbol","trend_score","momentum","vol_regime","composite","daily_chg_%","liquidity")
    return {
        "stocks": [{k: v for k, v in f.items() if k in keys} for f in features.get("stocks",[])[:n]],
        "crypto": [{k: v for k, v in f.items() if k in keys} for f in features.get("crypto",[])[:n]],
        "cross_asset": features.get("cross_asset", {}),
    }


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 1 - Specialized AI Agents (4 independent analysts)
# ══════════════════════════════════════════════════════════════════════════════

def _fundamental_agent(stocks, crypto, regime) -> dict:
    print("    [1/4] Fundamental Agent...")
    data = {"stocks": _slim_stocks(stocks), "regime": regime.get("composite_regime")}
    return _call(
        "You are a Fundamental Analyst. Evaluate P/E, EPS, market cap, beta, dividends, sector. "
        "Respond ONLY with valid JSON, no markdown.",
        f"""Return JSON:
{{
  "top_fundamental_stocks": [{{"symbol":"X","pe_ratio":0,"eps":0,"verdict":"UNDERVALUED|FAIR|OVERVALUED","note":"reason"}}],
  "weak_fundamental_stocks": [{{"symbol":"X","reason":"why"}}],
  "macro_fundamental_bias": "BULLISH|BEARISH|NEUTRAL",
  "summary": "2 sentences"
}}
DATA: {json.dumps(data)}"""
    )

def _technical_agent(stocks, crypto, features, regime) -> dict:
    print("    [2/4] Technical Agent...")
    data = {
        "market_data": _slim_stocks(stocks) + _slim_crypto(crypto, 5),
        "features": _slim_features(features),
        "regime": {"trend": regime.get("trend_regime"), "volatility": regime.get("volatility_regime")},
    }
    return _call(
        "You are a Technical Analyst. Evaluate RSI, MACD, EMA alignment, VWAP, Bollinger Bands, ATR. "
        "Respond ONLY with valid JSON, no markdown.",
        f"""Return JSON:
{{
  "bullish_setups": [{{"symbol":"X","signals":["s1","s2"],"strength":"STRONG|MODERATE|WEAK"}}],
  "bearish_setups": [{{"symbol":"X","signals":["s1"],"strength":"STRONG|MODERATE|WEAK"}}],
  "macro_technical_bias": "BULLISH|BEARISH|NEUTRAL",
  "summary": "2 sentences"
}}
DATA: {json.dumps(data)}"""
    )

def _sentiment_agent(stocks, crypto, analysis, microstructure, regime) -> dict:
    print("    [3/4] Sentiment Agent...")
    micro_summary = {
        "avg_liquidity": round(sum(m.get("liquidity_score",50) for m in microstructure.get("stocks",[])[:10]) / max(1, len(microstructure.get("stocks",[])[:10])), 1),
        "buying_pressure": sum(1 for m in microstructure.get("stocks",[]) if m.get("flow_bias") == "BUYING"),
        "selling_pressure": sum(1 for m in microstructure.get("stocks",[]) if m.get("flow_bias") == "SELLING"),
    }
    data = {
        "analysis_scores": _slim_analysis(analysis),
        "microstructure_summary": micro_summary,
        "regime": regime.get("composite_regime"),
        "cross_asset_bias": regime.get("cross_asset_bias"),
    }
    return _call(
        "You are a Market Sentiment Analyst. Evaluate momentum, volume, order flow, composite scores. "
        "Respond ONLY with valid JSON, no markdown.",
        f"""Return JSON:
{{
  "fear_greed_index": 0,
  "fear_greed_label": "EXTREME FEAR|FEAR|NEUTRAL|GREED|EXTREME GREED",
  "momentum_leaders": [{{"symbol":"X","momentum":"reason"}}],
  "momentum_laggards": [{{"symbol":"X","weakness":"reason"}}],
  "overall_sentiment": "RISK-ON|RISK-OFF|NEUTRAL",
  "summary": "2 sentences"
}}
DATA: {json.dumps(data)}"""
    )

def _news_agent(news, regime) -> dict:
    print("    [4/4] News Agent...")
    headlines = [{"title": n["title"], "sentiment": n["sentiment"],
                  "categories": n.get("categories",[])} for n in news[:40]]
    return _call(
        "You are a Financial News Analyst. Identify market-moving themes, macro catalysts, risks. "
        "Respond ONLY with valid JSON, no markdown.",
        f"""Return JSON:
{{
  "dominant_themes": ["t1","t2","t3"],
  "macro_catalysts": [{{"event":"X","impact":"BULLISH|BEARISH|NEUTRAL","affected_sectors":["X"]}}],
  "key_risks_from_news": ["r1","r2"],
  "news_macro_bias": "BULLISH|BEARISH|NEUTRAL",
  "summary": "2 sentences"
}}
REGIME: {regime.get("composite_regime")}
HEADLINES: {json.dumps(headlines)}"""
    )


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 2 - Debate & Coordination
# ══════════════════════════════════════════════════════════════════════════════

def _debate_agent(fundamental, technical, sentiment, news_analysis, regime) -> dict:
    print("    [Debate] Bull vs Bear Coordination...")
    context = {
        "regime": {
            "composite":  regime.get("composite_regime"),
            "trend":      regime.get("trend_regime"),
            "volatility": regime.get("volatility_regime"),
            "macro":      regime.get("macro_regime"),
            "momentum":   regime.get("momentum_regime"),
            "strategy":   regime.get("recommended_strategy"),
        },
        "fundamental_bias":  fundamental.get("macro_fundamental_bias"),
        "technical_bias":    technical.get("macro_technical_bias"),
        "sentiment":         sentiment.get("overall_sentiment"),
        "fear_greed":        f"{sentiment.get('fear_greed_index')} {sentiment.get('fear_greed_label')}",
        "news_bias":         news_analysis.get("news_macro_bias"),
        "top_fundamental":   fundamental.get("top_fundamental_stocks",[])[:4],
        "bullish_setups":    technical.get("bullish_setups",[])[:4],
        "bearish_setups":    technical.get("bearish_setups",[])[:3],
        "momentum_leaders":  sentiment.get("momentum_leaders",[])[:3],
        "macro_catalysts":   news_analysis.get("macro_catalysts",[])[:3],
        "key_risks":         news_analysis.get("key_risks_from_news",[]),
    }
    return _call(
        "You are a debate moderator. Given all analyst inputs AND the detected market regime, "
        "construct the strongest bull and bear cases, then determine the winner. "
        "Respond ONLY with valid JSON, no markdown.",
        f"""Run the bull vs bear debate and return JSON:
{{
  "bull_case": {{
    "arguments": ["a1","a2","a3"],
    "strongest_point": "best bull argument",
    "top_long_candidates": ["SYM1","SYM2","SYM3"]
  }},
  "bear_case": {{
    "arguments": ["a1","a2","a3"],
    "strongest_point": "best bear argument",
    "top_short_candidates": ["SYM1","SYM2"]
  }},
  "debate_winner": "BULL|BEAR|DRAW",
  "conviction": "HIGH|MEDIUM|LOW",
  "regime_alignment": "CONFIRMS_BULL|CONFIRMS_BEAR|MIXED",
  "verdict": "2 sentence conclusion"
}}
CONTEXT: {json.dumps(context)}""",
        max_tokens=1000
    )


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 3 - Risk Optimization (Trader + Risk Manager combined)
# ══════════════════════════════════════════════════════════════════════════════

def _trader_agent(debate, technical, sentiment, stocks, crypto, regime) -> dict:
    print("    [Trader] Generating setups...")
    context = {
        "debate_winner":    debate.get("debate_winner"),
        "conviction":       debate.get("conviction"),
        "regime":           regime.get("composite_regime"),
        "regime_strategy":  regime.get("recommended_strategy"),
        "top_longs":        debate.get("bull_case",{}).get("top_long_candidates",[]),
        "top_shorts":       debate.get("bear_case",{}).get("top_short_candidates",[]),
        "bullish_setups":   technical.get("bullish_setups",[])[:5],
        "bearish_setups":   technical.get("bearish_setups",[])[:3],
        "momentum_leaders": sentiment.get("momentum_leaders",[])[:3],
        "prices":           {s["symbol"]: s.get("price") for s in stocks[:12] if s.get("symbol")},
    }
    return _call(
        "You are a disciplined Trader. Generate specific trade setups aligned with the regime. "
        "Respond ONLY with valid JSON, no markdown.",
        f"""Generate trade setups and return JSON:
{{
  "trade_ideas": [{{
    "symbol":"X","direction":"LONG|SHORT",
    "entry_zone":"price","stop_loss":"price",
    "target1":"price","target2":"price",
    "timeframe":"intraday|swing|position",
    "regime_fit":"HIGH|MEDIUM|LOW",
    "rationale":"1 sentence"
  }}],
  "best_trade": "symbol",
  "trades_to_avoid": ["SYM1"],
  "trader_bias": "AGGRESSIVE-LONG|CAUTIOUS-LONG|NEUTRAL|CAUTIOUS-SHORT|AGGRESSIVE-SHORT"
}}
Up to 5 ideas. CONTEXT: {json.dumps(context)}""",
        max_tokens=1200
    )

def _risk_manager(trader, debate, news_analysis, regime, microstructure) -> dict:
    print("    [Risk Manager] Optimizing risk...")
    avg_liq = 50
    micro_stocks = microstructure.get("stocks", [])
    if micro_stocks:
        avg_liq = round(sum(m.get("liquidity_score",50) for m in micro_stocks) / len(micro_stocks), 1)

    context = {
        "trade_ideas":       trader.get("trade_ideas",[]),
        "trader_bias":       trader.get("trader_bias"),
        "regime":            regime.get("composite_regime"),
        "volatility_regime": regime.get("volatility_regime"),
        "liquidity_regime":  regime.get("liquidity_regime"),
        "avg_market_liquidity": avg_liq,
        "debate_conviction": debate.get("conviction"),
        "key_risks":         news_analysis.get("key_risks_from_news",[]),
        "vix":               regime.get("vix"),
    }
    return _call(
        "You are a Risk Manager. Stress-test trades, set position sizing, identify tail risks. "
        "Be conservative. Respond ONLY with valid JSON, no markdown.",
        f"""Return risk assessment JSON:
{{
  "approved_trades": ["SYM1","SYM2"],
  "rejected_trades": [{{"symbol":"X","reason":"why"}}],
  "risk_adjustments": [{{"symbol":"X","adjustment":"what to change"}}],
  "max_position_size_%": 0,
  "portfolio_heat": "LOW|MEDIUM|HIGH|EXTREME",
  "tail_risks": ["r1","r2"],
  "kelly_fraction": 0.0,
  "risk_verdict": "2 sentences"
}}
CONTEXT: {json.dumps(context)}""",
        max_tokens=1000
    )


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 4 - Portfolio Optimization
# ══════════════════════════════════════════════════════════════════════════════

def _portfolio_manager(trader, risk, debate, fundamental, sentiment, regime) -> dict:
    print("    [Portfolio Manager] Optimizing allocation...")
    context = {
        "approved_trades":     risk.get("approved_trades",[]),
        "rejected_trades":     risk.get("rejected_trades",[]),
        "risk_adjustments":    risk.get("risk_adjustments",[]),
        "max_position_size_%": risk.get("max_position_size_%"),
        "portfolio_heat":      risk.get("portfolio_heat"),
        "kelly_fraction":      risk.get("kelly_fraction"),
        "trade_ideas":         trader.get("trade_ideas",[]),
        "best_trade":          trader.get("best_trade"),
        "regime":              regime.get("composite_regime"),
        "regime_strategy":     regime.get("recommended_strategy"),
        "debate_winner":       debate.get("debate_winner"),
        "fear_greed":          sentiment.get("fear_greed_label"),
        "top_fundamental":     fundamental.get("top_fundamental_stocks",[])[:3],
    }
    return _call(
        "You are a Portfolio Manager. Build an optimal allocation using Kelly criterion, "
        "regime-aware sizing, and diversification. Respond ONLY with valid JSON, no markdown.",
        f"""Build portfolio and return JSON:
{{
  "allocations": [{{
    "symbol":"X","direction":"LONG|SHORT|HOLD",
    "allocation_%":0,"priority":"CORE|TACTICAL|SPECULATIVE",
    "kelly_adjusted_%":0
  }}],
  "cash_reserve_%": 0,
  "portfolio_bias": "BULLISH|BEARISH|BALANCED",
  "sector_weights": {{"tech":0,"energy":0,"finance":0,"other":0}},
  "rebalance_trigger": "condition",
  "portfolio_summary": "2 sentences"
}}
CONTEXT: {json.dumps(context)}""",
        max_tokens=1000
    )


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 5 - Execution Optimization
# ══════════════════════════════════════════════════════════════════════════════

def _execution_agent(portfolio, trader, microstructure, regime) -> dict:
    print("    [Execution] Optimizing entry/exit...")
    micro_map = {m["symbol"]: m for m in microstructure.get("stocks",[]) + microstructure.get("crypto",[])}

    exec_context = []
    for alloc in portfolio.get("allocations",[])[:6]:
        sym = alloc.get("symbol","")
        m   = micro_map.get(sym, {})
        exec_context.append({
            "symbol":       sym,
            "direction":    alloc.get("direction"),
            "allocation_%": alloc.get("allocation_%"),
            "liquidity":    m.get("liquidity_score"),
            "flow_bias":    m.get("flow_bias"),
            "vwap_dev_%":   m.get("vwap_deviation_%"),
            "spread_%":     m.get("spread_proxy_%"),
        })

    context = {
        "positions":        exec_context,
        "regime":           regime.get("composite_regime"),
        "volatility":       regime.get("volatility_regime"),
        "liquidity_regime": regime.get("liquidity_regime"),
    }
    return _call(
        "You are an Execution Strategist. Optimize entry timing, order types, and slippage "
        "based on microstructure and regime. Respond ONLY with valid JSON, no markdown.",
        f"""Return execution plan JSON:
{{
  "execution_plan": [{{
    "symbol":"X",
    "order_type":"MARKET|LIMIT|TWAP|VWAP",
    "entry_timing":"NOW|WAIT_PULLBACK|WAIT_BREAKOUT|SCALE_IN",
    "urgency":"HIGH|MEDIUM|LOW",
    "slippage_risk":"LOW|MEDIUM|HIGH",
    "execution_note":"1 sentence"
  }}],
  "overall_execution_strategy": "1-2 sentences on how to execute today",
  "avoid_execution": ["SYM1"]
}}
CONTEXT: {json.dumps(context)}""",
        max_tokens=900
    )


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 6 - Learning & Reflection
# ══════════════════════════════════════════════════════════════════════════════

def _reflection_agent(fundamental, technical, sentiment, news_analysis,
                      debate, trader, risk, portfolio, execution, regime) -> dict:
    print("    [Reflection] Learning from pipeline...")
    context = {
        "regime":            regime.get("composite_regime"),
        "debate_winner":     debate.get("debate_winner"),
        "conviction":        debate.get("conviction"),
        "regime_alignment":  debate.get("regime_alignment"),
        "approved_trades":   risk.get("approved_trades",[]),
        "rejected_trades":   risk.get("rejected_trades",[]),
        "portfolio_heat":    risk.get("portfolio_heat"),
        "tail_risks":        risk.get("tail_risks",[]),
        "agent_biases": {
            "fundamental": fundamental.get("macro_fundamental_bias"),
            "technical":   technical.get("macro_technical_bias"),
            "sentiment":   sentiment.get("overall_sentiment"),
            "news":        news_analysis.get("news_macro_bias"),
        },
        "best_trade":        trader.get("best_trade"),
        "execution_strategy": execution.get("overall_execution_strategy"),
    }
    return _call(
        "You are a Reflective Analyst. Review the entire pipeline output, identify "
        "inconsistencies, blind spots, and what could go wrong. Provide learning insights "
        "for continuous adaptation. Respond ONLY with valid JSON, no markdown.",
        f"""Reflect on the pipeline and return JSON:
{{
  "pipeline_consistency": "HIGH|MEDIUM|LOW",
  "agent_disagreements": ["disagreement1","disagreement2"],
  "blind_spots": ["what the pipeline might be missing"],
  "scenario_risks": [{{
    "scenario":"what if X happens",
    "impact":"HIGH|MEDIUM|LOW",
    "hedge":"how to protect"
  }}],
  "confidence_in_thesis": "HIGH|MEDIUM|LOW",
  "adaptation_signals": ["what to watch that would change the thesis"],
  "reflection_summary": "2-3 sentences on overall pipeline quality"
}}
CONTEXT: {json.dumps(context)}""",
        max_tokens=1000
    )


# ══════════════════════════════════════════════════════════════════════════════
# LAYER 7 - Continuous Adaptation / Final CIO Decision
# ══════════════════════════════════════════════════════════════════════════════

def _final_cio(fundamental, technical, sentiment, news_analysis,
               debate, trader, risk, portfolio, execution, reflection, regime) -> dict:
    print("    [CIO] Final decision + adaptation plan...")
    context = {
        "regime": {
            "composite":  regime.get("composite_regime"),
            "trend":      regime.get("trend_regime"),
            "volatility": regime.get("volatility_regime"),
            "macro":      regime.get("macro_regime"),
            "strategy":   regime.get("recommended_strategy"),
        },
        "agent_biases": {
            "fundamental": fundamental.get("macro_fundamental_bias"),
            "technical":   technical.get("macro_technical_bias"),
            "sentiment":   sentiment.get("overall_sentiment"),
            "news":        news_analysis.get("news_macro_bias"),
        },
        "debate_winner":     debate.get("debate_winner"),
        "conviction":        debate.get("conviction"),
        "best_trade":        trader.get("best_trade"),
        "trader_bias":       trader.get("trader_bias"),
        "approved_trades":   risk.get("approved_trades",[]),
        "portfolio_heat":    risk.get("portfolio_heat"),
        "tail_risks":        risk.get("tail_risks",[]),
        "allocations":       portfolio.get("allocations",[]),
        "cash_reserve_%":    portfolio.get("cash_reserve_%"),
        "execution_strategy": execution.get("overall_execution_strategy"),
        "pipeline_consistency": reflection.get("pipeline_consistency"),
        "blind_spots":       reflection.get("blind_spots",[]),
        "adaptation_signals": reflection.get("adaptation_signals",[]),
        "confidence":        reflection.get("confidence_in_thesis"),
    }
    return _call(
        "You are the Chief Investment Officer. Synthesize ALL agent outputs into the final "
        "definitive decision. Account for regime, execution, and reflection insights. "
        "Be specific, actionable, and decisive. Respond ONLY with valid JSON, no markdown.",
        f"""Return the final CIO decision JSON:
{{
  "overall_market_bias": "STRONG BULL|BULL|NEUTRAL|BEAR|STRONG BEAR",
  "regime_summary": "1 sentence on current regime",
  "final_trades": [{{
    "symbol":"X","action":"BUY NOW|BUY|HOLD|SELL|SELL NOW|AVOID",
    "conviction":"HIGH|MEDIUM|LOW","allocation_%":0,
    "entry_zone":"price","stop_loss":"price","target":"price",
    "timeframe":"intraday|swing|position",
    "order_type":"MARKET|LIMIT|TWAP",
    "rationale":"1-2 sentences"
  }}],
  "top_opportunity": "best trade with full rationale",
  "biggest_risk": "single biggest threat",
  "cash_reserve_%": 0,
  "do_not_touch": ["SYM1"],
  "adaptation_plan": "what to monitor and when to change thesis",
  "executive_summary": "4-5 sentence definitive outlook and action plan"
}}
ALL OUTPUTS: {json.dumps(context)}""",
        max_tokens=1800
    )


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def run_ai_analysis(stocks: list[dict], crypto: list[dict],
                    analysis: dict, news: list[dict],
                    features: dict = None, microstructure: dict = None,
                    regime: dict = None, stochastic: list = None,
                    portfolio_opt: dict = None,
                    world_model: dict = None,
                    info_theory: dict = None,
                    simulation: dict = None,
                    research: dict = None) -> dict:

    features       = features       or {}
    microstructure = microstructure or {}
    regime         = regime         or {"composite_regime": "UNKNOWN"}
    stochastic     = stochastic     or []
    portfolio_opt  = portfolio_opt  or {}
    world_model    = world_model    or {}
    info_theory    = info_theory    or {}
    simulation     = simulation     or {}
    research       = research       or {}

    # Inject memory context
    vix        = regime.get("vix") or 0
    bias_guess = "BULL" if regime.get("composite_regime") == "BULL-MARKET" else "BEAR"
    mem_ctx    = get_memory_context(regime.get("composite_regime",""), vix, bias_guess)

    print("\n  ============================================================")
    print("  HIGHEST-LEVEL MULTI-AGENT AI PIPELINE")
    print("  ============================================================")

    # Layer 1 - Specialized Agents
    print("  [Layer 1] Specialized AI Agents")
    fundamental   = _fundamental_agent(stocks, crypto, regime)
    technical     = _technical_agent(stocks, crypto, features, regime)
    sentiment     = _sentiment_agent(stocks, crypto, analysis, microstructure, regime)
    news_analysis = _news_agent(news, regime)
    # Layer 2 - Debate & Coordination
    print("  [Layer 2] Debate & Coordination")
    debate = _debate_agent(fundamental, technical, sentiment, news_analysis, regime)

    # Layer 3 - Risk Optimization
    print("  [Layer 3] Risk Optimization")
    trader = _trader_agent(debate, technical, sentiment, stocks, crypto, regime)
    risk   = _risk_manager(trader, debate, news_analysis, regime, microstructure)

    # Layer 4 - Portfolio Optimization
    print("  [Layer 4] Portfolio Optimization")
    portfolio = _portfolio_manager(trader, risk, debate, fundamental, sentiment, regime)

    # Layer 5 - Execution Optimization
    print("  [Layer 5] Execution Optimization")
    execution = _execution_agent(portfolio, trader, microstructure, regime)

    # Layer 6 - Learning & Reflection
    print("  [Layer 6] Learning & Reflection")
    reflection = _reflection_agent(fundamental, technical, sentiment, news_analysis,
                                   debate, trader, risk, portfolio, execution, regime)

    # Layer 7 - Continuous Adaptation / Final CIO
    print("  [Layer 7] Continuous Adaptation + Final CIO Decision")
    final = _final_cio(fundamental, technical, sentiment, news_analysis,
                       debate, trader, risk, portfolio, execution, reflection, regime)

    # Inject civilization-level context into final decision
    if world_model or info_theory or simulation or research:
        civ_context = {
            "world_state":       world_model.get("world_state"),
            "central_bank":      world_model.get("central_bank",{}).get("policy_stance"),
            "geo_risk":          world_model.get("geopolitical",{}).get("risk_level"),
            "inst_flow":         world_model.get("inst_flows",{}).get("dominant_flow"),
            "info_regime":       info_theory.get("info_regime"),
            "kl_signal":         info_theory.get("kl_divergence",{}).get("regime_change_signal"),
            "market_direction":  simulation.get("market_direction"),
            "nash_equilibrium":  simulation.get("market_equilibrium",{}).get("equilibrium_state"),
            "research_verdict":  research.get("ai_research",{}).get("research_verdict"),
            "top_alpha":         research.get("ai_research",{}).get("top_alpha_signals",[])[:2],
        }
        if "civilization_context" not in final:
            final["civilization_context"] = civ_context

    print("  ============================================================\n")

    result = {
        "agents": {
            "fundamental": fundamental,
            "technical":   technical,
            "sentiment":   sentiment,
            "news":        news_analysis,
        },
        "debate":      debate,
        "trader":      trader,
        "risk":        risk,
        "portfolio":   portfolio,
        "execution":   execution,
        "reflection":  reflection,
        "final":       final,
        "memory_context": mem_ctx,
    }

    # Store to memory for continuous learning
    try:
        store_reflection({"final": final, "reflection": reflection, "regime": regime})
        store_episode(
            regime.get("composite_regime", ""),
            final.get("top_opportunity", "")[:80],
            final.get("overall_market_bias", ""),
            vix,
            sentiment.get("fear_greed_index", 50),
            reflection.get("reflection_summary", "")[:200],
        )
    except Exception:
        pass

    return result
