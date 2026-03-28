# 📈 TradingView Financial Scraper

A high-performance, real-time financial data scraper built with **Playwright** and **BeautifulSoup** that pulls live **stocks**, **crypto**, **forex**, **commodities**, **indices**, and **market news** from [TradingView](https://www.tradingview.com) — all concurrently in a single run.

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

- Market data is fetched from TradingView's **internal scanner API** — the same endpoint their UI uses — so prices are always real-time tick-level.
- News requires a headless browser because the page is JavaScript-rendered. Playwright scrolls the page to load more articles, then BeautifulSoup parses the HTML.
- All 6 fetches run **concurrently** via `asyncio.gather` — total runtime is dominated by the slowest single fetch, not the sum of all.

---

## 🗂 Project Structure

```
FIn scrapper/
├── scraper.py        # Orchestrator — runs everything, prints results, exports files
├── scanner.py        # TradingView scanner API — stocks, crypto, forex, commodities, indices
├── news.py           # Playwright + BeautifulSoup — news scraper with sentiment & categories
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

## 🖥 Example Output

```
  [1/2] Fetching market data + news concurrently...
  [2/2] Done in 8s — printing results...

+----------------------+--------------+----------+----------------+------------------+---------+--------------+----------------------+
  STOCKS — Real-Time
+----------------------+--------------+----------+----------------+------------------+---------+--------------+----------------------+
 SYMBOL               | PRICE        | CHG%     | VOLUME         | MKT CAP          | RSI     | SIGNAL       | SECTOR               |
+----------------------+--------------+----------+----------------+------------------+---------+--------------+----------------------+
 AAPL                 | 189.3        | -0.42    | 55,234,100     | 2,920,000,000,000| 48.2    | NEUTRAL      | Technology           |
 MSFT                 | 415.2        | 0.87     | 21,100,400     | 3,080,000,000,000| 61.4    | BUY          | Technology           |
 NVDA                 | 875.4        | 1.23     | 43,200,000     | 2,160,000,000,000| 72.1    | STRONG BUY   | Technology           |
 ...

+---------------------------+----------------+----------+--------------------+---------+------------+--------------+----------------+
  CRYPTO — Real-Time
+---------------------------+----------------+----------+--------------------+---------+------------+--------------+----------------+
 SYMBOL                    | PRICE          | CHG%     | VOLUME             | RSI     | MACD       | SIGNAL       | VWAP           |
+---------------------------+----------------+----------+--------------------+---------+------------+--------------+----------------+
 BINANCE:BTCUSDT           | 67,420.1       | 2.15     | 18,900,000,000     | 64.3    | 312.5      | BUY          | 66,980.2       |
 BINANCE:ETHUSDT           | 3,521.8        | 1.87     | 9,200,000,000      | 59.7    | 45.2       | BUY          | 3,490.1        |
 ...

================================================================================
  NEWS (24 articles)
================================================================================
    1. ▲ [macro, forex] Fed signals rate cuts may be delayed further
         2024-05-10T13:45:00Z | Reuters | https://www.tradingview.com/news/...

    2. ▲ [crypto] Bitcoin surges past $67K amid ETF inflows
         2024-05-10T12:30:00Z | CoinDesk | https://www.tradingview.com/news/...
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

- `output.json` — all data in one structured file
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
- Intended for personal/educational use. Review [TradingView's Terms of Service](https://www.tradingview.com/policies/) before any commercial use.
