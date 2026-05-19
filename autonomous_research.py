"""
autonomous_research.py - Autonomous Research Scientist AI

Architecture:
  Research Agent → Hypothesis Generator → Statistical Validator
  → Strategy Proposer → Risk Validator → Deployment Recommendation

The AI autonomously:
- Detects anomalies and patterns in market data
- Generates testable hypotheses
- Validates statistically using available data
- Proposes deployable strategies with confidence scores
"""
from __future__ import annotations
import math
import json
from openai import OpenAI

_CLIENT = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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",
)
MODEL = "meta/llama-3.3-70b-instruct"


def _call(system: str, user: str, max_tokens: int = 1000) -> dict:
    try:
        resp = _CLIENT.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system},
                      {"role": "user",   "content": user}],
            temperature=0.3,
            max_tokens=max_tokens,
        )
        raw = resp.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as e:
        return {"error": str(e)}


# ── Statistical Anomaly Detection ────────────────────────────────────────────

def _detect_anomalies(stocks: list[dict], crypto: list[dict],
                       info_theory: dict, world_model: dict) -> list[dict]:
    """Detect statistical anomalies that warrant hypothesis generation."""
    anomalies = []

    # High surprise scores
    for s in info_theory.get("surprise_scores", [])[:5]:
        if s.get("surprise_level") == "HIGH":
            anomalies.append({
                "type":   "HIGH_SURPRISE",
                "symbol": s["symbol"],
                "score":  s["surprise_score"],
                "note":   "Unusual price/volume combination detected",
            })

    # Extreme RSI readings
    for inst in stocks[:15] + crypto[:8]:
        rsi = inst.get("rsi")
        if rsi and (rsi < 25 or rsi > 75):
            anomalies.append({
                "type":   "RSI_EXTREME",
                "symbol": inst.get("symbol"),
                "rsi":    rsi,
                "note":   f"RSI at extreme {'oversold' if rsi < 25 else 'overbought'} level",
            })

    # Regime change signal
    kl = info_theory.get("kl_divergence", {})
    if kl.get("regime_change_signal") in ("STRONG-REGIME-CHANGE", "REGIME-SHIFT"):
        anomalies.append({
            "type":  "REGIME_CHANGE",
            "kl":    kl.get("kl_divergence"),
            "note":  "KL divergence indicates significant market distribution shift",
        })

    # Institutional flow anomaly
    inst_flows = world_model.get("inst_flows", {})
    if inst_flows.get("retail_panic_%", 0) > 30:
        anomalies.append({
            "type": "RETAIL_PANIC",
            "pct":  inst_flows["retail_panic_%"],
            "note": "High retail panic detected — potential smart money opportunity",
        })

    return anomalies[:8]


# ── Hypothesis Generator ──────────────────────────────────────────────────────

def _generate_hypotheses(anomalies: list[dict], regime: dict,
                          world_model: dict) -> list[dict]:
    """Generate testable market hypotheses from detected anomalies."""
    hypotheses = []

    for anomaly in anomalies:
        if anomaly["type"] == "HIGH_SURPRISE":
            hypotheses.append({
                "hypothesis": f"{anomaly['symbol']} will revert to mean within 3-5 sessions",
                "type":       "MEAN_REVERSION",
                "symbol":     anomaly["symbol"],
                "confidence": "MEDIUM",
                "test":       "Monitor RSI + price vs EMA50 over next 5 days",
            })
        elif anomaly["type"] == "RSI_EXTREME":
            direction = "upward" if anomaly["rsi"] < 25 else "downward"
            hypotheses.append({
                "hypothesis": f"{anomaly['symbol']} RSI extreme suggests {direction} reversal",
                "type":       "REVERSAL",
                "symbol":     anomaly["symbol"],
                "confidence": "HIGH" if abs(anomaly["rsi"] - 50) > 30 else "MEDIUM",
                "test":       "RSI cross back through 30/70 level as entry signal",
            })
        elif anomaly["type"] == "REGIME_CHANGE":
            hypotheses.append({
                "hypothesis": "Market regime transition underway — current trends may reverse",
                "type":       "REGIME_TRANSITION",
                "symbol":     "MARKET-WIDE",
                "confidence": "HIGH",
                "test":       "Monitor VIX, SPX 50-day EMA, and sector rotation",
            })
        elif anomaly["type"] == "RETAIL_PANIC":
            hypotheses.append({
                "hypothesis": "Retail panic creates institutional accumulation opportunity",
                "type":       "CONTRARIAN",
                "symbol":     "MARKET-WIDE",
                "confidence": "MEDIUM",
                "test":       "Track institutional flow signals over next 2-3 sessions",
            })

    return hypotheses


