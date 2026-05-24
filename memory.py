"""
memory.py - AI Reasoning + Memory System

Implements:
- Episodic memory: stores past market setups and outcomes
- Semantic memory: stores market knowledge and patterns
- Strategic memory: stores successful/failed strategies per regime
- Trade reflection: learns from past decisions
- Pattern matching: recognizes current setup similarity to past events
"""
from __future__ import annotations
import json
import os
from datetime import datetime

MEMORY_FILE = "memory.json"


def _load() -> dict:
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "episodic":  [],   # past market events + outcomes
        "semantic":  {},   # market knowledge: regime -> patterns
        "strategic": {},   # strategy performance per regime
        "reflections": [], # pipeline self-assessments
    }


def _save(memory: dict) -> None:
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)


# ── Episodic Memory ───────────────────────────────────────────────────────────

def store_episode(regime: str, top_trade: str, bias: str,
                  vix: float, fear_greed: int, reflection_summary: str,
                  price: float = None) -> None:
    """Store a market episode for future pattern matching."""
    memory = _load()
    episode = {
        "timestamp":   datetime.utcnow().isoformat() + "Z",
        "regime":      regime,
        "top_trade":   top_trade,
        "bias":        bias,
        "vix":         vix,
        "fear_greed":  fear_greed,
        "reflection":  reflection_summary,
        "price_at_time": price,
    }
    memory["episodic"].append(episode)
    # Keep last 50 episodes
    memory["episodic"] = memory["episodic"][-50:]
    _save(memory)


# ── Semantic Memory ───────────────────────────────────────────────────────────

def update_semantic(regime: str, patterns: list[str]) -> None:
    """Update market knowledge for a given regime."""
    memory = _load()
    if regime not in memory["semantic"]:
        memory["semantic"][regime] = []
    memory["semantic"][regime].extend(patterns)
    # Keep last 20 patterns per regime
    memory["semantic"][regime] = list(set(memory["semantic"][regime]))[-20:]
    _save(memory)


# ── Strategic Memory ──────────────────────────────────────────────────────────

def update_strategy(regime: str, strategy: str, outcome: str) -> None:
    """Track strategy performance per regime."""
    memory = _load()
    if regime not in memory["strategic"]:
        memory["strategic"][regime] = {}
    if strategy not in memory["strategic"][regime]:
        memory["strategic"][regime][strategy] = {"wins": 0, "losses": 0}
    if outcome == "WIN":
        memory["strategic"][regime][strategy]["wins"] += 1
    else:
        memory["strategic"][regime][strategy]["losses"] += 1
    _save(memory)


# ── Pattern Matching ──────────────────────────────────────────────────────────

def recall_similar(regime: str, vix: float, bias: str, n: int = 3) -> list[dict]:
    """Find similar past episodes to current market state."""
    memory = _load()
    episodes = memory.get("episodic", [])
    if not episodes:
        return []

    scored = []
    for ep in episodes:
        score = 0
        if ep.get("regime") == regime:       score += 3
        if ep.get("bias") == bias:            score += 2
        if vix and ep.get("vix"):
            if abs(ep["vix"] - vix) < 3:     score += 2
            elif abs(ep["vix"] - vix) < 7:   score += 1
        scored.append((score, ep))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [ep for _, ep in scored[:n]]


# ── Reflection Storage ────────────────────────────────────────────────────────

def store_reflection(pipeline_output: dict) -> None:
    """Store pipeline self-assessment for continuous learning."""
    memory = _load()
    final      = pipeline_output.get("final", {})
    reflection = pipeline_output.get("reflection", {})
    regime_data = pipeline_output.get("regime", {})

    entry = {
        "timestamp":            datetime.utcnow().isoformat() + "Z",
        "regime":               regime_data.get("composite_regime"),
        "bias":                 final.get("overall_market_bias"),
        "top_opportunity":      final.get("top_opportunity"),
        "biggest_risk":         final.get("biggest_risk"),
        "final_trades":         final.get("final_trades", []),
        "pipeline_consistency": reflection.get("pipeline_consistency"),
        "blind_spots":          reflection.get("blind_spots", []),
        "adaptation_signals":   reflection.get("adaptation_signals", []),
    }
    memory["reflections"].append(entry)
    memory["reflections"] = memory["reflections"][-30:]
    _save(memory)


# ── Memory Context for AI Agents ─────────────────────────────────────────────

def get_memory_context(regime: str, vix: float, bias: str) -> dict:
    """
    Build memory context to inject into AI agents.
    Returns similar past episodes + regime patterns + strategy performance.
    """
    memory   = _load()
    similar  = recall_similar(regime, vix, bias)
    patterns = memory.get("semantic", {}).get(regime, [])
    strategy = memory.get("strategic", {}).get(regime, {})

    # Build strategy win rates
    strategy_summary = {}
    for strat, counts in strategy.items():
        wins   = counts.get("wins", 0)
        losses = counts.get("losses", 0)
        total  = wins + losses
        if total > 0:
            strategy_summary[strat] = {
                "win_rate_%": round(wins / total * 100, 1),
                "total_trades": total,
            }

    return {
        "similar_past_episodes": similar,
        "regime_patterns":       patterns[:5],
        "strategy_performance":  strategy_summary,
        "memory_note": (
            f"Last time {regime} regime appeared: "
            f"{similar[0].get('reflection', 'no data')}"
            if similar else "No similar past episodes found."
        ),
    }
