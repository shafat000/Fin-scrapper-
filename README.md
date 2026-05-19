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
│  OFI formula, Microprice model, Queue position modeling,    │
│  Spread modeling, Adverse selection, Fill probability       │
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
│  Hidden Markov Model (4 states), Bayesian Switching,        │
│  5-dimensional scoring → BULL-MARKET | BEAR-MARKET |        │
│  CRISIS-MODE | CONSOLIDATION | TRANSITIONAL                 │
+─────────────────────────────────────────────────────────────+
                            |
                            v
+─────────────────────────────────────────────────────────────+
│  LAYER 5 — Stochastic Mathematics                           │
│  GBM price simulation, Ornstein-Uhlenbeck mean reversion,   │
│  Heston stochastic volatility, Monte Carlo (1000 paths),    │
│  Black-Scholes options pricing + full Greeks                │
+─────────────────────────────────────────────────────────────+
                            |
                            v
+─────────────────────────────────────────────────────────────+
│  LAYER 6 — Portfolio Optimization                           │
│  Markowitz mean-variance, Risk Parity, Hierarchical Risk    │
│  Parity (HRP), Kelly Criterion, consensus weights           │
+─────────────────────────────────────────────────────────────+
                            |
                            v
+─────────────────────────────────────────────────────────────+
│  LAYER 7 — Specialized AI Agents (4 independent)           │
│  [Fundamental] P/E, EPS, market cap, beta, dividends        │
│  [Technical]   RSI, MACD, EMA, VWAP, BB, ATR + regime       │
│  [Sentiment]   Fear/Greed, OFI, microprice, volume          │
│  [News]        Themes, macro catalysts, geopolitical risks  │
│  + Memory context injected from past episodes               │
+─────────────────────────────────────────────────────────────+
                            |
                            v
+─────────────────────────────────────────────────────────────+
│  LAYER 8 — Debate & Coordination                            │
│  Bull case vs Bear case — regime-aligned                    │
│  Winner + conviction + regime_alignment field               │
+─────────────────────────────────────────────────────────────+
                            |
                            v
+─────────────────────────────────────────────────────────────+
│  LAYER 9 — Risk Optimization                                │
│  Trader: entry/stop/target + regime_fit per trade           │
│  Risk Manager: approve/reject, Kelly fraction,              │
│  portfolio heat, tail risks                                 │
+─────────────────────────────────────────────────────────────+
                            |
                            v
+─────────────────────────────────────────────────────────────+
│  LAYER 10 — Execution Optimization                          │
│  Order type (MARKET/LIMIT/TWAP/VWAP), entry timing,         │
│  urgency, slippage risk, fill probability per position      │
+─────────────────────────────────────────────────────────────+
                            |
                            v
+─────────────────────────────────────────────────────────────+
│  LAYER 11 — Learning & Reflection + Continuous Adaptation   │
│  Pipeline consistency, blind spots, scenario risks,         │
│  episodic/semantic/strategic memory, adaptation plan,       │
│  Final CIO decision + executive summary                     │
+─────────────────────────────────────────────────────────────+
```

---

## Project Structure

```
Fin-scrapper-/
├── scraper.py              # Orchestrator — runs all 11 layers end to end
├── scanner.py              # TradingView scanner API client
├── news.py                 # Playwright + BeautifulSoup news scraper
├── microstructure.py       # Layer 2 — OFI, microprice, queue model, spread
├── features.py             # Layer 3 — feature vectors + cross-asset signals
├── regime.py               # Layer 4 — HMM + Bayesian regime detection
├── stochastic.py           # Layer 5 — GBM, OU, Heston, Monte Carlo, B-S
├── portfolio_optimizer.py  # Layer 6 — Markowitz, Risk Parity, HRP, Kelly
├── analyst.py              # Rule-based scoring engine (0–100 composite)
├── signals.py              # ATR-based entry / stop-loss / take-profit
├── insights.py             # Event detection + macro regime classifier
├── ai_analyst.py           # Layers 7–11 — full multi-agent AI pipeline
├── memory.py               # AI memory system (episodic/semantic/strategic)
├── export.py               # Console output + JSON/CSV export
├── requirements.txt        # Python dependencies
├── memory.json             # Persistent AI memory (auto-generated)
├── output.json             # Generated on each run (gitignored)
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

