"""
monitor.py — Real-Time Signal Monitor
Polls TradingView every INTERVAL seconds and prints alerts when signals change.

Usage:
    python monitor.py              # default 60s interval
    python monitor.py --interval 30
"""
from __future__ import annotations
import asyncio
import argparse
from datetime import datetime

import httpx

from scanner import fetch, STOCK_SYMBOLS, CRYPTO_SYMBOLS
from news import scrape_news
from analyst import analyze_all
from signals import generate_all

INTERVAL = 60  # seconds between polls

# ── Alert thresholds ──────────────────────────────────────────────────────────
# Only alert when action is one of these (ignore HOLD / WAIT)
ALERT_ACTIONS = {"BUY NOW", "BUY", "SELL NOW", "SELL"}

# Minimum composite score change to re-alert the same symbol
SCORE_CHANGE_THRESHOLD = 5.0

# ── Colour codes (Windows CMD supports ANSI via VT100 if enabled) ─────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


def _color(action: str) -> str:
    if "BUY" in action:
        return GREEN
    if "SELL" in action:
        return RED
    return YELLOW


def _stars(n: int) -> str:
    return "★" * n + "☆" * (5 - n)


def _fmt(val) -> str:
    if val is None:
        return "N/A"
    if isinstance(val, float):
        return f"{val:,.4f}".rstrip("0").rstrip(".")
    return str(val)


def _print_alert(sig: dict, prev_action: str | None, category: str) -> None:
    action = sig["action"]
    sym    = sig.get("symbol", "")
    price  = sig.get("price")
    score  = sig.get("score", 0)
    conf   = sig.get("confidence", 0)
    c      = _color(action)
    ts     = datetime.now().strftime("%H:%M:%S")
    change = f"  [{prev_action} → {action}]" if prev_action and prev_action != action else ""

    print(f"\n{BOLD}{c}{'='*70}{RESET}")
    print(f"{BOLD}{c}  [{ts}] {category.upper()} SIGNAL ALERT{RESET}{change}")
    print(f"{BOLD}{c}  {action:<14}  {sym:<28}  ${_fmt(price):<14}  Score: {score:.1f}/100  {_stars(conf)}{RESET}")

    if sig.get("entry") is not None:
        print(
            f"  Entry: ${_fmt(sig['entry'])}  "
            f"Stop: ${_fmt(sig['stop_loss'])} ({sig['stop_pct']}%)  "
            f"T1: ${_fmt(sig['target1'])} ({sig['target1_pct']}%)  "
            f"T2: ${_fmt(sig['target2'])} ({sig['target2_pct']}%)  "
            f"R/R: {sig['rr2']}x"
        )

    for r in sig.get("reasons", [])[:4]:
        print(f"  > {r}")
    print(f"{c}{'='*70}{RESET}")


async def _poll(prev_state: dict) -> dict:
    """Fetch fresh data, generate signals, print alerts for changes."""
    async with httpx.AsyncClient(timeout=20) as client:
        stocks, crypto, news = await asyncio.gather(
            fetch("america", STOCK_SYMBOLS, client),
            fetch("crypto",  CRYPTO_SYMBOLS, client),
            scrape_news(max_scrolls=1),
        )

    analysis = analyze_all(stocks, crypto, news)
    signals  = generate_all(analysis, stocks, crypto)

    new_state: dict = {}

    for category in ("stocks", "crypto"):
        for sig in signals.get(category, []):
            sym    = sig.get("symbol")
            action = sig.get("action", "HOLD")
            score  = sig.get("score", 50)

            prev = prev_state.get(sym)

            should_alert = False
            if action in ALERT_ACTIONS:
                if prev is None:
                    should_alert = True  # first time seeing this symbol
                elif prev["action"] != action:
                    should_alert = True  # action changed
                elif abs(score - prev["score"]) >= SCORE_CHANGE_THRESHOLD:
                    should_alert = True  # same action but score moved significantly

            if should_alert:
                _print_alert(sig, prev["action"] if prev else None, category)

            new_state[sym] = {"action": action, "score": score}

    return new_state


async def run(interval: int) -> None:
    # Enable ANSI on Windows
    import os
    os.system("")

    print(f"{CYAN}{BOLD}")
    print("  ╔══════════════════════════════════════════╗")
    print("  ║   REAL-TIME SIGNAL MONITOR  v1.0         ║")
    print(f"  ║   Polling every {interval}s                      ║")
    print("  ║   Ctrl+C to stop                         ║")
    print("  ╚══════════════════════════════════════════╝")
    print(f"{RESET}")

    state: dict = {}
    poll_count  = 0

    while True:
        poll_count += 1
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{CYAN}  [Poll #{poll_count}] {ts} — fetching...{RESET}", end="", flush=True)

        try:
            state = await _poll(state)
            buy_now  = sum(1 for v in state.values() if v["action"] == "BUY NOW")
            sell_now = sum(1 for v in state.values() if v["action"] == "SELL NOW")
            buy_     = sum(1 for v in state.values() if v["action"] == "BUY")
            sell_    = sum(1 for v in state.values() if v["action"] == "SELL")
            print(
                f"\r{CYAN}  [Poll #{poll_count}] {ts} — "
                f"{GREEN}BUY NOW:{buy_now} BUY:{buy_}{CYAN}  "
                f"{RED}SELL NOW:{sell_now} SELL:{sell_}{CYAN}  "
                f"(next in {interval}s){RESET}"
            )
        except Exception as e:
            print(f"\r  [!] Poll error: {e}")

        await asyncio.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real-time trading signal monitor")
    parser.add_argument("--interval", type=int, default=INTERVAL,
                        help=f"Seconds between polls (default: {INTERVAL})")
    args = parser.parse_args()

    try:
        asyncio.run(run(args.interval))
    except KeyboardInterrupt:
        print("\n\n  [Stopped] Monitor shut down.\n")
