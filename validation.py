"""
validation.py - Microstructure & Signal Validation Engine
Filters out false signals by requiring confluence between microstructure and technicals.
"""
from __future__ import annotations

def validate_signals(instruments: list[dict], microstructure: list[dict]) -> list[dict]:
    """
    Cross-references technical signals with microstructure data.
    Returns a list of 'validated' signals with a confluence score.
    """
    validated = []
    # Create micro lookup
    micro_map = {m["symbol"]: m for m in microstructure}

    for inst in instruments:
        sym = inst.get("symbol")
        m = micro_map.get(sym)
        if not m:
            continue

        # Technical Signal
        tech_signal = inst.get("signal", "HOLD")
        
        # Microstructure Signal
        micro_signal = m.get("microprice_signal", "NEUTRAL")
        flow_bias = m.get("flow_bias", "NEUTRAL")
        
        # Confluence Score (0 to 100)
        confluence_score = 50
        
        # Bullish Confluence
        if "BUY" in tech_signal:
            if micro_signal == "BULLISH": confluence_score += 20
            if "BUYING" in flow_bias:      confluence_score += 20
            if m.get("order_flow_imbalance", 0) > 0.2: confluence_score += 10
        
        # Bearish Confluence
        if "SELL" in tech_signal:
            if micro_signal == "BEARISH": confluence_score += 20
            if "SELLING" in flow_bias:     confluence_score += 20
            if m.get("order_flow_imbalance", 0) < -0.2: confluence_score += 10

        # Penalize lack of volume confirmation
        if not m.get("volume_confirms", False):
            confluence_score -= 15

        # Cap at 100
        confluence_score = min(100, max(0, confluence_score))

        # Final verdict
        status = "VALIDATED" if confluence_score >= 70 else "WEAK" if confluence_score >= 50 else "REJECTED"

        validated.append({
            "symbol": sym,
            "tech_signal": tech_signal,
            "micro_signal": micro_signal,
            "flow_bias": flow_bias,
            "confluence_score": confluence_score,
            "status": status,
            "price": inst.get("price"),
            "change_%": inst.get("change_%")
        })

    return validated

def print_validation_results(validated: list[dict]):
    """Prints the validated signals table."""
    print(f"\n  ============================================================")
    print(f"  SIGNAL CONFLUENCE VALIDATION (Micro + Tech)")
    print(f"  ============================================================")
    print(f"  {'SYMBOL':<15} {'TECH':<12} {'MICRO':<10} {'CONF%':>6}  {'STATUS'}")
    print(f"  {'-'*60}")
    for v in validated[:15]:
        print(f"  {v['symbol']:<15} {v['tech_signal']:<12} {v['micro_signal']:<10} {v['confluence_score']:>5}%  {v['status']}")
    print(f"  ============================================================\n")
