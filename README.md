# TradingView Financial Scraper + Multi-Agent AI Investment System

A real-time financial data scraper and **multi-agent AI investment engine** built with **Playwright**, **BeautifulSoup**, **httpx**, and **NVIDIA LLaMA 3.3-70B**. Pulls live market data across stocks, crypto, forex, commodities, and indices — then runs it through a 6-layer AI agent pipeline to produce a final, institutional-grade trade decision.

---

## How It Works

| Data | Source | Method |
|------|--------|--------|
| Stocks | `scanner.tradingview.com/america/scan` | `httpx` async POST |
| Crypto | `scanner.tradingview.com/crypto/scan` | `httpx` async POST |
| Forex | `scanner.tradingview.com/forex/scan` | `httpx` async POST |
| Commodities | `scanner.tradingview.com/global/scan` | `httpx` async POST |
| Indices | `scanner.tradingview.com/global/scan` | `httpx` async POST |
| News | `tradingview.com/news/` | Playwright + BeautifulSoup |
| Rule-Based Analysis | `analyst.py` | Python scoring engine (0–100) |
| Trading Signals | `signals.py` | ATR-based entry/stop/target |
| AI Pipeline | `ai_analyst.py` | NVIDIA LLaMA 3.3-70B (6 agents) |

All 6 data fetches run **concurrently** via `asyncio.gather`. After fetching, the full AI pipeline runs sequentially — each agent receives the previous agent's output as context.

---

## Project Structure

```
Fin-scrapper-/
├── scraper.py        # Orchestrator — runs everything end to end
├── scanner.py        # TradingView scanner API client
├── news.py           # Playwright + BeautifulSoup news scraper
├── analyst.py        # Rule-based scoring engine (0–100 composite)
├── signals.py        # ATR-based entry / stop-loss / take-profit generator
├── insights.py       # Event detection + macro regime classifier
├── ai_analyst.py     # Multi-agent AI pipeline (NVIDIA LLaMA 3.3-70B)
├── export.py         # Console output + JSON/CSV export
├── requirements.txt  # Python dependencies
├── output.json       # Generated on each run (gitignored)
└── README.md
```

---

## Requirements

- Python 3.10+
- Internet connection
- NVIDIA API key (included in `ai_analyst.py`)

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

## Multi-Agent AI Pipeline

The core of the system. After all market data is fetched and rule-based analysis is complete, `ai_analyst.py` runs a **6-layer sequential agent pipeline** powered by NVIDIA's LLaMA 3.3-70B via the OpenAI-compatible API.

```
Market Data  +  Rule-Based Scores  +  News
        |
        v
+-----------------------------------------------+
|  LAYER 1 — Analyst Agents (4 independent)     |
|                                               |
|  [Fundamental Agent]   P/E, EPS, market cap,  |
|                        beta, dividend yield   |
|                                               |
|  [Technical Agent]     RSI, MACD, EMA align,  |
|                        VWAP, BB, ATR          |
|                                               |
|  [Sentiment Agent]     Fear/Greed index,      |
|                        momentum leaders,      |
|                        volume patterns        |
|                                               |
|  [News Agent]          Dominant themes,       |
|                        macro catalysts,       |
|                        geopolitical risks     |
+-----------------------------------------------+
        |
        v
+-----------------------------------------------+
|  LAYER 2 — Bull vs Bear Debate                |
|                                               |
|  Bull case arguments vs Bear case arguments   |
|  Debate winner + conviction + market regime   |
+-----------------------------------------------+
        |
        v
+-----------------------------------------------+
|  LAYER 3 — Trader Agent                       |
|                                               |
|  Generates specific trade ideas:              |
|  entry zone, stop loss, target 1 & 2,         |
|  timeframe, rationale                         |
+-----------------------------------------------+
        |
        v
+-----------------------------------------------+
|  LAYER 4 — Risk Manager                       |
|                                               |
|  Approves / rejects trades, sets max          |
|  position size, identifies tail risks,        |
|  flags portfolio heat level                   |
+-----------------------------------------------+
        |
        v
+-----------------------------------------------+
|  LAYER 5 — Portfolio Manager                  |
|                                               |
|  Builds final allocation: symbol, direction,  |
|  allocation %, priority (CORE/TACTICAL/SPEC)  |
|  cash reserve, rebalance trigger              |
+-----------------------------------------------+
        |
        v
+-----------------------------------------------+
|  LAYER 6 — Final Trade Decision (CIO)         |
|                                               |
|  Overall market bias, final trades with       |
|  full rationale, top opportunity, biggest     |
|  risk, do-not-touch list, executive summary   |
+-----------------------------------------------+
```

