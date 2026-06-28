# %% [markdown]
# # 01 · Smoke test (the spend gate)
# Run ONE keyword per path, verify the unified schema, and confirm the China enriched
# rows merge with `twitter_enriched.csv`. Fix the adapters here BEFORE bulk runs.
#
# Run: `conda activate ml && python notebooks/01_smoke_test.py`

# %%
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from scrapers import apify_client_xhs, normalize
from config.settings import TWITTER_ENRICHED_CSV, DATA_PROCESSED

# %% [markdown]
# ## 1. Apify XHS — one keyword, tiny cap (~$0.10). Inspect raw item schema.
# After running, eyeball the printed keys and adjust `scrapers/normalize._xhs_apify`
# if the actor uses different field names.

# %%
items = apify_client_xhs.run_search(
    keywords=["蛋白质饮料推荐"], max_per_keyword=20, dump_name="smoke_xhs.jsonl"
)
print(f"Collected {len(items)} XHS items")
if items:
    print("Sample item keys:", sorted(items[0].keys()))
    print("Sample item:", {k: items[0][k] for k in list(items[0])[:8]})

# %% [markdown]
# ## 2. Normalize → unified RAW schema

# %%
raw_df = normalize.normalize(items, platform="xiaohongshu")
print(raw_df[["tweet_id", "text", "favorite_count", "query_group", "platform"]].head())
assert list(raw_df.columns) == normalize.RAW_COLUMNS, "RAW schema mismatch!"

# %% [markdown]
# ## 3. Enrich the smoke rows end-to-end (clean → route → sentiment → entities)

# %%
from preprocessing import language_router, text_cleaner_cn
from nlp import sentiment_cn
from nlp.entity_extractor_cn import enrich_cn   # thin wrapper (see 02)

df = language_router.route_languages(raw_df, text_col="text")
df = text_cleaner_cn.process_dataframe(df, text_col="text", lang_col="detected_lang")
df = sentiment_cn.analyze_dataframe(df, text_col="clean_text", lang_col="detected_lang")
df = enrich_cn(df, text_col="clean_text")
print("Enriched columns:", len(df.columns))
print(df[["clean_text", "detected_lang", "sentiment_label", "flavors", "pains"]].head())

# %% [markdown]
# ## 4. Verify merge with the Twitter enriched CSV (column compatibility)

# %%
import pandas as pd

if TWITTER_ENRICHED_CSV.exists():
    tw = pd.read_csv(TWITTER_ENRICHED_CSV, nrows=5)
    union = sorted(set(tw.columns) | set(df.columns))
    merged = pd.concat(
        [tw.reindex(columns=union), df.reindex(columns=union)], ignore_index=True
    )
    print(f"Merge OK: twitter cols={len(tw.columns)}, china cols={len(df.columns)}, "
          f"union={len(union)}, merged rows={len(merged)}")
    missing_in_china = set(tw.columns) - set(df.columns)
    print("Twitter cols absent in China (expected NaN on merge):", missing_in_china)
else:
    print(f"WARNING: {TWITTER_ENRICHED_CSV} not found — run the sibling pipeline first.")

# %%
df.to_csv(DATA_PROCESSED / "smoke_china_enriched.csv", index=False)
print("Smoke test complete. Inspect smoke_china_enriched.csv, then proceed to bulk runs.")
