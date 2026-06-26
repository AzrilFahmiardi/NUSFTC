"""
Twitter/X Scraper — Network Interception (Playwright).

Reuses the proven cookie-based interception approach from the predecessor
project. Tweets are scraped per query and tagged with their query_group
(flavor / morning / pain / yogurt / occasion / competitor) so that downstream
analysis can answer brief questions Q1–Q6 directly.
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
    TWITTER_MAX_PER_QUERY,
    DATA_RAW,
    LOG_PATH,
)
from config.queries import QUERY_GROUPS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwitterScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.all_tweets: list[dict] = []
        self._intercepted = []
        self._log_lines: list[str] = []

    async def _random_delay(self):
        await asyncio.sleep(random.uniform(TWITTER_DELAY_MIN, TWITTER_DELAY_MAX))

    def _parse_tweet_entry(self, entry: dict, query: str, group: str) -> dict | None:
        try:
            content = entry.get("content", {})
            item_content = content.get("itemContent", {})
            tweet_results = item_content.get("tweet_results", {}).get("result", {})
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
                "query_group": group,
                "scraped_at": datetime.now().isoformat(),
            }
        except Exception:
            return None

    async def _handle_response(self, response, query: str, group: str):
        if "SearchTimeline" in response.url and response.status == 200:
            try:
                body = await response.json()
                instructions = (
                    body.get("data", {})
                    .get("search_by_raw_query", {})
                    .get("search_timeline", {})
                    .get("timeline", {})
                    .get("instructions", [])
                )
                entries = []
                for inst in instructions:
                    if inst.get("type") == "TimelineAddEntries":
                        entries = inst.get("entries", [])
                        break
                    elif inst.get("type") == "TimelineReplaceEntry":
                        e = inst.get("entry")
                        if e:
                            entries.append(e)

                for entry in entries:
                    if entry.get("entryId", "").startswith("cursor"):
                        continue
                    parsed = self._parse_tweet_entry(entry, query, group)
                    if parsed:
                        self._intercepted.append(parsed)
            except Exception:
                pass

    async def scrape_query(self, page, query: str, group: str, max_tweets: int) -> list[dict]:
        self._intercepted = []
        start = datetime.now()
        logger.info("[%s] '%s' (max=%d)", group, query, max_tweets)

        encoded = query.replace(" ", "%20")
        url = f"https://x.com/search?q={encoded}&src=typed_query&f=live"

        handler = lambda response: asyncio.create_task(
            self._handle_response(response, query, group)
        )
        try:
            page.on("response", handler)
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(4)

            scrolls = 0
            while len(self._intercepted) < max_tweets and scrolls < 25:
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                await self._random_delay()
                scrolls += 1
        except Exception as e:
            logger.error("Navigation error '%s': %s", query, e)
        finally:
            try:
                page.remove_listener("response", handler)
            except Exception:
                pass

        unique = list({t["tweet_id"]: t for t in self._intercepted}.values())[:max_tweets]
        self._log_lines.append(
            f"{start.isoformat()}\t{group}\t{query}\t{len(unique)}\t{(datetime.now()-start).seconds}s"
        )
        return unique

    async def scrape_groups(
        self,
        groups: dict[str, list[str]] | None = None,
        max_per_query: int = TWITTER_MAX_PER_QUERY,
    ) -> pd.DataFrame:
        if not TWITTER_COOKIES_PATH.exists():
            raise FileNotFoundError(f"Cookies not found at {TWITTER_COOKIES_PATH}")

        if groups is None:
            groups = QUERY_GROUPS

        with open(TWITTER_COOKIES_PATH) as f:
            cookie_dict = json.load(f)
        playwright_cookies = [
            {"name": k, "value": v, "domain": ".x.com", "path": "/"}
            for k, v in cookie_dict.items()
        ]

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                viewport={"width": 1366, "height": 768},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36",
            )
            await context.add_cookies(playwright_cookies)
            page = await context.new_page()

            queries_flat = [(g, q) for g, qs in groups.items() for q in qs]
            for group, query in tqdm(queries_flat, desc="Scraping Twitter"):
                tweets = await self.scrape_query(page, query, group, max_per_query)
                self.all_tweets.extend(tweets)
                await asyncio.sleep(random.uniform(5, 10))
                if len(self.all_tweets) >= TWITTER_MAX_TWEETS:
                    logger.info("Global cap reached (%d)", TWITTER_MAX_TWEETS)
                    break

            await browser.close()

        df = pd.DataFrame(self.all_tweets)
        if not df.empty:
            before = len(df)
            df = df.drop_duplicates(subset=["tweet_id"]).reset_index(drop=True)
            logger.info("Deduplicated: %d -> %d", before, len(df))
        return df

    def save_log(self):
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "w") as f:
            f.write("timestamp\tgroup\tquery\ttweet_count\telapsed\n")
            f.writelines(line + "\n" for line in self._log_lines)
        logger.info("Log written: %s", LOG_PATH)

    async def scrape_and_save(
        self,
        filename: str = "twitter_raw.csv",
        groups: dict[str, list[str]] | None = None,
        max_per_query: int = TWITTER_MAX_PER_QUERY,
    ) -> pd.DataFrame:
        df = await self.scrape_groups(groups, max_per_query)
        path = DATA_RAW / filename
        df.to_csv(path, index=False)
        self.save_log()
        logger.info("Saved %d tweets -> %s", len(df), path)
        return df


async def _main():
    scraper = TwitterScraper(headless=True)
    df = await scraper.scrape_and_save(max_per_query=TWITTER_MAX_PER_QUERY)
    print(f"\n=== Done: {len(df)} tweets ===")


if __name__ == "__main__":
    asyncio.run(_main())
