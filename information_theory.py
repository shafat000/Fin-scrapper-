"""
information_theory.py - Information Theory Trading Engine

Implements:
- Shannon Entropy: H(X) = -sum p(x) * log p(x)
- KL Divergence: D_KL(P||Q) = sum P(x) * log(P(x)/Q(x))
- Mutual Information: I(X;Y) = sum p(x,y) * log(p(x,y)/(p(x)*p(y)))
- Entropy shift detection (regime change signal)
- Information surprise score (novelty detection)
- Cross-asset information flow
"""
from __future__ import annotations
import math


def _safe(v, d=0.0):
    return v if v is not None else d


# ── Shannon Entropy ───────────────────────────────────────────────────────────

def shannon_entropy(prices: list[float]) -> float:
    """
    Compute Shannon entropy of price return distribution.
    High entropy = disordered/uncertain market.
    Low entropy  = ordered/trending market.
    """
    if len(prices) < 2:
        return 0.0
    returns = [(prices[i] - prices[i-1]) / prices[i-1]
               for i in range(1, len(prices)) if prices[i-1] != 0]
    if not returns:
        return 0.0

    # Discretize into bins
    min_r, max_r = min(returns), max(returns)
    if min_r == max_r:
        return 0.0
    n_bins = min(10, len(returns))
    bin_w  = (max_r - min_r) / n_bins
    counts = [0] * n_bins
    for r in returns:
        idx = min(int((r - min_r) / bin_w), n_bins - 1)
        counts[idx] += 1

    n     = len(returns)
    probs = [c / n for c in counts if c > 0]
    H     = -sum(p * math.log2(p) for p in probs)
    return round(H, 4)


def market_entropy(instruments: list[dict]) -> dict:
    """Compute entropy for each instrument from intraday price action."""
    results = []
    for inst in instruments:
        price  = _safe(inst.get("price"), 1)
        high   = _safe(inst.get("high"), price)
        low    = _safe(inst.get("low"), price)
        open_  = _safe(inst.get("open"), price)
        vwap   = _safe(inst.get("vwap"), price)

        # Synthetic intraday price series from available data
        prices = [open_, low, vwap, high, price]
        H      = shannon_entropy(prices)

        # Entropy regime
        if H > 2.5:   entropy_regime = "HIGH-DISORDER"
        elif H > 1.5: entropy_regime = "NORMAL"
        elif H > 0.5: entropy_regime = "LOW-DISORDER"
        else:          entropy_regime = "ORDERED"

        results.append({
            "symbol":         inst.get("symbol"),
            "entropy":        H,
            "entropy_regime": entropy_regime,
            "market_order":   "TRENDING" if H < 1.5 else "RANDOM",
        })
    return {"instrument_entropy": results}


# ── KL Divergence ─────────────────────────────────────────────────────────────

def kl_divergence(p_dist: list[float], q_dist: list[float]) -> float:
    """
    D_KL(P||Q) = sum P(x) * log(P(x)/Q(x))
    Measures how much P diverges from reference distribution Q.
    Large KL = significant regime change.
    """
    eps = 1e-10
    kl  = 0.0
    for p, q in zip(p_dist, q_dist):
        if p > 0:
            kl += p * math.log((p + eps) / (q + eps))
    return round(kl, 6)


def regime_change_signal(current_instruments: list[dict],
                         baseline_rsi: float = 50.0,
                         baseline_vol: float = 0.02) -> dict:
    """
    Detect regime change using KL divergence between
    current market distribution and historical baseline.
    """
    if not current_instruments:
        return {"kl_divergence": 0, "regime_change_signal": "NONE"}

    # Current distribution: RSI-based
    rsi_vals = [_safe(i.get("rsi"), 50) for i in current_instruments]
    avg_rsi  = sum(rsi_vals) / len(rsi_vals)

    # Normalize to probability distribution (5 buckets: <30, 30-45, 45-55, 55-70, >70)
    buckets_curr = [0.0] * 5
    for r in rsi_vals:
        if r < 30:    buckets_curr[0] += 1
        elif r < 45:  buckets_curr[1] += 1
        elif r < 55:  buckets_curr[2] += 1
        elif r < 70:  buckets_curr[3] += 1
        else:          buckets_curr[4] += 1
    n = len(rsi_vals)
    p_curr = [b / n for b in buckets_curr]

    # Baseline: normal distribution centered at RSI=50
    p_base = [0.05, 0.20, 0.50, 0.20, 0.05]

    kl = kl_divergence(p_curr, p_base)

    if kl > 0.5:    signal = "STRONG-REGIME-CHANGE"
    elif kl > 0.2:  signal = "REGIME-SHIFT"
    elif kl > 0.05: signal = "MILD-DRIFT"
    else:            signal = "STABLE"

    return {
        "kl_divergence":        kl,
        "regime_change_signal": signal,
        "current_rsi_dist":     [round(p, 3) for p in p_curr],
        "baseline_rsi_dist":    p_base,
        "avg_rsi":              round(avg_rsi, 2),
    }


