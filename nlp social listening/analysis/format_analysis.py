"""Q4 — Format share & yogurt-drink appetite."""

from collections import Counter
import pandas as pd

from analysis._utils import explode_entity, sentiment_breakdown


def format_share(df: pd.DataFrame) -> pd.DataFrame:
    flat = explode_entity(df, "formats")
    out = sentiment_breakdown(flat, "formats").rename(columns={"formats": "format"})
    out["pct_of_mentions"] = out["mentions"] / out["mentions"].sum() * 100
    return out


def yogurt_drink_appetite(df: pd.DataFrame) -> dict:
    mask = df["formats"].apply(lambda fs: isinstance(fs, list) and "yogurt_drink" in fs)
    sub = df[mask]
    if sub.empty:
        return {"mentions": 0, "net_sentiment": 0, "top_flavors": [], "top_pains": []}

    pos = (sub["sentiment_label"] == "positive").mean() * 100
    neg = (sub["sentiment_label"] == "negative").mean() * 100

    flavors = Counter()
    for fs in sub["flavors"]:
        if isinstance(fs, list):
            flavors.update(fs)
    pains = Counter()
    for ps in sub["pains"]:
        if isinstance(ps, list):
            pains.update(ps)

    return {
        "mentions":      int(len(sub)),
        "pos_pct":       round(pos, 1),
        "neg_pct":       round(neg, 1),
        "net_sentiment": round(pos - neg, 1),
        "avg_score":     round(sub["sentiment_score"].mean(), 3),
        "top_flavors":   flavors.most_common(5),
        "top_pains":     pains.most_common(5),
    }


def format_comparison(df: pd.DataFrame) -> pd.DataFrame:
    return format_share(df).sort_values("mentions", ascending=False).reset_index(drop=True)
