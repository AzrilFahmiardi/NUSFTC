"""
Twitter Auth Extractor — Headed browser manual login.

Run when cookies.json is missing or stale.
    python -m scrapers.twitter_auth
"""

import asyncio
import json
import logging
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    raise ImportError("pip install playwright && playwright install chromium")

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import TWITTER_COOKIES_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_auth():
    print("=" * 60)
    print("🔒 TWITTER AUTHENTICATION — manual login window")
    print("=" * 60)
    print("Browser akan terbuka. Login manual menggunakan akun burner.")
    print("Setelah masuk ke halaman home, cookies akan tersimpan otomatis.")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        try:
            await page.goto("https://twitter.com/i/flow/login")
        except Exception as e:
            logger.error("Gagal membuka halaman login: %s", e)
            await browser.close()
            return

        print("\nMenunggu login (max 2 menit)...")
        logged_in = False
        for _ in range(120):
            await asyncio.sleep(1)
            if "twitter.com/home" in page.url or "x.com/home" in page.url:
                logged_in = True
                break

        if not logged_in:
            print("❌ Timeout. Tutup browser dan ulangi.")
            await browser.close()
            return

        raw_cookies = await context.cookies()
        cookie_dict = {c["name"]: c["value"] for c in raw_cookies}

        if "auth_token" not in cookie_dict or "ct0" not in cookie_dict:
            print("❌ auth_token/ct0 tidak ditemukan.")
            await browser.close()
            return

        TWITTER_COOKIES_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TWITTER_COOKIES_PATH, "w") as f:
            json.dump(cookie_dict, f, indent=4)

        print(f"\n🎉 Cookies tersimpan: {TWITTER_COOKIES_PATH}")
        await asyncio.sleep(2)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(run_auth())