# ── Mutual Information ────────────────────────────────────────────────────────

def mutual_information_proxy(inst_a: dict, inst_b: dict) -> float:
    """
    Proxy mutual information between two instruments.
    I(X;Y) ≈ correlation-based MI estimate.
    Uses change%, RSI, and volume ratio as joint features.
    """
    def _features(inst):
        return [
            _safe(inst.get("change_%")) / 10,
            (_safe(inst.get("rsi"), 50) - 50) / 50,
            min(1.0, _safe(inst.get("relative_volume"), 1) / 3),
        ]

    fa = _features(inst_a)
    fb = _features(inst_b)

    # Pearson correlation as MI proxy
    n    = len(fa)
    mean_a = sum(fa) / n
    mean_b = sum(fb) / n
    cov    = sum((fa[i] - mean_a) * (fb[i] - mean_b) for i in range(n))
    std_a  = math.sqrt(sum((x - mean_a)**2 for x in fa) + 1e-10)
    std_b  = math.sqrt(sum((x - mean_b)**2 for x in fb) + 1e-10)
    rho    = cov / (std_a * std_b)

    # MI from Gaussian approximation: I = -0.5 * log(1 - rho^2)
    mi = -0.5 * math.log(max(1e-10, 1 - rho**2))
    return round(mi, 4)


def cross_asset_information_flow(stocks: list[dict],
                                  crypto: list[dict],
                                  indices: list[dict]) -> dict:
    """
    Compute information flow between asset classes.
    Detects which assets are leading vs lagging.
    """
    # Key instruments
    spx = next((i for i in indices if "SPX" in str(i.get("symbol", ""))), None)
    btc = next((c for c in crypto if "BTC" in str(c.get("symbol", ""))), None)
    vix = next((i for i in indices if "VIX" in str(i.get("symbol", ""))), None)

    flows = []
    for stock in stocks[:8]:
        mi_spx = mutual_information_proxy(stock, spx) if spx else 0
        mi_btc = mutual_information_proxy(stock, btc) if btc else 0
        mi_vix = mutual_information_proxy(stock, vix) if vix else 0
        flows.append({
            "symbol":    stock.get("symbol"),
            "mi_spx":    mi_spx,
            "mi_btc":    mi_btc,
            "mi_vix":    mi_vix,
            "dominant_driver": "SPX" if mi_spx >= mi_btc and mi_spx >= mi_vix
                               else ("BTC" if mi_btc >= mi_vix else "VIX"),
        })

    return {"cross_asset_flows": flows}


# ── Information Surprise Score ────────────────────────────────────────────────

def information_surprise(instruments: list[dict]) -> list[dict]:
    """
    Detect instruments with anomalous information content.
    High surprise = unusual price/volume combination = potential alpha.
    """
    results = []
    for inst in instruments:
        chg     = abs(_safe(inst.get("change_%")))
        rel_vol = _safe(inst.get("relative_volume"), 1)
        rsi     = _safe(inst.get("rsi"), 50)

        # Surprise = unexpected move relative to normal behavior
        price_surprise = chg / 2.0                    # normalized daily move
        volume_surprise = max(0, rel_vol - 1.0)       # excess volume
        rsi_surprise   = abs(rsi - 50) / 50           # RSI extremity

        surprise_score = round(
            price_surprise * 0.4 +
            volume_surprise * 0.4 +
            rsi_surprise * 0.2,
            4
        )

        results.append({
            "symbol":         inst.get("symbol"),
            "surprise_score": surprise_score,
            "surprise_level": "HIGH" if surprise_score > 1.5 else
                              ("MEDIUM" if surprise_score > 0.5 else "LOW"),
        })

    results.sort(key=lambda x: x["surprise_score"], reverse=True)
    return results


# ── Main entry point ──────────────────────────────────────────────────────────

def run_information_theory(stocks: list[dict], crypto: list[dict],
                            indices: list[dict]) -> dict:
    all_instruments = stocks + crypto

    entropy_data   = market_entropy(all_instruments)
    kl_signal      = regime_change_signal(all_instruments)
    info_flow      = cross_asset_information_flow(stocks, crypto, indices)
    surprise       = information_surprise(all_instruments)

    # Overall information regime
    kl = kl_signal.get("kl_divergence", 0)
    avg_entropy = (sum(e["entropy"] for e in entropy_data["instrument_entropy"])
                   / max(1, len(entropy_data["instrument_entropy"])))

    if kl > 0.3 and avg_entropy > 2.0:
        info_regime = "HIGH-INFORMATION-FLOW"
    elif kl < 0.05 and avg_entropy < 1.0:
        info_regime = "LOW-INFORMATION-FLOW"
    else:
        info_regime = "NORMAL-INFORMATION-FLOW"

    return {
        "entropy":          entropy_data,
        "kl_divergence":    kl_signal,
        "information_flow": info_flow,
        "surprise_scores":  surprise[:10],
        "info_regime":      info_regime,
        "avg_market_entropy": round(avg_entropy, 4),
    }
