# TradingView Financial Scraper + Highest-Level Multi-Agent AI Investment System

A real-time financial data scraper and **institutional-grade multi-agent AI investment engine** built with **Playwright**, **BeautifulSoup**, **httpx**, and **NVIDIA LLaMA 3.3-70B**. Pulls live market data across stocks, crypto, forex, commodities, and indices — then runs it through a complete 11-layer AI pipeline from raw data to final trade decision with execution optimization, learning, and continuous adaptation.

---

## Highest-Level Architecture

```
+─────────────────────────────────────────────────────────────+
│  LAYER 1 — Market Data Layer                                │
│  Stocks / Crypto / Forex / Commodities / Indices / News     │
│  All 6 sources fetched concurrently via asyncio.gather      │
+─────────────────────────────────────────────────────────────+
                            |
                            v
+─────────────────────────────────────────────────────────────+
│  LAYER 2 — Microstructure Engine                            │
│  Spread proxy, liquidity score, order flow imbalance,       │
│  VWAP deviation, Bollinger Band width, volume confirmation  │
+─────────────────────────────────────────────────────────────+
                            |
                            v
+─────────────────────────────────────────────────────────────+
│  LAYER 3 — Feature Extraction                               │
│  Trend score, momentum, volume-weighted momentum,           │
│  volatility regime, EMA deviation, composite feature        │
│  vector (-100 to +100), cross-asset signals                 │
+─────────────────────────────────────────────────────────────+
                            |
                            v
+─────────────────────────────────────────────────────────────+
│  LAYER 4 — Regime Detection                                 │
│  Trend / Volatility / Liquidity / Macro / Momentum          │
│  → Composite: BULL-MARKET | BEAR-MARKET | CRISIS-MODE       │
│               CONSOLIDATION | TRANSITIONAL                  │
│  + Recommended strategy per regime                          │
+─────────────────────────────────────────────────────────────+
                            |
                            v
+─────────────────────────────────────────────────────────────+
│  LAYER 5 — Specialized AI Agents (4 independent)           │
│                                                             │
│  [Fundamental]  P/E, EPS, market cap, beta, dividends       │
│  [Technical]    RSI, MACD, EMA, VWAP, BB, ATR + regime      │
│  [Sentiment]    Fear/Greed, order flow, volume patterns     │
│  [News]         Themes, macro catalysts, geopolitical risks │
+─────────────────────────────────────────────────────────────+
                            |
                            v
+─────────────────────────────────────────────────────────────+
│  LAYER 6 — Debate & Coordination                            │
│  Bull case vs Bear case — regime-aligned                    │
│  Winner + conviction + regime_alignment field               │
+─────────────────────────────────────────────────────────────+
                            |
                            v
+─────────────────────────────────────────────────────────────+
│  LAYER 7 — Risk Optimization                                │
│  Trader: entry/stop/target + regime_fit per trade           │
│  Risk Manager: approve/reject, Kelly fraction,              │
│  portfolio heat, tail risks                                 │
+─────────────────────────────────────────────────────────────+
                            |
                            v
+─────────────────────────────────────────────────────────────+
│  LAYER 8 — Portfolio Optimization                           │
│  Kelly-adjusted allocation %, sector weights,               │
│  cash reserve, rebalance trigger, diversification           │
+─────────────────────────────────────────────────────────────+
                            |
                            v
+─────────────────────────────────────────────────────────────+
│  LAYER 9 — Execution Optimization                           │
│  Order type (MARKET/LIMIT/TWAP/VWAP), entry timing,         │
│  urgency, slippage risk per position                        │
+─────────────────────────────────────────────────────────────+
                            |
                            v
+─────────────────────────────────────────────────────────────+
│  LAYER 10 — Learning & Reflection                           │
│  Pipeline consistency check, agent disagreements,           │
│  blind spots, scenario risks, adaptation signals            │
+─────────────────────────────────────────────────────────────+
                            |
                            v
+─────────────────────────────────────────────────────────────+
│  LAYER 11 — Continuous Adaptation / Final CIO Decision      │
│  Overall bias, final trades with order type + timeframe,    │
│  top opportunity, biggest risk, do-not-touch list,          │
│  adaptation plan, executive summary                         │
+─────────────────────────────────────────────────────────────+
```

