from __future__ import annotations
import json
import csv
import os
from datetime import datetime


def _fmt(val) -> str:
    if val is None:
        return "N/A"
    if isinstance(val, float):
        return f"{val:,.4f}".rstrip("0").rstrip(".")
    return str(val)


def _wrap(text: str, width: int = 88, indent: str = "  ") -> None:
    if not text:
        return
    words, line = str(text).split(), ""
    for w in words:
        if len(line) + len(w) + 1 > width:
            print(f"{indent}{line}")
            line = w
        else:
            line = (line + " " + w).strip()
    if line:
        print(f"{indent}{line}")


def print_table(title: str, rows: list[dict], fields: list[tuple]) -> None:
    sep = "+" + "+".join("-" * (w + 2) for _, _, w in fields) + "+"
    header = "|" + "|".join(f" {h:<{w}} " for _, h, w in fields) + "|"
    print(f"\n{'='*len(sep)}")
    print(f"  {title}")
    print(sep)
    print(header)
    print(sep)
    for row in rows:
        line = "|"
        for key, _, w in fields:
            val = _fmt(row.get(key))
            line += f" {val:<{w}} |"
        print(line)
    print(sep)


def print_stocks(stocks: list[dict]) -> None:
    print_table("STOCKS - Real-Time", stocks, [
        ("symbol",     "SYMBOL",  20),
        ("price",      "PRICE",   12),
        ("change_%",   "CHG%",     8),
        ("volume",     "VOLUME",  14),
        ("market_cap", "MKT CAP", 16),
        ("rsi",        "RSI",      7),
        ("signal",     "SIGNAL",  12),
        ("sector",     "SECTOR",  20),
    ])


def print_crypto(crypto: list[dict]) -> None:
    print_table("CRYPTO - Real-Time", crypto, [
        ("symbol",   "SYMBOL",  25),
        ("price",    "PRICE",   14),
        ("change_%", "CHG%",     8),
        ("volume",   "VOLUME",  18),
        ("rsi",      "RSI",      7),
        ("macd",     "MACD",    10),
        ("signal",   "SIGNAL",  12),
        ("vwap",     "VWAP",    14),
    ])


def print_forex(forex: list[dict]) -> None:
    print_table("FOREX - Real-Time", forex, [
        ("symbol",   "PAIR",   12),
        ("price",    "PRICE",  10),
        ("change_%", "CHG%",    8),
        ("high",     "HIGH",   10),
        ("low",      "LOW",    10),
        ("signal",   "SIGNAL", 12),
    ])


def print_commodities(comms: list[dict]) -> None:
    print_table("COMMODITIES - Real-Time", comms, [
        ("symbol",   "COMMODITY", 16),
        ("price",    "PRICE",     12),
        ("change_%", "CHG%",       8),
        ("high",     "HIGH",      12),
        ("low",      "LOW",       12),
        ("signal",   "SIGNAL",    12),
    ])


def print_indices(indices: list[dict]) -> None:
    print_table("INDICES - Real-Time", indices, [
        ("symbol",   "INDEX",  14),
        ("price",    "PRICE",  12),
        ("change_%", "CHG%",    8),
        ("high",     "HIGH",   12),
        ("low",      "LOW",    12),
        ("signal",   "SIGNAL", 12),
    ])


def print_news(news: list[dict]) -> None:
    print(f"\n{'='*80}")
    print(f"  NEWS ({len(news)} articles)")
    print("=" * 80)
    for i, n in enumerate(news, 1):
        icon  = {"bullish": "[+]", "bearish": "[-]", "neutral": "[=]"}.get(n.get("sentiment", ""), "[=]")
        cats  = ", ".join(n.get("categories", []))
        title = n["title"].encode("ascii", "replace").decode("ascii")
        link  = n["link"].encode("ascii", "replace").decode("ascii")
        print(f"  {i:>3}. {icon} [{cats}] {title}")
        print(f"       {n.get('published', 'N/A')} | {n.get('source', 'N/A')} | {link}")
        print()


