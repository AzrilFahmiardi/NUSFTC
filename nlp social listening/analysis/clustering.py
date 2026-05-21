"""
BONUS — K-means clustering for consumer segments.
TF-IDF + KMeans, silhouette score to pick k. Per-cluster profile for radar viz.
"""

from collections import Counter
import logging
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import (
    TFIDF_MAX_FEATURES, TFIDF_MIN_DF, TFIDF_NGRAM_RANGE,
    KMEANS_K_RANGE, KMEANS_RANDOM_STATE, KMEANS_N_INIT,
)

logger = logging.getLogger(__name__)


def vectorize(texts) -> tuple:
    vec = TfidfVectorizer(
        max_features=TFIDF_MAX_FEATURES,
        min_df=TFIDF_MIN_DF,
        ngram_range=TFIDF_NGRAM_RANGE,
        stop_words="english",
    )
    X = vec.fit_transform(list(texts))
    return X, vec


def find_optimal_k(X, k_range: tuple = KMEANS_K_RANGE) -> tuple[int, dict]:
    scores = {}
    for k in range(k_range[0], k_range[1] + 1):
        km = KMeans(n_clusters=k, random_state=KMEANS_RANDOM_STATE, n_init=KMEANS_N_INIT)
        labels = km.fit_predict(X)
        if len(set(labels)) < 2:
            continue
        scores[k] = silhouette_score(X, labels, sample_size=min(2000, X.shape[0]))
    best_k = max(scores, key=scores.get)
    logger.info("Silhouette scores: %s -> best k=%d", scores, best_k)
    return best_k, scores


def fit(X, k: int) -> KMeans:
    km = KMeans(n_clusters=k, random_state=KMEANS_RANDOM_STATE, n_init=KMEANS_N_INIT)
    km.fit(X)
    return km


def cluster_top_terms(km: KMeans, vec: TfidfVectorizer, top_n: int = 10) -> dict[int, list[str]]:
    features = vec.get_feature_names_out()
    out = {}
    for i, center in enumerate(km.cluster_centers_):
        top_idx = center.argsort()[-top_n:][::-1]
        out[i] = [features[j] for j in top_idx]
    return out


def _top_entity(series: pd.Series) -> str:
    c = Counter()
    for lst in series:
        if isinstance(lst, list):
            c.update(lst)
    return c.most_common(1)[0][0] if c else "—"


def profile_clusters(df: pd.DataFrame, cluster_col: str = "cluster") -> pd.DataFrame:
    """Per cluster: size%, dominant flavor / pain / occasion / format, avg sentiment."""
    rows = []
    total = len(df)
    for cid, sub in df.groupby(cluster_col):
        rows.append({
            "cluster":          int(cid),
            "size":             int(len(sub)),
            "size_pct":         round(len(sub) / total * 100, 1),
            "top_flavor":       _top_entity(sub["flavors"]),
            "top_pain":         _top_entity(sub["pains"]),
            "top_occasion":     _top_entity(sub["occasions"]),
            "top_format":       _top_entity(sub["formats"]),
            "avg_sentiment":    round(sub["sentiment_score"].mean(), 3),
            "pct_positive":     round((sub["sentiment_label"] == "positive").mean() * 100, 1),
        })
    return pd.DataFrame(rows).sort_values("size_pct", ascending=False).reset_index(drop=True)


def label_cluster(top_terms: list[str], profile_row: dict) -> str:
    """Heuristic human-readable label from profile."""
    parts = []
    if profile_row.get("top_occasion") and profile_row["top_occasion"] != "—":
        parts.append(profile_row["top_occasion"].title().replace("_", "-"))
    if profile_row.get("top_flavor") and profile_row["top_flavor"] != "—":
        parts.append(profile_row["top_flavor"].title())
    if profile_row.get("top_pain") and profile_row["top_pain"] != "—":
        parts.append(f"({profile_row['top_pain']})")
    return " / ".join(parts) if parts else " ".join(top_terms[:3])
