"""
regime.py - Advanced Market Regime Detection Engine

Implements:
- Hidden Markov Model-inspired regime classification
- Bayesian regime switching (probability-weighted)
- Regime clustering (Trending / Mean-Reverting / High-Vol / Panic)
- Dynamic factor model signals
- 5-dimensional regime scoring
"""
from __future__ import annotations
import math


def _safe(v, d=0.0):
    return v if v is not None else d


# ── HMM-Inspired Regime States ────────────────────────────────────────────────
# 4 hidden states: Trending, Mean-Reverting, High-Volatility, Panic

REGIME_STATES = {
    "TRENDING":       {"trend_weight": 0.5, "vol_weight": 0.1, "mom_weight": 0.4},
    "MEAN-REVERTING": {"trend_weight": 0.1, "vol_weight": 0.3, "mom_weight": 0.6},
    "HIGH-VOLATILITY":{"trend_weight": 0.2, "vol_weight": 0.6, "mom_weight": 0.2},
    "PANIC":          {"trend_weight": 0.1, "vol_weight": 0.7, "mom_weight": 0.2},
}


def _hmm_regime(trend_score: float, vol_score: float, mom_score: float,
                vix: float = None) -> dict:
    """
    Classify regime using HMM-inspired emission probabilities.
    Returns state probabilities (Bayesian posterior approximation).
    """
    # Normalize inputs to 0-1
    t = (trend_score + 3) / 6        # trend_score: -3 to +3
    v = min(1.0, vol_score / 50)     # vol_score: 0-50+
    m = (mom_score + 1) / 2          # mom_score: -1 to +1

    # Panic override: VIX > 30
    if vix and vix > 30:
        return {
            "hmm_state": "PANIC",
            "state_probabilities": {"PANIC": 0.85, "HIGH-VOLATILITY": 0.10,
                                    "MEAN-REVERTING": 0.04, "TRENDING": 0.01},
        }

    # Emission scores per state
    scores = {
        "TRENDING":        t * 0.5 + m * 0.4 + (1 - v) * 0.1,
        "MEAN-REVERTING":  (1 - abs(t - 0.5)) * 0.4 + (1 - m) * 0.4 + (1 - v) * 0.2,
        "HIGH-VOLATILITY": v * 0.6 + (1 - t) * 0.2 + (1 - m) * 0.2,
        "PANIC":           v * 0.7 + (1 - t) * 0.2 + (1 - m) * 0.1,
    }

    total = sum(scores.values()) or 1
    probs = {k: round(v / total, 3) for k, v in scores.items()}
    state = max(probs, key=probs.get)

    return {"hmm_state": state, "state_probabilities": probs}


# ── Bayesian Regime Switching ─────────────────────────────────────────────────

def _bayesian_switch(features: dict, cross: dict, news: list[dict]) -> dict:
    """
    Bayesian posterior over regime states.
    Prior: uniform. Likelihood from market signals.
    """
    all_f   = features.get("stocks", []) + features.get("crypto", [])
    vix     = _safe(cross.get("vix"))
    spx_chg = _safe(cross.get("spx_chg_%"))
    btc_chg = _safe(cross.get("btc_chg_%"))

    bull_news = sum(1 for n in news if n.get("sentiment") == "bullish")
    bear_news = sum(1 for n in news if n.get("sentiment") == "bearish")
    news_bull_ratio = bull_news / max(1, len(news))

    # Likelihood signals
    avg_trend = sum(_safe(f.get("trend_score")) for f in all_f) / max(1, len(all_f))
    avg_mom   = sum(_safe(f.get("momentum")) for f in all_f) / max(1, len(all_f))
    avg_vol   = sum(_safe(f.get("vol_pct")) for f in all_f) / max(1, len(all_f))

    # Posterior scores (unnormalized)
    bull_score = (
        max(0, avg_trend) * 2 +
        max(0, avg_mom) * 2 +
        (1 if spx_chg and spx_chg > 0 else 0) +
        news_bull_ratio * 2
    )
    bear_score = (
        max(0, -avg_trend) * 2 +
        max(0, -avg_mom) * 2 +
        (1 if spx_chg and spx_chg < 0 else 0) +
        (1 - news_bull_ratio) * 2
    )
    vol_score  = avg_vol * 10 + (vix / 10 if vix else 0)
    panic_score = (vix / 10 if vix and vix > 20 else 0) + max(0, -spx_chg / 2 if spx_chg else 0)

    total = bull_score + bear_score + vol_score + panic_score + 0.01
    return {
        "bull_probability":   round(bull_score / total, 3),
        "bear_probability":   round(bear_score / total, 3),
        "vol_probability":    round(vol_score / total, 3),
        "panic_probability":  round(panic_score / total, 3),
        "dominant_regime":    max(
            {"BULL": bull_score, "BEAR": bear_score,
             "HIGH-VOL": vol_score, "PANIC": panic_score},
            key=lambda k: {"BULL": bull_score, "BEAR": bear_score,
                           "HIGH-VOL": vol_score, "PANIC": panic_score}[k]
        ),
    }