def print_insights(insights: dict) -> None:
    print(f"\n{'='*90}")
    print(f"  AI-POWERED MARKET INSIGHTS")
    print(f"{'='*90}")
    print(f"\n  [MARKET BRIEFING]")
    summary = insights.get("market_summary", "").encode("ascii", "replace").decode("ascii")
    words, line = summary.split(), ""
    for w in words:
        if len(line) + len(w) + 1 > 85:
            print(f"  {line}")
            line = w
        else:
            line = (line + " " + w).strip()
    if line:
        print(f"  {line}")
    print(f"\n  [MACRO REGIME] {insights.get('macro_regime', 'N/A')}")
    movers = insights.get("market_movers", [])
    if movers:
        print(f"\n  [MARKET-MOVING NEWS] ({len(movers)} high-impact events detected)")
        for m in movers:
            title  = m.get("title", "").encode("ascii", "replace").decode("ascii")
            events = ", ".join(m.get("events", []))
            print(f"    ! [{events}] {title[:80]}")
    for category, label in (("stocks", "STOCKS"), ("crypto", "CRYPTO")):
        items = insights.get(category, [])
        if not items:
            continue
        print(f"\n  [{label} INSIGHTS]")
        for item in items:
            sym       = item.get("symbol", "").split(":")[-1]
            direction = item.get("direction", "neutral").upper()
            tag       = {"BULLISH": "[+]", "BEARISH": "[-]", "NEUTRAL": "[=]"}.get(direction, "[=]")
            insight   = item.get("insight", "").encode("ascii", "replace").decode("ascii")
            chg       = item.get("change_%", 0) or 0
            chg_str   = f"+{chg:.2f}%" if chg >= 0 else f"{chg:.2f}%"
            print(f"    {tag} {sym:<10} {chg_str:>8}   {insight}")
            for mv in item.get("market_movers", [])[:1]:
                t = mv.get("title", "").encode("ascii", "replace").decode("ascii")
                print(f"           >> {t[:75]}")


def print_signals(signals: dict) -> None:
    for category, label in (("stocks", "STOCKS"), ("crypto", "CRYPTO")):
        items = signals.get(category, [])
        if not items:
            continue
        print(f"\n{'='*100}")
        print(f"  REAL-TIME TRADING SIGNALS -- {label}")
        print(f"  {'SYMBOL':<22} {'ACTION':<22} {'CONF':>4}  {'ENTRY':>10} {'STOP':>10} {'STOP%':>7} {'T1':>10} {'T1%':>7} {'T2':>10} {'T2%':>7} {'R/R':>5}")
        print(f"{'='*100}")
        for s in items:
            action = s.get("action", "HOLD")
            stars  = "*" * s.get("confidence", 0)
            sym    = (s.get("symbol") or "")[:22]
            price  = s.get("price")
            if s.get("entry") is not None:
                print(
                    f"  {sym:<22} {action:<22} {stars:>4}  "
                    f"${_fmt(s['entry']):>9} "
                    f"${_fmt(s['stop_loss']):>9} "
                    f"{str(s['stop_pct'])+'%':>7} "
                    f"${_fmt(s['target1']):>9} "
                    f"{str(s['target1_pct'])+'%':>7} "
                    f"${_fmt(s['target2']):>9} "
                    f"{str(s['target2_pct'])+'%':>7} "
                    f"{str(s['rr2'])+'x':>5}"
                )
            else:
                print(f"  {sym:<22} {action:<22} {stars:>4}  ${_fmt(price):>9}")
            for r in s.get("reasons", [])[:3]:
                print(f"    > {r}")
            print()
        buy_now  = [s["symbol"] for s in items if s.get("action") == "BUY NOW"][:5]
        sell_now = [s["symbol"] for s in items if s.get("action") == "SELL NOW"][:5]
        buy_     = [s["symbol"] for s in items if s.get("action") == "BUY"][:5]
        if buy_now:  print(f"  [BUY NOW]  : {', '.join(buy_now)}")
        if buy_:     print(f"  [BUY]      : {', '.join(buy_)}")
        if sell_now: print(f"  [SELL NOW] : {', '.join(sell_now)}")


