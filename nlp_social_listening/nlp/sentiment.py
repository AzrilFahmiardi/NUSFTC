"""
Sentiment analyzer — VADER (primary) + TextBlob (cross-validation consensus).
"""

import logging
import pandas as pd

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import SENTIMENT_POS_THRESHOLD, SENTIMENT_NEG_THRESHOLD

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()

    def _vader(self, text: str) -> dict:
        if not text:
            return {"compound": 0.0, "pos": 0.0, "neu": 0.0, "neg": 0.0}
        s = self.vader.polarity_scores(text)
        return {"compound": s["compound"], "pos": s["pos"], "neu": s["neu"], "neg": s["neg"]}

    def _textblob(self, text: str) -> dict:
        if not text:
            return {"polarity": 0.0, "subjectivity": 0.0}
        b = TextBlob(text)
        return {"polarity": b.sentiment.polarity, "subjectivity": b.sentiment.subjectivity}

    @staticmethod
    def label(score: float) -> str:
        if score >= SENTIMENT_POS_THRESHOLD:
            return "positive"
        if score <= SENTIMENT_NEG_THRESHOLD:
            return "negative"
        return "neutral"

    def analyze(self, text: str) -> dict:
        v = self._vader(text)
        t = self._textblob(text)
        consensus = (v["compound"] + t["polarity"]) / 2
        diff = abs(v["compound"] - t["polarity"])
        return {
            "vader_compound": v["compound"],
            "vader_pos": v["pos"],
            "vader_neu": v["neu"],
            "vader_neg": v["neg"],
            "textblob_polarity": t["polarity"],
            "textblob_subjectivity": t["subjectivity"],
            "sentiment_score": consensus,
            "sentiment_label": self.label(consensus),
            "sentiment_confidence": max(0.0, 1.0 - diff),
        }

    def analyze_dataframe(self, df: pd.DataFrame, text_col: str = "clean_text") -> pd.DataFrame:
        df = df.copy()
        rows = df[text_col].fillna("").apply(lambda t: pd.Series(self.analyze(t)))
        df = pd.concat([df, rows], axis=1)
        logger.info("Sentiment distribution: %s", df["sentiment_label"].value_counts().to_dict())
        return df
