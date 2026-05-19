"""
market_simulator.py - Multi-Agent Market Simulator

Simulates a synthetic financial universe with competing agents:
- AI Hedge Fund agents (trend-following, mean-reversion, momentum)
- Retail Trader agents (momentum-chasing, panic-selling)
- Market Maker agents (spread capture, inventory management)
- Central Bank agent (liquidity injection, rate policy)

Produces emergent market behavior and Nash equilibrium estimates.
"""
from __future__ import annotations
import math
import random


def _safe(v, d=0.0):
    return v if v is not None else d


# ── Agent Definitions ─────────────────────────────────────────────────────────

class HedgeFundAgent:
    """Institutional trend-following agent."""
    def __init__(self, name: str, strategy: str, capital: float):
        self.name     = name
        self.strategy = strategy
        self.capital  = capital
        self.pnl      = 0.0

    def decide(self, price: float, trend_score: float, momentum: float,
               regime: str) -> dict:
        if self.strategy == "TREND":
            signal = "BUY" if trend_score > 1 else ("SELL" if trend_score < -1 else "HOLD")
            size   = min(0.15, abs(trend_score) * 0.05) * self.capital
        elif self.strategy == "MEAN_REVERSION":
            signal = "BUY" if momentum < -0.3 else ("SELL" if momentum > 0.3 else "HOLD")
            size   = min(0.10, abs(momentum) * 0.08) * self.capital
        else:  # MOMENTUM
            signal = "BUY" if momentum > 0.2 else ("SELL" if momentum < -0.2 else "HOLD")
            size   = min(0.12, abs(momentum) * 0.06) * self.capital

        # Regime adjustment
        if regime == "CRISIS-MODE" and signal == "BUY":
            signal = "HOLD"
            size   = 0

        return {"agent": self.name, "type": "HEDGE_FUND",
                "strategy": self.strategy, "signal": signal,
                "size_usd": round(size, 2), "conviction": abs(trend_score + momentum)}


class RetailAgent:
    """Retail trader — momentum-chasing, panic-prone."""
    def __init__(self, name: str, capital: float):
        self.name    = name
        self.capital = capital

    def decide(self, price: float, chg_pct: float, vix: float) -> dict:
        # Retail chases momentum and panics on drops
        if chg_pct > 3:
            signal = "BUY"   # FOMO buying
            size   = 0.05 * self.capital
        elif chg_pct < -3:
            signal = "SELL"  # panic selling
            size   = 0.08 * self.capital
        elif vix and vix > 25:
            signal = "SELL"  # fear-driven
            size   = 0.06 * self.capital
        else:
            signal = "HOLD"
            size   = 0

        return {"agent": self.name, "type": "RETAIL",
                "signal": signal, "size_usd": round(size, 2),
                "behavior": "FOMO" if signal == "BUY" else ("PANIC" if signal == "SELL" else "PASSIVE")}


class MarketMakerAgent:
    """Market maker — provides liquidity, captures spread."""
    def __init__(self, name: str, capital: float):
        self.name    = name
        self.capital = capital

    def decide(self, spread_pct: float, vol_ratio: float) -> dict:
        # Market makers widen spreads in volatile markets
        if spread_pct > 0.3 or vol_ratio > 2.5:
            action = "WIDEN_SPREAD"
            liquidity_provided = 0.3 * self.capital
        elif spread_pct < 0.05:
            action = "TIGHTEN_SPREAD"
            liquidity_provided = 0.8 * self.capital
        else:
            action = "MAINTAIN"
            liquidity_provided = 0.5 * self.capital

        return {"agent": self.name, "type": "MARKET_MAKER",
                "action": action, "liquidity_provided_usd": round(liquidity_provided, 2),
                "spread_action": action}


class CentralBankAgent:
    """Central bank — injects/withdraws liquidity based on conditions."""
    def decide(self, vix: float, policy_stance: str) -> dict:
        if vix and vix > 30:
            action   = "EMERGENCY_LIQUIDITY"
            amount   = 500e9
        elif policy_stance == "DOVISH":
            action   = "QE_INJECTION"
            amount   = 100e9
        elif policy_stance == "HAWKISH":
            action   = "QT_WITHDRAWAL"
            amount   = -50e9
        else:
            action   = "NEUTRAL"
            amount   = 0

        return {"agent": "CENTRAL_BANK", "type": "CENTRAL_BANK",
                "action": action, "liquidity_change_usd": amount,
                "market_impact": "BULLISH" if amount > 0 else ("BEARISH" if amount < 0 else "NEUTRAL")}


# ── Nash Equilibrium Estimation ───────────────────────────────────────────────

