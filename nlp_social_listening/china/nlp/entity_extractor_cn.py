"""
Chinese entity enrichment — reuses the sibling project's language-agnostic
`extract()` substring matcher, but fed the BILINGUAL dictionaries_cn.

The sibling `entity_extractor.enrich()` hard-binds the English dicts at module level,
so we re-implement only the thin `enrich_cn()` wrapper here, delegating the actual
matching to the proven sibling `extract()` function.

Runs on `clean_text` (NOT the jieba-tokenized text) so multi-char Chinese keywords
like 酸奶饮料 aren't split across token boundaries.
"""

import logging
from pathlib import Path

import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.dictionaries_cn import (
    FLAVOR_DICT, PAIN_DICT, OCCASION_DICT, FORMAT_DICT, BRAND_DICT, REGION_HINT_DICT,
)

logger = logging.getLogger(__name__)


def extract(text: str, dictionary: dict[str, list[str]]) -> list[str]:
    """Substring-match entities (language-agnostic: lowercases + `in`).
    Identical logic to the sibling project's entity_extractor.extract."""
    if not isinstance(text, str):
        return []
    t = text.lower()
    return [entity for entity, kws in dictionary.items() if any(kw.lower() in t for kw in kws)]


def _tag_region(text: str) -> str:
    if not isinstance(text, str):
        return "Global"
    t = text.lower()
    return "APAC" if any(kw.lower() in t for kw in REGION_HINT_DICT["APAC"]) else "Global"


def enrich_cn(df: pd.DataFrame, text_col: str = "clean_text") -> pd.DataFrame:
    """Add flavors/pains/occasions/formats/brands/region_tag + n_* counts (Chinese dicts)."""
    df = df.copy()
    src = df[text_col].fillna("")
    df["flavors"]    = src.apply(lambda t: extract(t, FLAVOR_DICT))
    df["pains"]      = src.apply(lambda t: extract(t, PAIN_DICT))
    df["occasions"]  = src.apply(lambda t: extract(t, OCCASION_DICT))
    df["formats"]    = src.apply(lambda t: extract(t, FORMAT_DICT))
    df["brands"]     = src.apply(lambda t: extract(t, BRAND_DICT))
    df["region_tag"] = src.apply(_tag_region)

    df["n_flavors"]   = df["flavors"].str.len()
    df["n_pains"]     = df["pains"].str.len()
    df["n_occasions"] = df["occasions"].str.len()
    df["n_formats"]   = df["formats"].str.len()
    df["n_brands"]    = df["brands"].str.len()

    logger.info(
        "Enriched %d rows | flavor: %d | pain: %d | brand: %d",
        len(df), int(df["n_flavors"].sum()), int(df["n_pains"].sum()), int(df["n_brands"].sum()),
    )
    return df
