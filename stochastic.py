"""
stochastic.py - Stochastic Mathematics Engine

Implements:
- Geometric Brownian Motion (GBM): dS = mu*S*dt + sigma*S*dW
- Ornstein-Uhlenbeck (mean reversion): dX = theta*(mu-X)*dt + sigma*dW
- Heston Stochastic Volatility Model
- Monte Carlo price simulation (1000 paths)
- Black-Scholes options pricing + Greeks
- Implied volatility estimation
"""
from __future__ import annotations
import math
import random


def _safe(v, d=0.0):
    return v if v is not None else d


# ── Normal CDF (for Black-Scholes) ────────────────────────────────────────────

def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2)))


# ── Geometric Brownian Motion ─────────────────────────────────────────────────
# dS_t = mu*S_t*dt + sigma*S_t*dW_t
# S_{t+1} = S_t * exp((mu - sigma^2/2)*dt + sigma*sqrt(dt)*Z)

def gbm_simulate(S0: float, mu: float, sigma: float,
                 dt: float = 1/252, steps: int = 21, paths: int = 500) -> dict:
    """Simulate GBM paths. Returns statistics over all paths."""
    random.seed(42)
    finals = []
    for _ in range(paths):
        S = S0
        for _ in range(steps):
            Z = random.gauss(0, 1)
            S = S * math.exp((mu - 0.5 * sigma**2) * dt + sigma * math.sqrt(dt) * Z)
        finals.append(S)

    finals.sort()
    mean_final  = sum(finals) / len(finals)
    p5          = finals[int(0.05 * paths)]
    p25         = finals[int(0.25 * paths)]
    p75         = finals[int(0.75 * paths)]
    p95         = finals[int(0.95 * paths)]
    prob_up     = sum(1 for f in finals if f > S0) / paths

    return {
        "model":          "GBM",
        "S0":             round(S0, 4),
        "mu_annual":      round(mu, 4),
        "sigma_annual":   round(sigma, 4),
        "horizon_days":   steps,
        "paths":          paths,
        "mean_price":     round(mean_final, 4),
        "p5_price":       round(p5, 4),
        "p25_price":      round(p25, 4),
        "p75_price":      round(p75, 4),
        "p95_price":      round(p95, 4),
        "prob_up_%":      round(prob_up * 100, 1),
        "expected_return_%": round((mean_final / S0 - 1) * 100, 2),
        "var_95_%":       round((S0 - p5) / S0 * 100, 2),
    }


# ── Ornstein-Uhlenbeck (Mean Reversion) ──────────────────────────────────────
# dX_t = theta*(mu - X_t)*dt + sigma*dW_t

def ou_process(X0: float, mu: float, theta: float, sigma: float,
               dt: float = 1/252, steps: int = 21) -> dict:
    """Simulate OU process for mean reversion analysis."""
    random.seed(42)
    X = X0
    path = [X0]
    for _ in range(steps):
        dW = random.gauss(0, math.sqrt(dt))
        X  = X + theta * (mu - X) * dt + sigma * dW
        path.append(X)

    half_life = math.log(2) / theta if theta > 0 else float("inf")
    mean_rev_signal = "MEAN-REVERTING" if abs(X0 - mu) > sigma else "AT-EQUILIBRIUM"

    return {
        "model":            "Ornstein-Uhlenbeck",
        "X0":               round(X0, 4),
        "long_run_mean":    round(mu, 4),
        "theta_speed":      round(theta, 4),
        "sigma":            round(sigma, 4),
        "half_life_days":   round(half_life * 252, 1) if half_life != float("inf") else None,
        "final_value":      round(path[-1], 4),
        "deviation_from_mean": round(X0 - mu, 4),
        "mean_rev_signal":  mean_rev_signal,
        "z_score":          round((X0 - mu) / sigma, 2) if sigma > 0 else 0,
    }


# ── Heston Stochastic Volatility ─────────────────────────────────────────────
# dS = mu*S*dt + sqrt(v)*S*dW_S
# dv = kappa*(theta-v)*dt + xi*sqrt(v)*dW_v

def heston_vol_estimate(price: float, atr: float, vix: float = None) -> dict:
    """Estimate Heston model parameters from market data."""
    # Current variance from ATR
    sigma_daily = atr / price if price > 0 else 0.02
    v0          = (sigma_daily * math.sqrt(252)) ** 2  # annualized variance

    # Long-run variance from VIX or ATR
    vix_sigma   = (vix / 100) if vix else sigma_daily * math.sqrt(252)
    theta       = vix_sigma ** 2

    # Mean reversion speed (typical: 2-10)
    kappa       = 3.0

    # Vol of vol (typical: 0.3-0.8)
    xi          = 0.5

    # Feller condition: 2*kappa*theta > xi^2
    feller_ok   = 2 * kappa * theta > xi ** 2

    # Implied vol surface approximation
    iv_atm      = round(math.sqrt(theta) * 100, 2)
    iv_skew     = round((math.sqrt(v0) - math.sqrt(theta)) * 100, 2)

    return {
        "model":            "Heston",
        "v0_current":       round(v0, 6),
        "theta_long_run":   round(theta, 6),
        "kappa_mean_rev":   kappa,
        "xi_vol_of_vol":    xi,
        "feller_condition": feller_ok,
        "iv_atm_%":         iv_atm,
        "iv_skew_%":        iv_skew,
        "vol_regime":       "HIGH-VOL" if v0 > theta * 1.5 else ("LOW-VOL" if v0 < theta * 0.5 else "NORMAL"),
    }


# ── Black-Scholes Options Pricing + Greeks ────────────────────────────────────
# C = S0*N(d1) - K*e^(-rT)*N(d2)

