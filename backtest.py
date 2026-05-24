"""
backtest.py - Performance Backtesting Module
Compares past AI trade recommendations with current market prices.
"""
from __future__ import annotations
import json
import os
from datetime import datetime

MEMORY_FILE = "memory.json"

def run_backtest(current_data: dict) -> dict:
    """
    Analyzes past recommendations in memory.json and compares them with current_data.
    current_data should contain 'stocks' and 'crypto' lists with current prices.
    """
    if not os.path.exists(MEMORY_FILE):
        return {"status": "No memory file found for backtesting"}

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            memory = json.load(f)
    except Exception as e:
        return {"status": f"Error loading memory: {e}"}

    reflections = memory.get("reflections", [])
    if not reflections:
        return {"status": "No past reflections found in memory"}

    # Create a lookup for current prices
    current_prices = {}
    for cat in ("stocks", "crypto"):
        for item in current_data.get(cat, []):
            sym = item.get("symbol")
            price = item.get("price")
            if sym and price:
                current_prices[sym] = price

    results = []
    total_pnl = 0.0
    wins = 0
    losses = 0

    # We look at final_trades stored in reflections
    for entry in reflections:
        timestamp = entry.get("timestamp")
        trades = entry.get("final_trades", [])
        
        for trade in trades:
            sym = trade.get("symbol")
            action = trade.get("action", "")
            # We need an entry price. If 'entry_zone' was a single price or we can parse it.
            # In our new schema, we should ideally store the exact price at time of recommendation.
            # For now, let's try to extract price from entry_zone or assume it's missing if not numeric.
            
            entry_price_raw = trade.get("entry_zone")
            try:
                # If entry_zone is like "$150.25" or "150.25"
                entry_price = float(str(entry_price_raw).replace("$", "").replace(",", ""))
            except (ValueError, TypeError):
                continue

            current_price = current_prices.get(sym)
            if current_price:
                # Calculate P&L
                if "BUY" in action:
                    pnl_pct = (current_price - entry_price) / entry_price * 100
                elif "SELL" in action:
                    pnl_pct = (entry_price - current_price) / entry_price * 100
                else:
                    continue

                is_win = pnl_pct > 0
                if is_win: wins += 1
                else: losses += 1
                total_pnl += pnl_pct

                results.append({
                    "timestamp": timestamp,
                    "symbol": sym,
                    "action": action,
                    "entry": entry_price,
                    "current": current_price,
                    "pnl_%": round(pnl_pct, 2),
                    "result": "WIN" if is_win else "LOSS"
                })

    total_trades = wins + losses
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

    return {
        "summary": {
            "total_trades": total_trades,
            "wins": wins,
            "losses": losses,
            "win_rate_%": round(win_rate, 2),
            "avg_pnl_%": round(total_pnl / total_trades, 2) if total_trades > 0 else 0,
        },
        "trades": results[-10:] # Return last 10 for display
    }

def print_backtest_results(results: dict):
    """Utility to print backtest results in a nice format."""
    if "summary" not in results:
        print(f"\n  [Backtest] {results.get('status', 'No data')}")
        return

    s = results["summary"]
    print(f"\n  ============================================================")
    print(f"  PERFORMANCE BACKTEST (Past AI Recommendations)")
    print(f"  ============================================================")
    print(f"  Total Trades : {s['total_trades']}")
    print(f"  Win Rate     : {s['win_rate_%']}% ({s['wins']}W / {s['losses']}L)")
    print(f"  Avg P&L      : {s['avg_pnl_%']}%")
    print(f"  ------------------------------------------------------------")
    
    if results["trades"]:
        print(f"  {'TIMESTAMP':<22} {'SYMBOL':<12} {'ACTION':<10} {'P&L%':>8} {'RESULT'}")
        for t in results["trades"]:
            ts = t["timestamp"][:16].replace("T", " ")
            print(f"  {ts:<22} {t['symbol']:<12} {t['action']:<10} {t['pnl_%']:>7}%  {t['result']}")
    
    print(f"  ============================================================\n")