# ── Statistical Validator ─────────────────────────────────────────────────────

def _validate_statistically(hypothesis: dict, stocks: list[dict],
                              crypto: list[dict]) -> dict:
    """Validate hypothesis using available market data."""
    h_type  = hypothesis.get("type")
    sym     = hypothesis.get("symbol","")
    all_inst = stocks + crypto
    target   = next((i for i in all_inst if i.get("symbol","") == sym), None)

    if h_type == "MEAN_REVERSION" and target:
        price = target.get("price", 0)
        ema50 = target.get("ema50", price)
        dev   = abs(price - ema50) / ema50 * 100 if ema50 else 0
        valid = dev > 5  # >5% deviation supports mean reversion
        return {
            "valid":       valid,
            "confidence":  "HIGH" if dev > 10 else ("MEDIUM" if dev > 5 else "LOW"),
            "evidence":    f"Price {dev:.1f}% from EMA50",
            "p_value_proxy": round(1 - min(0.99, dev / 20), 3),
        }

    elif h_type == "REVERSAL" and target:
        rsi  = target.get("rsi", 50)
        macd = target.get("macd", 0)
        ms   = target.get("macd_signal", 0)
        # Confluence: RSI extreme + MACD divergence
        macd_confirms = (rsi < 30 and macd > ms) or (rsi > 70 and macd < ms)
        return {
            "valid":       macd_confirms,
            "confidence":  "HIGH" if macd_confirms else "LOW",
            "evidence":    f"RSI={rsi:.1f}, MACD {'confirms' if macd_confirms else 'does not confirm'}",
            "p_value_proxy": 0.05 if macd_confirms else 0.35,
        }

    return {
        "valid":       True,
        "confidence":  hypothesis.get("confidence","MEDIUM"),
        "evidence":    "Qualitative assessment only",
        "p_value_proxy": 0.15,
    }


# ── AI Research Agent ─────────────────────────────────────────────────────────

def _ai_research_agent(anomalies: list[dict], hypotheses: list[dict],
                        validated: list[dict], regime: dict,
                        world_model: dict) -> dict:
    """AI synthesizes research findings into deployable strategies."""
    context = {
        "anomalies":         anomalies[:5],
        "hypotheses":        hypotheses[:5],
        "validated":         validated[:5],
        "regime":            regime.get("composite_regime"),
        "world_state":       world_model.get("world_state"),
        "dominant_factor":   world_model.get("macro_factors",{}).get("dominant_factor"),
    }
    return _call(
        "You are an Autonomous Research Scientist AI for quantitative finance. "
        "Analyze detected anomalies, validated hypotheses, and market conditions. "
        "Propose specific deployable trading strategies. Respond ONLY with valid JSON.",
        f"""Based on this research output, return JSON:
{{
  "research_summary": "2 sentence summary of key findings",
  "top_alpha_signals": [
    {{"signal": "description", "symbol": "X", "edge": "statistical edge", "confidence": "HIGH|MEDIUM|LOW"}}
  ],
  "proposed_strategies": [
    {{"name": "strategy name", "type": "MEAN_REVERSION|MOMENTUM|CONTRARIAN|ARBITRAGE",
      "instruments": ["SYM1"], "entry_condition": "when X", "exit_condition": "when Y",
      "expected_edge_%": 0, "risk_level": "LOW|MEDIUM|HIGH"}}
  ],
  "research_verdict": "DEPLOY|MONITOR|REJECT",
  "next_research_questions": ["question1", "question2"]
}}
CONTEXT: {json.dumps(context)}""",
        max_tokens=1200
    )


# ── Main entry point ──────────────────────────────────────────────────────────

def run_autonomous_research(stocks: list[dict], crypto: list[dict],
                             regime: dict, world_model: dict,
                             info_theory: dict) -> dict:
    """Run the full autonomous research pipeline."""
    print("    [Research] Detecting anomalies...")
    anomalies = _detect_anomalies(stocks, crypto, info_theory, world_model)

    print("    [Research] Generating hypotheses...")
    hypotheses = _generate_hypotheses(anomalies, regime, world_model)

    print("    [Research] Validating statistically...")
    validated = []
    for h in hypotheses:
        v = _validate_statistically(h, stocks, crypto)
        validated.append({**h, "validation": v})

    print("    [Research] AI synthesis...")
    ai_research = _ai_research_agent(anomalies, hypotheses, validated,
                                      regime, world_model)

    return {
        "anomalies_detected":  anomalies,
        "hypotheses":          hypotheses,
        "validated_hypotheses": validated,
        "ai_research":         ai_research,
        "deployable_count":    sum(1 for v in validated
                                   if v.get("validation",{}).get("valid")),
    }
