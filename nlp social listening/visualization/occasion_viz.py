"""Q2 + Q5 — Morning/APAC analysis and occasion distribution."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    import squarify
except ImportError:
    squarify = None

from visualization.style import apply_theme, save_fig, PALETTE


def plot_morning_apac(
    apac_breakdown: pd.DataFrame,
    trend: pd.DataFrame,
    filename: str = "Q2_morning_apac.png",
):
    """Two-panel: (a) APAC vs Global morning share, (b) monthly morning% trend."""
    apply_theme()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # (a) APAC vs Global
    ax = axes[0]
    if not apac_breakdown.empty:
        colors = [PALETTE["accent"] if r == "APAC" else PALETTE["primary"]
                  for r in apac_breakdown["region_tag"]]
        ax.bar(apac_breakdown["region_tag"], apac_breakdown["mentions"], color=colors)
        for i, r in apac_breakdown.iterrows():
            ax.text(i, r["mentions"], f"{r['share']:.0f}%", ha="center", va="bottom", fontsize=11)
    ax.set_title("Morning-occasion mentions by region")
    ax.set_ylabel("Tweets mentioning morning occasion")

    # (b) trend
    ax = axes[1]
    if not trend.empty:
        ax.plot(trend["month"], trend["morning_pct"], marker="o",
                color=PALETTE["accent"], linewidth=2.5)
        ax.fill_between(trend["month"], trend["morning_pct"], alpha=0.18, color=PALETTE["accent"])
        ax.set_ylim(0, max(20, trend["morning_pct"].max() * 1.3))
    ax.set_title("Monthly share of morning-occasion tweets")
    ax.set_ylabel("% of tweets that month")
    ax.tick_params(axis="x", rotation=45)

    fig.suptitle("Q2 · Do APAC consumers discuss protein in the morning?", y=1.02)
    fig.tight_layout()
    return save_fig(fig, filename)


def plot_occasion_treemap(dist: pd.DataFrame, filename: str = "Q5_occasion_treemap.png"):
    apply_theme()
    fig, ax = plt.subplots(figsize=(11, 6))
    d = dist.sort_values("mentions", ascending=False)
    labels = [
        f"{o.replace('_', ' ').title()}\n{m} ({p:.0f}%)"
        for o, m, p in zip(d["occasion"], d["mentions"], d["pct_of_total"])
    ]
    if squarify is None:
        # Fallback: horizontal bar
        ax.barh(d["occasion"], d["mentions"], color=PALETTE["primary"])
        ax.set_title("Q5 · Occasion distribution (treemap fallback)")
    else:
        squarify.plot(
            sizes=d["mentions"], label=labels, ax=ax,
            color=plt.cm.viridis(np.linspace(0.15, 0.85, len(d))),
            alpha=0.88, edgecolor="white", linewidth=2,
            text_kwargs={"fontsize": 11, "color": "white", "weight": "bold"},
        )
        ax.axis("off")
        ax.set_title("Q5 · Dominant consumption occasions")
    fig.tight_layout()
    return save_fig(fig, filename)


def plot_occasion_flavor_heatmap(
    matrix: pd.DataFrame, filename: str = "Q5_occasion_x_flavor_heatmap.png"
):
    apply_theme()
    if matrix.empty:
        return None
    # Trim to top columns (flavors) to keep readable
    top_cols = matrix.sum(axis=0).sort_values(ascending=False).head(12).index
    m = matrix[top_cols]

    fig, ax = plt.subplots(figsize=(max(8, 0.6 * len(top_cols)), max(4, 0.5 * len(m))))
    im = ax.imshow(m.values, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(top_cols)))
    ax.set_xticklabels([c.replace("_", " ").title() for c in top_cols], rotation=45, ha="right")
    ax.set_yticks(range(len(m)))
    ax.set_yticklabels([i.replace("_", " ").title() for i in m.index])
    for i in range(len(m)):
        for j in range(len(top_cols)):
            val = int(m.values[i, j])
            if val > 0:
                ax.text(j, i, val, ha="center", va="center",
                        color="white" if val > m.values.max() * 0.5 else "black", fontsize=9)
    fig.colorbar(im, ax=ax, label="Co-occurrences")
    ax.set_title("Q5 · Which flavors win which occasion?")
    fig.tight_layout()
    return save_fig(fig, filename)
