# %% [markdown]
# # 01b · Apify scraping — Weibo + Douyin (pain + competitor weighted)
# **This is where Apify spend begins** (~$0.005/result; Weibo ~$0.019, Douyin ~$0.005).
# Xiaohongshu is ALREADY collected (`data/raw/xiaohongshu_raw.csv`, ~11k rows) — do NOT
# re-scrape it here. This round adds Weibo + Douyin to capture the pain points XHS buries
# (XHS is a 种草 platform, ~82% positive). See the finals strategy doc, Section 11.
#
# Run: `conda activate ml && python notebooks/01b_scrape_apify.py`
# Prereq: APIFY_TOKEN in nlp_social_china/.env
#
# ## Free-credit account cycling (idempotent)
# One free Apify account ≈ $5 credit ≈ ~250 Weibo posts, so the ~800-1,000 target needs
# 3-4 throwaway accounts. Workflow:
#   1. Run this script until the account's credit is exhausted (actor errors out / stops).
#   2. Create a new free Apify account, put its token in `.env` (replace APIFY_TOKEN).
#   3. Re-run this script. Keywords already present in the interim dumps are SKIPPED, so
#      no spend is duplicated — it resumes exactly where the previous account stopped.

# %%
import logging
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from scrapers import apify_client_generic
from config.queries_cn import WEIBO_GROUPS, DOUYIN_GROUPS
from config.settings import (
    APIFY_WEIBO_ACTOR, APIFY_DOUYIN_ACTOR, WEIBO_MAX_PAGES, DOUYIN_MAX_PER_QUERY,
)

logger = logging.getLogger("01b")


def _remaining(groups: dict, dump_name: str, min_keep: int = 1) -> list[str]:
    """Flatten a platform's keyword groups, dropping keywords already scraped to a healthy
    count (>= min_keep) in the dump. Makes account-cycling resume without double-paying.
    For Douyin set min_keep=12 (healthy = the free-tier cap) so keywords that came back
    degraded (1 item, account's free runs exhausted) get retried on the next fresh account."""
    all_kws = [kw for kws in groups.values() for kw in kws if kw]
    counts = Counter(it.get("keyword_source") for it in apify_client_generic.load_dump(dump_name))
    todo = [kw for kw in all_kws if counts.get(kw, 0) < min_keep]
    logger.info("%s: %d keywords total, %d already done (>=%d), %d remaining",
                dump_name, len(all_kws), len(all_kws) - len(todo), min_keep, len(todo))
    return todo

# %% [markdown]
# ## Xiaohongshu — ALREADY DONE (data/raw/xiaohongshu_raw.csv). Intentionally skipped.
# Re-enable ONLY if you need to rebuild the XHS dataset from scratch (re-incurs spend).

# %%
# from config.queries_cn import XHS_GROUPS
# from config.settings import XHS_MAX_PER_KEYWORD
# from scrapers import apify_client_xhs
# xhs_items = apify_client_xhs.run_search(max_per_keyword=XHS_MAX_PER_KEYWORD)
# note_urls = [u for it in xhs_items if (u := it.get("url") or it.get("noteUrl"))][:300]
# apify_client_xhs.run_comments(note_urls, max_per_note=30)

# %% [markdown]
# ## Douyin FIRST — primary, cheap, high-relevance pain-point signal.
# Run before Weibo so the highest-value data is secured before the costlier Weibo actor
# can drain a free account's credit. zen-studio actor: `keywords` array + `maxResultsPerQuery`.

# %%
douyin_kws = _remaining(DOUYIN_GROUPS, "douyin_apify_dump.jsonl", min_keep=12)
if douyin_kws:
    apify_client_generic.run_keywords(
        APIFY_DOUYIN_ACTOR, douyin_kws, "douyin", DOUYIN_GROUPS,
        input_builder=lambda kw: {
            "keywords": [kw.lstrip("#")], "maxResultsPerQuery": DOUYIN_MAX_PER_QUERY,
            "sort": "general",
        },
        dump_name="douyin_apify_dump.jsonl",
    )

# %% [markdown]
# ## Weibo — sian.agency/weibo-scraper, `searchWeibo` keyword mode (no login cookie).
# Supporting/credibility platform; costlier (~$18.75/1k). Compact no-space keywords only.

# %%
weibo_kws = _remaining(WEIBO_GROUPS, "weibo_apify_dump.jsonl")
if weibo_kws:
    apify_client_generic.run_keywords(
        APIFY_WEIBO_ACTOR, weibo_kws, "weibo", WEIBO_GROUPS,
        input_builder=lambda kw: {
            "operation": "searchWeibo", "keyword": kw, "maxPages": WEIBO_MAX_PAGES,
        },
        dump_name="weibo_apify_dump.jsonl",
    )

# %%
print("Apify runs done. Dumps saved in data/interim/. Proceed to 01c to normalize.")
print("If credit ran out mid-run, swap APIFY_TOKEN in .env and re-run — done keywords skip.")
