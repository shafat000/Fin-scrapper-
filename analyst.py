from __future__ import annotations
"""
analyst.py — Investment Analysis Engine
Scores every stock/crypto across 4 dimensions using all available market data.

Scores are 0–100. Weighted composite → final verdict + reasoning.
"""

# ── Weights ────────────────────────────────────────────────────────────────────
W_TECHNICAL   = 0.35
W_MOMENTUM    = 0.25
W_FUNDAMENTAL = 0.20   # stocks only; redistributed for crypto
W_NEWS        = 0.20

VERDICT_ICONS = {
    "STRONG BUY":  "** STRONG BUY **",
    "BUY":         ">> BUY",
    "HOLD":        "-- HOLD",
    "SELL":        "<< SELL",
    "STRONG SELL": "!! STRONG SELL",
}

VERDICT_LABELS = {
    (80, 101): ("** STRONG BUY **",  "Strong across all dimensions. High conviction entry."),
    (62,  80): (">> BUY",            "Mostly positive signals. Favorable risk/reward."),
    (42,  62): ("-- HOLD",           "Mixed signals. Wait for clearer confirmation."),
    (25,  42): ("<< SELL",           "Weak technicals or fundamentals. Consider reducing."),
    (  0, 25): ("!! STRONG SELL",    "Multiple red flags. High risk of further downside."),
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _safe(val, default=None):
    return val if val is not None else default


def _clamp(val: float, lo=0.0, hi=100.0) -> float:
    return max(lo, min(hi, val))


def _verdict(score: float) -> tuple[str, str]:
    for (lo, hi), (label, desc) in VERDICT_LABELS.items():
        if lo <= score < hi:
            return label, desc
    return "🟡 HOLD", "Insufficient data."


# ── 1. Technical Score (0–100) ─────────────────────────────────────────────────

def _technical_score(d: dict) -> tuple[float, list[str]]:
    score, reasons = 50.0, []

    price  = _safe(d.get("price"), 0)
    rsi    = _safe(d.get("rsi"))
    rsi_p  = _safe(d.get("rsi_prev"))
    macd   = _safe(d.get("macd"))
    macd_s = _safe(d.get("macd_signal"))
    ema20  = _safe(d.get("ema20"))
    ema50  = _safe(d.get("ema50"))
    ema200 = _safe(d.get("ema200"))
    vwap   = _safe(d.get("vwap"))
    bb_u   = _safe(d.get("bb_upper"))
    bb_l   = _safe(d.get("bb_lower"))
    atr    = _safe(d.get("atr"))

    # RSI
    if rsi is not None:
        if rsi < 30:
            score += 18; reasons.append(f"RSI oversold ({rsi:.1f}) — potential reversal")
        elif rsi < 45:
            score += 8;  reasons.append(f"RSI low ({rsi:.1f}) — building momentum")
        elif rsi > 70:
            score -= 15; reasons.append(f"RSI overbought ({rsi:.1f}) — pullback risk")
        elif rsi > 55:
            score += 8;  reasons.append(f"RSI healthy ({rsi:.1f}) — bullish zone")
        # RSI trending up
        if rsi_p is not None and rsi > rsi_p:
            score += 5; reasons.append("RSI rising — momentum building")

    # MACD crossover
    if macd is not None and macd_s is not None:
        if macd > macd_s:
            score += 12; reasons.append(f"MACD bullish crossover ({macd:.2f} > {macd_s:.2f})")
        else:
            score -= 10; reasons.append(f"MACD bearish ({macd:.2f} < {macd_s:.2f})")

    # Price vs EMAs (trend alignment)
    if price and ema20 and ema50 and ema200:
        above = sum([price > ema20, price > ema50, price > ema200])
        if above == 3:
            score += 15; reasons.append("Price above EMA20/50/200 — strong uptrend")
        elif above == 2:
            score += 7;  reasons.append("Price above 2 of 3 EMAs — moderate uptrend")
        elif above == 0:
            score -= 15; reasons.append("Price below all EMAs — downtrend")
        else:
            score -= 5;  reasons.append("Price below majority of EMAs — weak trend")

    # EMA alignment (golden/death cross proxy)
    if ema20 and ema50 and ema200:
        if ema20 > ema50 > ema200:
            score += 8; reasons.append("EMA20 > EMA50 > EMA200 — golden alignment")
        elif ema20 < ema50 < ema200:
            score -= 8; reasons.append("EMA20 < EMA50 < EMA200 — death alignment")

    # VWAP
    if price and vwap:
        if price > vwap:
            score += 6; reasons.append(f"Price above VWAP ({vwap:.2f}) — intraday bullish")
        else:
            score -= 4; reasons.append(f"Price below VWAP ({vwap:.2f}) — intraday bearish")

    # Bollinger Band position
    if price and bb_u and bb_l:
        bb_range = bb_u - bb_l
        if bb_range > 0:
            bb_pct = (price - bb_l) / bb_range
            if bb_pct < 0.2:
                score += 10; reasons.append("Near lower Bollinger Band — oversold bounce zone")
            elif bb_pct > 0.85:
                score -= 8;  reasons.append("Near upper Bollinger Band — overbought zone")

    # ATR volatility penalty (extreme volatility = risk)
    if atr and price:
        atr_pct = (atr / price) * 100
        if atr_pct > 5:
            score -= 8; reasons.append(f"High ATR ({atr_pct:.1f}% of price) — elevated volatility risk")

    return _clamp(score), reasons


# ── 2. Momentum Score (0–100) ──────────────────────────────────────────────────

def _momentum_score(d: dict) -> tuple[float, list[str]]:
    score, reasons = 50.0, []

    chg       = _safe(d.get("change_%"), 0)
    vol       = _safe(d.get("volume"), 0)
    avg_vol   = _safe(d.get("avg_vol_10d"), 0)
    rel_vol   = _safe(d.get("relative_volume"), 0)
    pre_chg   = _safe(d.get("pre_market_change_%"), 0)
    after_chg = _safe(d.get("after_hours_change_%"), 0)
    gap       = _safe(d.get("gap_%"), 0)
    chg_open  = _safe(d.get("change_from_open_%"), 0)

    # Daily change
    if chg > 3:
        score += 18; reasons.append(f"Strong daily gain +{chg:.2f}%")
    elif chg > 1:
        score += 8;  reasons.append(f"Positive day +{chg:.2f}%")
    elif chg < -3:
        score -= 18; reasons.append(f"Sharp daily loss {chg:.2f}%")
    elif chg < -1:
        score -= 8;  reasons.append(f"Negative day {chg:.2f}%")

    # Volume vs average
    if avg_vol and avg_vol > 0 and vol:
        vol_ratio = vol / avg_vol
        if vol_ratio > 2.0:
            score += 15; reasons.append(f"Volume {vol_ratio:.1f}x above 10d avg — strong conviction")
        elif vol_ratio > 1.3:
            score += 7;  reasons.append(f"Volume {vol_ratio:.1f}x above avg — above-average interest")
        elif vol_ratio < 0.5:
            score -= 8;  reasons.append(f"Volume only {vol_ratio:.1f}x avg — weak participation")

    # Relative volume spike
    if rel_vol and rel_vol > 2:
        score += 10; reasons.append(f"Relative volume spike ({rel_vol:.1f}x) — unusual activity")

    # Pre-market / after-hours
    if pre_chg and abs(pre_chg) > 1:
        delta = 8 if pre_chg > 0 else -8
        score += delta
        reasons.append(f"Pre-market {'gap up' if pre_chg > 0 else 'gap down'} {pre_chg:.2f}%")

    if after_chg and abs(after_chg) > 1:
        delta = 6 if after_chg > 0 else -6
        score += delta
        reasons.append(f"After-hours {'up' if after_chg > 0 else 'down'} {after_chg:.2f}%")

    # Intraday momentum (change from open)
    if chg_open and chg_open > 1:
        score += 6; reasons.append(f"Gaining from open +{chg_open:.2f}% — intraday strength")
    elif chg_open and chg_open < -1:
        score -= 6; reasons.append(f"Fading from open {chg_open:.2f}% — intraday weakness")

    # Gap
    if gap and gap > 2:
        score += 8; reasons.append(f"Gap up {gap:.2f}% — strong open")
    elif gap and gap < -2:
        score -= 8; reasons.append(f"Gap down {gap:.2f}% — weak open")

    return _clamp(score), reasons


# ── 3. Fundamental Score (0–100, stocks only) ──────────────────────────────────

def _fundamental_score(d: dict) -> tuple[float, list[str]]:
    score, reasons = 50.0, []

    pe       = _safe(d.get("pe_ratio"))
    eps      = _safe(d.get("eps"))
    div_yld  = _safe(d.get("dividend_yield_%"))
    mkt_cap  = _safe(d.get("market_cap"))
    beta     = _safe(d.get("beta"))
    w52_hi   = _safe(d.get("price_52w_high"))   # % from 52w high
    w52_lo   = _safe(d.get("price_52w_low"))    # % from 52w low

    # P/E ratio
    if pe is not None and pe > 0:
        if pe < 15:
            score += 15; reasons.append(f"Low P/E ({pe:.1f}) — potentially undervalued")
        elif pe < 25:
            score += 8;  reasons.append(f"Fair P/E ({pe:.1f}) — reasonable valuation")
        elif pe < 40:
            score -= 5;  reasons.append(f"Elevated P/E ({pe:.1f}) — growth premium priced in")
        else:
            score -= 12; reasons.append(f"High P/E ({pe:.1f}) — expensive, needs strong growth")
    elif pe is not None and pe < 0:
        score -= 15; reasons.append("Negative P/E — company not yet profitable")

    # EPS
    if eps is not None:
        if eps > 0:
            score += 10; reasons.append(f"Positive EPS ({eps:.2f}) — profitable")
        else:
            score -= 10; reasons.append(f"Negative EPS ({eps:.2f}) — unprofitable")

    # Dividend yield
    if div_yld and div_yld > 0:
        if div_yld > 4:
            score += 12; reasons.append(f"High dividend yield {div_yld:.2f}% — income attractive")
        elif div_yld > 1.5:
            score += 6;  reasons.append(f"Dividend yield {div_yld:.2f}% — income positive")

    # Market cap (stability)
    if mkt_cap:
        if mkt_cap > 200e9:
            score += 8;  reasons.append("Mega-cap — high liquidity and stability")
        elif mkt_cap > 10e9:
            score += 4;  reasons.append("Large-cap — established company")
        elif mkt_cap < 2e9:
            score -= 6;  reasons.append("Small-cap — higher risk profile")

    # Beta (risk)
    if beta is not None:
        if beta < 0.8:
            score += 6;  reasons.append(f"Low beta ({beta:.2f}) — defensive, low market correlation")
        elif beta > 1.5:
            score -= 8;  reasons.append(f"High beta ({beta:.2f}) — amplified market moves, higher risk")

    # 52-week position
    if w52_hi is not None and w52_lo is not None:
        if w52_lo > 20:
            score += 10; reasons.append(f"+{w52_lo:.1f}% above 52w low — strong recovery")
        if w52_hi < -20:
            score += 8;  reasons.append(f"{w52_hi:.1f}% below 52w high — potential value entry")
        elif w52_hi > -5:
            score -= 5;  reasons.append("Near 52w high — limited upside, resistance ahead")

    return _clamp(score), reasons


# ── 4. News Sentiment Score (0–100) ───────────────────────────────────────────

def _news_score(d: dict, news: list[dict]) -> tuple[float, list[str]]:
    score, reasons = 50.0, []

    symbol = (d.get("symbol") or "").lower()
    sector = (d.get("sector") or "").lower()
    desc   = (d.get("description") or "").lower()

    # Extract ticker name (e.g. NASDAQ:AAPL → aapl, apple)
    ticker = symbol.split(":")[-1].replace("usdt", "").lower()
    keywords = {ticker, desc.split()[0] if desc else "", sector}
    keywords.discard("")

    bull_count = bear_count = matched = 0

    for article in news:
        title_lower = article.get("title", "").lower()
        cats = article.get("categories", [])

        # Check if article is relevant to this instrument
        relevant = any(k in title_lower for k in keywords if len(k) > 2)
        if not relevant:
            # sector-level match
            relevant = (
                ("tech" in sector and "tech" in cats) or
                ("crypto" in symbol and "crypto" in cats) or
                ("energy" in sector and "commodities" in cats) or
                ("financial" in sector and "stocks" in cats)
            )

        if relevant:
            matched += 1
            sentiment = article.get("sentiment", "neutral")
            if sentiment == "bullish":
                bull_count += 1
            elif sentiment == "bearish":
                bear_count += 1

    if matched > 0:
        bull_ratio = bull_count / matched
        bear_ratio = bear_count / matched
        score += (bull_ratio - bear_ratio) * 40
        if bull_count > bear_count:
            reasons.append(f"News sentiment positive ({bull_count} bullish vs {bear_count} bearish in {matched} relevant articles)")
        elif bear_count > bull_count:
            reasons.append(f"News sentiment negative ({bear_count} bearish vs {bull_count} bullish in {matched} relevant articles)")
        else:
            reasons.append(f"News sentiment neutral ({matched} relevant articles)")
    else:
        reasons.append("No directly relevant news found")

    return _clamp(score), reasons


# ── Composite Analyzer ─────────────────────────────────────────────────────────

def analyze(instrument: dict, news: list[dict], is_crypto: bool = False) -> dict:
    tech_score,  tech_reasons  = _technical_score(instrument)
    mom_score,   mom_reasons   = _momentum_score(instrument)
    fund_score,  fund_reasons  = _fundamental_score(instrument)
    news_score,  news_reasons  = _news_score(instrument, news)

    if is_crypto:
        # Crypto has no fundamentals — redistribute weight
        composite = (
            tech_score * 0.40 +
            mom_score  * 0.35 +
            news_score * 0.25
        )
    else:
        composite = (
            tech_score  * W_TECHNICAL   +
            mom_score   * W_MOMENTUM    +
            fund_score  * W_FUNDAMENTAL +
            news_score  * W_NEWS
        )

    verdict, verdict_desc = _verdict(composite)

    return {
        "symbol":        instrument.get("symbol"),
        "price":         instrument.get("price"),
        "composite":     round(composite, 1),
        "verdict":       verdict,
        "verdict_desc":  verdict_desc,
        "scores": {
            "technical":   round(tech_score, 1),
            "momentum":    round(mom_score, 1),
            "fundamental": round(fund_score, 1) if not is_crypto else "N/A",
            "news":        round(news_score, 1),
        },
        "reasons": {
            "technical":   tech_reasons,
            "momentum":    mom_reasons,
            "fundamental": fund_reasons if not is_crypto else [],
            "news":        news_reasons,
        },
    }


def analyze_all(stocks: list[dict], crypto: list[dict], news: list[dict]) -> dict:
    stock_analysis  = [analyze(s, news, is_crypto=False) for s in stocks]
    crypto_analysis = [analyze(c, news, is_crypto=True)  for c in crypto]

    # Sort by composite score descending
    stock_analysis.sort(key=lambda x: x["composite"], reverse=True)
    crypto_analysis.sort(key=lambda x: x["composite"], reverse=True)

    return {"stocks": stock_analysis, "crypto": crypto_analysis}
