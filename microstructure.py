"""
microstructure.py - Elite Market Microstructure Engine

Implements:
- Order Flow Imbalance (OFI) with buy/sell pressure quantification
- Microprice Model (bid/ask volume-weighted fair value)
- Queue Position Modeling (fill probability, slippage estimation)
- Spread Modeling (effective spread, adverse selection cost)
- Liquidity Score (0-100)
- VWAP deviation, BB width, volume confirmation
"""
from __future__ import annotations
import math


def _safe(v, d=0.0):
    return v if v is not None else d


# ── Order Flow Imbalance ──────────────────────────────────────────────────────
# OFI_t = sum(q_bid) - sum(q_ask)
# Approximated from intraday price position and volume

def _compute_ofi(price: float, high: float, low: float,
                 volume: float, chg: float) -> dict:
    intraday_range = high - low
    if intraday_range <= 0:
        ofi_raw = 0.0
    else:
        # Price position in range: 1 = at high (all buying), 0 = at low (all selling)
        price_position = (price - low) / intraday_range

    # Estimate bid/ask volume split from price position
    vol_bid = volume * price_position
    vol_ask = volume * (1 - price_position)

    # OFI = net buy volume - net sell volume (normalized)
    ofi_raw   = vol_bid - vol_ask
    ofi_norm  = round(ofi_raw / volume, 4) if volume > 0 else 0.0  # -1 to +1

    # Cumulative OFI signal
    if ofi_norm > 0.3:   flow_bias = "STRONG-BUYING"
    elif ofi_norm > 0.1: flow_bias = "BUYING"
    elif ofi_norm < -0.3: flow_bias = "STRONG-SELLING"
    elif ofi_norm < -0.1: flow_bias = "SELLING"
    else:                 flow_bias = "NEUTRAL"

    return {
        "ofi_normalized":  ofi_norm,
        "vol_bid_est":     round(vol_bid, 0),
        "vol_ask_est":     round(vol_ask, 0),
        "flow_bias":       flow_bias,
        "price_position":  round(price_position, 4) if intraday_range > 0 else 0.5,
    }


# ── Microprice Model ──────────────────────────────────────────────────────────
# P_micro = (P_ask * V_bid + P_bid * V_ask) / (V_bid + V_ask)
# Predicts short-term fair value using bid/ask imbalance

def _compute_microprice(price: float, atr: float,
                        vol_bid: float, vol_ask: float) -> dict:
    # Estimate bid/ask from ATR spread
    half_spread = atr * 0.1
    p_bid = price - half_spread
    p_ask = price + half_spread

    total_vol = vol_bid + vol_ask
    if total_vol <= 0:
        microprice = price
        imbalance  = 0.0
    else:
        microprice = (p_ask * vol_bid + p_bid * vol_ask) / total_vol
        imbalance  = (vol_bid - vol_ask) / total_vol  # -1 to +1

    # Direction signal from microprice vs mid
    mid = (p_bid + p_ask) / 2
    micro_signal = "BULLISH" if microprice > mid else ("BEARISH" if microprice < mid else "NEUTRAL")

    return {
        "microprice":        round(microprice, 6),
        "mid_price":         round(mid, 6),
        "microprice_signal": micro_signal,
        "bid_ask_imbalance": round(imbalance, 4),
        "estimated_bid":     round(p_bid, 6),
        "estimated_ask":     round(p_ask, 6),
    }


# ── Queue Position & Fill Probability ────────────────────────────────────────
# Estimates execution probability and expected slippage
# Used in HFT for limit order placement

def _compute_queue_model(price: float, atr: float, vol_ratio: float,
                         liquidity_score: float, ofi_norm: float) -> dict:
    # Fill probability for a limit order at current price
    # Higher liquidity + favorable OFI = higher fill probability
    base_fill_prob = min(0.95, max(0.05,
        0.5 +
        (ofi_norm * 0.3) +           # OFI contribution
        ((liquidity_score - 50) / 200)  # liquidity contribution
    ))

    # Expected slippage (in ATR units)
    # Low liquidity + high volatility = more slippage
    vol_factor     = max(0.5, min(3.0, 1.0 / vol_ratio)) if vol_ratio > 0 else 1.0
    slippage_atr   = round(0.1 * vol_factor * (1 - liquidity_score / 100), 4)
    slippage_pct   = round(slippage_atr * atr / price * 100, 4) if price > 0 else 0

    # Adverse selection cost: probability that the market moves against you after fill
    adverse_sel    = round(max(0, 0.5 - abs(ofi_norm) * 0.4), 4)

    # Market impact estimate
    market_impact_pct = round(slippage_pct * 1.5, 4)

    return {
        "fill_probability_%":    round(base_fill_prob * 100, 1),
        "expected_slippage_%":   slippage_pct,
        "adverse_selection":     adverse_sel,
        "market_impact_%":       market_impact_pct,
        "recommended_order":     "LIMIT" if liquidity_score > 60 else "TWAP" if liquidity_score > 30 else "VWAP",
    }