### Layer 2 — Elite Microstructure Engine (`microstructure.py`)

Retail traders analyze candles. This engine analyzes what elite firms analyze.

**Order Flow Imbalance (OFI)**
```
OFI_t = Σ q_bid - Σ q_ask
```
Approximated from intraday price position and volume split. Normalized to -1 (full selling) to +1 (full buying).

**Microprice Model**
```
P_micro = (P_ask * V_bid + P_bid * V_ask) / (V_bid + V_ask)
```
Predicts short-term fair value using bid/ask volume imbalance. Signals BULLISH when microprice > mid.

**Queue Position Modeling**
Estimates fill probability, expected slippage, adverse selection cost, and market impact for every instrument. Used in HFT for limit order placement decisions.

**Spread Modeling**
Effective spread, Roll's spread estimator, and spread regime (TIGHT / NORMAL / WIDE / VERY-WIDE).

| Metric | Description |
|--------|-------------|
| `ofi_normalized` | -1 to +1 order flow imbalance |
| `flow_bias` | STRONG-BUYING / BUYING / NEUTRAL / SELLING / STRONG-SELLING |
| `microprice` | Volume-weighted fair value estimate |
| `microprice_signal` | BULLISH / BEARISH / NEUTRAL |
| `fill_probability_%` | Probability a limit order gets filled |
| `expected_slippage_%` | Expected execution slippage |
| `adverse_selection` | Probability market moves against you after fill |
| `market_impact_%` | Estimated market impact of order |
| `recommended_order` | LIMIT / TWAP / VWAP based on liquidity |
| `effective_spread_%` | Effective bid/ask spread proxy |
| `spread_regime` | TIGHT / NORMAL / WIDE / VERY-WIDE |

---

### Layer 3 — Feature Extraction (`features.py`)

| Feature | Range | Description |
|---------|-------|-------------|
| `trend_score` | -3 to +3 | EMA alignment score |
| `momentum` | -1 to +1 | RSI + MACD combined |
| `vw_momentum` | -2 to +2 | Volume-weighted momentum |
| `vol_regime` | LOW/NORMAL/HIGH | ATR-based volatility |
| `ema50_dev_%` | % | Distance from EMA50 |
| `composite` | -100 to +100 | Weighted feature score |

**Cross-asset signals:** VIX, DXY, SPX change, Gold change, BTC change → `cross_asset_bias`

---

### Layer 4 — Advanced Regime Detection (`regime.py`)

**Hidden Markov Model (4 states)**

| State | Characteristics |
|-------|----------------|
| TRENDING | Strong directional move, high momentum |
| MEAN-REVERTING | Price oscillates around equilibrium |
| HIGH-VOLATILITY | Elevated ATR, wide spreads, uncertain direction |
| PANIC | VIX > 30, extreme selling, liquidity collapse |

**Bayesian Regime Switching**
Computes posterior probabilities over Bull / Bear / High-Vol / Panic states using market signals as likelihood functions.

**5-Dimensional Composite Regime**

| Regime | Strategy |
|--------|----------|
| `BULL-MARKET` | Trend-following longs, increase size, reduce cash |
| `BEAR-MARKET` | Defensive, shorts on weak names, raise cash |
| `CRISIS-MODE` | Capital preservation, max cash, safe havens only |
| `CONSOLIDATION` | Fade extremes, tight stops, reduce size |
| `TRANSITIONAL` | Wait for confirmation, small positions |

---

### Layer 5 — Stochastic Mathematics (`stochastic.py`)

