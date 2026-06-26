"""Q2 (morning APAC) + Q5 (occasion distribution) analyses."""

import pandas as pd

from analysis._utils import explode_entity, sentiment_breakdown


def occasion_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """All occasions: mentions, %, sentiment breakdown."""
    flat = explode_entity(df, "occasions")
    out = sentiment_breakdown(flat, "occasions").rename(columns={"occasions": "occasion"})
    out["pct_of_total"] = out["mentions"] / out["mentions"].sum() * 100
    return out


def morning_apac_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Morning mentions, split by region tag (APAC vs Global)."""
    flat = explode_entity(df, "occasions")
    morning = flat[flat["occasions"] == "morning"]
    if morning.empty:
        return pd.DataFrame(columns=["region_tag", "mentions", "share"])
    cnt = morning.groupby("region_tag").size().reset_index(name="mentions")
    cnt["share"] = cnt["mentions"] / cnt["mentions"].sum() * 100
    return cnt


def morning_trend_over_time(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly % of tweets tagged 'morning' over the collection window."""
    d = df.copy()
    d["post_dt"] = pd.to_datetime(d["created_at"], errors="coerce", utc=True)
    d = d.dropna(subset=["post_dt"])
    if d.empty:
        return pd.DataFrame(columns=["month", "morning_pct", "total"])
    d["month"] = d["post_dt"].dt.to_period("M").astype(str)
    d["is_morning"] = d["occasions"].apply(
        lambda lst: isinstance(lst, list) and "morning" in lst
    )
    g = d.groupby("month").agg(
        total=("is_morning", "size"),
        morning=("is_morning", "sum"),
    ).reset_index()
    g["morning_pct"] = g["morning"] / g["total"] * 100
    return g[["month", "total", "morning", "morning_pct"]]


def occasion_flavor_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    """Counts matrix: occasion (rows) × flavor (cols)."""
    d = df[
        df["occasions"].apply(lambda x: isinstance(x, list) and len(x) > 0)
        & df["flavors"].apply(lambda x: isinstance(x, list) and len(x) > 0)
    ].copy()
    if d.empty:
        return pd.DataFrame()
    d = d.explode("occasions").explode("flavors")
    pivot = d.pivot_table(
        index="occasions", columns="flavors", values="tweet_id",
        aggfunc="count", fill_value=0,
    )
    return pivot
