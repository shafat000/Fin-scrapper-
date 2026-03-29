from __future__ import annotations
import re
from collections import defaultdict

# ── Market-moving event patterns ──────────────────────────────────────────────
MARKET_MOVING = {
    "earnings_beat":  ["beat", "beats", "topped", "surpassed", "record earnings", "profit surge", "earnings surprise"],
    "earnings_miss":  ["miss", "missed", "fell short", "below expectations", "earnings disappoint", "profit warning"],
    "fed_hawkish":    ["rate hike", "raises rates", "hawkish", "tightening", "inflation concern", "fed hikes"],
    "fed_dovish":     ["rate cut", "cuts rates", "dovish", "easing", "pivot", "fed cuts", "pause"],
    "geopolitical":   ["war", "conflict", "sanctions", "attack", "strike", "invasion", "crisis", "tension"],
    "crash":          ["crash", "collapse", "plunge", "meltdown", "circuit breaker", "black swan", "panic sell"],
    "rally":          ["rally", "surge", "soar", "breakout", "all-time high", "record high", "bull run"],
    "bankruptcy":     ["bankrupt", "bankruptcy", "default", "insolvency", "chapter 11", "liquidation"],
    "merger_acq":     ["merger", "acquisition", "takeover", "buyout", "deal", "acquire"],
    "upgrade":        ["upgrade", "outperform", "overweight", "price target raised", "buy rating"],
    "downgrade":      ["downgrade", "underperform", "underweight", "price target cut", "sell rating"],
    "ipo":            ["ipo", "initial public offering", "goes public", "listing", "debut"],
    "regulation":     ["ban", "regulation", "sec", "lawsuit", "fine", "probe", "investigation", "antitrust"],
    "macro_positive": ["gdp growth", "jobs report", "strong economy", "consumer confidence", "retail sales beat"],
    "macro_negative": ["recession", "gdp contraction", "unemployment rise", "inflation surge", "stagflation"],
}

BULLISH_EVENTS  = {"earnings_beat", "fed_dovish", "rally", "merger_acq", "upgrade", "ipo", "macro_positive"}
BEARISH_EVENTS  = {"earnings_miss", "fed_hawkish", "geopolitical", "crash", "bankruptcy", "downgrade", "regulation", "macro_negative"}

# Insight templates per event type
INSIGHT_TEMPLATES = {
    "earnings_beat":  "{sym} likely to rise — positive earnings beat detected in news",
    "earnings_miss":  "{sym} faces downside risk — earnings miss reported in news",
    "fed_dovish":     "{sym} may benefit — Fed dovish signals detected, rate cut expectations rising",
    "fed_hawkish":    "{sym} under pressure — Fed hawkish tone detected, higher rates ahead",
    "geopolitical":   "{sym} at risk — geopolitical tensions detected, expect volatility",
    "crash":          "{sym} high risk — market crash/panic signals detected in news",
    "rally":          "{sym} momentum building — rally/breakout signals detected in news",
    "bankruptcy":     "{sym} extreme risk — bankruptcy/default signals in news",
    "merger_acq":     "{sym} potential catalyst — M&A activity detected in news",
    "upgrade":        "{sym} bullish catalyst — analyst upgrade/price target raise detected",
    "downgrade":      "{sym} bearish signal — analyst downgrade/price target cut detected",
    "regulation":     "{sym} regulatory risk — legal/regulatory action detected in news",
    "macro_positive": "{sym} tailwind — positive macro data detected, broad market support",
    "macro_negative": "{sym} headwind — negative macro data detected, broad market pressure",
}


def _detect_events(title: str) -> list[str]:
    lower = title.lower()
    found = []
    for event, keywords in MARKET_MOVING.items():
        if any(k in lower for k in keywords):
            found.append(event)
    return found


def _is_market_moving(events: list[str]) -> bool:
    high_impact = {"earnings_beat", "earnings_miss", "fed_hawkish", "fed_dovish",
                   "crash", "geopolitical", "bankruptcy", "regulation"}
    return bool(set(events) & high_impact)


def _match_instrument(title: str, symbol: str, description: str, sector: str) -> bool:
    lower = title.lower()
    ticker = symbol.split(":")[-1].replace("usdt", "").lower()
    desc_word = description.split()[0].lower() if description else ""
    keywords = {ticker, desc_word, sector.lower() if sector else ""}
    keywords.discard("")
    if any(k in lower for k in keywords if len(k) > 2):
        return True
    # sector-level fallback
    if sector:
        s = sector.lower()
        if ("tech" in s and any(w in lower for w in ["tech", "ai", "chip", "software", "semiconductor"])):
            return True
        if ("energy" in s and any(w in lower for w in ["oil", "gas", "energy", "crude"])):
            return True
        if ("finance" in s and any(w in lower for w in ["bank", "fed", "rate", "financial", "lending"])):
            return True
        if ("health" in s and any(w in lower for w in ["drug", "fda", "pharma", "biotech", "clinical"])):
            return True
    return False


