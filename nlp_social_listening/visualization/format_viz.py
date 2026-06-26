"""Q4 — Format share donut + side-by-side comparison."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from visualization.style import apply_theme, save_fig, PALETTE


def plot_format_appeal(
    fmt_df: pd.DataFrame, filename: str = "Q4_format_yogurt_appeal.png"
):
    apply_theme()
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    d = fmt_df.sort_values("mentions", ascending=False)
    labels = [f.replace("_", " ").title() for f in d["format"]]

    # (a) donut for share-of-voice
    ax = axes[0]
    colors = plt.cm.Set2(np.linspace(0, 1, len(d)))
    wedges, texts, autotexts = ax.pie(
        d["mentions"], labels=labels, colors=colors, autopct="%1.0f%%",
        startangle=90, wedgeprops={"width": 0.42, "edgecolor": "white"},
        textprops={"fontsize": 11},
    )
    # Highlight yogurt_drink wedge
    for w, fmt in zip(wedges, d["format"]):
        if fmt == "yogurt_drink":
            w.set_edgecolor(PALETTE["accent"])
            w.set_linewidth(3)
    ax.set_title("Format share-of-voice")

    # (b) comparison: mentions (bar) + net sentiment (line)
    ax2 = axes[1]
    x = np.arange(len(d))
    bars = ax2.bar(x, d["mentions"], color=PALETTE["primary"], alpha=0.75, label="Mentions")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, rotation=30, ha="right")
    ax2.set_ylabel("Mentions", color=PALETTE["primary"])

    ax3 = ax2.twinx()
    ax3.plot(x, d["net_score"], marker="o", color=PALETTE["accent"], linewidth=2.5, label="Net sentiment %")
    ax3.set_ylabel("Net sentiment (%)", color=PALETTE["accent"])
    ax3.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    ax2.set_title("Mentions vs Net Sentiment per Format")

    # Annotate yogurt_drink
    if "yogurt_drink" in d["format"].values:
        idx = list(d["format"]).index("yogurt_drink")
        ax2.annotate("yogurt drink",
                     xy=(idx, d.iloc[idx]["mentions"]),
                     xytext=(idx, d["mentions"].max() * 1.1),
                     ha="center", fontsize=10, color=PALETTE["accent"],
                     arrowprops=dict(arrowstyle="->", color=PALETTE["accent"]))

    fig.suptitle("Q4 · Appetite for protein yogurt drink among format alternatives", y=1.02)
    fig.tight_layout()
    return save_fig(fig, filename)
