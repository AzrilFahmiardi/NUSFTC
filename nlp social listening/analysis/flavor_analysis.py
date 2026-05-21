"""Q1 — Flavor preferences (most desired / most rejected)."""

import pandas as pd

from analysis._utils import explode_entity, sentiment_breakdown


def flavor_frequency(df: pd.DataFrame) -> pd.DataFrame:
    """Per-flavor mentions, sentiment breakdown, and net score."""
    flat = explode_entity(df, "flavors")
    return sentiment_breakdown(flat, "flavors").rename(columns={"flavors": "flavor"})


def top_flavors(df: pd.DataFrame, n: int = 10, min_mentions: int = 5) -> pd.DataFrame:
    freq = flavor_frequency(df)
    return (
        freq[freq["mentions"] >= min_mentions]
        .sort_values("net_score", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )


def flavor_examples(df: pd.DataFrame, flavor: str, n: int = 3) -> dict:
    """Return n top positive and n top negative example tweets for a flavor."""
    mask = df["flavors"].apply(lambda fs: isinstance(fs, list) and flavor in fs)
    sub = df[mask]
    pos = sub[sub["sentiment_label"] == "positive"].nlargest(n, "sentiment_score")
    neg = sub[sub["sentiment_label"] == "negative"].nsmallest(n, "sentiment_score")
    return {
        "positive": pos[["text", "sentiment_score"]].to_dict("records"),
        "negative": neg[["text", "sentiment_score"]].to_dict("records"),
    }