**Geometric Brownian Motion**
```
dS_t = μS_t dt + σS_t dW_t
S_{t+1} = S_t * exp((μ - σ²/2)Δt + σ√Δt * Z_t)
```
Simulates 500 price paths over 21 days. Outputs mean, P5/P95 range, VaR 95%, probability of profit.

**Ornstein-Uhlenbeck (Mean Reversion)**
```
dX_t = θ(μ - X_t)dt + σdW_t
```
Detects mean-reverting instruments. Computes z-score vs EMA50 and half-life of reversion.

**Heston Stochastic Volatility**
```
dv_t = κ(θ - v_t)dt + ξ√v_t dW_t^v
```
Dynamic volatility modeling. Estimates ATM implied vol, vol skew, and checks Feller condition.

**Monte Carlo Simulation (1000 paths)**
Full risk estimation: VaR 95%, VaR 99%, CVaR 95%, best/worst case, expected return.

**Black-Scholes Options Pricing + Greeks**
```
C = S₀N(d₁) - Ke^(-rT)N(d₂)
```
ATM call and put pricing with full Greeks: Delta, Gamma, Vega, Theta, Rho.

---

### Layer 6 — Portfolio Optimization (`portfolio_optimizer.py`)

**Markowitz Mean-Variance**
```
min w'Σw - λμ'w   subject to Σw = 1, w ≥ 0
```
Gradient descent optimization. Outputs expected return, portfolio volatility, Sharpe ratio.

**Risk Parity**
Equal risk contribution: each position contributes equally to total portfolio risk. Uses inverse-volatility weighting.

**Hierarchical Risk Parity (HRP)**
Clusters instruments by sector, applies risk parity within clusters, equal weight across clusters. Reduces concentration risk.

**Kelly Criterion**
```
f* = (p*b - q) / b
```
Maps composite score to win probability. Outputs full Kelly, half-Kelly (recommended), quarter-Kelly.

---

### Layer 7 — Specialized AI Agents (`ai_analyst.py`)

4 independent LLM agents, each receiving regime context + memory context from past episodes.

| Agent | Inputs | Outputs |
|-------|--------|---------|
| Fundamental | Stocks + regime | Top/weak stocks, macro bias |
| Technical | Price + features + regime | Bullish/bearish setups with strength |
| Sentiment | Scores + microstructure + OFI + regime | Fear/Greed, momentum leaders |
| News | Headlines + regime | Themes, catalysts, key risks |

---

### Layer 8 — Debate & Coordination

Bull case vs Bear case constructed from all 4 agent outputs. Regime alignment field added — `CONFIRMS_BULL`, `CONFIRMS_BEAR`, or `MIXED`.

---

### Layer 9 — Risk Optimization

**Trader Agent:** Generates trade ideas with `regime_fit` (HIGH/MEDIUM/LOW) per trade.

**Risk Manager:** Approves/rejects trades, sets Kelly fraction, portfolio heat, identifies tail risks.

---

### Layer 10 — Execution Optimization

Uses microstructure data (fill probability, slippage, spread regime, OFI) to recommend:
- Order type: MARKET / LIMIT / TWAP / VWAP
- Entry timing: NOW / WAIT_PULLBACK / WAIT_BREAKOUT / SCALE_IN
- Urgency and slippage risk per position

---

### Layer 11 — Learning & Reflection + Continuous Adaptation

**Reflection Agent:** Reviews entire pipeline for inconsistencies, blind spots, scenario risks.

**Memory System (`memory.py`):**

| Memory Type | Description |
|-------------|-------------|
| Episodic | Stores past market setups, regime, VIX, bias, outcome |
| Semantic | Stores regime-specific market patterns |
| Strategic | Tracks win/loss rate per strategy per regime |
| Reflections | Stores pipeline self-assessments for learning |

On every run, the system recalls similar past episodes and injects them into AI agents as context:
> *"Last time BULL-MARKET regime appeared with VIX at 18: strategy succeeded with energy longs, tech underperformed due to rate concerns."*

