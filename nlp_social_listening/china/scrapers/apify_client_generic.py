"""
Generic Apify fallback client — for Weibo / Douyin / Bilibili when the self-hosted
MediaCrawler path fails (e.g. throwaway-account login challenged, geoblock).

Thin wrapper: pass an actor slug + run_input; items are dumped to interim then returned.
The caller normalizes via scrapers/normalize.py with the matching platform name.
"""

import json
import logging
import os
import time
from pathlib import Path

from dotenv import load_dotenv

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import DATA_INTERIM, SCRAPE_DELAY_MIN

load_dotenv(Path(__file__).parent.parent / ".env")
logger = logging.getLogger(__name__)


def _client():
    from apify_client import ApifyClient
    token = os.getenv("APIFY_TOKEN")
    if not token:
        raise RuntimeError("APIFY_TOKEN not set. Put it in nlp_social_china/.env")
    return ApifyClient(token)


def _dataset_id(run) -> str | None:
    """Get the run's default dataset id across apify-client versions.
    v3 returns a Pydantic `Run` object (attribute `default_dataset_id`);
    older versions returned a dict (`defaultDatasetId`)."""
    if isinstance(run, dict):
        return run.get("defaultDatasetId") or run.get("default_dataset_id")
    return getattr(run, "default_dataset_id", None)


def run_actor(actor_slug: str, run_input: dict, platform: str,
              query_group: str = "flavor", keyword_source: str = "",
              dump_name: str | None = None) -> list[dict]:
    """Run one Apify actor, tag + dump items, return them."""
    client = _client()
    dump_path = DATA_INTERIM / (dump_name or f"{platform}_apify_dump.jsonl")
    results: list[dict] = []
    try:
        run = client.actor(actor_slug).call(run_input=run_input)
        with open(dump_path, "a", encoding="utf-8") as fh:
            for item in client.dataset(_dataset_id(run)).iterate_items():
                item["platform"] = platform
                item["query_group"] = query_group
                item["keyword_source"] = keyword_source
                fh.write(json.dumps(item, ensure_ascii=False) + "\n")
                results.append(item)
    except Exception as e:
        logger.error("Apify actor '%s' failed: %s", actor_slug, e)
    logger.info("Apify %s via %s -> %d items", platform, actor_slug, len(results))
    time.sleep(SCRAPE_DELAY_MIN)
    return results


def run_keywords(actor_slug: str, keywords: list[str], platform: str,
                 groups_map: dict[str, list[str]],
                 input_builder, dump_name: str | None = None) -> list[dict]:
    """Run an actor across many keywords. `input_builder(kw)` -> run_input dict.
    `groups_map` maps group -> keyword list (to tag query_group per keyword)."""
    kw_to_group = {kw: g for g, kws in groups_map.items() for kw in kws}
    all_items = []
    for kw in keywords:
        items = run_actor(
            actor_slug, input_builder(kw), platform,
            query_group=kw_to_group.get(kw, "flavor"),
            keyword_source=kw, dump_name=dump_name,
        )
        all_items.extend(items)
    return all_items


def load_dump(dump_name: str) -> list[dict]:
    path = DATA_INTERIM / dump_name
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]