### Agent Roles

| Agent | Role | Output |
|-------|------|--------|
| Fundamental | Evaluates P/E, EPS, market cap, beta, dividends | Top/weak fundamental stocks, macro bias |
| Technical | Evaluates RSI, MACD, EMA, VWAP, Bollinger Bands | Bullish/bearish setups with strength rating |
| Sentiment | Evaluates momentum, volume, composite scores | Fear/Greed index, momentum leaders/laggards |
| News | Identifies themes, catalysts, geopolitical risks | Dominant themes, macro catalysts, key risks |
| Bull/Bear Debate | Moderates bull vs bear argument | Winner, conviction level, market regime |
| Trader | Generates trade setups from debate + technicals | Entry, stop, target, timeframe per symbol |
| Risk Manager | Stress-tests trades, sets position sizing | Approved/rejected trades, tail risks, heat |
| Portfolio Manager | Builds optimal allocation from approved trades | Allocations %, cash reserve, rebalance trigger |
| Final Decision (CIO) | Synthesizes all agents into one verdict | Final trades, top opportunity, exec summary |

---

## Rule-Based Analysis Engine

`analyst.py` scores every stock and crypto on a **0–100 composite** across 4 weighted dimensions before the AI pipeline runs. The AI uses these scores as additional context.

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

## Real-Time Trading Signals

`signals.py` generates ATR-based trade setups independently of the AI pipeline:

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

### News Fields

| Field | Description |
|-------|-------------|
| `title` | Article headline |
| `link` | Full URL |
| `published` | ISO timestamp |
| `source` | Publisher name |
| `sentiment` | `bullish` / `bearish` / `neutral` |
| `categories` | `crypto`, `stocks`, `forex`, `commodities`, `macro`, `tech`, `general` |

---

## Output Files

Every run generates:

