"""
Apify client for Xiaohongshu (小红书 / RED) — the PRIMARY path for XHS, which is
login-gated and hard to self-host on a non-China phone number.

Two passes:
  1. search  — easyapi/rednote-xiaohongshu-search-scraper, per keyword
  2. comments — easyapi/rednote-xiaohongshu-comments-scraper, on collected note urls

Raw dumps are persisted to data/interim/ immediately (brief §10: recover partial runs)
BEFORE normalization, so a mid-run failure never loses collected data.

Requires APIFY_TOKEN in .env. Cost ~ $0.005 / result (PAY_PER_EVENT) — bounded by
`max_per_keyword`. Verify run_input field names against the actor's schema on the
first smoke-test run; adjust _SEARCH_INPUT below if the actor expects different keys.
"""

import json
import logging
import os
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import (
    DATA_INTERIM, XHS_MAX_PER_KEYWORD, SCRAPE_DELAY_MIN,
    APIFY_XHS_SEARCH_ACTOR, APIFY_XHS_COMMENTS_ACTOR,
)
from config.queries_cn import XHS_GROUPS, group_for_keyword

load_dotenv(Path(__file__).parent.parent / ".env")
logger = logging.getLogger(__name__)


def _client():
    from apify_client import ApifyClient
    token = os.getenv("APIFY_TOKEN")
    if not token:
        raise RuntimeError("APIFY_TOKEN not set. Put it in nlp_social_china/.env")
    return ApifyClient(token)


def _dataset_id(run) -> str | None:
    """Get the run's default dataset id across apify-client versions (v3 returns a
    Pydantic `Run` object; older versions returned a dict)."""
    if isinstance(run, dict):
        return run.get("defaultDatasetId") or run.get("default_dataset_id")
    return getattr(run, "default_dataset_id", None)


def _search_input(keyword: str, limit: int) -> dict:
    # Field names per easyapi rednote search actor; confirm on smoke test.
    return {"keyword": keyword, "maxItems": limit, "sort": "general"}


def _comments_input(note_urls: list[str], limit: int) -> dict:
    return {"startUrls": [{"url": u} for u in note_urls], "maxItems": limit}


def run_search(keywords: list[str] | None = None,
               max_per_keyword: int = XHS_MAX_PER_KEYWORD,
               dump_name: str = "xhs_search_dump.jsonl") -> list[dict]:
    """Run XHS search for each keyword; tag keyword_source/platform/query_group.
    Appends every item to data/interim/<dump_name> as it arrives."""
    if keywords is None:
        keywords = [kw for kws in XHS_GROUPS.values() for kw in kws]
    client = _client()
    dump_path = DATA_INTERIM / dump_name
    results: list[dict] = []

    with open(dump_path, "a", encoding="utf-8") as fh:
        for kw in keywords:
            try:
                run = client.actor(APIFY_XHS_SEARCH_ACTOR).call(
                    run_input=_search_input(kw, max_per_keyword)
                )
                n = 0
                for item in client.dataset(_dataset_id(run)).iterate_items():
                    item["keyword_source"] = kw
                    item["platform"] = "xiaohongshu"
                    item["query_group"] = group_for_keyword(kw)
                    fh.write(json.dumps(item, ensure_ascii=False) + "\n")
                    results.append(item)
                    n += 1
                logger.info("XHS search '%s' -> %d items", kw, n)
            except Exception as e:
                logger.error("XHS search failed for '%s': %s", kw, e)
            time.sleep(SCRAPE_DELAY_MIN)

    logger.info("XHS search total: %d items -> %s", len(results), dump_path)
    return results


def run_comments(note_urls: list[str], max_per_note: int = 30,
                 dump_name: str = "xhs_comments_dump.jsonl") -> list[dict]:
    """Fetch comments for collected note urls (consumer pain points live here)."""
    if not note_urls:
        return []
    client = _client()
    dump_path = DATA_INTERIM / dump_name
    results: list[dict] = []
    with open(dump_path, "a", encoding="utf-8") as fh:
        # batch urls to limit per-run cost
        for i in range(0, len(note_urls), 20):
            batch = note_urls[i:i + 20]
            try:
                run = client.actor(APIFY_XHS_COMMENTS_ACTOR).call(
                    run_input=_comments_input(batch, max_per_note)
                )
                for item in client.dataset(_dataset_id(run)).iterate_items():
                    item["platform"] = "xiaohongshu"
                    item["query_group"] = "pain"      # comments mined mainly for pain/sensory
                    fh.write(json.dumps(item, ensure_ascii=False) + "\n")
                    results.append(item)
            except Exception as e:
                logger.error("XHS comments batch %d failed: %s", i, e)
            time.sleep(SCRAPE_DELAY_MIN)
    logger.info("XHS comments total: %d -> %s", len(results), dump_path)
    return results


def load_dump(dump_name: str) -> list[dict]:
    """Reload a previously saved jsonl dump (resume without re-spending)."""
    path = DATA_INTERIM / dump_name
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]
