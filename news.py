import re
from playwright.async_api import async_playwright, Page
from bs4 import BeautifulSoup

BASE_URL = "https://www.tradingview.com"
NEWS_URL  = f"{BASE_URL}/news/"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Simple keyword-based sentiment
BULLISH_WORDS = {
    "surge", "soar", "rally", "gain", "rise", "jump", "beat", "record",
    "high", "bull", "growth", "profit", "upgrade", "buy", "strong",
    "outperform", "positive", "boost", "recover", "breakout",
}
BEARISH_WORDS = {
    "crash", "fall", "drop", "plunge", "loss", "miss", "low", "bear",
    "decline", "sell", "downgrade", "weak", "risk", "fear", "recession",
    "inflation", "cut", "layoff", "bankruptcy", "warning", "concern",
}

# News category keywords
CATEGORY_MAP = {
    "crypto":      ["bitcoin", "crypto", "ethereum", "btc", "eth", "blockchain", "defi", "nft"],
    "stocks":      ["stock", "equity", "shares", "nasdaq", "nyse", "ipo", "earnings", "dividend"],
    "forex":       ["dollar", "euro", "yen", "currency", "forex", "fx", "fed", "rate"],
    "commodities": ["gold", "oil", "silver", "crude", "commodity", "gas", "wheat", "copper"],
    "macro":       ["gdp", "inflation", "recession", "fed", "central bank", "interest rate", "cpi", "ppi"],
    "tech":        ["ai", "artificial intelligence", "tech", "semiconductor", "chip", "software"],
}


def _sentiment(title: str) -> str:
    words = set(re.findall(r"\w+", title.lower()))
    bull = len(words & BULLISH_WORDS)
    bear = len(words & BEARISH_WORDS)
    if bull > bear:
        return "bullish"
    if bear > bull:
        return "bearish"
    return "neutral"


def _category(title: str) -> list[str]:
    lower = title.lower()
    return [cat for cat, kws in CATEGORY_MAP.items() if any(k in lower for k in kws)] or ["general"]


def _parse_articles(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    seen, articles = set(), []

    # Strategy 1: structured article tags
    selectors = [
        "article",
        "div[class*='news-headline']",
        "div[class*='newsItem']",
        "div[class*='news-item']",
        "div[class*='story']",
        "li[class*='news']",
    ]
    items = soup.select(", ".join(selectors))

    for item in items:
        a_tag    = item.select_one("a[href]")
        title_el = item.select_one("h1, h2, h3, h4, a[href]")
        time_el  = item.select_one("time[datetime], [class*='date'], [class*='time'], [class*='ago']")
        source_el = item.select_one("[class*='source'], [class*='provider'], [class*='author']")

        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        if not title or len(title) < 15 or title in seen:
            continue

        href = a_tag["href"] if a_tag and a_tag.get("href") else ""
        link = href if href.startswith("http") else BASE_URL + href

        published = None
        if time_el:
            published = time_el.get("datetime") or time_el.get_text(strip=True)

        source = source_el.get_text(strip=True) if source_el else None

        seen.add(title)
        articles.append({
            "title":     title,
            "link":      link,
            "published": published,
            "source":    source,
            "sentiment": _sentiment(title),
            "categories": _category(title),
        })

    # Strategy 2: fallback — grab all anchor tags that look like news links
    if len(articles) < 5:
        for a in soup.select("a[href*='/news/']"):
            title = a.get_text(strip=True)
            if not title or len(title) < 15 or title in seen:
                continue
            href = a["href"]
            link = href if href.startswith("http") else BASE_URL + href
            seen.add(title)
            articles.append({
                "title":      title,
                "link":       link,
                "published":  None,
                "source":     None,
                "sentiment":  _sentiment(title),
                "categories": _category(title),
            })

    return articles


async def _scroll_and_load(page: Page, scrolls: int = 5) -> None:
    for _ in range(scrolls):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1500)


async def scrape_news(max_scrolls: int = 6) -> list[dict]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/New_York",
        )
        page = await context.new_page()

        # Block images/fonts to speed up loading
        await page.route("**/*.{png,jpg,jpeg,gif,webp,svg,woff,woff2,ttf}", lambda r: r.abort())

        await page.goto(NEWS_URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)
        await _scroll_and_load(page, max_scrolls)

        html = await page.content()
        await browser.close()

    return _parse_articles(html)
