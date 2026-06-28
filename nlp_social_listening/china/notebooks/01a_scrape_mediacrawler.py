# %% [markdown]
# # 01a · Self-hosted scraping (MediaCrawler) — near-zero cost
# Xiaohongshu (RED), Weibo, Bilibili, Zhihu, Douyin via QR login.
# A Chrome window opens per platform — scan the QR with the app to log in.
#
# Run: `conda activate ml && python notebooks/01a_scrape_mediacrawler.py`
# Prereq: third_party/MediaCrawler cloned + `uv sync`; Chrome >= 144; account logged in.
#
# SMOKE_TEST = True  → 1 keyword only (safe to run first to verify login works)
# SMOKE_TEST = False → full keyword list for all platforms

# %%
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from scrapers import mediacrawler_runner as mc
from config.queries_cn import (
    XHS_GROUPS, WEIBO_GROUPS, BILI_GROUPS, ZHIHU_GROUPS, DOUYIN_GROUPS,
)
from config.settings import (
    XHS_MAX_PER_KEYWORD,
    WEIBO_MAX_PER_KEYWORD, BILI_MAX_PER_KEYWORD,
    ZHIHU_MAX_PER_KEYWORD, DOUYIN_MAX_PER_KEYWORD,
)

SMOKE_TEST = True   # ← set False for full bulk run

# %%
def kws(group_map, smoke=False):
    """Flatten group map to keyword list. smoke=True → 1 keyword only."""
    all_kws = [kw for kws_ in group_map.values() for kw in kws_ if kw]
    return all_kws[:1] if smoke else all_kws

# %% [markdown]
# ## Xiaohongshu (RED) — priority #1
# MediaCrawler opens Chrome → scan QR with XHS app on your phone.
# Output: data/interim/xiaohongshu_*.csv

# %%
try:
    mc.run_platform(
        "xiaohongshu",
        kws(XHS_GROUPS, smoke=SMOKE_TEST),
        max_notes=XHS_MAX_PER_KEYWORD,
        get_comments=True,
        max_comments=20,
    )
    print("XHS done.")
except Exception as e:
    logging.error("XHS run failed: %s", e)

# %% [markdown]
# ## Weibo (priority #2) — accepts intl numbers, most reliable self-host path

# %%
try:
    mc.run_platform(
        "weibo",
        kws(WEIBO_GROUPS, smoke=SMOKE_TEST),
        max_notes=WEIBO_MAX_PER_KEYWORD,
    )
    print("Weibo done.")
except Exception as e:
    logging.error("Weibo run failed (fallback to Apify in 01b): %s", e)

# %% [markdown]
# ## Bilibili — public search, long-form reviews

# %%
try:
    mc.run_platform(
        "bilibili",
        kws(BILI_GROUPS, smoke=SMOKE_TEST),
        max_notes=BILI_MAX_PER_KEYWORD,
    )
    print("Bilibili done.")
except Exception as e:
    logging.error("Bilibili run failed: %s", e)

# %% [markdown]
# ## Zhihu — honest Q&A discussion

# %%
try:
    mc.run_platform(
        "zhihu",
        kws(ZHIHU_GROUPS, smoke=SMOKE_TEST),
        max_notes=ZHIHU_MAX_PER_KEYWORD,
    )
    print("Zhihu done.")
except Exception as e:
    logging.error("Zhihu run failed: %s", e)

# %% [markdown]
# ## Douyin — attempt self-host; device-binding may block, fallback in 01b

# %%
try:
    mc.run_platform(
        "douyin",
        kws(DOUYIN_GROUPS, smoke=SMOKE_TEST),
        max_notes=DOUYIN_MAX_PER_KEYWORD,
    )
    print("Douyin done.")
except Exception as e:
    logging.error("Douyin run failed (fallback to Apify in 01b): %s", e)

# %%
print("\nMediaCrawler runs done.")
print("Raw CSVs are in data/interim/. Proceed to 01c to normalize.")
print("If Weibo/Douyin failed login, run 01b (Apify fallback) first.")
