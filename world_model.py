"""
world_model.py - World Economic Model / Economic Digital Twin

Models the global financial ecosystem:
- Central bank policy state
- Geopolitical risk index
- Supply chain stress
- Institutional flow estimation
- Retail sentiment proxy
- Liquidity propagation model
- Macro factor decomposition
"""
from __future__ import annotations


def _safe(v, d=0.0):
    return v if v is not None else d


# ── Central Bank Policy Model ─────────────────────────────────────────────────

def _model_central_bank(indices: list[dict], news: list[dict]) -> dict:
    """Infer central bank policy stance from market signals."""
    dxy   = next((i.get("price") for i in indices if "DXY" in str(i.get("symbol",""))), None)
    vix   = next((i.get("price") for i in indices if "VIX" in str(i.get("symbol",""))), None)
    dxy_c = next((i.get("change_%") for i in indices if "DXY" in str(i.get("symbol",""))), 0)

    # Hawkish/dovish signals from news
    hawk_words = ["rate hike", "hawkish", "tightening", "inflation", "raises rates"]
    dove_words = ["rate cut", "dovish", "easing", "pivot", "pause", "cuts rates"]
    hawk_count = sum(1 for n in news
                     if any(w in n.get("title","").lower() for w in hawk_words))
    dove_count = sum(1 for n in news
                     if any(w in n.get("title","").lower() for w in dove_words))

    if hawk_count > dove_count + 1:
        stance = "HAWKISH"
    elif dove_count > hawk_count + 1:
        stance = "DOVISH"
    else:
        stance = "NEUTRAL"

    # Dollar strength as policy proxy
    dollar_signal = "STRONG" if (dxy and dxy > 100) else ("WEAK" if dxy and dxy < 95 else "NEUTRAL")

    return {
        "policy_stance":   stance,
        "dollar_signal":   dollar_signal,
        "dxy":             dxy,
        "hawk_signals":    hawk_count,
        "dove_signals":    dove_count,
        "rate_direction":  "UP" if stance == "HAWKISH" else ("DOWN" if stance == "DOVISH" else "HOLD"),
    }


# ── Geopolitical Risk Index ───────────────────────────────────────────────────

def _model_geopolitical_risk(news: list[dict]) -> dict:
    """Build geopolitical risk index from news signals."""
    geo_words = ["war", "conflict", "sanctions", "attack", "invasion",
                 "crisis", "tension", "military", "nuclear", "tariff",
                 "trade war", "embargo", "coup", "protest"]
    safe_words = ["peace", "deal", "agreement", "ceasefire", "diplomacy", "treaty"]

    geo_count  = sum(1 for n in news
                     if any(w in n.get("title","").lower() for w in geo_words))
    safe_count = sum(1 for n in news
                     if any(w in n.get("title","").lower() for w in safe_words))

    total = len(news) if news else 1
    geo_ratio = geo_count / total

    if geo_ratio > 0.15:   risk_level = "EXTREME"
    elif geo_ratio > 0.08: risk_level = "HIGH"
    elif geo_ratio > 0.03: risk_level = "ELEVATED"
    else:                   risk_level = "LOW"

    return {
        "geo_risk_index":  round(geo_ratio * 100, 2),
        "risk_level":      risk_level,
        "geo_events":      geo_count,
        "safe_events":     safe_count,
        "market_impact":   "RISK-OFF" if risk_level in ("EXTREME","HIGH") else "NEUTRAL",
    }


# ── Supply Chain Stress Model ─────────────────────────────────────────────────

