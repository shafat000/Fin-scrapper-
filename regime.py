"""
regime.py - Market Regime Detection Engine
Classifies the current market regime across trend, volatility,
liquidity, and macro dimensions. Used by all downstream AI agents.
"""
from __future__ import annotations


def _safe(v, d=0.0):
    return v if v is not None else d


# ── Trend Regime ──────────────────────────────────────────────────────────────

def _detect_trend_regime(features: dict) -> str:
    stock_features = features.get("stocks", [])
    if not stock_features:
        return "UNKNOWN"

    bull = sum(1 for f in stock_features if f.get("trend_score", 0) >= 2)
    bear = sum(1 for f in stock_features if f.get("trend_score", 0) <= -2)
    total = len(stock_features)

    bull_pct = bull / total if total else 0
    bear_pct = bear / total if total else 0

    if bull_pct > 0.6:   return "STRONG-UPTREND"
    if bull_pct > 0.4:   return "UPTREND"
    if bear_pct > 0.6:   return "STRONG-DOWNTREND"
    if bear_pct > 0.4:   return "DOWNTREND"
    return "RANGING"


# ── Volatility Regime ─────────────────────────────────────────────────────────

def _detect_volatility_regime(features: dict, cross: dict) -> str:
    vix = _safe(cross.get("vix"))
    all_features = features.get("stocks", []) + features.get("crypto", [])

    high_vol = sum(1 for f in all_features if f.get("vol_regime") == "HIGH")
    total    = len(all_features) if all_features else 1

    if vix and vix > 30:          return "CRISIS"
    if vix and vix > 20:          return "ELEVATED"
    if high_vol / total > 0.5:    return "VOLATILE"
    if vix and vix < 15:          return "COMPRESSED"
    return "NORMAL"


# ── Liquidity Regime ──────────────────────────────────────────────────────────

def _detect_liquidity_regime(microstructure: dict) -> str:
    all_micro = (microstructure.get("stocks", []) +
                 microstructure.get("crypto", []))
    if not all_micro:
        return "NORMAL"

    avg_liq = sum(_safe(m.get("liquidity_score"), 50) for m in all_micro) / len(all_micro)
    avg_vol_ratio = sum(_safe(m.get("volume_ratio"), 1) for m in all_micro) / len(all_micro)

    if avg_liq > 70 and avg_vol_ratio > 1.5:  return "HIGH-LIQUIDITY"
    if avg_liq < 30 or avg_vol_ratio < 0.5:   return "LOW-LIQUIDITY"
    return "NORMAL"


# ── Macro Regime ──────────────────────────────────────────────────────────────

def _detect_macro_regime(cross: dict, news: list[dict]) -> str:
    bias = cross.get("cross_asset_bias", "NEUTRAL")

    # Count macro news signals
    bullish_news = sum(1 for n in news if n.get("sentiment") == "bullish")
    bearish_news = sum(1 for n in news if n.get("sentiment") == "bearish")
    total_news   = len(news) if news else 1

    news_bull_ratio = bullish_news / total_news

    if bias == "RISK-ON" and news_bull_ratio > 0.3:   return "RISK-ON"
    if bias == "RISK-OFF" or news_bull_ratio < 0.15:  return "RISK-OFF"
    return "MIXED"


# ── Momentum Regime ───────────────────────────────────────────────────────────

def _detect_momentum_regime(features: dict) -> str:
    all_f = features.get("stocks", []) + features.get("crypto", [])
    if not all_f:
        return "NEUTRAL"

    avg_mom = sum(_safe(f.get("momentum")) for f in all_f) / len(all_f)
    avg_vwm = sum(_safe(f.get("vw_momentum")) for f in all_f) / len(all_f)

    if avg_mom > 0.3 and avg_vwm > 0.3:   return "STRONG-BULLISH"
    if avg_mom > 0.1:                      return "BULLISH"
    if avg_mom < -0.3 and avg_vwm < -0.3: return "STRONG-BEARISH"
    if avg_mom < -0.1:                     return "BEARISH"
    return "NEUTRAL"


# ── Composite Regime Score ────────────────────────────────────────────────────

def _composite_regime(trend: str, volatility: str, macro: str, momentum: str) -> str:
    bull_signals = sum([
        trend in ("STRONG-UPTREND", "UPTREND"),
        macro == "RISK-ON",
        momentum in ("STRONG-BULLISH", "BULLISH"),
        volatility in ("NORMAL", "COMPRESSED"),
    ])
    bear_signals = sum([
        trend in ("STRONG-DOWNTREND", "DOWNTREND"),
        macro == "RISK-OFF",
        momentum in ("STRONG-BEARISH", "BEARISH"),
        volatility in ("CRISIS", "ELEVATED"),
    ])

    if bull_signals >= 3:   return "BULL-MARKET"
    if bear_signals >= 3:   return "BEAR-MARKET"
    if volatility == "CRISIS": return "CRISIS-MODE"
    if trend == "RANGING":  return "CONSOLIDATION"
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

    # Recommended strategy per regime
    strategy_map = {
        "BULL-MARKET":    "Trend-following longs. Increase position sizes. Reduce cash.",
        "BEAR-MARKET":    "Defensive positioning. Shorts on weak names. Raise cash.",
        "CRISIS-MODE":    "Capital preservation. Max cash. Only safe-haven assets.",
        "CONSOLIDATION":  "Range trading. Fade extremes. Tight stops. Reduce size.",
        "TRANSITIONAL":   "Wait for confirmation. Small positions. Monitor closely.",
    }

    return {
        "composite_regime":  composite,
        "trend_regime":      trend,
        "volatility_regime": volatility,
        "liquidity_regime":  liquidity,
        "macro_regime":      macro,
        "momentum_regime":   momentum,
        "recommended_strategy": strategy_map.get(composite, "Monitor and wait."),
        "vix":               cross_asset.get("vix"),
        "dxy":               cross_asset.get("dxy"),
        "cross_asset_bias":  cross_asset.get("cross_asset_bias"),
    }
