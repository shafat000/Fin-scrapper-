# TradingView Financial Scraper

A real-time financial data scraper that pulls **stock prices**, **crypto prices**, and **market news** from [TradingView](https://www.tradingview.com) using Playwright and BeautifulSoup.

---

## How It Works

| Data | Method |
|------|--------|
| Stock prices | TradingView internal scanner API (`scanner.tradingview.com/america/scan`) via `httpx` |
| Crypto prices | TradingView internal scanner API (`scanner.tradingview.com/crypto/scan`) via `httpx` |
| News headlines | Playwright (headless Chromium) + BeautifulSoup HTML parsing |

Stock and crypto data is fetched directly from TradingView's own scanner API — the same endpoint their UI uses — so prices are always real-time. News requires a headless browser because the page is JavaScript-rendered.

All three fetches run **concurrently** via `asyncio.gather`.

---

## Project Structure

```
FIn scrapper/
├── scraper.py        # Main scraper
├── requirements.txt  # Python dependencies
├── output.json       # Generated output (created on first run)
└── README.md
```

---

## Requirements

- Python 3.10+
- Internet connection

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

### Example console output

```
[14:32:01] Fetching real-time data...

=== STOCKS ===
  AAPL                 $189.30  -0.42%  vol=55234100
  MSFT                 $415.20   0.87%  vol=21100400
  NVDA                 $875.40   1.23%  vol=43200000
  ...

=== CRYPTO ===
  BINANCE:BTCUSDT      $67420.10   2.15%  vol=18900000000
  BINANCE:ETHUSDT      $3521.80    1.87%  vol=9200000000
  ...

=== NEWS (18 articles) ===
  [2024-05-10T13:45:00Z] Fed signals rate cuts may be delayed further
  [2024-05-10T12:30:00Z] Bitcoin surges past $67K amid ETF inflows
  ...

Saved to output.json
```

---

## Output Format

Results are saved to `output.json` with the following structure:

```json
{
  "fetched_at": "2024-05-10T14:32:01Z",
  "stocks": [
    {
      "symbol": "AAPL",
      "price": 189.30,
      "change_%": -0.42,
      "change_abs": -0.80,
      "volume": 55234100,
      "market_cap": 2920000000000,
      "high": 190.10,
      "low": 188.50
    }
  ],
  "crypto": [
    {
      "symbol": "BTCUSDT",
      "price": 67420.10,
      "change_%": 2.15,
      "change_abs": 1420.10,
      "volume": 18900000000,
      "market_cap": null,
      "high": 68100.00,
      "low": 65900.00
    }
  ],
  "news": [
    {
      "title": "Fed signals rate cuts may be delayed further",
      "link": "https://www.tradingview.com/news/...",
      "published": "2024-05-10T13:45:00Z"
    }
  ]
}
```

---

## Customizing Symbols

Edit the symbol lists at the top of `scraper.py`:

```python
# Stocks — format: EXCHANGE:TICKER
STOCK_SYMBOLS = [
    "NASDAQ:AAPL", "NASDAQ:MSFT", "NASDAQ:NVDA",
    "NYSE:TSLA", "NYSE:JPM", "NYSE:BAC",
    "NYSE:AMZN", "NASDAQ:GOOGL",   # add more here
]

# Crypto — format: EXCHANGE:PAIR
CRYPTO_SYMBOLS = [
    "BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:BNBUSDT",
    "BINANCE:SOLUSDT", "BINANCE:XRPUSDT", "BINANCE:DOGEUSDT",
    "BINANCE:ADAUSDT", "BINANCE:MATICUSDT",   # add more here
]
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `playwright` | Headless browser for JS-rendered news page |
| `beautifulsoup4` | HTML parsing for news articles |
| `httpx` | Async HTTP client for scanner API calls |

---

## Notes

- TradingView's CSS class names for the news page may change over time. If news stops parsing, inspect the live page with browser DevTools and update the selectors in `parse_news()`.
- The scanner API does not require authentication for public market data.
- This tool is intended for personal/educational use. Review [TradingView's Terms of Service](https://www.tradingview.com/policies/) before any commercial use.
