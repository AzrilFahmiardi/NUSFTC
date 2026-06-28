# %% [markdown]
# # 03b · Consumer segmentation (K-means) — China corpus
# Vectorizes the jieba-tokenized text with `stop_words=None` (the sibling `vectorize()`
# hard-codes English stopwords), then reuses the sibling clustering helpers
# (`find_optimal_k`, `fit`, `cluster_top_terms`, `profile_clusters`, `label_cluster`).
#
# Run: `conda activate ml && python notebooks/03b_clustering.py`

# %%
import ast
import logging
import sys
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from config.settings import (
    DATA_PROCESSED, DATA_RESULTS, SIBLING_PROJECT,
    TFIDF_MAX_FEATURES, TFIDF_MIN_DF, TFIDF_NGRAM_RANGE,
)

sys.path.append(str(SIBLING_PROJECT))
from analysis import clustering  # noqa: E402

# %%
LIST_COLS = ["flavors", "pains", "occasions", "formats", "brands"]
df = pd.read_csv(DATA_PROCESSED / "china_enriched.csv")
for c in LIST_COLS:
    df[c] = df[c].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

# Cluster the Chinese-language subset on tokenized text (en rows are sparse here).
texts = df["clean_text_no_stop"].fillna("")
mask = texts.str.len() > 0
df = df[mask].reset_index(drop=True)
texts = texts[mask].reset_index(drop=True)
print(f"Clustering {len(df)} rows")

# %% [markdown]
# ## Vectorize (stop_words=None for CJK) + pick k by silhouette

# %%
vec = TfidfVectorizer(
    max_features=TFIDF_MAX_FEATURES, min_df=TFIDF_MIN_DF,
    ngram_range=TFIDF_NGRAM_RANGE, stop_words=None,
)
X = vec.fit_transform(list(texts))

best_k, scores = clustering.find_optimal_k(X)
print(f"Best k={best_k} | silhouette scores: {scores}")

# %% [markdown]
# ## Fit + profile clusters

# %%
km = clustering.fit(X, best_k)
df["cluster"] = km.labels_

top_terms = clustering.cluster_top_terms(km, vec, top_n=10)
profiles = clustering.profile_clusters(df, cluster_col="cluster")
profiles["top_terms"] = profiles["cluster"].map(lambda c: ", ".join(top_terms.get(c, [])))
profiles["label"] = profiles.apply(
    lambda r: clustering.label_cluster(top_terms.get(r["cluster"], []), r.to_dict()), axis=1
)

profiles.to_csv(DATA_RESULTS / "cluster_profiles.csv", index=False)
df[["tweet_id", "platform", "cluster"]].to_csv(DATA_RESULTS / "cluster_assignments.csv", index=False)
print(profiles.to_string())
print("\n03b done. cluster_profiles.csv + cluster_assignments.csv in data/results/.")