---

## Project Structure

```
Fin-scrapper-/
├── scraper.py          # Orchestrator — runs all 11 layers end to end
├── scanner.py          # TradingView scanner API client
├── news.py             # Playwright + BeautifulSoup news scraper
├── microstructure.py   # Layer 2 — spread, liquidity, order flow imbalance
├── features.py         # Layer 3 — feature vectors + cross-asset signals
├── regime.py           # Layer 4 — 5-dimensional market regime detection
├── analyst.py          # Rule-based scoring engine (0–100 composite)
├── signals.py          # ATR-based entry / stop-loss / take-profit generator
├── insights.py         # Event detection + macro regime classifier
├── ai_analyst.py       # Layers 5–11 — full multi-agent AI pipeline
├── export.py           # Console output + JSON/CSV export
├── requirements.txt    # Python dependencies
├── output.json         # Generated on each run (gitignored)
└── README.md
```

---

## Requirements

- Python 3.10+
- Internet connection
- NVIDIA API key (set in `ai_analyst.py`)

---

## Installation

```bash
pip install -r requirements.txt
playwright install chromium
```

---

## Usage

```bash
python scraper.py
```

---

## Data Sources

| Data | Source | Method |
|------|--------|--------|
| Stocks | `scanner.tradingview.com/america/scan` | `httpx` async POST |
| Crypto | `scanner.tradingview.com/crypto/scan` | `httpx` async POST |
| Forex | `scanner.tradingview.com/forex/scan` | `httpx` async POST |
| Commodities | `scanner.tradingview.com/global/scan` | `httpx` async POST |
| Indices | `scanner.tradingview.com/global/scan` | `httpx` async POST |
| News | `tradingview.com/news/` | Playwright + BeautifulSoup |

---

## Layer Details

### Layer 2 — Microstructure Engine (`microstructure.py`)

Computes market microstructure metrics for every instrument before any analysis runs.

| Metric | Description |
|--------|-------------|
| `spread_proxy_%` | ATR as % of price — proxy for bid/ask spread |
| `liquidity_score` | 0–100 score based on volume ratio and spread |
| `order_flow_imbalance` | 0–1 price position within day's range (0=at low, 1=at high) |
| `flow_bias` | `BUYING` / `SELLING` / `NEUTRAL` from OFI |
| `vwap_deviation_%` | % distance of price from VWAP |
| `bb_width_%` | Bollinger Band width as % of price (volatility expansion) |
| `volume_ratio` | Today's volume vs 10-day average |
| `volume_confirms` | Whether volume confirms the price move |

---

### Layer 3 — Feature Extraction (`features.py`)

Derives a feature vector for every instrument and cross-asset signals.

**Per-instrument features:**

| Feature | Range | Description |
|---------|-------|-------------|
| `trend_score` | -3 to +3 | EMA alignment score |
| `momentum` | -1 to +1 | RSI + MACD combined |
| `vw_momentum` | -2 to +2 | Volume-weighted momentum |
| `vol_regime` | LOW/NORMAL/HIGH | ATR-based volatility classification |
| `ema50_dev_%` | % | Distance from EMA50 (mean reversion signal) |
| `composite` | -100 to +100 | Weighted feature score |

**Cross-asset signals:**

| Signal | Description |
|--------|-------------|
| `vix` | Current VIX level |
| `dxy` | US Dollar Index |
| `spx_chg_%` | S&P 500 daily change |
| `gold_chg_%` | Gold daily change |
| `btc_chg_%` | Bitcoin daily change |
| `cross_asset_bias` | `RISK-ON` / `RISK-OFF` / `NEUTRAL` |

---

### Layer 4 — Regime Detection (`regime.py`)

5-dimensional regime classification used by all downstream AI agents.

| Dimension | Possible Values |
|-----------|----------------|
| Trend | `STRONG-UPTREND` / `UPTREND` / `RANGING` / `DOWNTREND` / `STRONG-DOWNTREND` |
| Volatility | `COMPRESSED` / `NORMAL` / `VOLATILE` / `ELEVATED` / `CRISIS` |
| Liquidity | `HIGH-LIQUIDITY` / `NORMAL` / `LOW-LIQUIDITY` |
| Macro | `RISK-ON` / `MIXED` / `RISK-OFF` |
| Momentum | `STRONG-BULLISH` / `BULLISH` / `NEUTRAL` / `BEARISH` / `STRONG-BEARISH` |

