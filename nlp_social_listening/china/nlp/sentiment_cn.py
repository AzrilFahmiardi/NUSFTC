"""
Language-routed sentiment — mirrors the sibling project's VADER+TextBlob consensus
pattern, but per language:

  zh rows : RoBERTa-JD (primary, binary) + SnowNLP (cross-validator) -> consensus
  en rows : reuse sibling SentimentAnalyzer (VADER + TextBlob) unchanged
  other   : VADER fallback (degrades gracefully)

Output columns (superset, schema-compatible with twitter_enriched.csv):
  sentiment_score, sentiment_label, sentiment_confidence      [all rows]
  vader_compound, vader_pos, vader_neu, vader_neg,
  textblob_polarity, textblob_subjectivity                    [en rows; NaN for zh]
  roberta_signed, snownlp_signed                              [zh rows; NaN for en]

Sentiment runs on ORIGINAL-LANGUAGE text (no pre-translation) per brief §10.2.
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import (
    SENTIMENT_POS_THRESHOLD, SENTIMENT_NEG_THRESHOLD,
    CN_SENTIMENT_MODEL, CN_SENTIMENT_BATCH_SIZE, CN_SENTIMENT_MAX_LEN,
)

# English analyzer is vendored locally (the `nlp` package name collides with the
# sibling project, so it cannot be safely imported at runtime).
from nlp.sentiment_en import SentimentAnalyzer as EnglishSentimentAnalyzer

logger = logging.getLogger(__name__)

_CANONICAL = ["sentiment_score", "sentiment_label", "sentiment_confidence"]
_EN_COLS = ["vader_compound", "vader_pos", "vader_neu", "vader_neg",
            "textblob_polarity", "textblob_subjectivity"]
_ZH_COLS = ["roberta_signed", "snownlp_signed"]
ALL_SENTIMENT_COLS = _CANONICAL + _EN_COLS + _ZH_COLS


def _label(score: float) -> str:
    if score >= SENTIMENT_POS_THRESHOLD:
        return "positive"
    if score <= SENTIMENT_NEG_THRESHOLD:
        return "negative"
    return "neutral"


class ChineseSentimentAnalyzer:
    """RoBERTa-JD (binary) primary + SnowNLP cross-validator, consensus + confidence."""

    def __init__(self):
        self._pipe = None        # lazy — avoids importing torch until needed
        self._snownlp = None

    def _load(self):
        if self._pipe is None:
            from transformers import pipeline
            logger.info("Loading Chinese sentiment model: %s", CN_SENTIMENT_MODEL)
            self._pipe = pipeline(
                "text-classification",
                model=CN_SENTIMENT_MODEL,
                truncation=True,
                max_length=CN_SENTIMENT_MAX_LEN,
            )
        if self._snownlp is None:
            from snownlp import SnowNLP
            self._snownlp = SnowNLP

    @staticmethod
    def _roberta_signed(result: dict) -> float:
        """Map {label, score} -> signed score in [-1, 1]. Label is 'positive (stars 4 and 5)'
        / 'negative (stars 1, 2 and 3)' or similar; we key on the word 'positive'."""
        score = float(result.get("score", 0.0))
        label = str(result.get("label", "")).lower()
        return score if "pos" in label or label.endswith("1") else -score

    def _snownlp_signed(self, text: str) -> float:
        try:
            return 2.0 * float(self._snownlp(text).sentiments) - 1.0   # [0,1] -> [-1,1]
        except Exception:
            return 0.0

    def analyze_batch(self, texts: list[str]) -> list[dict]:
        self._load()
        clean = [t if isinstance(t, str) and t.strip() else "无" for t in texts]
        roberta = self._pipe(clean, batch_size=CN_SENTIMENT_BATCH_SIZE,
                             truncation=True, max_length=CN_SENTIMENT_MAX_LEN)
        out = []
        for text, r in zip(clean, roberta):
            rs = self._roberta_signed(r)
            ss = self._snownlp_signed(text)
            consensus = (rs + ss) / 2.0
            out.append({
                "roberta_signed": rs,
                "snownlp_signed": ss,
                "sentiment_score": consensus,
                "sentiment_label": _label(consensus),
                "sentiment_confidence": max(0.0, 1.0 - abs(rs - ss)),
                **{c: np.nan for c in _EN_COLS},
            })
        return out


def _empty_result() -> dict:
    return {c: np.nan for c in ALL_SENTIMENT_COLS}


def analyze_dataframe(df: pd.DataFrame, text_col: str = "clean_text",
                      lang_col: str = "detected_lang") -> pd.DataFrame:
    """Route by language, write the unified sentiment schema for every row.

    Builds one result dict per row (full ALL_SENTIMENT_COLS keys, NaN where N/A) and
    concatenates as a DataFrame, so pandas infers each column's dtype from the data
    (avoids LossySetitemError from assigning strings into pre-created float columns).
    """
    df = df.reset_index(drop=True).copy()
    is_zh = df[lang_col].astype(str).str.startswith("zh")
    results: list[dict] = [None] * len(df)

    # ── English (+ other) rows: VADER + TextBlob ────────────────────
    en_analyzer = EnglishSentimentAnalyzer()
    for i in df.index[~is_zh]:
        txt = df.at[i, text_col]
        res = _empty_result()
        res.update(en_analyzer.analyze(txt if isinstance(txt, str) else ""))
        results[i] = res

    # ── Chinese rows: RoBERTa + SnowNLP (batched) ───────────────────
    zh_idx = df.index[is_zh].tolist()
    if zh_idx:
        cn_analyzer = ChineseSentimentAnalyzer()
        texts = [df.at[i, text_col] for i in zh_idx]
        batch = cn_analyzer.analyze_batch(texts)
        for i, res in zip(zh_idx, batch):
            full = _empty_result()
            full.update(res)
            results[i] = full

    res_df = pd.DataFrame([r or _empty_result() for r in results], index=df.index)
    # Avoid duplicate columns if df already carried sentiment columns.
    df = df.drop(columns=[c for c in ALL_SENTIMENT_COLS if c in df.columns], errors="ignore")
    out = pd.concat([df, res_df], axis=1)

    logger.info("Sentiment by lang | zh: %d, other: %d | dist: %s",
                int(is_zh.sum()), int((~is_zh).sum()),
                out["sentiment_label"].value_counts().to_dict())
    return out
