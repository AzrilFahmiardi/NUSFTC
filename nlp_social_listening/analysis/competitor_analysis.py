"""Q6 — Competitor brand scorecards."""

from collections import Counter
import re
import pandas as pd

from analysis._utils import explode_entity, sentiment_breakdown

_TOKEN_RE = re.compile(r"[a-z]{3,}")
_GENERIC = {
    "protein", "drink", "shake", "the", "and", "for", "with", "this", "that",
    "have", "from", "just", "like", "really", "very", "but", "all", "not",
    "are", "was", "you", "your", "they", "their", "out", "get", "got", "one",
    "its", "has", "had", "any", "can", "will", "would", "should", "could",
}


def _top_ngrams(texts: pd.Series, top: int = 5) -> list[tuple[str, int]]:
    c = Counter()
    for t in texts.dropna():
        toks = [w for w in _TOKEN_RE.findall(t.lower()) if w not in _GENERIC]
        c.update(toks)
    return c.most_common(top)


def brand_scorecard(df: pd.DataFrame, min_mentions: int = 5) -> pd.DataFrame:
    flat = explode_entity(df, "brands")
    if flat.empty:
        return pd.DataFrame()

    base = sentiment_breakdown(flat, "brands").rename(columns={"brands": "brand"})
    base = base[base["mentions"] >= min_mentions].copy()

    praise, complaint = [], []
    for brand in base["brand"]:
        sub = flat[flat["brands"] == brand]
        praise.append(
            _top_ngrams(sub[sub["sentiment_label"] == "positive"]["clean_text_no_stop"])
        )
        complaint.append(
            _top_ngrams(sub[sub["sentiment_label"] == "negative"]["clean_text_no_stop"])
        )
    base["top_praise"] = praise
    base["top_complaint"] = complaint
    return base.sort_values("mentions", ascending=False).reset_index(drop=True)


def share_of_voice(df: pd.DataFrame) -> pd.DataFrame:
    flat = explode_entity(df, "brands")
    if flat.empty:
        return pd.DataFrame(columns=["brand", "mentions", "share_pct"])
    cnt = flat.groupby("brands").size().reset_index(name="mentions")
    cnt = cnt.rename(columns={"brands": "brand"})
    cnt["share_pct"] = cnt["mentions"] / cnt["mentions"].sum() * 100
    return cnt.sort_values("mentions", ascending=False).reset_index(drop=True)