def _model_supply_chain(commodities: list[dict], news: list[dict]) -> dict:
    """Estimate supply chain stress from commodity prices and news."""
    oil   = next((c.get("price") for c in commodities if "OIL" in str(c.get("symbol","")).upper()), None)
    oil_c = next((c.get("change_%") for c in commodities if "OIL" in str(c.get("symbol","")).upper()), 0)
    gold  = next((c.get("price") for c in commodities if "GOLD" in str(c.get("symbol","")).upper()), None)

    supply_words = ["shortage", "supply chain", "disruption", "delay", "shortage",
                    "shipping", "port", "logistics", "inventory"]
    supply_stress = sum(1 for n in news
                        if any(w in n.get("title","").lower() for w in supply_words))

    # Oil price as supply chain proxy
    oil_stress = "HIGH" if (oil_c and abs(oil_c) > 3) else "NORMAL"

    stress_score = min(100, supply_stress * 10 + (abs(_safe(oil_c)) * 5))

    return {
        "supply_chain_stress": round(stress_score, 1),
        "oil_price":           oil,
        "oil_change_%":        oil_c,
        "oil_stress":          oil_stress,
        "supply_disruptions":  supply_stress,
        "stress_level":        "HIGH" if stress_score > 50 else ("MEDIUM" if stress_score > 20 else "LOW"),
    }


# ── Institutional Flow Estimation ─────────────────────────────────────────────

def _model_institutional_flows(stocks: list[dict],
                                microstructure: dict) -> dict:
    """
    Estimate institutional vs retail flow from volume and microstructure.
    Large blocks + low spread = institutional.
    High relative volume + wide spread = retail panic.
    """
    micro_stocks = microstructure.get("stocks", [])
    micro_map    = {m["symbol"]: m for m in micro_stocks}

    inst_buying  = 0
    inst_selling = 0
    retail_panic = 0

    for stock in stocks[:15]:
        sym   = stock.get("symbol","")
        micro = micro_map.get(sym, {})
        vol_r = _safe(micro.get("volume_ratio"), 1)
        liq   = _safe(micro.get("liquidity_score"), 50)
        ofi   = _safe(micro.get("order_flow_imbalance"), 0.5)
        chg   = _safe(stock.get("change_%"))

        # High liquidity + high volume + positive OFI = institutional buying
        if liq > 65 and vol_r > 1.5 and ofi > 0.6:
            inst_buying += 1
        elif liq > 65 and vol_r > 1.5 and ofi < 0.4:
            inst_selling += 1
        # Low liquidity + extreme volume = retail panic
        elif liq < 40 and vol_r > 2.0:
            retail_panic += 1

    total = len(stocks[:15]) or 1
    return {
        "institutional_buying_%":  round(inst_buying / total * 100, 1),
        "institutional_selling_%": round(inst_selling / total * 100, 1),
        "retail_panic_%":          round(retail_panic / total * 100, 1),
        "dominant_flow":           "INSTITUTIONAL-BUY" if inst_buying > inst_selling
                                   else ("INSTITUTIONAL-SELL" if inst_selling > inst_buying
                                   else "MIXED"),
    }


# ── Liquidity Propagation Model ───────────────────────────────────────────────

def _model_liquidity_propagation(indices: list[dict],
                                  microstructure: dict) -> dict:
    """
    Model how liquidity propagates through the market.
    VIX + average liquidity scores → liquidity state.
    """
    vix = next((i.get("price") for i in indices if "VIX" in str(i.get("symbol",""))), 18)
    all_micro = (microstructure.get("stocks",[]) + microstructure.get("crypto",[]))
    avg_liq   = (sum(_safe(m.get("liquidity_score"),50) for m in all_micro)
                 / max(1, len(all_micro)))
    avg_spread = (sum(_safe(m.get("effective_spread_%"),0.1) for m in all_micro)
                  / max(1, len(all_micro)))

    # Liquidity stress index
    liq_stress = max(0, (_safe(vix,18) - 15) * 2 + (avg_spread - 0.1) * 100)

    if liq_stress > 50:   liq_state = "LIQUIDITY-CRISIS"
    elif liq_stress > 25: liq_state = "LIQUIDITY-STRESS"
    elif liq_stress > 10: liq_state = "NORMAL"
    else:                  liq_state = "ABUNDANT-LIQUIDITY"

    return {
        "liquidity_stress_index": round(liq_stress, 2),
        "liquidity_state":        liq_state,
        "avg_market_liquidity":   round(avg_liq, 1),
        "avg_spread_%":           round(avg_spread, 4),
        "vix":                    vix,
        "propagation_risk":       "HIGH" if liq_state == "LIQUIDITY-CRISIS" else "LOW",
    }