# ── Trend Regime ──────────────────────────────────────────────────────────────

def _detect_trend_regime(features: dict) -> str:
    stock_features = features.get("stocks", [])
    if not stock_features:
        return "UNKNOWN"
    bull  = sum(1 for f in stock_features if f.get("trend_score", 0) >= 2)
    bear  = sum(1 for f in stock_features if f.get("trend_score", 0) <= -2)
    total = len(stock_features)
    bull_pct = bull / total if total else 0
    bear_pct = bear / total if total else 0
    if bull_pct > 0.6:  return "STRONG-UPTREND"
    if bull_pct > 0.4:  return "UPTREND"
    if bear_pct > 0.6:  return "STRONG-DOWNTREND"
    if bear_pct > 0.4:  return "DOWNTREND"
    return "RANGING"


# ── Volatility Regime ─────────────────────────────────────────────────────────

def _detect_volatility_regime(features: dict, cross: dict) -> str:
    vix      = _safe(cross.get("vix"))
    all_f    = features.get("stocks", []) + features.get("crypto", [])
    high_vol = sum(1 for f in all_f if f.get("vol_regime") == "HIGH")
    total    = len(all_f) if all_f else 1
    if vix and vix > 30:         return "CRISIS"
    if vix and vix > 20:         return "ELEVATED"
    if high_vol / total > 0.5:   return "VOLATILE"
    if vix and vix < 15:         return "COMPRESSED"
    return "NORMAL"


# ── Liquidity Regime ──────────────────────────────────────────────────────────

def _detect_liquidity_regime(microstructure: dict) -> str:
    all_micro = microstructure.get("stocks", []) + microstructure.get("crypto", [])
    if not all_micro:
        return "NORMAL"
    avg_liq   = sum(_safe(m.get("liquidity_score"), 50) for m in all_micro) / len(all_micro)
    avg_vol_r = sum(_safe(m.get("volume_ratio"), 1) for m in all_micro) / len(all_micro)
    if avg_liq > 70 and avg_vol_r > 1.5:  return "HIGH-LIQUIDITY"
    if avg_liq < 30 or avg_vol_r < 0.5:   return "LOW-LIQUIDITY"
    return "NORMAL"


# ── Macro Regime ──────────────────────────────────────────────────────────────

def _detect_macro_regime(cross: dict, news: list[dict]) -> str:
    bias          = cross.get("cross_asset_bias", "NEUTRAL")
    bull_news     = sum(1 for n in news if n.get("sentiment") == "bullish")
    total_news    = len(news) if news else 1
    news_bull_r   = bull_news / total_news
    if bias == "RISK-ON" and news_bull_r > 0.3:  return "RISK-ON"
    if bias == "RISK-OFF" or news_bull_r < 0.15: return "RISK-OFF"
    return "MIXED"


# ── Momentum Regime ───────────────────────────────────────────────────────────