def generate_instrument_insight(instrument: dict, news: list[dict]) -> dict:
    symbol      = instrument.get("symbol", "")
    description = instrument.get("description", "") or ""
    sector      = instrument.get("sector", "") or ""
    price       = instrument.get("price")
    chg         = instrument.get("change_%", 0) or 0

    matched_events  = defaultdict(int)
    market_movers   = []
    relevant_titles = []

    for article in news:
        title = article.get("title", "")
        if not _match_instrument(title, symbol, description, sector):
            continue

        events = _detect_events(title)
        relevant_titles.append(title)

        for e in events:
            matched_events[e] += 1

        if _is_market_moving(events):
            market_movers.append({
                "title":     title,
                "events":    events,
                "sentiment": article.get("sentiment", "neutral"),
                "link":      article.get("link", ""),
            })

    # Pick dominant event
    if not matched_events:
        # Fallback: use price action
        if chg > 2:
            insight = f"{symbol} up {chg:.1f}% today — momentum driven, no specific news catalyst found"
        elif chg < -2:
            insight = f"{symbol} down {chg:.1f}% today — selling pressure, no specific news catalyst found"
        else:
            insight = f"{symbol} — no significant news detected. Monitor for catalysts."
        direction = "neutral"
    else:
        top_event = max(matched_events, key=matched_events.get)
        sym_short = symbol.split(":")[-1]
        insight   = INSIGHT_TEMPLATES.get(top_event, "{sym} — notable activity detected").format(sym=sym_short)
        direction = "bullish" if top_event in BULLISH_EVENTS else "bearish"

    return {
        "symbol":         symbol,
        "price":          price,
        "change_%":       chg,
        "insight":        insight,
        "direction":      direction,
        "market_movers":  market_movers[:3],
        "matched_events": dict(matched_events),
        "relevant_news":  len(relevant_titles),
    }


def _macro_regime(news: list[dict]) -> str:
    risk_on  = 0
    risk_off = 0
    for article in news:
        events = _detect_events(article.get("title", ""))
        for e in events:
            if e in BULLISH_EVENTS:
                risk_on  += 1
            elif e in BEARISH_EVENTS:
                risk_off += 1
    total = risk_on + risk_off
    if total == 0:
        return "NEUTRAL"
    ratio = risk_on / total
    if ratio > 0.6:
        return "RISK-ON  (market favors growth assets — stocks, crypto)"
    elif ratio < 0.4:
        return "RISK-OFF (market favors safe havens — gold, bonds, cash)"
    return "MIXED    (conflicting signals — reduce position size)"


def _market_summary(news: list[dict], stocks_insights: list[dict], crypto_insights: list[dict]) -> str:
    total      = len(news)
    bullish    = sum(1 for n in news if n.get("sentiment") == "bullish")
    bearish    = sum(1 for n in news if n.get("sentiment") == "bearish")
    neutral    = total - bullish - bearish

    all_events: list[str] = []
    for article in news:
        all_events.extend(_detect_events(article.get("title", "")))

    event_counts = defaultdict(int)
    for e in all_events:
        event_counts[e] += 1

    top_events = sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    top_str    = ", ".join(f"{e}({c})" for e, c in top_events) if top_events else "no dominant theme"

    top_bull = [i["symbol"].split(":")[-1] for i in stocks_insights + crypto_insights if i["direction"] == "bullish"][:3]
    top_bear = [i["symbol"].split(":")[-1] for i in stocks_insights + crypto_insights if i["direction"] == "bearish"][:3]

    regime = _macro_regime(news)

    summary = (
        f"Market Briefing ({total} articles analyzed): "
        f"Sentiment is {bullish} bullish / {bearish} bearish / {neutral} neutral. "
        f"Dominant themes: {top_str}. "
        f"Macro regime: {regime}. "
    )
    if top_bull:
        summary += f"Instruments with bullish catalysts: {', '.join(top_bull)}. "
    if top_bear:
        summary += f"Instruments with bearish signals: {', '.join(top_bear)}. "

    return summary.strip()


def generate_all_insights(stocks: list[dict], crypto: list[dict], news: list[dict]) -> dict:
    stocks_insights = [generate_instrument_insight(s, news) for s in stocks]
    crypto_insights = [generate_instrument_insight(c, news) for c in crypto]

    # Sort: bullish first, then bearish, then neutral
    order = {"bullish": 0, "bearish": 1, "neutral": 2}
    stocks_insights.sort(key=lambda x: order.get(x["direction"], 2))
    crypto_insights.sort(key=lambda x: order.get(x["direction"], 2))

    market_movers_all = []
    for article in news:
        events = _detect_events(article.get("title", ""))
        if _is_market_moving(events):
            market_movers_all.append({
                "title":   article.get("title", "").encode("ascii", "replace").decode("ascii"),
                "events":  events,
                "link":    article.get("link", ""),
            })

    return {
        "market_summary":  _market_summary(news, stocks_insights, crypto_insights),
        "macro_regime":    _macro_regime(news),
        "market_movers":   market_movers_all[:10],
        "stocks":          stocks_insights,
        "crypto":          crypto_insights,
    }