**Composite Regimes:**

| Regime | Condition | Strategy |
|--------|-----------|----------|
| `BULL-MARKET` | 3+ bull signals | Trend-following longs, increase size, reduce cash |
| `BEAR-MARKET` | 3+ bear signals | Defensive, shorts on weak names, raise cash |
| `CRISIS-MODE` | VIX > 30 | Capital preservation, max cash, safe havens only |
| `CONSOLIDATION` | Ranging trend | Fade extremes, tight stops, reduce size |
| `TRANSITIONAL` | Mixed signals | Wait for confirmation, small positions |

---

### Layers 5–11 — Multi-Agent AI Pipeline (`ai_analyst.py`)

9 sequential LLM calls to NVIDIA LLaMA 3.3-70B. Each agent receives the regime context and all previous agent outputs.

| Layer | Agent | Input | Output |
|-------|-------|-------|--------|
| 5 | Fundamental | Stocks + regime | Top/weak stocks, macro bias |
| 5 | Technical | Price data + features + regime | Bullish/bearish setups with strength |
| 5 | Sentiment | Scores + microstructure + regime | Fear/Greed index, momentum leaders |
| 5 | News | Headlines + regime | Themes, catalysts, key risks |
| 6 | Debate | All 4 agents + regime | Winner, conviction, regime_alignment |
| 7 | Trader | Debate + technicals + regime | Trade ideas with regime_fit per trade |
| 7 | Risk Manager | Trades + regime + VIX | Approved/rejected, Kelly fraction, heat |
| 8 | Portfolio Manager | Approved trades + Kelly | Allocations with Kelly-adjusted %, sector weights |
| 9 | Execution Strategist | Portfolio + microstructure | Order type, timing, slippage risk |
| 10 | Reflector | Full pipeline output | Blind spots, disagreements, scenario risks |
| 11 | Final CIO | Everything | Final trades, adaptation plan, executive summary |

---

## Rule-Based Analysis Engine (`analyst.py`)

Scores every stock and crypto on a **0–100 composite** across 4 weighted dimensions. Runs before the AI pipeline and feeds into the Sentiment Agent.

| Dimension | Weight (Stocks) | Weight (Crypto) |
|-----------|:-:|:-:|
| Technical | 35% | 40% |
| Momentum | 25% | 35% |
| Fundamental | 20% | — |
| News Sentiment | 20% | 25% |

### Verdict Scale

| Score | Verdict |
|-------|---------|
| 80–100 | `** STRONG BUY **` |
| 62–80 | `>> BUY` |
| 42–62 | `-- HOLD` |
| 25–42 | `<< SELL` |
| 0–25 | `!! STRONG SELL` |

---

## Real-Time Trading Signals (`signals.py`)

ATR-based trade setups generated independently of the AI pipeline.

| Field | Description |
|-------|-------------|
| `action` | BUY NOW / BUY / HOLD / SELL / SELL NOW / WAIT |
| `confidence` | 1–5 stars based on signal alignment |
| `entry` | Current price at signal time |
| `stop_loss` | ATR × 2.0 below entry (or 5% max) |
| `target1` | ATR × 2.0 above entry (1:1 R/R) |
| `target2` | ATR × 4.0 above entry (1:2 R/R) |
| `rr2` | Risk/reward ratio to target 2 |

---

## Data Fields

### Stocks (46 fields)

| Category | Fields |
|----------|--------|
| Price | `price`, `open`, `high`, `low`, `change_%`, `change_abs`, `change_from_open_%` |
| Volume | `volume`, `volume_change_%`, `relative_volume`, `avg_vol_10d`, `avg_vol_30d` |
| Market | `market_cap`, `pe_ratio`, `eps`, `dividend_yield_%`, `sector`, `industry` |
| Technicals | `rsi`, `rsi_prev`, `macd`, `macd_signal`, `vwap`, `atr`, `beta` |
| Moving Avgs | `ema20`, `ema50`, `ema200`, `sma20`, `sma50`, `sma200` |
| Bands | `bb_upper`, `bb_lower` |
| 52-Week | `52w_high`, `52w_low`, `price_52w_high`, `price_52w_low` |
| Extended | `gap_%`, `pre_market_change_%`, `after_hours_change_%`, `exchange` |

