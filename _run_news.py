import asyncio
from news import scrape_news
from export import print_news

async def main():
    print("  Scraping news...")
    news = await scrape_news(max_scrolls=3)
    print_news(news)
    bullish = sum(1 for n in news if n.get("sentiment") == "bullish")
    bearish = sum(1 for n in news if n.get("sentiment") == "bearish")
    print(f"\n  Total: {len(news)} articles")
    print(f"  Sentiment -> Bullish: {bullish}  Bearish: {bearish}  Neutral: {len(news)-bullish-bearish}")

asyncio.run(main())
