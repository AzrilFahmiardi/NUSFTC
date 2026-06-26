"""Q6 — Competitor brand scorecard small-multiples."""

import math
import matplotlib.pyplot as plt
import pandas as pd

from visualization.style import apply_theme, save_fig, PALETTE


def plot_competitor_scorecard(scorecard: pd.DataFrame, filename: str = "Q6_competitor_scorecard.png"):
    apply_theme()
    if scorecard.empty:
        return None

    n = len(scorecard)
    cols = min(4, n)
    rows = math.ceil(n / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4.6, rows * 4.2))
    if rows * cols == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    for ax, (_, row) in zip(axes, scorecard.iterrows()):
        ax.set_axis_off()
        # Title block
        ax.text(0.5, 0.95, row["brand"], ha="center", va="top",
                fontsize=14, weight="bold", color=PALETTE["primary"])
        # Sentiment gauge
        score = row["net_score"]
        gauge_color = PALETTE["pos"] if score >= 5 else (PALETTE["neg"] if score <= -5 else PALETTE["neu"])
        ax.text(0.5, 0.78, f"Net sentiment", ha="center", fontsize=9, color="#666")
        ax.text(0.5, 0.68, f"{score:+.0f}%", ha="center", fontsize=22, weight="bold", color=gauge_color)
        ax.text(0.5, 0.58, f"{int(row['mentions'])} mentions", ha="center", fontsize=10, color="#666")

        # Top praise
        praise = row.get("top_praise") or []
        praise_str = ", ".join(t for t, _ in praise[:3]) if praise else "—"
        ax.text(0.05, 0.42, "Praise:", fontsize=9, weight="bold", color=PALETTE["pos"])
        ax.text(0.05, 0.34, praise_str, fontsize=9, color="#333", wrap=True)

        # Top complaints
        complaint = row.get("top_complaint") or []
        complaint_str = ", ".join(t for t, _ in complaint[:3]) if complaint else "—"
        ax.text(0.05, 0.20, "Complaints:", fontsize=9, weight="bold", color=PALETTE["neg"])
        ax.text(0.05, 0.12, complaint_str, fontsize=9, color="#333", wrap=True)

        # Frame
        for spine in ["top", "right", "left", "bottom"]:
            ax.spines[spine].set_visible(True)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        rect = plt.Rectangle((0.02, 0.02), 0.96, 0.96, fill=False, edgecolor="#ddd", linewidth=1.5)
        ax.add_patch(rect)

    for ax in axes[n:]:
        ax.set_visible(False)

    fig.suptitle("Q6 · Competitor brand scorecards", y=1.0, fontsize=18, weight="bold")
    fig.tight_layout()
    return save_fig(fig, filename)
