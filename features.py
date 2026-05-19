"""
features.py - Feature Extraction Engine
Derives momentum factors, volatility features, cross-asset signals,
and composite feature vectors used by the regime detector and AI agents.
"""
from __future__ import annotations
import math


def _safe(v, d=0.0):
    return v if v is not None else d


# ── Per-instrument feature vector ─────────────────────────────────────────────

def extract_features(instrument: dict, micro: dict) -> dict:
    price    = _safe(instrument.get("price"), 1)
    rsi      = _safe(instrument.get("rsi"), 50)
    macd     = _safe(instrument.get("macd"))
    macd_s   = _safe(instrument.get("macd_signal"))
    ema20    = _safe(instrument.get("ema20"), price)
    ema50    = _safe(instrument.get("ema50"), price)
    ema200   = _safe(instrument.get("ema200"), price)
    atr      = _safe(instrument.get("atr"), price * 0.02)
    chg      = _safe(instrument.get("change_%"))
    vol_r    = _safe(micro.get("volume_ratio"), 1.0)
    ofi      = _safe(micro.get("order_flow_imbalance"), 0.5)
    liq      = _safe(micro.get("liquidity_score"), 50)
    bb_w     = _safe(micro.get("bb_width_%"))

    # Trend strength: EMA alignment score (-3 to +3)
    trend_score = 0
    if price > ema20: trend_score += 1
    if price > ema50: trend_score += 1
    if price > ema200: trend_score += 1
    if ema20 > ema50: trend_score += 0  # already counted via price
    if ema20 < ema50: trend_score -= 1
    if ema50 < ema200: trend_score -= 1

    # Momentum: RSI + MACD combined
    rsi_norm    = (rsi - 50) / 50          # -1 to +1
    macd_signal = 1 if macd > macd_s else -1
    momentum    = round((rsi_norm + macd_signal) / 2, 4)

    # Volatility: ATR as % of price, normalized
    vol_pct     = (atr / price * 100) if price else 0
    vol_regime  = "HIGH" if vol_pct > 3 else ("LOW" if vol_pct < 1 else "NORMAL")

    # Volume-weighted momentum
    vw_momentum = round(momentum * min(vol_r, 2.0), 4)

    # Mean reversion signal: distance from EMA50
    ema50_dev   = round((price - ema50) / ema50 * 100, 4) if ema50 else 0

    # Composite feature score (-100 to +100)
    composite = round(
        trend_score * 15 +
        momentum * 30 +
        ofi * 20 - 10 +          # ofi: 0.5=neutral, 1=full buy
        (vol_r - 1) * 10 +
        (liq / 100) * 10,
        2
    )
    composite = max(-100, min(100, composite))

    return {
        "symbol":         instrument.get("symbol"),
        "trend_score":    trend_score,       # -3 to +3
        "momentum":       momentum,          # -1 to +1
        "vw_momentum":    vw_momentum,
        "vol_pct":        round(vol_pct, 4),
        "vol_regime":     vol_regime,
        "ema50_dev_%":    ema50_dev,
        "ofi":            ofi,
        "liquidity":      liq,
        "bb_width_%":     bb_w,
        "composite":      composite,         # -100 to +100
        "daily_chg_%":    chg,
    }


# ── Cross-asset feature extraction ────────────────────────────────────────────

def extract_cross_asset(stocks: list[dict], crypto: list[dict],
                        forex: list[dict], commodities: list[dict],
                        indices: list[dict]) -> dict:

    def _avg_chg(items):
        vals = [_safe(i.get("change_%")) for i in items if i.get("change_%") is not None]
        return round(sum(vals) / len(vals), 4) if vals else 0.0

    def _avg_rsi(items):
        vals = [_safe(i.get("rsi")) for i in items if i.get("rsi") is not None]
        return round(sum(vals) / len(vals), 2) if vals else 50.0

    # VIX level
    vix = next((i.get("price") for i in indices if "VIX" in str(i.get("symbol", ""))), None)
    dxy = next((i.get("price") for i in indices if "DXY" in str(i.get("symbol", ""))), None)
    spx = next((i.get("change_%") for i in indices if "SPX" in str(i.get("symbol", ""))), None)
    gold = next((i.get("change_%") for i in commodities if "GOLD" in str(i.get("symbol", ""))), None)
    btc  = next((i.get("change_%") for i in crypto if "BTC" in str(i.get("symbol", ""))), None)

    # Risk-on/off signal from cross-asset
    risk_signals = 0
    if spx and spx > 0:   risk_signals += 1
    if btc and btc > 0:   risk_signals += 1
    if gold and gold < 0: risk_signals += 1   # gold down = risk-on
    if vix and vix < 20:  risk_signals += 1
    if dxy and dxy < 0:   risk_signals -= 1   # strong dollar = risk-off

    cross_asset_bias = "RISK-ON" if risk_signals >= 3 else ("RISK-OFF" if risk_signals <= 1 else "NEUTRAL")

    return {
        "stock_avg_chg_%":  _avg_chg(stocks),
        "crypto_avg_chg_%": _avg_chg(crypto),
        "forex_avg_chg_%":  _avg_chg(forex),
        "stock_avg_rsi":    _avg_rsi(stocks),
        "crypto_avg_rsi":   _avg_rsi(crypto),
        "vix":              vix,
        "dxy":              dxy,
        "spx_chg_%":        spx,
        "gold_chg_%":       gold,
        "btc_chg_%":        btc,
        "risk_signal_score": risk_signals,
        "cross_asset_bias": cross_asset_bias,
    }


# ── Main entry point ──────────────────────────────────────────────────────────

def run_feature_extraction(stocks: list[dict], crypto: list[dict],
                           forex: list[dict], commodities: list[dict],
                           indices: list[dict], microstructure: dict) -> dict:

    def _extract(instruments, key):
        micros = {m["symbol"]: m for m in microstructure.get(key, [])}
        return [extract_features(inst, micros.get(inst.get("symbol"), {}))
                for inst in instruments]

    cross = extract_cross_asset(stocks, crypto, forex, commodities, indices)

    return {
        "stocks":       _extract(stocks, "stocks"),
        "crypto":       _extract(crypto, "crypto"),
        "forex":        _extract(forex, "forex"),
        "commodities":  _extract(commodities, "commodities"),
        "indices":      _extract(indices, "indices"),
        "cross_asset":  cross,
    }
