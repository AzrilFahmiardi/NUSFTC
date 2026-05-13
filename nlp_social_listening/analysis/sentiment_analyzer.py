"""
Sentiment Analyzer — Dual Engine (VADER + TextBlob)

VADER optimized for social media, TextBlob for cross-validation.

Usage:
    from analysis.sentiment_analyzer import SentimentAnalyzer
    analyzer = SentimentAnalyzer()
    df = analyzer.analyze_dataframe(df)
"""

import logging
from pathlib import Path

import pandas as pd
import numpy as np

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError:
    raise ImportError("pip install vaderSentiment")

try:
    from textblob import TextBlob
except ImportError:
    raise ImportError("pip install textblob")

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Dual-engine sentiment analysis with consensus scoring."""

    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()

    def vader_score(self, text: str) -> dict:
        """Get VADER sentiment scores."""
        if not text:
            return {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
        scores = self.vader.polarity_scores(text)
        return {
            "compound": scores["compound"],
            "pos": scores["pos"],
            "neu": scores["neu"],
            "neg": scores["neg"],
        }

    def textblob_score(self, text: str) -> dict:
        """Get TextBlob polarity and subjectivity."""
        if not text:
            return {"polarity": 0, "subjectivity": 0}
        blob = TextBlob(text)
        return {
            "polarity": blob.sentiment.polarity,
            "subjectivity": blob.sentiment.subjectivity,
        }

    def classify_sentiment(self, compound: float) -> str:
        """Classify compound score into label."""
        if compound >= 0.05:
            return "positive"
        elif compound <= -0.05:
            return "negative"
        return "neutral"

    def consensus_score(self, vader_compound: float, tb_polarity: float) -> dict:
        """Compute consensus between VADER and TextBlob."""
        avg = (vader_compound + tb_polarity) / 2
        label = self.classify_sentiment(avg)

        # Confidence: how much the two engines agree
        diff = abs(vader_compound - tb_polarity)
        confidence = max(0, 1 - diff)

        return {"consensus_score": avg, "consensus_label": label, "confidence": confidence}

    def analyze_text(self, text: str) -> dict:
        """Full sentiment analysis on a single text."""
        v = self.vader_score(text)
        t = self.textblob_score(text)
        c = self.consensus_score(v["compound"], t["polarity"])
        return {
            "vader_compound": v["compound"],
            "vader_pos": v["pos"],
            "vader_neu": v["neu"],
            "vader_neg": v["neg"],
            "textblob_polarity": t["polarity"],
            "textblob_subjectivity": t["subjectivity"],
            **c,
        }

    def analyze_dataframe(self, df: pd.DataFrame, text_col: str = "clean_text") -> pd.DataFrame:
        """
        Add sentiment columns to DataFrame.

        Returns DataFrame with columns:
            vader_compound, vader_pos/neu/neg, textblob_polarity/subjectivity,
            consensus_score, consensus_label, confidence
        """
        df = df.copy()
        results = df[text_col].apply(lambda t: pd.Series(self.analyze_text(t or "")))
        df = pd.concat([df, results], axis=1)

        logger.info(
            "Sentiment distribution: %s",
            df["consensus_label"].value_counts().to_dict(),
        )
        return df

    def get_summary_stats(self, df: pd.DataFrame) -> dict:
        """Get summary statistics of sentiment analysis."""
        if "consensus_label" not in df.columns:
            return {}
        counts = df["consensus_label"].value_counts()
        total = len(df)
        return {
            "total_analyzed": total,
            "positive": int(counts.get("positive", 0)),
            "neutral": int(counts.get("neutral", 0)),
            "negative": int(counts.get("negative", 0)),
            "positive_pct": round(counts.get("positive", 0) / total * 100, 1),
            "negative_pct": round(counts.get("negative", 0) / total * 100, 1),
            "avg_vader_compound": round(df["vader_compound"].mean(), 3),
            "avg_confidence": round(df["confidence"].mean(), 3),
        }