### Crypto / Forex / Commodities / Indices (36 fields)

Same as above minus: `market_cap`, `pe_ratio`, `eps`, `dividend_yield_%`, `sector`, `industry`, `beta`, `gap_%`, `pre_market_change_%`, `after_hours_change_%`.

---

## Output Files

Every run generates:

- `output.json` — complete pipeline output (all 11 layers)
- `stocks_<timestamp>.csv`
- `crypto_<timestamp>.csv`
- `forex_<timestamp>.csv`
- `commodities_<timestamp>.csv`
- `indices_<timestamp>.csv`
- `news_<timestamp>.csv`

### JSON Structure

```json
{
  "fetched_at": "2026-05-19T13:17:11Z",
  "stocks":         [...],
  "crypto":         [...],
  "forex":          [...],
  "commodities":    [...],
  "indices":        [...],
  "news":           [...],
  "microstructure": {
    "stocks": [{ "symbol": "AAPL", "liquidity_score": 74, "flow_bias": "BUYING", ... }],
    "crypto": [...], "forex": [...], "commodities": [...], "indices": [...]
  },
  "features": {
    "stocks": [{ "symbol": "AAPL", "trend_score": 3, "momentum": 0.4, "composite": 62, ... }],
    "crypto": [...],
    "cross_asset": { "vix": 17.9, "dxy": 99.1, "cross_asset_bias": "RISK-ON", ... }
  },
  "regime": {
    "composite_regime":  "BULL-MARKET",
    "trend_regime":      "UPTREND",
    "volatility_regime": "NORMAL",
    "liquidity_regime":  "HIGH-LIQUIDITY",
    "macro_regime":      "RISK-ON",
    "momentum_regime":   "BULLISH",
    "recommended_strategy": "Trend-following longs. Increase position sizes. Reduce cash.",
    "vix": 17.9,
    "dxy": 99.1
  },
  "insights":  { "macro_regime": "RISK-ON", "market_movers": [...], ... },
  "analysis":  { "stocks": [...], "crypto": [...] },
  "signals":   { "stocks": [...], "crypto": [...] },
  "ai_analysis": {
    "agents": {
      "fundamental": { "macro_fundamental_bias": "BULLISH", "top_fundamental_stocks": [...] },
      "technical":   { "macro_technical_bias": "BULLISH", "bullish_setups": [...] },
      "sentiment":   { "fear_greed_index": 62, "fear_greed_label": "GREED", ... },
      "news":        { "dominant_themes": [...], "macro_catalysts": [...] }
    },
    "debate": {
      "debate_winner": "BULL", "conviction": "HIGH",
      "regime_alignment": "CONFIRMS_BULL",
      "bull_case": { "arguments": [...], "top_long_candidates": ["XOM", "NVDA"] },
      "bear_case": { "arguments": [...], "top_short_candidates": ["ADAUSDT"] }
    },
    "trader": {
      "trade_ideas": [{ "symbol": "XOM", "direction": "LONG", "regime_fit": "HIGH", ... }],
      "best_trade": "XOM", "trader_bias": "CAUTIOUS-LONG"
    },
    "risk": {
      "approved_trades": ["XOM", "NVDA"],
      "portfolio_heat": "MEDIUM",
      "max_position_size_%": 10,
      "kelly_fraction": 0.15,
      "tail_risks": ["inflation spike", "Fed hawkish surprise"]
    },
    "portfolio": {
      "allocations": [{ "symbol": "XOM", "allocation_%": 15, "kelly_adjusted_%": 12, "priority": "CORE" }],
      "cash_reserve_%": 25,
      "sector_weights": { "energy": 30, "tech": 25, "finance": 15, "other": 5 }
    },
    "execution": {
      "execution_plan": [{ "symbol": "XOM", "order_type": "LIMIT", "entry_timing": "WAIT_PULLBACK", "urgency": "MEDIUM", "slippage_risk": "LOW" }],
      "overall_execution_strategy": "..."
    },
    "reflection": {
      "pipeline_consistency": "HIGH",
      "blind_spots": ["..."],
      "scenario_risks": [{ "scenario": "Fed hikes", "impact": "HIGH", "hedge": "reduce tech" }],
      "adaptation_signals": ["watch CPI print", "monitor VIX above 20"]
    },
    "final": {
      "overall_market_bias": "BULL",
      "final_trades": [{ "symbol": "XOM", "action": "BUY", "order_type": "LIMIT", ... }],
      "top_opportunity": "XOM — energy strength + regime tailwind + high liquidity",
      "biggest_risk": "Fed hawkish pivot compresses valuations",
      "adaptation_plan": "Reduce longs if VIX breaks above 20 or SPX loses 50-day EMA",
      "executive_summary": "..."
    }
  },
  "summary": {
    "total_instruments": 50,
    "total_news": 80,
    "composite_regime": "BULL-MARKET",
    "trend_regime": "UPTREND",
    "volatility_regime": "NORMAL",
    "macro_regime": "RISK-ON"
  }
}
```

