"""
Twitter Auth Extractor — Headed Browser Login

This script bypasses Twitter's automated login blocks by opening a real browser window.
It lets the user log in manually, then extracts and saves the cookies (auth_token & ct0).

Usage:
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
    print("="*60)
    print("🔒 TWITTER AUTHENTICATION BYPASS")
    print("="*60)
    print("Membuka browser Chrome... Silakan login secara manual.")
    print("Pastikan Anda login menggunakan akun burner/cadangan Anda.")
    print("Script akan otomatis mendeteksi jika login telah berhasil.")
    print("="*60)

    async with async_playwright() as p:
        # Gunakan headed mode agar user bisa melihat dan berinteraksi
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            await page.goto("https://twitter.com/i/flow/login")
        except Exception as e:
            logger.error("Gagal membuka halaman login: %s", e)
            await browser.close()
            return

        print("\nMenunggu Anda login... (Selesaikan captcha jika ada)")
        
        # Polling url untuk mendeteksi kesuksesan login (biasanya dialihkan ke /home)
        logged_in = False
        for _ in range(120):  # Tunggu maksimal 2 menit
            await asyncio.sleep(1)
            if "twitter.com/home" in page.url or "x.com/home" in page.url:
                logged_in = True
                break

        if not logged_in:
            print("\n❌ Waktu tunggu login habis (2 menit) atau Anda menutup halaman.")
            await browser.close()
            return

        print("\n✅ Login berhasil terdeteksi!")
        print("Mengekstrak session cookies...")
        
        # Ekstrak semua cookies
        raw_cookies = await context.cookies()
        
        # Format ke bentuk dictionary sederhana seperti yang dibutuhkan twikit
        cookie_dict = {}
        for c in raw_cookies:
            cookie_dict[c["name"]] = c["value"]

        # Pastikan auth_token ada
        if "auth_token" not in cookie_dict or "ct0" not in cookie_dict:
            print("❌ Gagal mengekstrak auth_token atau ct0. Login mungkin tidak sempurna.")
            await browser.close()
            return

        # Simpan ke file
        TWITTER_COOKIES_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TWITTER_COOKIES_PATH, "w") as f:
            json.dump(cookie_dict, f, indent=4)

        print(f"\n🎉 Cookies berhasil disimpan ke: {TWITTER_COOKIES_PATH}")
        print("Sekarang Anda bisa menjalankan scraper Twitter secara otomatis tanpa error!")
        
        await asyncio.sleep(2)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_auth())
