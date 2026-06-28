# %% [markdown]
# # 01c · Normalize all sources → unified RAW schema
# Reads MediaCrawler CSVs + Apify jsonl dumps from data/interim/, maps each platform's
# native fields to the canonical RAW schema (MD5-hashing authors), writes
# `data/raw/<platform>_raw.csv` and the merged `china_all_raw.csv`.
#
# Run: `conda activate ml && python notebooks/01c_normalize_to_raw.py`

# %%
import json
import logging
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from scrapers import normalize
from config.settings import DATA_INTERIM, DATA_RAW

# %% [markdown]
# ## Apify jsonl dumps → normalized raw CSVs

# %%
APIFY_DUMPS = {
    "xiaohongshu": ["xhs_search_dump.jsonl", "xhs_comments_dump.jsonl"],
    "weibo":       ["weibo_apify_dump.jsonl"],
    "douyin":      ["douyin_apify_dump.jsonl"],
}

for platform, dumps in APIFY_DUMPS.items():
    records = []
    for name in dumps:
        path = DATA_INTERIM / name
        if path.exists():
            with open(path, encoding="utf-8") as fh:
                records += [json.loads(l) for l in fh if l.strip()]
    if records:
        df = normalize.normalize(records, platform=platform)
        df.to_csv(DATA_RAW / f"{platform}_raw.csv", index=False)
        print(f"{platform}: {len(df)} rows -> {platform}_raw.csv")

# %% [markdown]
# ## MediaCrawler CSV outputs → normalized raw CSVs
# MediaCrawler writes `data/interim/<platform>_*.csv` (copied by the runner).
# We concat per platform, convert to records, and normalize.

# %%
# xiaohongshu_mc = MediaCrawler XHS output (different field names than Apify)
# other platforms share the same field map regardless of source
MC_PLATFORMS = [
    ("xiaohongshu", "xiaohongshu_mc"),  # (output file prefix, normalize key)
    ("weibo",       "weibo"),
    ("bilibili",    "bilibili"),
    ("zhihu",       "zhihu"),
    ("douyin",      "douyin"),
]

for file_prefix, norm_key in MC_PLATFORMS:
    csvs = sorted(DATA_INTERIM.glob(f"{file_prefix}_*.csv"))
    if not csvs:
        continue
    frames = [pd.read_csv(c) for c in csvs]
    records = pd.concat(frames, ignore_index=True).to_dict("records")
    df = normalize.normalize(records, platform=norm_key)
    # Merge with any Apify-sourced file for the same platform.
    out = DATA_RAW / f"{file_prefix}_raw.csv"
    if out.exists():
        df = pd.concat([pd.read_csv(out), df], ignore_index=True)
    df.to_csv(out, index=False)
    print(f"{file_prefix} (MediaCrawler): {len(df)} rows -> {file_prefix}_raw.csv")

# %% [markdown]
# ## Merge all platforms → china_all_raw.csv

# %%
all_df = normalize.concat_all_raw(DATA_RAW, DATA_RAW / "china_all_raw.csv")
print(f"Total raw rows: {len(all_df)}")
print(all_df["platform"].value_counts())