**Final CIO Decision:** Synthesizes all 10 layers into final trades with order type, adaptation plan, and executive summary.

---

## Rule-Based Analysis Engine (`analyst.py`)

| Dimension | Weight (Stocks) | Weight (Crypto) |
|-----------|:-:|:-:|
| Technical | 35% | 40% |
| Momentum | 25% | 35% |
| Fundamental | 20% | — |
| News Sentiment | 20% | 25% |

| Score | Verdict |
|-------|---------|
| 80–100 | `** STRONG BUY **` |
| 62–80 | `>> BUY` |
| 42–62 | `-- HOLD` |
| 25–42 | `<< SELL` |
| 0–25 | `!! STRONG SELL` |

---

## Real-Time Trading Signals (`signals.py`)

| Field | Description |
|-------|-------------|
| `action` | BUY NOW / BUY / HOLD / SELL / SELL NOW / WAIT |
| `confidence` | 1–5 stars |
| `entry` | Current price |
| `stop_loss` | ATR × 2.0 below entry (5% max) |
| `target1` | ATR × 2.0 above entry (1:1 R/R) |
| `target2` | ATR × 4.0 above entry (1:2 R/R) |

---

## Output Files

Every run generates:
- `output.json` — complete pipeline output (all 11 layers)
- `memory.json` — persistent AI memory (grows over time)
- `stocks_<timestamp>.csv`, `crypto_<timestamp>.csv`, `forex_<timestamp>.csv`
- `commodities_<timestamp>.csv`, `indices_<timestamp>.csv`, `news_<timestamp>.csv`

---

## Customizing Symbols

Edit symbol lists in `scanner.py`:

```python
STOCK_SYMBOLS    = ["NASDAQ:AAPL", "NASDAQ:NVDA", "NYSE:XOM"]
CRYPTO_SYMBOLS   = ["BINANCE:BTCUSDT", "BINANCE:ETHUSDT"]
FOREX_SYMBOLS    = ["FX:EURUSD", "FX:GBPUSD"]
COMMODITY_SYMBOLS = ["TVC:GOLD", "TVC:USOIL"]
INDEX_SYMBOLS    = ["TVC:SPX", "TVC:VIX", "TVC:DXY"]
```

---

## Performance

| Optimization | Detail |
|-------------|--------|
| Concurrent fetches | All 6 data sources via `asyncio.gather` |
| Split column sets | Stocks 46-field, others 36-field |
| Resource blocking | Playwright blocks images, media, fonts |
| Single HTTP client | One shared `httpx.AsyncClient` |
| AI token efficiency | Each agent receives only needed fields |
| Regime-aware agents | All agents receive regime + memory context |
| No external ML deps | Stochastic math uses only stdlib `math` + `random` |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `playwright` | Headless Chromium for JS-rendered news |
| `beautifulsoup4` | HTML parsing for news articles |
| `httpx` | Async HTTP client for TradingView scanner API |
| `openai` | NVIDIA API client (OpenAI-compatible) |

---

## Notes

- The AI pipeline makes **9 sequential LLM calls** per run (~45–90 seconds for AI section).
- All stochastic math (GBM, OU, Heston, Monte Carlo, Black-Scholes) uses only Python stdlib — no numpy/scipy required.
- The memory system grows with every run. After 10+ runs, agents start receiving meaningful historical context.
- The HMM regime classifier uses 4 hidden states: Trending, Mean-Reverting, High-Volatility, Panic.
- The Bayesian switcher computes posterior probabilities over Bull/Bear/HighVol/Panic states.
- Kelly fraction from Risk Manager feeds into Portfolio Manager — allocations are Kelly-adjusted.
- Execution Agent uses microstructure (fill probability, slippage, OFI) to recommend order types.
- TradingView CSS selectors in `news.py` may change — update if news stops parsing.
- This is not financial advice. Always do your own research.
- Intended for personal/educational use. Review [TradingView's Terms of Service](https://www.tradingview.com/policies/) before commercial use.