def _detect_momentum_regime(features: dict) -> str:
    all_f = features.get("stocks", []) + features.get("crypto", [])
    if not all_f:
        return "NEUTRAL"
    avg_mom = sum(_safe(f.get("momentum")) for f in all_f) / len(all_f)
    avg_vwm = sum(_safe(f.get("vw_momentum")) for f in all_f) / len(all_f)
    if avg_mom > 0.3 and avg_vwm > 0.3:    return "STRONG-BULLISH"
    if avg_mom > 0.1:                       return "BULLISH"
    if avg_mom < -0.3 and avg_vwm < -0.3:  return "STRONG-BEARISH"
    if avg_mom < -0.1:                      return "BEARISH"
    return "NEUTRAL"


# ── Composite Regime ──────────────────────────────────────────────────────────

def _composite_regime(trend: str, volatility: str, macro: str, momentum: str) -> str:
    bull = sum([
        trend in ("STRONG-UPTREND", "UPTREND"),
        macro == "RISK-ON",
        momentum in ("STRONG-BULLISH", "BULLISH"),
        volatility in ("NORMAL", "COMPRESSED"),
    ])
    bear = sum([
        trend in ("STRONG-DOWNTREND", "DOWNTREND"),
        macro == "RISK-OFF",
        momentum in ("STRONG-BEARISH", "BEARISH"),
        volatility in ("CRISIS", "ELEVATED"),
    ])
    if bull >= 3:              return "BULL-MARKET"
    if bear >= 3:              return "BEAR-MARKET"
    if volatility == "CRISIS": return "CRISIS-MODE"
    if trend == "RANGING":     return "CONSOLIDATION"
    return "TRANSITIONAL"


# ── Main entry point ──────────────────────────────────────────────────────────

def detect_regime(features: dict, microstructure: dict,
                  cross_asset: dict, news: list[dict]) -> dict:

    trend      = _detect_trend_regime(features)
    volatility = _detect_volatility_regime(features, cross_asset)
    liquidity  = _detect_liquidity_regime(microstructure)
    macro      = _detect_macro_regime(cross_asset, news)
    momentum   = _detect_momentum_regime(features)
    composite  = _composite_regime(trend, volatility, macro, momentum)

    # HMM regime classification
    all_f      = features.get("stocks", []) + features.get("crypto", [])
    avg_trend  = sum(_safe(f.get("trend_score")) for f in all_f) / max(1, len(all_f))
    avg_vol    = sum(_safe(f.get("vol_pct")) for f in all_f) / max(1, len(all_f))
    avg_mom    = sum(_safe(f.get("momentum")) for f in all_f) / max(1, len(all_f))
    vix        = cross_asset.get("vix")

    hmm        = _hmm_regime(avg_trend, avg_vol, avg_mom, vix)
    bayesian   = _bayesian_switch(features, cross_asset, news)

    strategy_map = {
        "BULL-MARKET":   "Trend-following longs. Increase position sizes. Reduce cash.",
        "BEAR-MARKET":   "Defensive positioning. Shorts on weak names. Raise cash.",
        "CRISIS-MODE":   "Capital preservation. Max cash. Only safe-haven assets.",
        "CONSOLIDATION": "Range trading. Fade extremes. Tight stops. Reduce size.",
        "TRANSITIONAL":  "Wait for confirmation. Small positions. Monitor closely.",
    }

    return {
        "composite_regime":    composite,
        "trend_regime":        trend,
        "volatility_regime":   volatility,
        "liquidity_regime":    liquidity,
        "macro_regime":        macro,
        "momentum_regime":     momentum,
        "hmm_state":           hmm["hmm_state"],
        "hmm_state_probs":     hmm["state_probabilities"],
        "bayesian_dominant":   bayesian["dominant_regime"],
        "bayesian_probs":      bayesian,
        "recommended_strategy": strategy_map.get(composite, "Monitor and wait."),
        "vix":                 vix,
        "dxy":                 cross_asset.get("dxy"),
        "cross_asset_bias":    cross_asset.get("cross_asset_bias"),
    }