---

## Customizing Symbols

Edit the symbol lists in `scanner.py`:

```python
STOCK_SYMBOLS = [
    "NASDAQ:AAPL", "NASDAQ:MSFT", "NYSE:XOM",
]
CRYPTO_SYMBOLS = [
    "BINANCE:BTCUSDT", "BINANCE:ETHUSDT",
]
FOREX_SYMBOLS = [
    "FX:EURUSD", "FX:GBPUSD",
]
COMMODITY_SYMBOLS = [
    "TVC:GOLD", "TVC:USOIL",
]
INDEX_SYMBOLS = [
    "TVC:SPX", "TVC:VIX", "TVC:DXY",
]
```

Format: `EXCHANGE:TICKER` — e.g. `NASDAQ:AAPL`, `BINANCE:BTCUSDT`, `FX:EURUSD`, `TVC:GOLD`.

---

## Performance

| Optimization | Detail |
|-------------|--------|
| Concurrent fetches | All 6 data sources run simultaneously via `asyncio.gather` |
| Split column sets | Stocks use 46-field payload; others use 36-field payload |
| Resource blocking | Playwright blocks images, media, fonts, stylesheets |
| Chromium flags | `--disable-gpu`, `--disable-extensions`, `--blink-settings=imagesEnabled=false` |
| Single HTTP client | One shared `httpx.AsyncClient` for all scanner API calls |
| AI token efficiency | Each agent receives only the fields it needs — no full data dumps |
| Regime-aware agents | All AI agents receive regime context, reducing hallucination and improving relevance |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `playwright` | Headless Chromium for JS-rendered news page |
| `beautifulsoup4` | HTML parsing for news articles |
| `httpx` | Async HTTP client for TradingView scanner API |
| `openai` | NVIDIA API client (OpenAI-compatible) |

---

## Notes

- The AI pipeline makes **9 sequential LLM calls** per run. Expect ~45–90 seconds for the AI section depending on API latency.
- Every AI agent receives the detected **market regime** as context — this prevents agents from making recommendations that contradict the current market environment.
- The **Reflection Agent** (Layer 10) reviews the entire pipeline output for inconsistencies and blind spots before the CIO makes the final decision.
- The **Adaptation Plan** in the final output tells you exactly what to monitor and what conditions would cause the thesis to change.
- The **Kelly fraction** from the Risk Manager feeds directly into the Portfolio Manager's position sizing — allocations are Kelly-adjusted, not arbitrary.
- The **Execution Agent** uses microstructure data (liquidity, VWAP deviation, spread) to recommend order types and timing — not just "buy at market".
- TradingView CSS class names for the news page may change. If news stops parsing, inspect the live page with DevTools and update selectors in `news.py`.
- The scanner API requires no authentication for public market data.
- This is not financial advice. Always do your own research.
- Intended for personal/educational use. Review [TradingView's Terms of Service](https://www.tradingview.com/policies/) before any commercial use.
