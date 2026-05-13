"""
Keyword Extractor — TF-IDF + N-gram + Sensory Lexicon

Multi-method keyword extraction for protein drink reviews.

Usage:
    from analysis.keyword_extractor import KeywordExtractor
    extractor = KeywordExtractor()
    top_keywords = extractor.extract_tfidf(df["clean_text_no_stop"])
    ngrams = extractor.extract_ngrams(df["clean_text_no_stop"])
"""

import logging
from collections import Counter
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import SENSORY_PRESERVE

logger = logging.getLogger(__name__)


class KeywordExtractor:
    """Multi-method keyword extraction optimized for sensory/product reviews."""

    def extract_tfidf(
        self,
        texts: pd.Series,
        top_n: int = 30,
        max_features: int = 5000,
    ) -> pd.DataFrame:
        """
        Extract top keywords using TF-IDF.

        Returns DataFrame with columns: keyword, tfidf_score
        """
        texts = texts.dropna().astype(str)
        tfidf = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),
            min_df=3,
            max_df=0.95,
        )
        matrix = tfidf.fit_transform(texts)
        feature_names = tfidf.get_feature_names_out()

        # Average TF-IDF score per term across all documents
        avg_scores = matrix.mean(axis=0).A1
        top_idx = avg_scores.argsort()[-top_n:][::-1]

        results = [
            {"keyword": feature_names[i], "tfidf_score": round(avg_scores[i], 4)}
            for i in top_idx
        ]
        return pd.DataFrame(results)

    def extract_ngrams(
        self,
        texts: pd.Series,
        n: int = 2,
        top_n: int = 30,
    ) -> pd.DataFrame:
        """
        Extract top n-grams (bigrams/trigrams).

        Returns DataFrame with columns: ngram, count
        """
        texts = texts.dropna().astype(str)
        vec = CountVectorizer(ngram_range=(n, n), min_df=2, max_df=0.95)
        matrix = vec.fit_transform(texts)
        feature_names = vec.get_feature_names_out()

        counts = matrix.sum(axis=0).A1
        top_idx = counts.argsort()[-top_n:][::-1]

        results = [
            {"ngram": feature_names[i], "count": int(counts[i])}
            for i in top_idx
        ]
        return pd.DataFrame(results)

    def extract_sensory_keywords(self, texts: pd.Series) -> pd.DataFrame:
        """
        Count frequency of sensory vocabulary words.

        Returns DataFrame with columns: word, count, percentage
        """
        all_words = " ".join(texts.dropna().astype(str)).lower().split()
        total = len(all_words)

        sensory_counts = Counter()
        for w in all_words:
            if w in SENSORY_PRESERVE:
                sensory_counts[w] += 1

        results = [
            {
                "word": word,
                "count": count,
                "percentage": round(count / total * 100, 2) if total > 0 else 0,
            }
            for word, count in sensory_counts.most_common(50)
        ]
        return pd.DataFrame(results)

    def compare_positive_negative(
        self,
        df: pd.DataFrame,
        text_col: str = "clean_text_no_stop",
        label_col: str = "consensus_label",
        top_n: int = 20,
    ) -> dict:
        """
        Compare top keywords between positive and negative reviews.

        Returns dict with 'positive_keywords' and 'negative_keywords' DataFrames.
        """
        pos_texts = df[df[label_col] == "positive"][text_col]
        neg_texts = df[df[label_col] == "negative"][text_col]

        return {
            "positive_keywords": self.extract_tfidf(pos_texts, top_n=top_n),
            "negative_keywords": self.extract_tfidf(neg_texts, top_n=top_n),
            "positive_bigrams": self.extract_ngrams(pos_texts, n=2, top_n=top_n),
            "negative_bigrams": self.extract_ngrams(neg_texts, n=2, top_n=top_n),
        }

    def extract_complaint_keywords(
        self,
        df: pd.DataFrame,
        text_col: str = "clean_text_no_stop",
        label_col: str = "consensus_label",
    ) -> pd.DataFrame:
        """Extract keywords that appear disproportionately in negative reviews."""
        neg = df[df[label_col] == "negative"][text_col]
        pos = df[df[label_col] == "positive"][text_col]

        neg_tfidf = self.extract_tfidf(neg, top_n=50)
        pos_tfidf = self.extract_tfidf(pos, top_n=50)

        # Merge and find words that are much more common in negative
        merged = neg_tfidf.merge(
            pos_tfidf, on="keyword", how="left", suffixes=("_neg", "_pos")
        )
        merged["tfidf_score_pos"] = merged["tfidf_score_pos"].fillna(0)
        merged["complaint_ratio"] = merged["tfidf_score_neg"] / (merged["tfidf_score_pos"] + 0.0001)
        merged = merged.sort_values("complaint_ratio", ascending=False)

        return merged.head(20)
