"""
Deduplication — exact (hash) + near-duplicate (TF-IDF cosine similarity).

VENDORED verbatim from `../nlp social listening/preprocessing/deduplicator.py`.
Copied (not imported) because the `preprocessing` package name collides across the
two sibling projects. Imports `config.settings.NEAR_DUP_THRESHOLD` from THIS project's
config (value identical to the sibling).
"""

import hashlib
import logging
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import NEAR_DUP_THRESHOLD

logger = logging.getLogger(__name__)


def _hash_text(t: str) -> str:
    return hashlib.md5(t.encode("utf-8")).hexdigest()


def remove_exact_duplicates(df: pd.DataFrame, text_col: str = "clean_text") -> pd.DataFrame:
    df = df.copy()
    df["_text_hash"] = df[text_col].apply(_hash_text)
    before = len(df)
    df = df.drop_duplicates(subset=["_text_hash"]).drop(columns="_text_hash").reset_index(drop=True)
    logger.info("Exact dedup: %d -> %d", before, len(df))
    return df


def remove_near_duplicates(
    df: pd.DataFrame,
    text_col: str = "clean_text",
    threshold: float = NEAR_DUP_THRESHOLD,
    chunk_size: int = 1000,
) -> pd.DataFrame:
    """Drop rows whose cosine similarity to an earlier kept row > threshold.
    Operates per chunk to keep memory bounded.

    NOTE: stop_words=None (not "english") so Chinese tokens are not silently kept/dropped
    by an English stop list; the input is expected to be the jieba-tokenized column.
    """
    if len(df) < 2:
        return df.copy()

    texts = df[text_col].fillna("").tolist()
    vec = TfidfVectorizer(min_df=1, ngram_range=(1, 2), stop_words=None)
    X = vec.fit_transform(texts)

    keep_mask = np.ones(len(df), dtype=bool)
    for start in range(0, len(df), chunk_size):
        end = min(start + chunk_size, len(df))
        sims = cosine_similarity(X[start:end], X[:end])
        for i in range(end - start):
            if not keep_mask[start + i]:
                continue
            row = sims[i]
            row[start + i] = 0  # ignore self
            for j in range(start + i):
                if keep_mask[j] and row[j] >= threshold:
                    keep_mask[start + i] = False
                    break

    out = df[keep_mask].reset_index(drop=True)
    logger.info("Near-dup (>=%.2f): %d -> %d", threshold, len(df), len(out))
    return out


def deduplicate(df: pd.DataFrame, text_col: str = "clean_text") -> pd.DataFrame:
    df = remove_exact_duplicates(df, text_col)
    df = remove_near_duplicates(df, text_col)
    return df