def black_scholes(S: float, K: float, T: float, r: float,
                  sigma: float, option_type: str = "call") -> dict:
    """Price an option and compute Greeks."""
    if T <= 0 or sigma <= 0 or S <= 0:
        return {"error": "Invalid inputs"}

    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    if option_type == "call":
        price  = S * _norm_cdf(d1) - K * math.exp(-r * T) * _norm_cdf(d2)
        delta  = _norm_cdf(d1)
    else:
        price  = K * math.exp(-r * T) * _norm_cdf(-d2) - S * _norm_cdf(-d1)
        delta  = _norm_cdf(d1) - 1

    # Greeks
    phi    = math.exp(-0.5 * d1**2) / math.sqrt(2 * math.pi)
    gamma  = phi / (S * sigma * math.sqrt(T))
    vega   = S * phi * math.sqrt(T) / 100  # per 1% vol change
    theta  = (-(S * phi * sigma) / (2 * math.sqrt(T)) -
               r * K * math.exp(-r * T) * _norm_cdf(d2 if option_type == "call" else -d2)) / 365
    rho    = (K * T * math.exp(-r * T) *
               (_norm_cdf(d2) if option_type == "call" else -_norm_cdf(-d2))) / 100

    return {
        "model":       "Black-Scholes",
        "option_type": option_type,
        "S":           S, "K": K, "T_years": T, "r": r, "sigma": sigma,
        "price":       round(price, 4),
        "delta":       round(delta, 4),
        "gamma":       round(gamma, 6),
        "vega":        round(vega, 4),
        "theta_daily": round(theta, 4),
        "rho":         round(rho, 4),
        "intrinsic":   round(max(0, S - K if option_type == "call" else K - S), 4),
        "time_value":  round(max(0, price - max(0, S - K if option_type == "call" else K - S)), 4),
        "moneyness":   "ITM" if (S > K if option_type == "call" else S < K) else "OTM",
    }


# ── Monte Carlo Simulation ────────────────────────────────────────────────────
# S_{t+1} = S_t * exp((mu - sigma^2/2)*dt + sigma*sqrt(dt)*Z_t)

def monte_carlo(S0: float, mu: float, sigma: float,
                horizon_days: int = 21, paths: int = 1000) -> dict:
    """Full Monte Carlo simulation for risk estimation."""
    random.seed(42)
    dt      = 1 / 252
    finals  = []
    min_path = []
    max_path = []

    for _ in range(paths):
        S    = S0
        low  = S0
        high = S0
        for _ in range(horizon_days):
            Z = random.gauss(0, 1)
            S = S * math.exp((mu - 0.5 * sigma**2) * dt + sigma * math.sqrt(dt) * Z)
            low  = min(low, S)
            high = max(high, S)
        finals.append(S)
        min_path.append(low)
        max_path.append(high)

    finals.sort()
    n = len(finals)

    return {
        "model":           "Monte Carlo GBM",
        "S0":              round(S0, 4),
        "horizon_days":    horizon_days,
        "paths":           paths,
        "mean_outcome":    round(sum(finals) / n, 4),
        "median_outcome":  round(finals[n // 2], 4),
        "var_95_%":        round((S0 - finals[int(0.05 * n)]) / S0 * 100, 2),
        "var_99_%":        round((S0 - finals[int(0.01 * n)]) / S0 * 100, 2),
        "cvar_95_%":       round((S0 - sum(finals[:int(0.05*n)]) / max(1, int(0.05*n))) / S0 * 100, 2),
        "best_case_%":     round((finals[-1] / S0 - 1) * 100, 2),
        "worst_case_%":    round((finals[0] / S0 - 1) * 100, 2),
        "prob_profit_%":   round(sum(1 for f in finals if f > S0) / n * 100, 1),
        "expected_return_%": round((sum(finals) / n / S0 - 1) * 100, 2),
    }


# ── Main entry point ──────────────────────────────────────────────────────────

def run_stochastic_analysis(instruments: list[dict], vix: float = None,
                             risk_free_rate: float = 0.05) -> list[dict]:
    """Run stochastic models on top instruments."""
    results = []
    for inst in instruments[:10]:
        price = _safe(inst.get("price"), 1)
        atr   = _safe(inst.get("atr"), price * 0.02)
        chg   = _safe(inst.get("change_%"))

        # Estimate annualized parameters
        sigma = (atr / price) * math.sqrt(252) if price > 0 else 0.25
        mu    = chg / 100 * 252 if chg else 0.08  # annualized drift

        # GBM simulation (21-day horizon)
        gbm   = gbm_simulate(price, mu, sigma, steps=21, paths=500)

        # OU process (mean reversion around EMA50)
        ema50 = _safe(inst.get("ema50"), price)
        ou    = ou_process(price, ema50, theta=2.0, sigma=atr)

        # Heston vol estimate
        heston = heston_vol_estimate(price, atr, vix)

        # Monte Carlo (21-day)
        mc    = monte_carlo(price, mu, sigma, horizon_days=21, paths=500)

        # ATM options (30-day expiry)
        call  = black_scholes(price, price, T=30/365, r=risk_free_rate, sigma=sigma, option_type="call")
        put   = black_scholes(price, price, T=30/365, r=risk_free_rate, sigma=sigma, option_type="put")

        results.append({
            "symbol":   inst.get("symbol"),
            "price":    price,
            "gbm":      gbm,
            "ou":       ou,
            "heston":   heston,
            "monte_carlo": mc,
            "options": {
                "atm_call": call,
                "atm_put":  put,
                "iv_%":     round(sigma * 100, 2),
            },
        })
    return results
