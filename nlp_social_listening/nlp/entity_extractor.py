"""
Entity extractor — substring-match against curated dictionaries.

Adds columns to enriched dataframe:
    flavors, pains, occasions, formats, brands, region_tag
"""

import logging
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.dictionaries import (
    FLAVOR_DICT, PAIN_DICT, OCCASION_DICT, FORMAT_DICT, BRAND_DICT, REGION_HINT_DICT
)

logger = logging.getLogger(__name__)


def extract(text: str, dictionary: dict[str, list[str]]) -> list[str]:
    if not isinstance(text, str):
        return []
    t = text.lower()
    return [entity for entity, kws in dictionary.items() if any(kw in t for kw in kws)]


def tag_region(text: str) -> str:
    if not isinstance(text, str):
        return "Global"
    t = text.lower()
    if any(kw in t for kw in REGION_HINT_DICT["APAC"]):
        return "APAC"
    return "Global"


def enrich(df: pd.DataFrame, text_col: str = "clean_text") -> pd.DataFrame:
    df = df.copy()
    src = df[text_col].fillna("")
    df["flavors"]    = src.apply(lambda t: extract(t, FLAVOR_DICT))
    df["pains"]      = src.apply(lambda t: extract(t, PAIN_DICT))
    df["occasions"]  = src.apply(lambda t: extract(t, OCCASION_DICT))
    df["formats"]    = src.apply(lambda t: extract(t, FORMAT_DICT))
    df["brands"]     = src.apply(lambda t: extract(t, BRAND_DICT))
    df["region_tag"] = src.apply(tag_region)

    df["n_flavors"]   = df["flavors"].str.len()
    df["n_pains"]     = df["pains"].str.len()
    df["n_occasions"] = df["occasions"].str.len()
    df["n_formats"]   = df["formats"].str.len()
    df["n_brands"]    = df["brands"].str.len()

    logger.info(
        "Enriched %d rows | flavor mentions: %d | pain mentions: %d | brand mentions: %d",
        len(df), int(df["n_flavors"].sum()), int(df["n_pains"].sum()), int(df["n_brands"].sum()),
    )
    return df
