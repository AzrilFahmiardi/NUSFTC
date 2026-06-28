# %% [markdown]
# # 05 · Joint EN + ZH segmentation
# Merges the Twitter (English) and China (Chinese) enriched corpora and clusters on
# **language-agnostic entity + sentiment features** — NOT bilingual TF-IDF, which would
# trivially split clusters by language. This is the defensible joint method for judges.
#
# Features: sentiment_score, n_flavors/n_pains/n_occasions/n_formats, and one-hot
# indicators for the top flavors / occasions (shared entity vocabulary across languages).
#
# Run: `conda activate ml && python notebooks/05_joint_clustering_en_zh.py`

# %%
import ast
import logging
import sys
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from config.settings import DATA_PROCESSED, DATA_RESULTS, TWITTER_ENRICHED_CSV, SIBLING_PROJECT

sys.path.append(str(SIBLING_PROJECT))
from analysis import clustering  # noqa: E402

LIST_COLS = ["flavors", "pains", "occasions", "formats", "brands"]


def _load(path, source):
    df = pd.read_csv(path)
    for c in LIST_COLS:
        if c in df.columns:
            df[c] = df[c].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        else:
            df[c] = [[] for _ in range(len(df))]
    df["source"] = source
    if "platform" not in df.columns:
        df["platform"] = "twitter"
    return df

# %%
china = _load(DATA_PROCESSED / "china_enriched.csv", "china")
frames = [china]
if TWITTER_ENRICHED_CSV.exists():
    frames.append(_load(TWITTER_ENRICHED_CSV, "twitter"))
else:
    print(f"WARNING: {TWITTER_ENRICHED_CSV} not found — clustering China only.")

union = sorted(set().union(*[set(f.columns) for f in frames]))
df = pd.concat([f.reindex(columns=union) for f in frames], ignore_index=True)
print(f"Joint corpus: {len(df)} rows | source: {df['source'].value_counts().to_dict()}")

# %% [markdown]
# ## Build language-agnostic feature matrix

# %%
from collections import Counter

flavor_counts = Counter(f for fs in df["flavors"] if isinstance(fs, list) for f in fs)
occ_counts = Counter(o for os_ in df["occasions"] if isinstance(os_, list) for o in os_)
TOP_FLAVORS = [f for f, _ in flavor_counts.most_common(10)]
TOP_OCC = [o for o, _ in occ_counts.most_common(6)]

feat = pd.DataFrame(index=df.index)
feat["sentiment_score"] = df["sentiment_score"].fillna(0)
for col in ["n_flavors", "n_pains", "n_occasions", "n_formats"]:
    feat[col] = df[col].fillna(0)
for f in TOP_FLAVORS:
    feat[f"flav_{f}"] = df["flavors"].apply(lambda xs: int(isinstance(xs, list) and f in xs))
for o in TOP_OCC:
    feat[f"occ_{o}"] = df["occasions"].apply(lambda xs: int(isinstance(xs, list) and o in xs))

X = StandardScaler().fit_transform(feat.values)
print(f"Feature matrix: {X.shape} | features: {list(feat.columns)}")

# %% [markdown]
# ## Cluster (reuse sibling silhouette picker + fit)

# %%
best_k, scores = clustering.find_optimal_k(X)
km = clustering.fit(X, best_k)
df["joint_cluster"] = km.labels_
print(f"Best k={best_k} | silhouette: {scores}")

# %% [markdown]
# ## Profile clusters + language composition (proves it's NOT just a language split)

# %%
profiles = clustering.profile_clusters(df, cluster_col="joint_cluster")
lang_mix = (
    df.groupby("joint_cluster")["source"]
    .value_counts(normalize=True).unstack(fill_value=0).round(2)
    .add_prefix("pct_")
)
profiles = profiles.merge(lang_mix, left_on="cluster", right_index=True, how="left")

profiles.to_csv(DATA_RESULTS / "joint_cluster_profiles.csv", index=False)
print(profiles.to_string())
print("\nIf clusters mix china+twitter sources (not 100%/0%), the joint segmentation is "
      "capturing real cross-market consumer types, not a language artifact.")