def print_analysis(analysis: dict) -> None:
    for category, label in (("stocks", "STOCKS"), ("crypto", "CRYPTO")):
        items = analysis.get(category, [])
        if not items:
            continue
        print(f"\n{'='*90}")
        print(f"  INVESTMENT ANALYSIS -- {label}")
        print(f"{'='*90}")
        for a in items:
            scores = a["scores"]
            fund   = scores["fundamental"]
            fund_s = f"{fund}" if fund != "N/A" else "N/A "
            print(
                f"  {a['verdict']:<22}  "
                f"{a['symbol']:<25}  "
                f"${_fmt(a['price']):<12}  "
                f"Score: {a['composite']:>5.1f}/100  "
                f"[T:{scores['technical']:>5.1f} M:{scores['momentum']:>5.1f} "
                f"F:{fund_s:>5} N:{scores['news']:>5.1f}]"
            )
            print(f"     -> {a['verdict_desc']}")
            all_reasons = []
            for dim in ("technical", "momentum", "fundamental", "news"):
                all_reasons.extend(a["reasons"].get(dim, [])[:2])
            for r in all_reasons[:6]:
                print(f"       * {r}")
            print()
        buys  = [a["symbol"] for a in items if "BUY"  in a["verdict"]][:5]
        sells = [a["symbol"] for a in items if "SELL" in a["verdict"]][:5]
        if buys:  print(f"  [TOP PICKS] : {', '.join(buys)}")
        if sells: print(f"  [AVOID]     : {', '.join(sells)}")


def print_regime(regime: dict) -> None:
    W = "=" * 92
    print(f"\n{W}")
    print(f"  MARKET REGIME DETECTION")
    print(W)
    print(f"  Composite  : {regime.get('composite_regime', 'N/A')}")
    print(f"  Trend      : {regime.get('trend_regime', 'N/A')}")
    print(f"  Volatility : {regime.get('volatility_regime', 'N/A')}")
    print(f"  Momentum   : {regime.get('momentum_regime', 'N/A')}")
    print(f"  Macro      : {regime.get('macro_regime', 'N/A')}")
    print(f"  Liquidity  : {regime.get('liquidity_regime', 'N/A')}")
    print(f"  VIX        : {regime.get('vix', 'N/A')}   DXY: {regime.get('dxy', 'N/A')}")
    print(f"  Strategy   : {regime.get('recommended_strategy', '')}")


