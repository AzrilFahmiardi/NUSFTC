# %% [markdown]
# # 02 · Preprocess + enrich (CJK-safe)
# china_all_raw.csv → clean (CJK-safe + jieba) → language route → dedup → routed
# sentiment (RoBERTa+SnowNLP / VADER) → entity extraction (bilingual dicts).
# Output: `data/processed/china_enriched.csv` (schema-mergeable with twitter_enriched.csv).
#
# Run: `conda activate ml && python notebooks/02_preprocess_and_enrich.py`

# %%
import logging
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from preprocessing import language_router, text_cleaner_cn, deduplicator
from nlp import sentiment_cn
from nlp.entity_extractor_cn import enrich_cn
from config.settings import DATA_RAW, DATA_PROCESSED

# %%
raw = pd.read_csv(DATA_RAW / "china_all_raw.csv")
print(f"Loaded {len(raw)} raw rows | platforms: {raw['platform'].value_counts().to_dict()}")

# %% [markdown]
# ## Language routing (adds detected_lang; keeps all rows)

# %%
df = language_router.route_languages(raw, text_col="text")

# %% [markdown]
# ## Clean (CJK-safe) + jieba tokenize

# %%
df = text_cleaner_cn.process_dataframe(df, text_col="text", lang_col="detected_lang")

# %% [markdown]
# ## Deduplicate (exact MD5 + near-dup). Near-dup on tokenized text, stop_words=None.

# %%
df = deduplicator.remove_exact_duplicates(df, text_col="clean_text")
# Near-dup: the sibling uses stop_words="english"; for CJK we run on the jieba-tokenized
# column where the English stop list is harmless (Chinese tokens are unaffected).
df = deduplicator.remove_near_duplicates(df, text_col="clean_text_no_stop")
print(f"After dedup: {len(df)} rows")

# %% [markdown]
# ## Self-seeding hygiene — drop rows mentioning our own product name
# The finals strategy doc (Section 11) flagged that the team's own product name appears in
# the China data (self-seeding contamination), which biases sentiment positive. Remove those
# rows so the corpus reflects organic consumer voice, not our own marketing/seeding.

# %%
MOBAI_TERMS = ["mobai", "mo bai", "茉白", "莫白", "茉百"]
_pat = "|".join(MOBAI_TERMS)
_seed_mask = df["text"].fillna("").str.lower().str.contains(_pat, regex=True)
n_seed = int(_seed_mask.sum())
df = df[~_seed_mask].reset_index(drop=True)
print(f"Removed {n_seed} self-seeding rows (own product name) -> {len(df)} rows")

# %% [markdown]
# ## Relevance filter — keep only rows about protein/drink (Weibo full-text search noise)
# Weibo keyword search returns off-topic posts that merely contain a fragment of the query
# (smoke test surfaced diet/cafe posts). Drop any row whose text mentions no protein/drink
# core term. XHS keywords are already protein-specific so few XHS rows are affected; logged
# per platform for transparency.

# %%
CORE_TERMS = ["蛋白", "乳清", "代餐", "奶昔", "酸奶", "饮料", "饮品",
              "protein", "whey", "shake", "yogurt", "yoghurt"]
_core_pat = "|".join(CORE_TERMS)
_rel_mask = df["text"].fillna("").str.lower().str.contains(_core_pat, regex=True)
print("Off-topic rows by platform:",
      df.loc[~_rel_mask, "platform"].value_counts().to_dict())
n_off = int((~_rel_mask).sum())
df = df[_rel_mask].reset_index(drop=True)
print(f"Removed {n_off} off-topic rows -> {len(df)} rows")

# %% [markdown]
# ## Sentiment (language-routed) — runs on ORIGINAL-language clean_text

# %%
df = sentiment_cn.analyze_dataframe(df, text_col="clean_text", lang_col="detected_lang")

# %% [markdown]
# ## Entity extraction (bilingual dicts) on clean_text

# %%
df = enrich_cn(df, text_col="clean_text")

# %%
out = DATA_PROCESSED / "china_enriched.csv"
df.to_csv(out, index=False)
print(f"Saved {len(df)} enriched rows -> {out}")
print("Sentiment dist:", df["sentiment_label"].value_counts().to_dict())
print("Lang dist:", df["detected_lang"].value_counts().to_dict())
print("Columns:", len(df.columns))

# Thesis check: per-platform sentiment. Expect Weibo/Douyin markedly less positive than
# XHS (~82% positive), confirming they surface the pain points XHS buries.
print("\nSentiment by platform (%):")
print((df.groupby("platform")["sentiment_label"]
         .value_counts(normalize=True).mul(100).round(1).unstack(fill_value=0)))