# ── Spread Modeling ───────────────────────────────────────────────────────────

def _compute_spread(price: float, atr: float, vol_ratio: float) -> dict:
    # Effective spread proxy (ATR-based)
    effective_spread_pct = round(atr / price * 100 * 0.2, 4) if price > 0 else 0

    # Roll's spread estimator proxy
    roll_spread = round(effective_spread_pct * 0.8, 4)

    # Spread regime
    if effective_spread_pct < 0.05:   spread_regime = "TIGHT"
    elif effective_spread_pct < 0.2:  spread_regime = "NORMAL"
    elif effective_spread_pct < 0.5:  spread_regime = "WIDE"
    else:                              spread_regime = "VERY-WIDE"

    return {
        "effective_spread_%": effective_spread_pct,
        "roll_spread_%":      roll_spread,
        "spread_regime":      spread_regime,
    }


# ── Main instrument analysis ──────────────────────────────────────────────────

def analyze_microstructure(instrument: dict) -> dict:
    price    = _safe(instrument.get("price"), 1)
    high     = _safe(instrument.get("high"), price)
    low      = _safe(instrument.get("low"), price)
    open_    = _safe(instrument.get("open"), price)
    volume   = _safe(instrument.get("volume"))
    avg_vol  = _safe(instrument.get("avg_vol_10d"), 1)
    rel_vol  = _safe(instrument.get("relative_volume"))
    atr      = _safe(instrument.get("atr"), price * 0.02)
    vwap     = _safe(instrument.get("vwap"), price)
    bb_upper = _safe(instrument.get("bb_upper"), price * 1.02)
    bb_lower = _safe(instrument.get("bb_lower"), price * 0.98)
    chg      = _safe(instrument.get("change_%"))

    vol_ratio       = volume / avg_vol if avg_vol > 0 else 1.0
    intraday_range  = high - low
    range_pct       = round(intraday_range / price * 100, 4) if price else 0
    spread_proxy    = round(atr / price * 100, 4) if price else 0
    liquidity_score = min(100, round(50 * min(vol_ratio, 3.0) + 50 * max(0, 1 - spread_proxy / 5), 1))
    vwap_dev_pct    = round((price - vwap) / vwap * 100, 4) if vwap else 0
    bb_width        = round((bb_upper - bb_lower) / price * 100, 4) if price else 0
    volume_confirms = (chg > 0 and vol_ratio > 1.2) or (chg < 0 and vol_ratio > 1.2)

    # Advanced microstructure
    ofi_data    = _compute_ofi(price, high, low, volume, chg)
    micro_data  = _compute_microprice(price, atr, ofi_data["vol_bid_est"], ofi_data["vol_ask_est"])
    queue_data  = _compute_queue_model(price, atr, vol_ratio, liquidity_score, ofi_data["ofi_normalized"])
    spread_data = _compute_spread(price, atr, vol_ratio)

    return {
        "symbol":              instrument.get("symbol"),
        "price":               price,
        # Basic
        "intraday_range_%":    range_pct,
        "spread_proxy_%":      spread_proxy,
        "liquidity_score":     liquidity_score,
        "vwap_deviation_%":    vwap_dev_pct,
        "bb_width_%":          bb_width,
        "volume_ratio":        round(vol_ratio, 2),
        "volume_confirms":     volume_confirms,
        "relative_volume":     round(rel_vol, 2) if rel_vol else None,
        # OFI
        "order_flow_imbalance": ofi_data["ofi_normalized"],
        "flow_bias":           ofi_data["flow_bias"],
        "vol_bid_est":         ofi_data["vol_bid_est"],
        "vol_ask_est":         ofi_data["vol_ask_est"],
        "price_position":      ofi_data["price_position"],
        # Microprice
        "microprice":          micro_data["microprice"],
        "microprice_signal":   micro_data["microprice_signal"],
        "bid_ask_imbalance":   micro_data["bid_ask_imbalance"],
        # Queue / Execution
        "fill_probability_%":  queue_data["fill_probability_%"],
        "expected_slippage_%": queue_data["expected_slippage_%"],
        "adverse_selection":   queue_data["adverse_selection"],
        "market_impact_%":     queue_data["market_impact_%"],
        "recommended_order":   queue_data["recommended_order"],
        # Spread
        "effective_spread_%":  spread_data["effective_spread_%"],
        "spread_regime":       spread_data["spread_regime"],
    }


def run_microstructure(stocks, crypto, forex, commodities, indices) -> dict:
    return {
        "stocks":      [analyze_microstructure(s) for s in stocks],
        "crypto":      [analyze_microstructure(c) for c in crypto],
        "forex":       [analyze_microstructure(f) for f in forex],
        "commodities": [analyze_microstructure(c) for c in commodities],
        "indices":     [analyze_microstructure(i) for i in indices],
    }
