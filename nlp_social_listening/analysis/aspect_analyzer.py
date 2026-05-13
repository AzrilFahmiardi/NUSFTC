"""
Aspect-Based Sentiment Analysis (ABSA) — Custom Pipeline

Not just "this review is negative" but "this review is negative ABOUT texture
but positive ABOUT taste." This is the flagship feature for the judges.

Usage:
    from analysis.aspect_analyzer import AspectAnalyzer
    analyzer = AspectAnalyzer()
    df = analyzer.analyze_dataframe(df)
    matrix = analyzer.get_aspect_sentiment_matrix(df)
"""

import re
import logging
from pathlib import Path
from collections import defaultdict

import pandas as pd
import numpy as np

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError:
    raise ImportError("pip install vaderSentiment")

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import ASPECTS

logger = logging.getLogger(__name__)


class AspectAnalyzer:
    """
    Aspect-Based Sentiment Analysis using keyword matching + sentence-level VADER.
    Identifies WHICH aspect is being discussed and the sentiment ABOUT that aspect.
    """

    def __init__(self, aspects: dict | None = None):
        self.aspects = aspects or ASPECTS
        self.vader = SentimentIntensityAnalyzer()

        # Precompile aspect patterns for performance
        self._patterns = {}
        for aspect, keywords in self.aspects.items():
            # Sort by length (longest first) to match multi-word before single
            sorted_kw = sorted(keywords, key=len, reverse=True)
            pattern = "|".join(re.escape(kw) for kw in sorted_kw)
            self._patterns[aspect] = re.compile(pattern, re.IGNORECASE)

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Handle common Indonesian and English sentence boundaries
        sentences = re.split(r"[.!?;]\s+|[\n\r]+", text)
        # Also split on commas if sentences are very long
        result = []
        for s in sentences:
            s = s.strip()
            if len(s) > 200:
                result.extend(s.split(", "))
            elif len(s) > 3:
                result.append(s)
        return result

    def detect_aspects(self, text: str) -> list[str]:
        """Detect which aspects are mentioned in the text."""
        found = []
        for aspect, pattern in self._patterns.items():
            if pattern.search(text):
                found.append(aspect)
        return found

    def analyze_text(self, text: str) -> list[dict]:
        """
        Analyze a single text for aspect-level sentiments.

        Returns list of {aspect, sentence, keywords_found, sentiment_score, sentiment_label}
        """
        if not text:
            return []

        results = []
        sentences = self._split_sentences(text)

        for sentence in sentences:
            for aspect, pattern in self._patterns.items():
                matches = pattern.findall(sentence)
                if matches:
                    score = self.vader.polarity_scores(sentence)["compound"]
                    label = (
                        "positive" if score >= 0.05
                        else "negative" if score <= -0.05
                        else "neutral"
                    )
                    results.append({
                        "aspect": aspect,
                        "sentence": sentence,
                        "keywords_found": matches,
                        "sentiment_score": score,
                        "sentiment_label": label,
                    })

        return results

    def analyze_dataframe(
        self,
        df: pd.DataFrame,
        text_col: str = "clean_text",
    ) -> pd.DataFrame:
        """
        Add aspect analysis to DataFrame.

        Adds columns: aspects_found, aspect_details (JSON), dominant_aspect
        """
        df = df.copy()

        all_aspects = []
        all_details = []
        dominant_aspects = []

        for text in df[text_col]:
            results = self.analyze_text(text or "")
            aspects_found = list(set(r["aspect"] for r in results))
            all_aspects.append(aspects_found)
            all_details.append(results)

            # Dominant = most negative aspect (biggest pain point)
            if results:
                most_neg = min(results, key=lambda r: r["sentiment_score"])
                dominant_aspects.append(most_neg["aspect"])
            else:
                dominant_aspects.append(None)

        df["aspects_found"] = all_aspects
        df["aspect_details"] = all_details
        df["dominant_aspect"] = dominant_aspects
        df["num_aspects"] = df["aspects_found"].apply(len)

        logger.info(
            "Aspect coverage: %d/%d texts have at least 1 aspect",
            (df["num_aspects"] > 0).sum(), len(df),
        )
        return df

    def get_aspect_sentiment_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate the Aspect-Sentiment Matrix — key deliverable for presentation.

        Returns DataFrame:
            aspect | positive_pct | neutral_pct | negative_pct | avg_score | count
        """
        if "aspect_details" not in df.columns:
            raise ValueError("Run analyze_dataframe first")

        aspect_data = defaultdict(lambda: {"pos": 0, "neu": 0, "neg": 0, "scores": []})

        for details in df["aspect_details"]:
            for d in details:
                aspect = d["aspect"]
                label = d["sentiment_label"]
                aspect_data[aspect][label[:3]] += 1
                aspect_data[aspect]["scores"].append(d["sentiment_score"])

        rows = []
        for aspect in self.aspects:
            data = aspect_data[aspect]
            total = data["pos"] + data["neu"] + data["neg"]
            if total == 0:
                continue
            rows.append({
                "aspect": aspect,
                "positive_pct": round(data["pos"] / total * 100, 1),
                "neutral_pct": round(data["neu"] / total * 100, 1),
                "negative_pct": round(data["neg"] / total * 100, 1),
                "avg_sentiment": round(np.mean(data["scores"]), 3) if data["scores"] else 0,
                "mention_count": total,
            })

        matrix = pd.DataFrame(rows).sort_values("negative_pct", ascending=False)
        return matrix

    def get_pain_point_hierarchy(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate Pain Point Hierarchy — ranked by frequency × negativity.

        The flagship deliverable:
        "Pain Point #1: texture (66% negative, intensity 4.2/5)"
        """
        matrix = self.get_aspect_sentiment_matrix(df)
        if matrix.empty:
            return matrix

        # Pain score = negative_pct × abs(avg_sentiment) × log(count)
        matrix["pain_score"] = (
            matrix["negative_pct"] / 100
            * abs(matrix["avg_sentiment"])
            * np.log1p(matrix["mention_count"])
        )
        matrix = matrix.sort_values("pain_score", ascending=False)
        matrix["rank"] = range(1, len(matrix) + 1)

        return matrix[["rank", "aspect", "negative_pct", "avg_sentiment", "mention_count", "pain_score"]]
