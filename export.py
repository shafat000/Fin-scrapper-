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
    """fields = list of (key, header, width)"""
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
    print_table("STOCKS — Real-Time", stocks, [
        ("symbol",        "SYMBOL",    20),
        ("price",         "PRICE",     12),
        ("change_%",      "CHG%",       8),
        ("volume",        "VOLUME",    14),
        ("market_cap",    "MKT CAP",   16),
        ("rsi",           "RSI",        7),
        ("signal",        "SIGNAL",    12),
        ("sector",        "SECTOR",    20),
    ])


def print_crypto(crypto: list[dict]) -> None:
    print_table("CRYPTO — Real-Time", crypto, [
        ("symbol",    "SYMBOL",    25),
        ("price",     "PRICE",     14),
        ("change_%",  "CHG%",       8),
        ("volume",    "VOLUME",    18),
        ("rsi",       "RSI",        7),
        ("macd",      "MACD",      10),
        ("signal",    "SIGNAL",    12),
        ("vwap",      "VWAP",      14),
    ])


def print_forex(forex: list[dict]) -> None:
    print_table("FOREX — Real-Time", forex, [
        ("symbol",    "PAIR",      12),
        ("price",     "PRICE",     10),
        ("change_%",  "CHG%",       8),
        ("high",      "HIGH",      10),
        ("low",       "LOW",       10),
        ("signal",    "SIGNAL",    12),
    ])


def print_commodities(comms: list[dict]) -> None:
    print_table("COMMODITIES — Real-Time", comms, [
        ("symbol",    "COMMODITY", 16),
        ("price",     "PRICE",     12),
        ("change_%",  "CHG%",       8),
        ("high",      "HIGH",      12),
        ("low",       "LOW",       12),
        ("signal",    "SIGNAL",    12),
    ])


def print_indices(indices: list[dict]) -> None:
    print_table("INDICES — Real-Time", indices, [
        ("symbol",    "INDEX",     14),
        ("price",     "PRICE",     12),
        ("change_%",  "CHG%",       8),
        ("high",      "HIGH",      12),
        ("low",       "LOW",       12),
        ("signal",    "SIGNAL",    12),
    ])


def print_news(news: list[dict]) -> None:
    print(f"\n{'='*80}")
    print(f"  NEWS ({len(news)} articles)")
    print("=" * 80)
    for i, n in enumerate(news, 1):
        sentiment_icon = {"bullish": "▲", "bearish": "▼", "neutral": "●"}.get(n.get("sentiment", ""), "●")
        cats = ", ".join(n.get("categories", []))
        print(f"  {i:>3}. {sentiment_icon} [{cats}] {n['title']}")
        print(f"       {n.get('published', 'N/A')} | {n.get('source', 'N/A')} | {n['link']}")
        print()


def save_json(output: dict, path: str = "output.json") -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n[✓] JSON saved → {os.path.abspath(path)}")


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
        print(f"[✓] CSV  saved → {os.path.abspath(path)}")

    # news CSV
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
        print(f"[✓] CSV  saved → {os.path.abspath(path)}")