# ── Macro Factor Decomposition ────────────────────────────────────────────────

def _decompose_macro_factors(stocks: list[dict], indices: list[dict],
                              commodities: list[dict]) -> dict:
    """
    Decompose market moves into macro factors:
    Growth, Inflation, Risk, Dollar, Commodity.
    """
    spx_chg  = next((i.get("change_%",0) for i in indices if "SPX" in str(i.get("symbol",""))), 0)
    vix_chg  = next((i.get("change_%",0) for i in indices if "VIX" in str(i.get("symbol",""))), 0)
    dxy_chg  = next((i.get("change_%",0) for i in indices if "DXY" in str(i.get("symbol",""))), 0)
    gold_chg = next((c.get("change_%",0) for c in commodities if "GOLD" in str(c.get("symbol","")).upper()), 0)
    oil_chg  = next((c.get("change_%",0) for c in commodities if "OIL" in str(c.get("symbol","")).upper()), 0)

    avg_stock_chg = (sum(_safe(s.get("change_%")) for s in stocks)
                     / max(1, len(stocks)))

    return {
        "growth_factor":    round(_safe(spx_chg), 4),
        "risk_factor":      round(-_safe(vix_chg), 4),   # VIX up = risk off
        "dollar_factor":    round(_safe(dxy_chg), 4),
        "inflation_factor": round(_safe(gold_chg) + _safe(oil_chg), 4),
        "equity_factor":    round(avg_stock_chg, 4),
        "dominant_factor":  max(
            {"GROWTH": abs(_safe(spx_chg)),
             "RISK":   abs(_safe(vix_chg)),
             "DOLLAR": abs(_safe(dxy_chg)),
             "INFLATION": abs(_safe(gold_chg))},
            key=lambda k: {"GROWTH": abs(_safe(spx_chg)),
                           "RISK":   abs(_safe(vix_chg)),
                           "DOLLAR": abs(_safe(dxy_chg)),
                           "INFLATION": abs(_safe(gold_chg))}[k]
        ),
    }


# ── Main entry point ──────────────────────────────────────────────────────────

def run_world_model(stocks: list[dict], crypto: list[dict],
                    forex: list[dict], commodities: list[dict],
                    indices: list[dict], news: list[dict],
                    microstructure: dict) -> dict:
    """Build the Economic Digital Twin from all available data."""

    central_bank  = _model_central_bank(indices, news)
    geo_risk      = _model_geopolitical_risk(news)
    supply_chain  = _model_supply_chain(commodities, news)
    inst_flows    = _model_institutional_flows(stocks, microstructure)
    liquidity     = _model_liquidity_propagation(indices, microstructure)
    macro_factors = _decompose_macro_factors(stocks, indices, commodities)

    # World state summary
    risk_signals = sum([
        geo_risk["risk_level"] in ("EXTREME","HIGH"),
        liquidity["liquidity_state"] in ("LIQUIDITY-CRISIS","LIQUIDITY-STRESS"),
        central_bank["policy_stance"] == "HAWKISH",
        supply_chain["stress_level"] == "HIGH",
    ])

    world_state = (
        "CRISIS"       if risk_signals >= 3 else
        "RISK-OFF"     if risk_signals >= 2 else
        "CAUTIOUS"     if risk_signals == 1 else
        "RISK-ON"
    )

    return {
        "world_state":     world_state,
        "central_bank":    central_bank,
        "geopolitical":    geo_risk,
        "supply_chain":    supply_chain,
        "inst_flows":      inst_flows,
        "liquidity":       liquidity,
        "macro_factors":   macro_factors,
        "risk_signal_count": risk_signals,
    }
