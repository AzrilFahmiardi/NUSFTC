"""
Twitter/X Scraper — Network Interception (Playwright-based)

Bypasses Twitter's API token requirements by intercepting the background JSON
requests directly from the live browser DOM. Uses `cookies.json` for auth.
"""

import asyncio
import json
import random
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from tqdm import tqdm

try:
    from playwright.async_api import async_playwright
except ImportError:
    raise ImportError("pip install playwright && playwright install chromium")

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import (
    TWITTER_COOKIES_PATH,
    TWITTER_DELAY_MIN,
    TWITTER_DELAY_MAX,
    TWITTER_MAX_TWEETS,
    ALL_QUERIES,
    DATA_RAW,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwitterScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.all_tweets: list[dict] = []
        self._intercepted_tweets_current_query = []

    async def _random_delay(self):
        delay = random.uniform(TWITTER_DELAY_MIN, TWITTER_DELAY_MAX)
        await asyncio.sleep(delay)

    def _parse_tweet_entry(self, entry: dict, query: str) -> dict:
        try:
            content = entry.get("content", {})
            item_content = content.get("itemContent", {})
            tweet_results = item_content.get("tweet_results", {}).get("result", {})
            
            # Kadang ada tweet yang diretweet, formatnya sedikit beda
            if tweet_results.get("__typename") == "TweetWithVisibilityResults":
                tweet_results = tweet_results.get("tweet", {})

            legacy = tweet_results.get("legacy", {})
            core = tweet_results.get("core", {}).get("user_results", {}).get("result", {})
            user_legacy = core.get("legacy", {})

            if not legacy.get("id_str"):
                return None

            return {
                "tweet_id": legacy.get("id_str"),
                "text": legacy.get("full_text"),
                "created_at": legacy.get("created_at"),
                "user_name": user_legacy.get("name"),
                "user_screen_name": user_legacy.get("screen_name"),
                "user_followers": user_legacy.get("followers_count"),
                "favorite_count": legacy.get("favorite_count"),
                "retweet_count": legacy.get("retweet_count"),
                "reply_count": legacy.get("reply_count"),
                "language": legacy.get("lang"),
                "query": query,
                "scraped_at": datetime.now().isoformat(),
            }
        except Exception as e:
            # Silently ignore format errors for ads or weird entries
            return None

    async def _handle_response(self, response, query: str):
        """Intercepts background JSON requests and extracts tweets."""
        url = response.url
        if "SearchTimeline" in url and response.status == 200:
            try:
                body = await response.json()
                instructions = body.get("data", {}).get("search_by_raw_query", {}).get("search_timeline", {}).get("timeline", {}).get("instructions", [])
                
                entries = []
                for inst in instructions:
                    if inst.get("type") == "TimelineAddEntries":
                        entries = inst.get("entries", [])
                        break
                    elif inst.get("type") == "TimelineReplaceEntry":
                        # Kadang entry pertama di-replace
                        entry = inst.get("entry")
                        if entry:
                            entries.append(entry)

                for entry in entries:
                    # Lewati cursor entries
                    if entry.get("entryId", "").startswith("cursor"):
                        continue
                        
                    parsed = self._parse_tweet_entry(entry, query)
                    if parsed:
                        self._intercepted_tweets_current_query.append(parsed)

            except Exception as e:
                pass # Ignore non-JSON or weird responses

    async def scrape_query(self, page, query: str, max_tweets: int = 100) -> list[dict]:
        self._intercepted_tweets_current_query = []
        logger.info("Scraping query: '%s' (max=%d)", query, max_tweets)

        # Encode query untuk URL
        encoded_query = query.replace(" ", "%20")
        url = f"https://x.com/search?q={encoded_query}&src=typed_query&f=live"

        handler = lambda response: asyncio.create_task(self._handle_response(response, query))
        try:
            # Gunakan event listener untuk menangkap response
            page.on("response", handler)
            
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(4)

            # Scroll ke bawah untuk men-trigger fetch JSON API berikutnya
            scroll_attempts = 0
            while len(self._intercepted_tweets_current_query) < max_tweets and scroll_attempts < 20:
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                await self._random_delay()
                scroll_attempts += 1
                
                logger.info("  '%s': %d tweets intercepted so far...", query[:30], len(self._intercepted_tweets_current_query))

        except Exception as e:
            logger.error("Error navigating/scrolling '%s': %s", query, e)
        
        # Bersihkan event listener agar tidak bentrok dengan query berikutnya
        try:
            page.remove_listener("response", handler)
        except Exception:
            pass

        unique_tweets = list({t["tweet_id"]: t for t in self._intercepted_tweets_current_query}.values())
        return unique_tweets[:max_tweets]

    async def scrape_all_queries(self, queries: list[str] | None = None, max_per_query: int = 100) -> pd.DataFrame:
        if not TWITTER_COOKIES_PATH.exists():
            raise ValueError(
                "⚠️ Cookies tidak ditemukan!\n"
                "Silakan isi cookies di config/.twitter_cookies.json terlebih dahulu."
            )

        if queries is None:
            queries = ALL_QUERIES

        with open(TWITTER_COOKIES_PATH, "r") as f:
            cookie_dict = json.load(f)

        playwright_cookies = [
            {"name": k, "value": v, "domain": ".x.com", "path": "/"} for k, v in cookie_dict.items()
        ]

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                viewport={"width": 1366, "height": 768},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            await context.add_cookies(playwright_cookies)
            page = await context.new_page()

            for query in tqdm(queries, desc="Scraping Twitter via Interception"):
                tweets = await self.scrape_query(page, query, max_tweets=max_per_query)
                self.all_tweets.extend(tweets)

                await asyncio.sleep(random.uniform(5, 10))

                if len(self.all_tweets) >= TWITTER_MAX_TWEETS:
                    logger.info("Reached global tweet limit (%d)", TWITTER_MAX_TWEETS)
                    break

            await browser.close()

        df = pd.DataFrame(self.all_tweets)
        if not df.empty and "tweet_id" in df.columns:
            before = len(df)
            df = df.drop_duplicates(subset=["tweet_id"])
            logger.info("Deduplicated: %d -> %d tweets", before, len(df))

        return df

    async def scrape_and_save(self, filename: str = "twitter_raw.csv", queries: list[str] | None = None, max_per_query: int = 100) -> pd.DataFrame:
        df = await self.scrape_all_queries(queries, max_per_query)
        output_path = DATA_RAW / filename
        df.to_csv(output_path, index=False)
        logger.info("Saved %d tweets to %s", len(df), output_path)
        return df

async def main():
    scraper = TwitterScraper(headless=True)
    df = await scraper.scrape_and_save(max_per_query=50)
    print(f"\n=== Scraping Complete: {len(df)} tweets ===")

if __name__ == "__main__":
    asyncio.run(main())
