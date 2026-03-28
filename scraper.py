import asyncio
import json
import httpx
from datetime import datetime
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

BASE_URL = "https://www.tradingview.com"
SCANNER_URL = "https://scanner.tradingview.com/{market}/scan"

STOCK_SYMBOLS = [
    "NASDAQ:AAPL", "NASDAQ:MSFT", "NASDAQ:NVDA",
    "NYSE:TSLA", "NYSE:JPM", "NYSE:BAC",
]

CRYPTO_SYMBOLS = [
    "BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:BNBUSDT",
    "BINANCE:SOLUSDT", "BINANCE:XRPUSDT", "BINANCE:DOGEUSDT",
]

SCANNER_COLUMNS = [
    "name", "close", "change", "change_abs",
    "volume", "market_cap_basic", "high", "low",
]


def build_scanner_payload(symbols: list[str]) -> dict:
    return {
        "symbols": {"tickers": symbols, "query": {"types": []}},
        "columns": SCANNER_COLUMNS,
    }


def parse_scanner_response(data: dict) -> list[dict]:
    results = []
    for row in data.get("data", []):
        values = row.get("d", [])
        results.append({
            "symbol":     values[0] if len(values) > 0 else None,
            "price":      values[1] if len(values) > 1 else None,
            "change_%":   round(values[2], 2) if len(values) > 2 and values[2] else None,
            "change_abs": values[3] if len(values) > 3 else None,
            "volume":     values[4] if len(values) > 4 else None,
            "market_cap": values[5] if len(values) > 5 else None,
            "high":       values[6] if len(values) > 6 else None,
            "low":        values[7] if len(values) > 7 else None,
        })
    return results


async def fetch_realtime(market: str, symbols: list[str]) -> list[dict]:
    payload = build_scanner_payload(symbols)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Origin": BASE_URL,
        "Referer": BASE_URL,
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(SCANNER_URL.format(market=market), json=payload, headers=headers)
        resp.raise_for_status()
        return parse_scanner_response(resp.json())


async def fetch_news_html() -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
        )
        await page.goto(f"{BASE_URL}/news/", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(4000)
        html = await page.content()
        await browser.close()
        return html


def parse_news(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    articles = []

    for item in soup.select("article[class*='news'], div[class*='news-item'], div[class*='newsItem']")[:20]:
        a_tag = item.select_one("a[href]")
        title_tag = item.select_one("a[href], h2, h3")
        time_tag = item.select_one("time, [class*='date'], [class*='time']")

        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        href = a_tag["href"] if a_tag else ""
        link = href if href.startswith("http") else BASE_URL + href
        published = time_tag.get("datetime") or time_tag.get_text(strip=True) if time_tag else None

        if title and len(title) > 10:
            articles.append({"title": title, "link": link, "published": published})

    return articles


async def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching real-time data...\n")

    stocks_task  = fetch_realtime("america", STOCK_SYMBOLS)
    crypto_task  = fetch_realtime("crypto", CRYPTO_SYMBOLS)
    news_task    = fetch_news_html()

    stocks, crypto, news_html = await asyncio.gather(stocks_task, crypto_task, news_task)
    news = parse_news(news_html)

    output = {
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "stocks":     stocks,
        "crypto":     crypto,
        "news":       news,
    }

    print("=== STOCKS ===")
    for s in stocks:
        print(f"  {s['symbol']:<20} ${s['price']}  {s['change_%']}%  vol={s['volume']}")

    print("\n=== CRYPTO ===")
    for c in crypto:
        print(f"  {c['symbol']:<25} ${c['price']}  {c['change_%']}%  vol={c['volume']}")

    print(f"\n=== NEWS ({len(news)} articles) ===")
    for n in news:
        print(f"  [{n['published']}] {n['title']}")

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print("\nSaved to output.json")


if __name__ == "__main__":
    asyncio.run(main())
