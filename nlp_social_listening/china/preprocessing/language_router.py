"""
Language router — detect language and tag each row, WITHOUT dropping rows.

Unlike the sibling project's `language_filter` (which keeps only English), this
multi-language corpus keeps everything and routes each row to the correct NLP
engine downstream (Chinese RoBERTa vs English VADER).

Adds a `detected_lang` column (zh-cn / zh-tw / en / id / ...).
"""

import logging
import pandas as pd

try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0
except ImportError:
    detect = None

logger = logging.getLogger(__name__)

# CJK Unified Ideographs range — quick heuristic before trusting langdetect.
_CJK = (0x4E00, 0x9FFF)


def _has_cjk(text: str) -> bool:
    return any(_CJK[0] <= ord(c) <= _CJK[1] for c in text)


def detect_lang(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return "unknown"
    # Heuristic: presence of Han characters → Chinese (langdetect mislabels short zh).
    if _has_cjk(text):
        return "zh"
    if detect is None:
        return "unknown"
    try:
        return detect(text)
    except Exception:
        return "unknown"


def route_languages(
    df: pd.DataFrame, text_col: str = "clean_text", platform_hint_col: str = "language"
) -> pd.DataFrame:
    """Add `detected_lang`. Falls back to the platform language tag when unknown."""
    df = df.copy()
    df["detected_lang"] = df[text_col].apply(detect_lang)

    if platform_hint_col in df.columns:
        unknown = df["detected_lang"] == "unknown"
        df.loc[unknown, "detected_lang"] = (
            df.loc[unknown, platform_hint_col].fillna("unknown").replace("", "unknown")
        )

    # Normalize zh variants to a leading 'zh' so sentiment routing is simple.
    df["detected_lang"] = df["detected_lang"].apply(
        lambda x: "zh" if isinstance(x, str) and x.startswith("zh") else x
    )

    logger.info("Language distribution: %s", df["detected_lang"].value_counts().to_dict())
    return df
