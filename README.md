# 📈 TradingView Financial Scraper + Investment Analyst

A high-performance, real-time financial data scraper **and investment analysis engine** built with **Playwright** and **BeautifulSoup** that pulls live **stocks**, **crypto**, **forex**, **commodities**, **indices**, and **market news** from [TradingView](https://www.tradingview.com) — then scores every instrument across 4 dimensions to tell you exactly what to buy, hold, or avoid.

---

## ⚡ How It Works

| Data | Source | Method |
|------|--------|--------|
| Stocks | `scanner.tradingview.com/america/scan` | `httpx` async POST |
| Crypto | `scanner.tradingview.com/crypto/scan` | `httpx` async POST |
| Forex | `scanner.tradingview.com/forex/scan` | `httpx` async POST |
| Commodities | `scanner.tradingview.com/global/scan` | `httpx` async POST |
| Indices | `scanner.tradingview.com/global/scan` | `httpx` async POST |
| News | `tradingview.com/news/` | Playwright + BeautifulSoup |
| Analysis | `analyst.py` | Pure Python scoring engine |
| Signals | `signals.py` | Real-time entry/stop/target generator |

- Market data is fetched from TradingView's **internal scanner API** — the same endpoint their UI uses — so prices are always real-time tick-level.
- News requires a headless browser because the page is JavaScript-rendered. Playwright scrolls the page to load more articles, then BeautifulSoup parses the HTML.
- All 6 fetches run **concurrently** via `asyncio.gather`.
- After fetching, the **analyst engine** scores every stock and crypto using all available data fields + news sentiment.
- The **signals engine** converts analyst verdicts into actionable trade setups with entry, stop-loss, and take-profit levels.

> **Scanner API note:** Stocks use the full column set (46 fields including fundamentals). Crypto, forex, commodities, and indices use a reduced common column set — this is required by TradingView's API which rejects stock-only fields on non-equity endpoints.

---

## 🗂 Project Structure

```
FIn scrapper/
├── scraper.py        # Orchestrator — runs everything, prints results, exports files
├── scanner.py        # TradingView scanner API — stocks, crypto, forex, commodities, indices
├── news.py           # Playwright + BeautifulSoup — news scraper with sentiment & categories
├── analyst.py        # Investment analysis engine — scores every instrument 0–100
├── signals.py        # Real-time trading signals — entry, stop-loss, take-profit levels
├── export.py         # Console tables, JSON export, per-category CSV export
├── requirements.txt  # Python dependencies
├── output.json       # Generated on each run (gitignored)
└── README.md
```

---

## 📦 Requirements

- Python 3.10+
- Internet connection

---

## 🔧 Installation

```bash
pip install -r requirements.txt
playwright install chromium
```

---

## 🚀 Usage

```bash
python scraper.py
```

---

## 🧠 Investment Analysis Engine

`analyst.py` scores every stock and crypto on a **0–100 composite score** across 4 weighted dimensions:

| Dimension | Weight (Stocks) | Weight (Crypto) | What It Measures |
|-----------|:-:|:-:|-----------------|
| Technical | 35% | 40% | RSI, MACD, EMA alignment, VWAP, Bollinger Bands, ATR |
| Momentum  | 25% | 35% | Daily change%, volume vs avg, relative volume, pre/after-hours, gap |
| Fundamental | 20% | — | P/E ratio, EPS, dividend yield, market cap, beta, 52-week position |
| News Sentiment | 20% | 25% | Relevant news matched to symbol/sector, bullish vs bearish count |

### Verdict Scale

| Score | Verdict | Meaning |
|-------|---------|---------|
| 80–100 | `** STRONG BUY **` | Strong across all dimensions. High conviction entry. |
| 62–80 | `>> BUY` | Mostly positive signals. Favorable risk/reward. |
| 42–62 | `-- HOLD` | Mixed signals. Wait for clearer confirmation. |
| 25–42 | `<< SELL` | Weak technicals or fundamentals. Consider reducing. |
| 0–25 | `!! STRONG SELL` | Multiple red flags. High risk of further downside. |

### Technical Signals Analyzed

| Signal | Bullish Condition | Bearish Condition |
|--------|-------------------|-------------------|
| RSI | < 30 (oversold) | > 70 (overbought) |
| MACD | MACD > Signal line | MACD < Signal line |
| EMA Trend | Price > EMA20/50/200 | Price < all EMAs |
| EMA Alignment | EMA20 > EMA50 > EMA200 | EMA20 < EMA50 < EMA200 |
| VWAP | Price above VWAP | Price below VWAP |
| Bollinger Bands | Near lower band (oversold) | Near upper band (overbought) |
| ATR | Low volatility | ATR > 5% of price |

### Momentum Signals Analyzed

| Signal | Bullish | Bearish |
|--------|---------|---------|
| Daily change | > +3% | < -3% |
| Volume vs 10d avg | > 2x average | < 0.5x average |
| Relative volume | > 2x spike | — |
| Pre-market | Gap up > 1% | Gap down > 1% |
| After-hours | Up > 1% | Down > 1% |
| Intraday | Gaining from open | Fading from open |

### Fundamental Signals Analyzed (Stocks Only)

| Signal | Bullish | Bearish |
|--------|---------|---------|
| P/E Ratio | < 15 (undervalued) | > 40 (expensive) |
| EPS | Positive | Negative |
| Dividend Yield | > 4% | — |
| Market Cap | > $200B (mega-cap) | < $2B (small-cap risk) |
| Beta | < 0.8 (defensive) | > 1.5 (high risk) |
| 52-week position | > 20% above 52w low | Near 52w high |

---

## 📡 Real-Time Trading Signals

`signals.py` converts analyst verdicts into actionable trade setups:

| Field | Description |
|-------|-------------|
| `action` | BUY / SELL / HOLD / WAIT - BULLISH SETUP / WAIT - BEARISH SETUP |
| `confidence` | `*` (low) or `**` (high) based on signal alignment |
| `entry` | Current price at signal time |
| `stop` | Stop-loss level (ATR-based or 5% default) |
| `stop_%` | Stop distance as % |
| `t1` / `t1_%` | First take-profit target |
| `t2` / `t2_%` | Second take-profit target |
| `rr` | Risk/reward ratio |

---

## 🖥 Example Output

```
  [1/2] Fetching market data + news concurrently...
  [2/2] Done in 9s — printing results...

... (market data tables) ...

==========================================================================================
  INVESTMENT ANALYSIS -- STOCKS
==========================================================================================
  >> BUY                  XOM                        $170.99        Score:  70.8/100  [T: 73.0 M: 74.0 F: 80.0 N: 54.0]
     -> Mostly positive signals. Favorable risk/reward.
       * RSI overbought (76.1) — pullback risk
       * Strong daily gain +3.36%
       * Positive EPS (6.69) — profitable

  -- HOLD                 BTCUSDT                    $67,067.75     Score:  45.6/100  [T: 46.0 M: 42.0 F: N/A  N: 50.0]
     -> Mixed signals. Wait for clearer confirmation.
       * RSI low (42.9) — building momentum
       * Volume only 0.5x avg — weak participation

  [TOP PICKS] : XOM, CVX, KO, JNJ
  [AVOID]     : AMZN

==========================================================================================
  REAL-TIME TRADING SIGNALS -- STOCKS
  SYMBOL    ACTION    CONF    ENTRY      STOP    STOP%      T1      T1%      T2      T2%   R/R
==========================================================================================
  XOM       BUY        **   $170.99  $162.60   -4.91%  $179.38   4.91%  $187.77   9.81%  2.0x

  News Sentiment -> Bullish: 9  Bearish: 7  Neutral: 61
  Market Signals -> Buy: 3  Sell: 32

[OK] JSON saved -> C:\...\output.json
[OK] CSV  saved -> C:\...\stocks_20260328_162212.csv
[OK] CSV  saved -> C:\...\crypto_20260328_162212.csv
[OK] CSV  saved -> C:\...\forex_20260328_162212.csv
[OK] CSV  saved -> C:\...\commodities_20260328_162212.csv
[OK] CSV  saved -> C:\...\indices_20260328_162212.csv
[OK] CSV  saved -> C:\...\news_20260328_162212.csv

  Done in one shot. 50 instruments + 77 news articles.
```

---

## 📊 Data Fields Per Instrument

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
| Derived | `technical_rating`, `signal` |

### Crypto / Forex / Commodities / Indices (36 fields)

Same as above minus: `market_cap`, `pe_ratio`, `eps`, `dividend_yield_%`, `sector`, `industry`, `beta`, `gap_%`, `pre_market_change_%`, `after_hours_change_%`.

> These fields are not available on non-equity TradingView scanner endpoints.

---

## 📰 News Fields

| Field | Description |
|-------|-------------|
| `title` | Article headline |
| `link` | Full URL |
| `published` | ISO timestamp |
| `source` | Publisher name |
| `sentiment` | `bullish` / `bearish` / `neutral` (keyword-based) |
| `categories` | `crypto`, `stocks`, `forex`, `commodities`, `macro`, `tech`, `general` |

---

## 💾 Output Files

Every run generates:

- `output.json` — all data + full analysis + signals in one structured file
- `stocks_<timestamp>.csv`
- `crypto_<timestamp>.csv`
- `forex_<timestamp>.csv`
- `commodities_<timestamp>.csv`
- `indices_<timestamp>.csv`
- `news_<timestamp>.csv`

### JSON structure

```json
{
  "fetched_at": "2026-03-28T16:22:12Z",
  "stocks":      [ { "symbol": "AAPL", "price": 248.8, "rsi": 37.9, "signal": "SELL", ... } ],
  "crypto":      [ { "symbol": "BTCUSDT", "price": 67067.75, "macd": -509.2, ... } ],
  "forex":       [ { "symbol": "EURUSD", "price": 1.1508, ... } ],
  "commodities": [ { "symbol": "GOLD", "price": 4493.4, ... } ],
  "indices":     [ { "symbol": "DJI", "price": 45166.64, ... } ],
  "news":        [ { "title": "...", "sentiment": "bullish", "categories": ["crypto"] } ],
  "analysis": {
    "stocks": [
      {
        "symbol": "XOM",
        "price": 170.99,
        "composite": 70.8,
        "verdict": ">> BUY",
        "verdict_desc": "Mostly positive signals. Favorable risk/reward.",
        "scores": { "technical": 73.0, "momentum": 74.0, "fundamental": 80.0, "news": 54.0 },
        "reasons": {
          "technical":   ["RSI overbought (76.1) — pullback risk", "Price above EMA20/50/200"],
          "momentum":    ["Strong daily gain +3.36%", "Gaining from open +3.27%"],
          "fundamental": ["Positive EPS (6.69) — profitable"],
          "news":        ["No directly relevant news found"]
        }
      }
    ],
    "crypto": [ ... ]
  },
  "signals": {
    "stocks": [ { "symbol": "XOM", "action": "BUY", "entry": 170.99, "stop": 162.60, "t1": 179.38, "t2": 187.77, "rr": 2.0 } ],
    "crypto": [ ... ]
  },
  "summary": {
    "total_instruments": 50,
    "total_news": 77,
    "bullish_news": 9,
    "bearish_news": 7,
    "buy_signals": 3,
    "sell_signals": 32
  }
}
```

---

## ✏️ Customizing Symbols

Edit the symbol lists at the top of `scanner.py`:

```python
STOCK_SYMBOLS = [
    "NASDAQ:AAPL", "NASDAQ:MSFT", "NYSE:TSLA",  # add more
]

CRYPTO_SYMBOLS = [
    "BINANCE:BTCUSDT", "BINANCE:ETHUSDT",  # add more
]

FOREX_SYMBOLS = [
    "FX:EURUSD", "FX:GBPUSD",  # add more
]

COMMODITY_SYMBOLS = [
    "TVC:GOLD", "TVC:USOIL",  # add more
]

INDEX_SYMBOLS = [
    "TVC:SPX", "TVC:NDX",  # add more
]
```

Format is always `EXCHANGE:TICKER` (e.g. `NASDAQ:AAPL`, `BINANCE:BTCUSDT`, `FX:EURUSD`, `TVC:GOLD`).

---

## ⚙️ Performance

| Optimization | Detail |
|-------------|--------|
| Concurrent fetches | All 6 data sources run simultaneously via `asyncio.gather` |
| Split column sets | Stocks use full 46-field payload; crypto/forex/indices use 36-field common payload — prevents 400 errors |
| Resource blocking | Playwright blocks `image`, `media`, `font`, `stylesheet` — only HTML + JS loads |
| Chromium flags | `--disable-gpu`, `--disable-extensions`, `--blink-settings=imagesEnabled=false` |
| Reduced scroll waits | 3 scrolls × 800ms instead of 6 × 1500ms |
| Single HTTP client | One shared `httpx.AsyncClient` for all scanner API calls |

---

## 📚 Dependencies

| Package | Purpose |
|---------|---------|
| `playwright` | Headless Chromium for JS-rendered news page |
| `beautifulsoup4` | HTML parsing for news articles |
| `httpx` | Async HTTP client for scanner API calls |

---

## 📝 Notes

- TradingView's CSS class names for the news page may change. If news stops parsing, inspect the live page with DevTools and update selectors in `news.py → _parse_articles()`.
- The scanner API requires no authentication for public market data.
- Crypto, forex, commodities, and indices do not return fundamental fields (P/E, EPS, sector, etc.) — this is a TradingView API limitation, not a bug.
- The analysis engine is rule-based using real market data — it is not financial advice. Always do your own research.
- Intended for personal/educational use. Review [TradingView's Terms of Service](https://www.tradingview.com/policies/) before any commercial use.
