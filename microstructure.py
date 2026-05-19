"""
microstructure.py - Market Microstructure Engine
Computes spread, liquidity, volume profile, order flow imbalance,
and intraday structure from raw scanner data.
"""
from __future__ import annotations


def _safe(v, d=0.0):
    return v if v is not None else d


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
    chg_open = _safe(instrument.get("change_from_open_%"))

    # Intraday range and spread proxy
    intraday_range     = high - low
    range_pct          = round((intraday_range / price) * 100, 4) if price else 0
    spread_proxy       = round(atr / price * 100, 4) if price else 0

    # Liquidity score (0-100): high volume + low spread = high liquidity
    vol_ratio          = volume / avg_vol if avg_vol > 0 else 1.0
    liquidity_score    = min(100, round(50 * min(vol_ratio, 3.0) + 50 * max(0, 1 - spread_proxy / 5), 1))

    # Order flow imbalance proxy: price position within day's range
    if intraday_range > 0:
        ofi = round((price - low) / intraday_range, 4)  # 0=at low, 1=at high
    else:
        ofi = 0.5

    # Buying/selling pressure from intraday close position
    if ofi > 0.7:
        flow_bias = "BUYING"
    elif ofi < 0.3:
        flow_bias = "SELLING"
    else:
        flow_bias = "NEUTRAL"

    # VWAP deviation
    vwap_dev_pct = round((price - vwap) / vwap * 100, 4) if vwap else 0

    # Bollinger Band width (volatility expansion/contraction)
    bb_width = round((bb_upper - bb_lower) / price * 100, 4) if price else 0

    # Volume profile: is today's volume confirming the move?
    volume_confirms = (chg > 0 and vol_ratio > 1.2) or (chg < 0 and vol_ratio > 1.2)

    # Gap analysis
    gap_pct = round((open_ - _safe(instrument.get("price"), open_)) / open_ * 100, 4) if open_ else 0

    return {
        "symbol":           instrument.get("symbol"),
        "price":            price,
        "intraday_range_%": range_pct,
        "spread_proxy_%":   spread_proxy,
        "liquidity_score":  liquidity_score,
        "order_flow_imbalance": ofi,
        "flow_bias":        flow_bias,
        "vwap_deviation_%": vwap_dev_pct,
        "bb_width_%":       bb_width,
        "volume_ratio":     round(vol_ratio, 2),
        "volume_confirms":  volume_confirms,
        "relative_volume":  round(rel_vol, 2) if rel_vol else None,
    }


def run_microstructure(stocks: list[dict], crypto: list[dict],
                       forex: list[dict], commodities: list[dict],
                       indices: list[dict]) -> dict:
    return {
        "stocks":      [analyze_microstructure(s) for s in stocks],
        "crypto":      [analyze_microstructure(c) for c in crypto],
        "forex":       [analyze_microstructure(f) for f in forex],
        "commodities": [analyze_microstructure(c) for c in commodities],
        "indices":     [analyze_microstructure(i) for i in indices],
    }