def _estimate_nash_equilibrium(agent_decisions: list[dict]) -> dict:
    """
    Estimate Nash equilibrium from agent decisions.
    Equilibrium = no agent can improve by unilaterally changing strategy.
    """
    buy_pressure  = sum(d.get("size_usd",0) for d in agent_decisions if d.get("signal") == "BUY")
    sell_pressure = sum(d.get("size_usd",0) for d in agent_decisions if d.get("signal") == "SELL")
    total         = buy_pressure + sell_pressure + 1

    buy_ratio  = buy_pressure / total
    sell_ratio = sell_pressure / total

    # Equilibrium: market clears when buy = sell pressure
    imbalance = buy_pressure - sell_pressure
    if abs(imbalance) < total * 0.1:
        equilibrium = "NEAR-EQUILIBRIUM"
    elif imbalance > 0:
        equilibrium = "BUY-PRESSURE-DOMINANT"
    else:
        equilibrium = "SELL-PRESSURE-DOMINANT"

    return {
        "equilibrium_state":  equilibrium,
        "buy_pressure_usd":   round(buy_pressure, 2),
        "sell_pressure_usd":  round(sell_pressure, 2),
        "net_imbalance_usd":  round(imbalance, 2),
        "buy_ratio":          round(buy_ratio, 3),
        "sell_ratio":         round(sell_ratio, 3),
        "predicted_direction": "UP" if imbalance > 0 else ("DOWN" if imbalance < 0 else "FLAT"),
    }


# ── Emergent Behavior Detection ───────────────────────────────────────────────

def _detect_emergent_behavior(agent_decisions: list[dict],
                               nash: dict) -> list[str]:
    """Detect emergent market behaviors from agent interactions."""
    behaviors = []

    retail_panic = sum(1 for d in agent_decisions
                       if d.get("behavior") == "PANIC")
    hf_buying    = sum(1 for d in agent_decisions
                       if d.get("type") == "HEDGE_FUND" and d.get("signal") == "BUY")
    mm_widening  = sum(1 for d in agent_decisions
                       if d.get("spread_action") == "WIDEN_SPREAD")

    if retail_panic > 0 and hf_buying > 0:
        behaviors.append("SMART-MONEY-BUYING-RETAIL-PANIC: Institutional accumulation during retail fear")
    if mm_widening > 0:
        behaviors.append("LIQUIDITY-WITHDRAWAL: Market makers widening spreads, execution costs rising")
    if nash["equilibrium_state"] == "BUY-PRESSURE-DOMINANT":
        behaviors.append("DEMAND-IMBALANCE: More buyers than sellers, price pressure upward")
    if nash["equilibrium_state"] == "SELL-PRESSURE-DOMINANT":
        behaviors.append("SUPPLY-IMBALANCE: More sellers than buyers, price pressure downward")

    return behaviors if behaviors else ["NORMAL-MARKET-DYNAMICS"]


# ── Main entry point ──────────────────────────────────────────────────────────

def run_market_simulation(stocks: list[dict], regime: dict,
                           world_model: dict, microstructure: dict) -> dict:
    """Run multi-agent market simulation for top instruments."""
    random.seed(42)

    vix            = _safe(regime.get("vix"), 18)
    composite      = regime.get("composite_regime", "TRANSITIONAL")
    policy_stance  = world_model.get("central_bank", {}).get("policy_stance", "NEUTRAL")

    # Initialize agents
    hf_trend  = HedgeFundAgent("Citadel-Alpha",   "TREND",          10e9)
    hf_mr     = HedgeFundAgent("TwoSigma-MR",     "MEAN_REVERSION", 8e9)
    hf_mom    = HedgeFundAgent("Millennium-Mom",  "MOMENTUM",       6e9)
    retail1   = RetailAgent("RetailCrowd-A", 500e6)
    retail2   = RetailAgent("RetailCrowd-B", 300e6)
    mm        = MarketMakerAgent("Virtu-MM", 2e9)
    cb        = CentralBankAgent()

    simulation_results = []

    for stock in stocks[:5]:
        sym         = stock.get("symbol","")
        price       = _safe(stock.get("price"), 100)
        chg         = _safe(stock.get("change_%"))
        trend_score = 0
        momentum    = 0

        # Get features from microstructure
        micro_map = {m["symbol"]: m for m in microstructure.get("stocks",[])}
        micro     = micro_map.get(sym, {})
        spread    = _safe(micro.get("effective_spread_%"), 0.1)
        vol_ratio = _safe(micro.get("volume_ratio"), 1.0)
        ofi       = _safe(micro.get("order_flow_imbalance"), 0.5)

        # Agent decisions
        decisions = [
            hf_trend.decide(price, trend_score + ofi * 2 - 1, momentum, composite),
            hf_mr.decide(price, trend_score, momentum, composite),
            hf_mom.decide(price, trend_score, momentum, composite),
            retail1.decide(price, chg, vix),
            retail2.decide(price, chg, vix),
            mm.decide(spread, vol_ratio),
            cb.decide(vix, policy_stance),
        ]

        nash      = _estimate_nash_equilibrium(decisions)
        emergent  = _detect_emergent_behavior(decisions, nash)

        simulation_results.append({
            "symbol":            sym,
            "price":             price,
            "agent_decisions":   decisions,
            "nash_equilibrium":  nash,
            "emergent_behavior": emergent,
            "predicted_direction": nash["predicted_direction"],
        })

    # Aggregate market-wide simulation
    all_decisions = [d for r in simulation_results for d in r["agent_decisions"]]
    market_nash   = _estimate_nash_equilibrium(all_decisions)

    return {
        "simulation_results":  simulation_results,
        "market_equilibrium":  market_nash,
        "market_direction":    market_nash["predicted_direction"],
        "total_buy_pressure":  market_nash["buy_pressure_usd"],
        "total_sell_pressure": market_nash["sell_pressure_usd"],
        "agents_simulated":    7,
    }
