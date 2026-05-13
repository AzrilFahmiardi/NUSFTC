"""
Tokopedia Review Scraper — Unofficial, Free (Playwright-based)

Uses headless browser to scrape product reviews from Tokopedia.
No API key needed.

Usage:
    scraper = TokopediaScraper()
    df = await scraper.scrape_and_save()
"""

import asyncio
import random
import re
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup

try:
    from playwright.async_api import async_playwright
except ImportError:
    raise ImportError("pip install playwright && playwright install chromium")

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import (
    ECOMMERCE_DELAY_MIN, ECOMMERCE_DELAY_MAX,
    TOKOPEDIA_MAX_REVIEWS_PER_PRODUCT, DATA_RAW,
)
from config.competitors import COMPETITORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKOPEDIA_SEARCH = "https://www.tokopedia.com/search?q={query}&st=product"


class TokopediaScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.all_reviews: list[dict] = []

    async def _delay(self):
        await asyncio.sleep(random.uniform(ECOMMERCE_DELAY_MIN, ECOMMERCE_DELAY_MAX))

    async def _scroll(self, page, n: int = 10):
        for _ in range(n):
            await page.evaluate("window.scrollBy(0, 800)")
            await asyncio.sleep(random.uniform(0.5, 1.5))

    async def search_product(self, page, query: str) -> list[str]:
        """Search Tokopedia and return top product URLs."""
        url = TOKOPEDIA_SEARCH.format(query=query.replace(" ", "+"))
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)
            await self._scroll(page, 3)
            links = await page.eval_on_selector_all(
                'a[href*="tokopedia.com/"]',
                """els => els.map(e => e.href)
                   .filter(h => h && !h.includes('/search') && !h.includes('/discovery'))
                   .slice(0, 5)"""
            )
            logger.info("Found %d product links for '%s'", len(links), query)
            return links
        except Exception as e:
            logger.error("Search error '%s': %s", query, e)
            return []

    async def scrape_reviews(self, page, url: str, name: str, max_rev: int = 100) -> list[dict]:
        """Scrape reviews from a product page."""
        reviews = []
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)
            await self._scroll(page, 15)

            # Try clicking review tab
            for btn_text in ["Ulasan", "Review"]:
                try:
                    btn = page.locator(f'text="{btn_text}"').first
                    await btn.click(timeout=3000)
                    await asyncio.sleep(2)
                    break
                except Exception:
                    pass

            html = await page.content()
            soup = BeautifulSoup(html, "lxml")

            # Extract review text blocks (paragraphs > 10 chars in review area)
            for elem in soup.find_all(["span", "p", "div"], string=True):
                text = elem.get_text(strip=True)
                if 15 < len(text) < 2000 and not re.match(r"^(Rp|IDR|\d+%)", text):
                    reviews.append({
                        "text": text,
                        "product_name": name,
                        "product_url": url,
                        "source": "tokopedia",
                        "scraped_at": datetime.now().isoformat(),
                    })
                if len(reviews) >= max_rev:
                    break

        except Exception as e:
            logger.error("Review scrape error %s: %s", url[:60], e)

        # Deduplicate
        seen = set()
        unique = []
        for r in reviews:
            key = r["text"][:80]
            if key not in seen:
                seen.add(key)
                unique.append(r)

        logger.info("Got %d reviews from %s", len(unique), name)
        return unique

    async def scrape_all_products(self) -> pd.DataFrame:
        """Scrape reviews for all competitors."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            ctx = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1366, "height": 768},
                locale="id-ID",
            )
            page = await ctx.new_page()

            for comp_id, info in tqdm(COMPETITORS.items(), desc="Tokopedia"):
                links = await self.search_product(page, info["shopee_keywords"])
                for link in links[:3]:
                    revs = await self.scrape_reviews(page, link, info["name"], max_rev=TOKOPEDIA_MAX_REVIEWS_PER_PRODUCT // 3)
                    self.all_reviews.extend(revs)
                    await self._delay()
                await asyncio.sleep(random.uniform(5, 10))

            await browser.close()

        df = pd.DataFrame(self.all_reviews)
        if not df.empty:
            df = df.drop_duplicates(subset=["text"], keep="first")
        return df

    async def scrape_and_save(self, filename: str = "tokopedia_raw.csv") -> pd.DataFrame:
        df = await self.scrape_all_products()
        path = DATA_RAW / filename
        df.to_csv(path, index=False)
        logger.info("Saved %d reviews to %s", len(df), path)
        return df


async def main():
    scraper = TokopediaScraper(headless=True)
    df = await scraper.scrape_and_save()
    print(f"\nTokopedia done: {len(df)} reviews")

if __name__ == "__main__":
    asyncio.run(main())