def print_ai_analysis(ai: dict) -> None:
    W   = "=" * 92
    SEP = f"  {'-'*88}"
    print(f"\n{W}")
    print(f"  HIGHEST-LEVEL MULTI-AGENT AI INVESTMENT SYSTEM  (NVIDIA LLaMA 3.3-70B)")
    print(W)

    if "error" in ai:
        print(f"  [ERROR] {ai['error']}")
        return

    agents     = ai.get("agents", {})
    debate     = ai.get("debate", {})
    trader     = ai.get("trader", {})
    risk       = ai.get("risk", {})
    portfolio  = ai.get("portfolio", {})
    execution  = ai.get("execution", {})
    reflection = ai.get("reflection", {})
    final      = ai.get("final", {})
    fund = agents.get("fundamental", {})
    tech = agents.get("technical", {})
    sent = agents.get("sentiment", {})
    news = agents.get("news", {})

    # -- Layer 1: Specialized Agents ------------------------------------------
    print(f"\n{SEP}\n  LAYER 1 - SPECIALIZED AI AGENTS\n{SEP}")
    print(f"  [Fundamental]  Bias: {fund.get('macro_fundamental_bias','N/A')}")
    _wrap(fund.get("summary", ""))
    for s in fund.get("top_fundamental_stocks", [])[:4]:
        print(f"    + {s.get('symbol',''):<12} {s.get('verdict',''):<14} {s.get('note','')}")
    print(f"\n  [Technical]    Bias: {tech.get('macro_technical_bias','N/A')}")
    _wrap(tech.get("summary", ""))
    for s in tech.get("bullish_setups", [])[:3]:
        print(f"    + {s.get('symbol',''):<12} [{s.get('strength','')}]  {', '.join(s.get('signals',[])[:2])}")
    for s in tech.get("bearish_setups", [])[:2]:
        print(f"    - {s.get('symbol',''):<12} [{s.get('strength','')}]  {', '.join(s.get('signals',[])[:2])}")
    print(f"\n  [Sentiment]    {sent.get('overall_sentiment','N/A')}  "
          f"| Fear/Greed: {sent.get('fear_greed_index','?')} - {sent.get('fear_greed_label','?')}")
    _wrap(sent.get("summary", ""))
    print(f"\n  [News]         Bias: {news.get('news_macro_bias','N/A')}")
    _wrap(news.get("summary", ""))
    for c in news.get("macro_catalysts", [])[:3]:
        print(f"    ! [{c.get('impact','')}] {c.get('event','')}  -> {', '.join(c.get('affected_sectors',[]))}")

    # -- Layer 2: Debate & Coordination ---------------------------------------
    print(f"\n{SEP}\n  LAYER 2 - DEBATE & COORDINATION\n{SEP}")
    print(f"  Winner: {debate.get('debate_winner','?'):<8}  "
          f"Conviction: {debate.get('conviction','?'):<8}  "
          f"Regime Alignment: {debate.get('regime_alignment','?')}")
    bull = debate.get("bull_case", {})
    bear = debate.get("bear_case", {})
    print(f"  [BULL] {bull.get('strongest_point','')}")
    for a in bull.get("arguments", [])[:2]: print(f"    + {a}")
    print(f"  [BEAR] {bear.get('strongest_point','')}")
    for a in bear.get("arguments", [])[:2]: print(f"    - {a}")
    _wrap(debate.get("verdict", ""))

    # -- Layer 3: Risk Optimization -------------------------------------------
    print(f"\n{SEP}\n  LAYER 3 - RISK OPTIMIZATION  (Trader: {trader.get('trader_bias','N/A')})\n{SEP}")
    print(f"  {'SYMBOL':<12} {'DIR':<6} {'ENTRY':<14} {'STOP':<14} {'T1':<14} {'T2':<14} {'FIT':<8} {'TF'}")
    for t in trader.get("trade_ideas", []):
        print(f"  {t.get('symbol',''):<12} {t.get('direction',''):<6} "
              f"{str(t.get('entry_zone','')):<14} {str(t.get('stop_loss','')):<14} "
              f"{str(t.get('target1','')):<14} {str(t.get('target2','')):<14} "
              f"{t.get('regime_fit',''):<8} {t.get('timeframe','')}")
        print(f"    > {t.get('rationale','')}")
    print(f"  Best: {trader.get('best_trade','N/A')}  | Avoid: {', '.join(trader.get('trades_to_avoid',[]))}")
    print(f"\n  Risk: Heat={risk.get('portfolio_heat','N/A')}  "
          f"MaxSize={risk.get('max_position_size_%','N/A')}%  "
          f"Kelly={risk.get('kelly_fraction','N/A')}")
    approved = risk.get("approved_trades", [])
    print(f"  Approved: {', '.join(approved) if approved else 'none'}")
    for r in risk.get("rejected_trades", []):
        print(f"  Rejected: {r.get('symbol','')} - {r.get('reason','')}")
    for tr in risk.get("tail_risks", []):
        print(f"  Tail Risk: {tr}")
    _wrap(risk.get("risk_verdict", ""))

    # -- Layer 4: Portfolio Optimization --------------------------------------
    print(f"\n{SEP}\n  LAYER 4 - PORTFOLIO OPTIMIZATION  (Bias: {portfolio.get('portfolio_bias','N/A')})\n{SEP}")
    print(f"  Cash: {portfolio.get('cash_reserve_%','N/A')}%  | Rebalance: {portfolio.get('rebalance_trigger','')}")
    sw = portfolio.get("sector_weights", {})
    if sw:
        print(f"  Sector Weights: " + "  ".join(f"{k}:{v}%" for k, v in sw.items()))
    print(f"  {'SYMBOL':<12} {'DIR':<8} {'ALLOC%':>7}  {'KELLY%':>7}  {'PRIORITY'}")
    for a in portfolio.get("allocations", []):
        print(f"  {a.get('symbol',''):<12} {a.get('direction',''):<8} "
              f"{str(a.get('allocation_%','?')):>7}%  "
              f"{str(a.get('kelly_adjusted_%','?')):>7}%  "
              f"{a.get('priority','')}")
    _wrap(portfolio.get("portfolio_summary", ""))

    # -- Layer 5: Execution Optimization --------------------------------------
    print(f"\n{SEP}\n  LAYER 5 - EXECUTION OPTIMIZATION\n{SEP}")
    _wrap(execution.get("overall_execution_strategy", ""))
    print(f"  {'SYMBOL':<12} {'ORDER':<10} {'TIMING':<22} {'URGENCY':<8} {'SLIPPAGE'}")
    for e in execution.get("execution_plan", []):
        print(f"  {e.get('symbol',''):<12} {e.get('order_type',''):<10} "
              f"{e.get('entry_timing',''):<22} {e.get('urgency',''):<8} "
              f"{e.get('slippage_risk','')}")
        print(f"    > {e.get('execution_note','')}")

    # -- Layer 6: Learning & Reflection ---------------------------------------
    print(f"\n{SEP}\n  LAYER 6 - LEARNING & REFLECTION\n{SEP}")
    print(f"  Pipeline Consistency: {reflection.get('pipeline_consistency','N/A')}  "
          f"| Confidence: {reflection.get('confidence_in_thesis','N/A')}")
    for d in reflection.get("agent_disagreements", []):
        print(f"  [Disagreement] {d}")
    for b in reflection.get("blind_spots", []):
        print(f"  [Blind Spot]   {b}")
    for s in reflection.get("scenario_risks", [])[:3]:
        print(f"  [Scenario] {s.get('scenario','')} -> Impact: {s.get('impact','')} | Hedge: {s.get('hedge','')}")
    signals_watch = reflection.get("adaptation_signals", [])
    if signals_watch:
        print(f"  [Watch For]: {', '.join(signals_watch[:3])}")
    _wrap(reflection.get("reflection_summary", ""))

    # -- Layer 7: Final CIO Decision + Continuous Adaptation ------------------
    print(f"\n{SEP}\n  LAYER 7 - FINAL CIO DECISION + CONTINUOUS ADAPTATION\n{SEP}")
    print(f"  Overall Bias: {final.get('overall_market_bias','N/A')}  | Cash: {final.get('cash_reserve_%','N/A')}%")
    _wrap(final.get("regime_summary", ""))
    print(f"\n  {'ACTION':<10} {'SYMBOL':<12} {'CONV':<8} {'ALLOC%':>7}  "
          f"{'ENTRY':<14} {'STOP':<12} {'TARGET':<12} {'ORDER':<8} {'TF'}")
    for t in final.get("final_trades", []):
        print(f"  {t.get('action',''):<10} {t.get('symbol',''):<12} "
              f"{t.get('conviction',''):<8} {str(t.get('allocation_%','?')):>7}%  "
              f"{str(t.get('entry_zone','')):<14} {str(t.get('stop_loss','')):<12} "
              f"{str(t.get('target','')):<12} {t.get('order_type',''):<8} "
              f"{t.get('timeframe','')}")
        print(f"    > {t.get('rationale','')}")
    print(f"\n  [TOP OPPORTUNITY]")
    _wrap(final.get("top_opportunity", ""), indent="    ")
    print(f"\n  [BIGGEST RISK]")
    _wrap(final.get("biggest_risk", ""), indent="    ")
    dnt = final.get("do_not_touch", [])
    if dnt:
        print(f"\n  [DO NOT TOUCH]  {', '.join(dnt)}")
    print(f"\n  [ADAPTATION PLAN]")
    _wrap(final.get("adaptation_plan", ""), indent="    ")
    print(f"\n  [EXECUTIVE SUMMARY]")
    _wrap(final.get("executive_summary", ""), indent="    ")
    print()


def save_json(output: dict, path: str = "output.json") -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] JSON saved -> {os.path.abspath(path)}")


def save_csv(output: dict, folder: str = ".") -> None:
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    for key in ("stocks", "crypto", "forex", "commodities", "indices"):
        rows = output.get(key, [])
        if not rows:
            continue
        path = os.path.join(folder, f"{key}_{ts}.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"[OK] CSV  saved -> {os.path.abspath(path)}")
    news = output.get("news", [])
    if news:
        path = os.path.join(folder, f"news_{ts}.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "link", "published", "source", "sentiment", "categories"])
            writer.writeheader()
            for n in news:
                row = dict(n)
                row["categories"] = ", ".join(row.get("categories", []))
                writer.writerow(row)
        print(f"[OK] CSV  saved -> {os.path.abspath(path)}")
