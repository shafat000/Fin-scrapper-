from __future__ import annotations

# ── Signal Engine ──────────────────────────────────────────────────────────────
# Generates precise real-time trading signals:
#   ACTION     : BUY NOW / SELL NOW / WAIT / AVOID
#   Entry      : exact price to enter
#   Stop-Loss  : where to cut loss (ATR-based)
#   Target 1/2 : take-profit levels
#   Risk/Reward: ratio
#   Confidence : 1-5 stars
# ──────────────────────────────────────────────────────────────────────────────

def _safe(val, default=0):
    return val if val is not None else default


def _atr_stop(price: float, atr: float, multiplier: float) -> float:
    return round(price - atr * multiplier, 4)


def _pct(a: float, b: float) -> float:
    if b == 0:
        return 0.0
    return round((a - b) / b * 100, 2)


def generate_signal(d: dict, composite_score: float) -> dict:
    price  = _safe(d.get("price"),       0)
    atr    = _safe(d.get("atr"),         price * 0.02)   # fallback 2% ATR
    rsi    = _safe(d.get("rsi"),         50)
    macd   = _safe(d.get("macd"),        0)
    macd_s = _safe(d.get("macd_signal"), 0)
    ema20  = _safe(d.get("ema20"),       price)
    ema50  = _safe(d.get("ema50"),       price)
    ema200 = _safe(d.get("ema200"),      price)
    vwap   = _safe(d.get("vwap"),        price)
    bb_u   = _safe(d.get("bb_upper"),    price * 1.02)
    bb_l   = _safe(d.get("bb_lower"),    price * 0.98)
    chg    = _safe(d.get("change_%"),    0)
    vol    = _safe(d.get("volume"),      0)
    avg_v  = _safe(d.get("avg_vol_10d"), 1)

    if price <= 0:
        return {"action": "NO DATA", "confidence": 0}

    # ── Determine action ──────────────────────────────────────────────────────
    buy_signals  = 0
    sell_signals = 0
    reasons      = []

    # RSI
    if rsi < 30:
        buy_signals += 2; reasons.append("RSI oversold - strong buy zone")
    elif rsi < 45:
        buy_signals += 1; reasons.append("RSI low - building momentum")
    elif rsi > 70:
        sell_signals += 2; reasons.append("RSI overbought - sell/trim zone")
    elif rsi > 60:
        sell_signals += 1; reasons.append("RSI elevated - watch for reversal")

    # MACD
    if macd > macd_s:
        buy_signals += 2; reasons.append("MACD bullish crossover")
    else:
        sell_signals += 2; reasons.append("MACD bearish crossover")

    # Price vs EMAs
    if price > ema20 > ema50 > ema200:
        buy_signals += 3; reasons.append("Price above all EMAs - strong uptrend")
    elif price > ema20 and price > ema50:
        buy_signals += 2; reasons.append("Price above EMA20/50 - uptrend")
    elif price < ema20 < ema50 < ema200:
        sell_signals += 3; reasons.append("Price below all EMAs - strong downtrend")
    elif price < ema20 and price < ema50:
        sell_signals += 2; reasons.append("Price below EMA20/50 - downtrend")

    # VWAP
    if price > vwap:
        buy_signals += 1; reasons.append("Above VWAP - intraday bullish")
    else:
        sell_signals += 1; reasons.append("Below VWAP - intraday bearish")

    # Bollinger Bands
    bb_range = bb_u - bb_l
    if bb_range > 0:
        bb_pos = (price - bb_l) / bb_range
        if bb_pos < 0.15:
            buy_signals += 2; reasons.append("Near BB lower band - oversold bounce")
        elif bb_pos > 0.85:
            sell_signals += 2; reasons.append("Near BB upper band - overbought")

    # Volume confirmation
    if avg_v > 0:
        vol_ratio = vol / avg_v
        if vol_ratio > 1.5 and chg > 0:
            buy_signals += 1; reasons.append(f"High volume on up move ({vol_ratio:.1f}x avg)")
        elif vol_ratio > 1.5 and chg < 0:
            sell_signals += 1; reasons.append(f"High volume on down move ({vol_ratio:.1f}x avg)")

    # Daily momentum
    if chg > 2:
        buy_signals += 1; reasons.append(f"Strong momentum +{chg:.2f}%")
    elif chg < -2:
        sell_signals += 1; reasons.append(f"Selling pressure {chg:.2f}%")

    # ── Determine action from signal balance + composite score ────────────────
    net = buy_signals - sell_signals

    if composite_score >= 70 and net >= 4:
        action = "BUY NOW"
    elif composite_score >= 62 and net >= 2:
        action = "BUY"
    elif composite_score <= 30 and net <= -4:
        action = "SELL NOW"
    elif composite_score <= 42 and net <= -2:
        action = "SELL"
    elif composite_score >= 55 and net >= 0:
        action = "WAIT - BULLISH SETUP"
    elif composite_score <= 48 and net <= 0:
        action = "WAIT - BEARISH SETUP"
    else:
        action = "HOLD"

    # ── Confidence (1-5) ──────────────────────────────────────────────────────
    confidence = min(5, max(1, abs(net) // 2 + (1 if abs(composite_score - 50) > 15 else 0)))

    # ── Entry, Stop-Loss, Targets ─────────────────────────────────────────────
    if "BUY" in action:
        entry      = round(price, 4)
        stop_loss  = round(max(price - atr * 2.0, price * 0.95), 4)   # 2x ATR or 5% max
        target1    = round(price + atr * 2.0, 4)                       # 1:1 R/R
        target2    = round(price + atr * 4.0, 4)                       # 1:2 R/R
        risk       = round(entry - stop_loss, 4)
        reward1    = round(target1 - entry, 4)
        reward2    = round(target2 - entry, 4)
        rr1        = round(reward1 / risk, 2) if risk > 0 else 0
        rr2        = round(reward2 / risk, 2) if risk > 0 else 0
        stop_pct   = _pct(stop_loss, entry)
        t1_pct     = _pct(target1, entry)
        t2_pct     = _pct(target2, entry)
    elif "SELL" in action:
        entry      = round(price, 4)
        stop_loss  = round(min(price + atr * 2.0, price * 1.05), 4)   # stop above entry
        target1    = round(price - atr * 2.0, 4)
        target2    = round(price - atr * 4.0, 4)
        risk       = round(stop_loss - entry, 4)
        reward1    = round(entry - target1, 4)
        reward2    = round(entry - target2, 4)
        rr1        = round(reward1 / risk, 2) if risk > 0 else 0
        rr2        = round(reward2 / risk, 2) if risk > 0 else 0
        stop_pct   = _pct(stop_loss, entry)
        t1_pct     = _pct(target1, entry)
        t2_pct     = _pct(target2, entry)
    else:
        entry = stop_loss = target1 = target2 = None
        rr1 = rr2 = stop_pct = t1_pct = t2_pct = None

    return {
        "action":      action,
        "confidence":  confidence,
        "entry":       entry,
        "stop_loss":   stop_loss,
        "stop_pct":    stop_pct,
        "target1":     target1,
        "target1_pct": t1_pct,
        "target2":     target2,
        "target2_pct": t2_pct,
        "rr1":         rr1,
        "rr2":         rr2,
        "reasons":     reasons,
    }


def generate_all(analysis: dict, stocks_data: list[dict], crypto_data: list[dict]) -> dict:
    # Build lookup by symbol
    stock_map = {d.get("symbol"): d for d in stocks_data}
    crypto_map = {d.get("symbol"): d for d in crypto_data}

    result = {"stocks": [], "crypto": []}

    for a in analysis.get("stocks", []):
        sym = a.get("symbol")
        raw = stock_map.get(sym, {})
        sig = generate_signal(raw, a.get("composite", 50))
        sig["symbol"] = sym
        sig["price"]  = a.get("price")
        sig["score"]  = a.get("composite")
        result["stocks"].append(sig)

    for a in analysis.get("crypto", []):
        sym = a.get("symbol")
        raw = crypto_map.get(sym, {})
        sig = generate_signal(raw, a.get("composite", 50))
        sig["symbol"] = sym
        sig["price"]  = a.get("price")
        sig["score"]  = a.get("composite")
        result["crypto"].append(sig)

    return result
