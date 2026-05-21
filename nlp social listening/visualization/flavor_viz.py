"""Q1 — Flavor diverging bar chart."""

import matplotlib.pyplot as plt
import pandas as pd

from visualization.style import apply_theme, save_fig, PALETTE


def plot_flavor_diverging(freq_df: pd.DataFrame, filename: str = "Q1_flavor_diverging.png", top: int = 15):
    """Diverging bar: negative% to the left (red), positive% to the right (green).
    Sorted by net_score. Mention count annotated on each bar."""
    apply_theme()
    d = freq_df.sort_values("net_score", ascending=True).tail(top).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(11, max(6, 0.45 * len(d))))
    y = range(len(d))
    ax.barh(y, -d["neg_pct"], color=PALETTE["neg"], alpha=0.85, label="Negative %")
    ax.barh(y, d["pos_pct"],  color=PALETTE["pos"], alpha=0.85, label="Positive %")

    ax.set_yticks(list(y))
    ax.set_yticklabels(d["flavor"].str.replace("_", " ").str.title())
    ax.axvline(0, color="black", linewidth=0.8)

    for i, row in d.iterrows():
        ax.text(row["pos_pct"] + 1.5, i, f"n={int(row['mentions'])}",
                va="center", fontsize=9, color="#444")

    ax.set_xlabel("Sentiment share (%)")
    ax.set_title("Q1 · Flavor preferences — diverging sentiment (sorted by net score)")
    ax.legend(loc="lower right", frameon=True)
    fig.tight_layout()
    return save_fig(fig, filename)
