"""
Language filter — keep English tweets only.
Uses langdetect on cleaned text. Falls back to platform 'language' field
when langdetect fails.
"""

import logging
import pandas as pd

try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0
except ImportError:
    detect = None

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import TARGET_LANGUAGE

logger = logging.getLogger(__name__)


def detect_lang(text: str) -> str:
    if not text or detect is None:
        return "unknown"
    try:
        return detect(text)
    except Exception:
        return "unknown"


def filter_language(
    df: pd.DataFrame, text_col: str = "clean_text", keep: str = TARGET_LANGUAGE
) -> pd.DataFrame:
    """Add 'detected_lang' column then keep only rows where it == `keep`."""
    df = df.copy()
    df["detected_lang"] = df[text_col].apply(detect_lang)
    # Trust platform tag when detector returns unknown
    fallback_mask = (df["detected_lang"] == "unknown") & (df.get("language") == keep)
    df.loc[fallback_mask, "detected_lang"] = keep

    before = len(df)
    df = df[df["detected_lang"] == keep].reset_index(drop=True)
    logger.info("Language filter (%s): %d -> %d", keep, before, len(df))
    return df