- `output.json` — all data + rule-based analysis + signals + full AI pipeline output
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
  "stocks":      [ { "symbol": "AAPL", "price": 297.84, "rsi": 71.4, ... } ],
  "crypto":      [ { "symbol": "BTCUSDT", "price": 77239.14, ... } ],
  "forex":       [ { "symbol": "EURUSD", "price": 1.1635, ... } ],
  "commodities": [ { "symbol": "GOLD", "price": 4549.97, ... } ],
  "indices":     [ { "symbol": "DJI", "price": 49690.96, ... } ],
  "news":        [ { "title": "...", "sentiment": "bullish", ... } ],
  "insights":    { "macro_regime": "RISK-ON", "market_movers": [...], ... },
  "analysis": {
    "stocks": [ { "symbol": "XOM", "composite": 76.9, "verdict": ">> BUY", ... } ],
    "crypto": [ { "symbol": "NEARUSDT", "composite": 67.4, ... } ]
  },
  "signals": {
    "stocks": [ { "symbol": "CVX", "action": "BUY NOW", "entry": 196.12, ... } ],
    "crypto": [ ... ]
  },
  "ai_analysis": {
    "agents": {
      "fundamental": { "macro_fundamental_bias": "BULLISH", "top_fundamental_stocks": [...] },
      "technical":   { "macro_technical_bias": "BULLISH", "bullish_setups": [...] },
      "sentiment":   { "fear_greed_index": 62, "fear_greed_label": "GREED", ... },
      "news":        { "dominant_themes": [...], "macro_catalysts": [...] }
    },
    "debate": {
      "debate_winner": "BULL",
      "conviction": "MEDIUM",
      "market_regime": "TRENDING-UP",
      "bull_case": { "arguments": [...], "top_long_candidates": ["XOM", "NVDA"] },
      "bear_case": { "arguments": [...], "top_short_candidates": ["ADAUSDT"] }
    },
    "trader": {
      "trade_ideas": [ { "symbol": "XOM", "direction": "LONG", "entry_zone": "160", ... } ],
      "best_trade": "XOM",
      "trader_bias": "CAUTIOUS-LONG"
    },
    "risk": {
      "approved_trades": ["XOM", "NVDA", "NEARUSDT"],
      "portfolio_heat": "MEDIUM",
      "max_position_size_%": 10,
      "tail_risks": ["inflation spike", "Fed hawkish surprise"]
    },
    "portfolio": {
      "allocations": [ { "symbol": "XOM", "direction": "LONG", "allocation_%": 15, "priority": "CORE" } ],
      "cash_reserve_%": 25,
      "portfolio_bias": "BULLISH"
    },
    "final": {
      "overall_market_bias": "BULL",
      "final_trades": [ { "symbol": "XOM", "action": "BUY", "conviction": "HIGH", ... } ],
      "top_opportunity": "XOM — energy sector strength with strong technicals and positive EPS",
      "biggest_risk": "Fed hawkish pivot could compress valuations across all sectors",
      "executive_summary": "..."
    }
  },
  "summary": {
    "total_instruments": 50,
    "total_news": 80,
    "bullish_news": 22,
    "bearish_news": 8,
    "buy_signals": 17,
    "sell_signals": 14,
    "macro_regime": "RISK-ON"
  }
}
```

---

## Customizing Symbols

Edit the symbol lists at the top of `scanner.py`:

```python
STOCK_SYMBOLS = [
    "NASDAQ:AAPL", "NASDAQ:MSFT", "NYSE:TSLA",
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
    "TVC:SPX", "TVC:NDX",
]
```

Format is always `EXCHANGE:TICKER` — e.g. `NASDAQ:AAPL`, `BINANCE:BTCUSDT`, `FX:EURUSD`, `TVC:GOLD`.

---

## Performance

| Optimization | Detail |
|-------------|--------|
| Concurrent fetches | All 6 data sources run simultaneously via `asyncio.gather` |
| Split column sets | Stocks use 46-field payload; others use 36-field common payload |
| Resource blocking | Playwright blocks images, media, fonts, stylesheets |
| Chromium flags | `--disable-gpu`, `--disable-extensions`, `--blink-settings=imagesEnabled=false` |
| Single HTTP client | One shared `httpx.AsyncClient` for all scanner API calls |
| AI token efficiency | Each agent receives only the fields it needs — no full data dumps |

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

- The AI pipeline makes **6 sequential LLM calls** per run. Expect ~30–60 seconds for the AI section depending on API latency.
- Each agent is stateless and focused — the Fundamental Agent never sees news, the News Agent never sees price data. This prevents cross-contamination and keeps each agent's reasoning clean.
- The Bull/Bear Debate is the pivot point of the pipeline — it synthesizes all 4 analyst views before any trade ideas are generated.
- The Risk Manager can reject trades proposed by the Trader. The Portfolio Manager only allocates to approved trades.
- TradingView CSS class names for the news page may change. If news stops parsing, inspect the live page with DevTools and update selectors in `news.py`.
- The scanner API requires no authentication for public market data.
- This is not financial advice. Always do your own research.
- Intended for personal/educational use. Review [TradingView's Terms of Service](https://www.tradingview.com/policies/) before any commercial use.
