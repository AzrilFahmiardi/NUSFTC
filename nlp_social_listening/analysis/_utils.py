"""Shared helpers for analysis modules — explode list-columns, sentiment %."""

import pandas as pd


def explode_entity(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Explode a list column so each entity gets its own row.
    Empty lists drop their row."""
    sub = df[df[col].apply(lambda x: isinstance(x, list) and len(x) > 0)].copy()
    return sub.explode(col).reset_index(drop=True)


def sentiment_breakdown(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Per group_col value: mentions, pos%, neg%, neu%, net_score, avg_sentiment."""
    g = df.groupby(group_col)
    out = pd.DataFrame({
        "mentions":    g.size(),
        "pos_pct":     g["sentiment_label"].apply(lambda s: (s == "positive").mean() * 100),
        "neu_pct":     g["sentiment_label"].apply(lambda s: (s == "neutral").mean() * 100),
        "neg_pct":     g["sentiment_label"].apply(lambda s: (s == "negative").mean() * 100),
        "avg_score":   g["sentiment_score"].mean(),
    }).reset_index()
    out["net_score"] = out["pos_pct"] - out["neg_pct"]
    return out.sort_values("mentions", ascending=False).reset_index(drop=True)
