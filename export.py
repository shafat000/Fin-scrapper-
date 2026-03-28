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
        icon = {"bullish": "[+]", "bearish": "[-]", "neutral": "[=]"}.get(n.get("sentiment", ""), "[=]")
        cats = ", ".join(n.get("categories", []))
        title = n["title"].encode("ascii", "replace").decode("ascii")
        link  = n["link"].encode("ascii", "replace").decode("ascii")
        print(f"  {i:>3}. {icon} [{cats}] {title}")
        print(f"       {n.get('published', 'N/A')} | {n.get('source', 'N/A')} | {link}")
        print()


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

        # Summary
        buy_now  = [s["symbol"] for s in items if "BUY NOW" == s.get("action")][:5]
        sell_now = [s["symbol"] for s in items if "SELL NOW" == s.get("action")][:5]
        buy_     = [s["symbol"] for s in items if s.get("action") == "BUY"][:5]
        if buy_now:
            print(f"  [BUY NOW]  : {', '.join(buy_now)}")
        if buy_:
            print(f"  [BUY]      : {', '.join(buy_)}")
        if sell_now:
            print(f"  [SELL NOW] : {', '.join(sell_now)}")


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
        if buys:
            print(f"  [TOP PICKS] : {', '.join(buys)}")
        if sells:
            print(f"  [AVOID]     : {', '.join(sells)}")


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
