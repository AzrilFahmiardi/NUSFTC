"""Q3 — Pain points: ranked by frequency × severity."""

import numpy as np
import pandas as pd

from analysis._utils import explode_entity, sentiment_breakdown


def pain_ranking(df: pd.DataFrame) -> pd.DataFrame:
    flat = explode_entity(df, "pains")
    base = sentiment_breakdown(flat, "pains").rename(columns={"pains": "pain"})
    # Severity = how negative the avg sentiment is when pain is mentioned
    base["severity"] = -base["avg_score"].clip(upper=0)
    # Composite score: mentions weighted by severity (log-damped count)
    base["pain_score"] = base["severity"] * np.log1p(base["mentions"])
    return base.sort_values("pain_score", ascending=False).reset_index(drop=True)


def pain_examples(df: pd.DataFrame, pain: str, n: int = 3) -> list[dict]:
    """Return n representative tweets (most negative sentiment) per pain."""
    mask = df["pains"].apply(lambda ps: isinstance(ps, list) and pain in ps)
    sub = df[mask].sort_values("sentiment_score", ascending=True).head(n)
    return sub[["text", "sentiment_score"]].to_dict("records")
