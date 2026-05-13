"""
Shopee Review Scraper — Unofficial, Free (Playwright-based)

Uses headless browser to scrape product reviews from Shopee Indonesia.
No API key needed.

Usage:
    scraper = ShopeeScraper()
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
    SHOPEE_MAX_REVIEWS_PER_PRODUCT, DATA_RAW,
)
from config.competitors import COMPETITORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SHOPEE_SEARCH = "https://shopee.co.id/search?keyword={query}"


class ShopeeScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.all_reviews: list[dict] = []

    async def _delay(self):
        await asyncio.sleep(random.uniform(ECOMMERCE_DELAY_MIN, ECOMMERCE_DELAY_MAX))

    async def _scroll(self, page, n: int = 10):
        for _ in range(n):
            await page.evaluate("window.scrollBy(0, 600)")
            await asyncio.sleep(random.uniform(0.5, 1.5))

    async def search_product(self, page, query: str) -> list[str]:
        """Search Shopee and return top product URLs."""
        url = SHOPEE_SEARCH.format(query=query.replace(" ", "+"))
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(4)
            await self._scroll(page, 3)

            links = await page.eval_on_selector_all(
                'a[href*="-i."]',
                "els => els.map(e => 'https://shopee.co.id' + e.getAttribute('href')).slice(0, 5)"
            )

            if not links:
                links = await page.eval_on_selector_all(
                    'a[data-sqe="link"]',
                    "els => els.map(e => e.href).filter(h => h.includes('shopee.co.id')).slice(0, 5)"
                )

            logger.info("Shopee: %d links for '%s'", len(links), query)
            return links
        except Exception as e:
            logger.error("Shopee search error '%s': %s", query, e)
            return []

    async def scrape_reviews(self, page, url: str, name: str, max_rev: int = 100) -> list[dict]:
        """Scrape reviews from a Shopee product page."""
        reviews = []
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(4)
            await self._scroll(page, 15)

            # Try clicking review/rating tab
            for selector in [
                'div[class*="product-rating"]',
                'text="Penilaian Produk"',
                'text="Rating"',
            ]:
                try:
                    await page.locator(selector).first.click(timeout=3000)
                    await asyncio.sleep(2)
                    break
                except Exception:
                    pass

            # Parse reviews from page content
            html = await page.content()
            soup = BeautifulSoup(html, "lxml")

            # Shopee review containers
            review_divs = soup.find_all("div", class_=re.compile(r"shopee-product-rating"))
            if not review_divs:
                review_divs = soup.find_all("div", attrs={"data-sqe": "review"})

            for div in review_divs:
                text = div.get_text(separator=" ", strip=True)
                # Filter noise
                if len(text) > 15 and not text.startswith("Rp"):
                    reviews.append({
                        "text": text,
                        "product_name": name,
                        "product_url": url,
                        "source": "shopee",
                        "scraped_at": datetime.now().isoformat(),
                    })
                if len(reviews) >= max_rev:
                    break

            # Fallback: extract any long-ish text near rating elements
            if not reviews:
                for elem in soup.find_all(["p", "div", "span"], string=True):
                    t = elem.get_text(strip=True)
                    if 20 < len(t) < 2000:
                        reviews.append({
                            "text": t,
                            "product_name": name,
                            "product_url": url,
                            "source": "shopee",
                            "scraped_at": datetime.now().isoformat(),
                        })
                    if len(reviews) >= max_rev:
                        break

        except Exception as e:
            logger.error("Shopee review error %s: %s", url[:60], e)

        # Deduplicate
        seen = set()
        unique = []
        for r in reviews:
            key = r["text"][:80]
            if key not in seen:
                seen.add(key)
                unique.append(r)

        logger.info("Shopee: %d reviews from %s", len(unique), name)
        return unique

    async def scrape_all_products(self) -> pd.DataFrame:
        """Scrape reviews for all competitors from Shopee."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            ctx = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1366, "height": 768},
                locale="id-ID",
            )
            page = await ctx.new_page()

            for comp_id, info in tqdm(COMPETITORS.items(), desc="Shopee"):
                links = await self.search_product(page, info["shopee_keywords"])
                for link in links[:3]:
                    revs = await self.scrape_reviews(
                        page, link, info["name"],
                        max_rev=SHOPEE_MAX_REVIEWS_PER_PRODUCT // 3,
                    )
                    self.all_reviews.extend(revs)
                    await self._delay()
                await asyncio.sleep(random.uniform(5, 10))

            await browser.close()

        df = pd.DataFrame(self.all_reviews)
        if not df.empty:
            df = df.drop_duplicates(subset=["text"], keep="first")
        return df

    async def scrape_and_save(self, filename: str = "shopee_raw.csv") -> pd.DataFrame:
        df = await self.scrape_all_products()
        path = DATA_RAW / filename
        df.to_csv(path, index=False)
        logger.info("Saved %d reviews to %s", len(df), path)
        return df


async def main():
    scraper = ShopeeScraper(headless=True)
    df = await scraper.scrape_and_save()
    print(f"\nShopee done: {len(df)} reviews")

if __name__ == "__main__":
    asyncio.run(main())
