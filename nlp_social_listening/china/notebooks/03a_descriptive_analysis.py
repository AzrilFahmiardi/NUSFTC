# %% [markdown]
# # 03a · Descriptive analysis (Q1–Q6) — reuses sibling analysis modules
# Reuses `analysis/*` from `../nlp social listening/` (no package collision: this project
# has no `analysis` package). Produces the brief's output tables + a per-platform
# breakdown, saved to data/results/ and outputs/figures/.
#
# Run: `conda activate ml && python notebooks/03a_descriptive_analysis.py`

# %%
import ast
import logging
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from config.settings import DATA_PROCESSED, DATA_RESULTS, SIBLING_PROJECT

# Append sibling root so `analysis`/`visualization` resolve to the sibling project,
# while config/nlp/preprocessing stay local (this project's root is earlier on path).
sys.path.append(str(SIBLING_PROJECT))
from analysis import flavor_analysis, pain_analysis  # noqa: E402
from analysis._utils import explode_entity, sentiment_breakdown  # noqa: E402

# %% [markdown]
# ## Load enriched CSV; parse list-columns back from their string repr

# %%
LIST_COLS = ["flavors", "pains", "occasions", "formats", "brands"]


def _parse_lists(df):
    for c in LIST_COLS:
        df[c] = df[c].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    return df


df = _parse_lists(pd.read_csv(DATA_PROCESSED / "china_enriched.csv"))
print(f"Loaded {len(df)} enriched rows | platforms: {df['platform'].value_counts().to_dict()}")

# %% [markdown]
# ## Q1 — Flavor frequency + sentiment (with dominant platform)

# %%
flavor_freq = flavor_analysis.flavor_frequency(df)


def _dominant_platform(entity_col, entity):
    sub = df[df[entity_col].apply(lambda xs: isinstance(xs, list) and entity in xs)]
    return sub["platform"].value_counts().idxmax() if len(sub) else "—"


flavor_freq["top_platform"] = flavor_freq["flavor"].apply(lambda f: _dominant_platform("flavors", f))
flavor_freq.to_csv(DATA_RESULTS / "flavor_frequency.csv", index=False)
print(flavor_freq.head(10))

# %% [markdown]
# ## Q3 — Pain point ranking (frequency × severity)

# %%
pain_rank = pain_analysis.pain_ranking(df)
pain_rank.to_csv(DATA_RESULTS / "pain_point_frequency.csv", index=False)
print(pain_rank.head(10))

# Representative bilingual quotes for the top pains
for p in pain_rank["pain"].head(5):
    print(f"\n[{p}]")
    for ex in pain_analysis.pain_examples(df, p, n=2):
        print("  -", str(ex["text"])[:80], f"({ex['sentiment_score']:.2f})")

# %% [markdown]
# ## Q5 — Occasion distribution + Q4 format mentions

# %%
occ_tab = sentiment_breakdown(explode_entity(df, "occasions"), "occasions")
occ_tab.to_csv(DATA_RESULTS / "occasion_distribution.csv", index=False)
print(occ_tab)

fmt_tab = sentiment_breakdown(explode_entity(df, "formats"), "formats")
fmt_tab.to_csv(DATA_RESULTS / "format_mentions.csv", index=False)
print(fmt_tab)

# %% [markdown]
# ## Q6 — Competitor sentiment

# %%
comp_tab = sentiment_breakdown(explode_entity(df, "brands"), "brands")
comp_tab.to_csv(DATA_RESULTS / "competitor_sentiment.csv", index=False)
print(comp_tab)

# %% [markdown]
# ## Per-platform sentiment summary (methodology table for judges)

# %%
plat = df.groupby("platform").agg(
    posts=("tweet_id", "count"),
    pct_positive=("sentiment_label", lambda s: round((s == "positive").mean() * 100, 1)),
    pct_negative=("sentiment_label", lambda s: round((s == "negative").mean() * 100, 1)),
    avg_sentiment=("sentiment_score", "mean"),
).reset_index()
plat.to_csv(DATA_RESULTS / "platform_summary.csv", index=False)
print(plat)
print("\n03a done. Result CSVs in data/results/.")
