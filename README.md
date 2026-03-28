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

- Market data is fetched from TradingView's **internal scanner API** — the same endpoint their UI uses — so prices are always real-time tick-level.
- News requires a headless browser because the page is JavaScript-rendered. Playwright scrolls the page to load more articles, then BeautifulSoup parses the HTML.
- All 6 fetches run **concurrently** via `asyncio.gather`.
- After fetching, the **analyst engine** scores every stock and crypto using all 46 data fields + news sentiment.

---

## 🗂 Project Structure

```
FIn scrapper/
├── scraper.py        # Orchestrator — runs everything, prints results, exports files
├── scanner.py        # TradingView scanner API — stocks, crypto, forex, commodities, indices
├── news.py           # Playwright + BeautifulSoup — news scraper with sentiment & categories
├── analyst.py        # Investment analysis engine — scores every instrument 0–100
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
| 80–100 | 🟢 STRONG BUY | Strong across all dimensions. High conviction entry. |
| 62–80 | 🟩 BUY | Mostly positive signals. Favorable risk/reward. |
| 42–62 | 🟡 HOLD | Mixed signals. Wait for clearer confirmation. |
| 25–42 | 🟠 SELL | Weak technicals or fundamentals. Consider reducing. |
| 0–25 | 🔴 STRONG SELL | Multiple red flags. High risk of further downside. |

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

## 🖥 Example Output

```
  [1/2] Fetching market data + news concurrently...
  [2/2] Done in 8s — printing results...

... (market data tables) ...

==========================================================================================
  📊 INVESTMENT ANALYSIS — STOCKS
==========================================================================================
  🟢 STRONG BUY        NASDAQ:NVDA                $875.40       Score:  84.2/100  [T: 78.5 M: 91.2 F: 82.0 N: 85.0]
     → Strong across all dimensions. High conviction entry.
       • MACD bullish crossover (12.5 > 8.2)
       • Price above EMA20/50/200 — strong uptrend
       • Volume 2.4x above 10d avg — strong conviction
       • Strong daily gain +3.21%
       • Low P/E (22.1) — reasonable valuation
       • News sentiment positive (3 bullish vs 1 bearish in 4 relevant articles)

  🟩 BUY               NASDAQ:MSFT                $415.20       Score:  71.8/100  [T: 68.0 M: 74.5 F: 76.0 N: 70.0]
     → Mostly positive signals. Favorable risk/reward.
       ...

  🟡 HOLD              NYSE:JPM                   $198.50       Score:  54.3/100  [T: 52.0 M: 48.5 F: 65.0 N: 52.0]
     → Mixed signals. Wait for clearer confirmation.
       ...

  🟢 Top Picks  : NASDAQ:NVDA, NASDAQ:MSFT, NASDAQ:AAPL
  🔴 Avoid      : NYSE:BAC

==========================================================================================
  📊 INVESTMENT ANALYSIS — CRYPTO
==========================================================================================
  🟢 STRONG BUY        BINANCE:BTCUSDT            $67,420.10    Score:  81.5/100  [T: 79.0 M: 88.0 F:N/A  N: 76.0]
     → Strong across all dimensions. High conviction entry.
       ...

  News Sentiment  → Bullish: 11  Bearish: 8  Neutral: 5
  Market Signals  → Buy: 14  Sell: 3

[✓] JSON saved → C:\...\output.json
[✓] CSV  saved → C:\...\stocks_20240510_143201.csv
[✓] CSV  saved → C:\...\crypto_20240510_143201.csv
[✓] CSV  saved → C:\...\news_20240510_143201.csv
```

---

## 📊 Data Fields Per Instrument (46 fields)

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
| Derived | `technical_rating`, `signal` (STRONG BUY / BUY / NEUTRAL / SELL / STRONG SELL) |

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

- `output.json` — all data + full analysis in one structured file
- `stocks_<timestamp>.csv`
- `crypto_<timestamp>.csv`
- `forex_<timestamp>.csv`
- `commodities_<timestamp>.csv`
- `indices_<timestamp>.csv`
- `news_<timestamp>.csv`

### JSON structure

```json
{
  "fetched_at": "2024-05-10T14:32:01Z",
  "stocks":      [ { "symbol": "AAPL", "price": 189.3, "rsi": 48.2, "signal": "NEUTRAL", ... } ],
  "crypto":      [ { "symbol": "BTCUSDT", "price": 67420.1, "macd": 312.5, ... } ],
  "forex":       [ { "symbol": "EURUSD", "price": 1.0823, ... } ],
  "commodities": [ { "symbol": "GOLD", "price": 2345.6, ... } ],
  "indices":     [ { "symbol": "SPX", "price": 5248.3, ... } ],
  "news":        [ { "title": "...", "sentiment": "bullish", "categories": ["macro"] } ],
  "analysis": {
    "stocks": [
      {
        "symbol": "NASDAQ:NVDA",
        "price": 875.4,
        "composite": 84.2,
        "verdict": "🟢 STRONG BUY",
        "verdict_desc": "Strong across all dimensions. High conviction entry.",
        "scores": { "technical": 78.5, "momentum": 91.2, "fundamental": 82.0, "news": 85.0 },
        "reasons": {
          "technical":   ["MACD bullish crossover", "Price above EMA20/50/200"],
          "momentum":    ["Volume 2.4x above 10d avg", "Strong daily gain +3.21%"],
          "fundamental": ["Low P/E (22.1)", "Positive EPS (16.40)"],
          "news":        ["News sentiment positive (3 bullish vs 1 bearish)"]
        }
      }
    ],
    "crypto": [ ... ]
  },
  "summary": {
    "total_instruments": 61,
    "total_news": 24,
    "bullish_news": 11,
    "bearish_news": 8,
    "buy_signals": 14,
    "sell_signals": 3
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
- The analysis engine is rule-based using real market data — it is not financial advice. Always do your own research.
- Intended for personal/educational use. Review [TradingView's Terms of Service](https://www.tradingview.com/policies/) before any commercial use.
