"""BONUS — K-means: PCA 2D scatter + per-cluster radar."""

import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.decomposition import TruncatedSVD

from visualization.style import apply_theme, save_fig


def plot_pca_scatter(
    X, labels, cluster_labels: dict[int, str],
    filename: str = "BONUS_cluster_pca.png",
):
    apply_theme()
    svd = TruncatedSVD(n_components=2, random_state=42)
    coords = svd.fit_transform(X)

    fig, ax = plt.subplots(figsize=(11, 7))
    k = len(set(labels))
    palette = plt.cm.Set1(np.linspace(0, 1, k))
    for cid in range(k):
        mask = labels == cid
        ax.scatter(coords[mask, 0], coords[mask, 1],
                   s=18, alpha=0.55, color=palette[cid],
                   label=f"C{cid} · {cluster_labels.get(cid, '')[:40]}")
        cx, cy = coords[mask].mean(axis=0)
        ax.scatter(cx, cy, s=380, marker="X", color=palette[cid],
                   edgecolor="black", linewidth=1.5, zorder=5)
        ax.text(cx, cy, f"C{cid}", ha="center", va="center", fontsize=10, weight="bold")

    ax.set_xlabel(f"SVD-1 ({svd.explained_variance_ratio_[0]*100:.1f}%)")
    ax.set_ylabel(f"SVD-2 ({svd.explained_variance_ratio_[1]*100:.1f}%)")
    ax.set_title("Consumer segments (TF-IDF → SVD 2D)")
    ax.legend(loc="best", fontsize=9, frameon=True)
    fig.tight_layout()
    return save_fig(fig, filename)


def _radar_axes(ax, num_axes):
    angles = np.linspace(0, 2 * np.pi, num_axes, endpoint=False).tolist()
    angles += angles[:1]
    return angles


def plot_cluster_radar(
    profile_df: pd.DataFrame,
    df_enriched: pd.DataFrame,
    cluster_labels: dict[int, str],
    filename: str = "BONUS_cluster_radar.png",
):
    """Per cluster radar over normalized axes:
       morning, post_workout, yogurt_drink, sweet_tolerance (=1-too_sweet),
       chalky_tolerance (=1-chalky), positivity."""
    apply_theme()
    axes_labels = ["Morning", "Post-Workout", "Yogurt Drink", "Sweet-Tolerance",
                   "Chalky-Tolerance", "Positivity"]
    n_axes = len(axes_labels)

    rows = []
    for cid, sub in df_enriched.groupby("cluster"):
        size = len(sub)
        morning = sub["occasions"].apply(lambda l: isinstance(l, list) and "morning" in l).mean()
        postw   = sub["occasions"].apply(lambda l: isinstance(l, list) and "post_workout" in l).mean()
        yog     = sub["formats"].apply(lambda l: isinstance(l, list) and "yogurt_drink" in l).mean()
        sweet   = 1 - sub["pains"].apply(lambda l: isinstance(l, list) and "too_sweet" in l).mean()
        chalky  = 1 - sub["pains"].apply(lambda l: isinstance(l, list) and "chalky" in l).mean()
        pos     = (sub["sentiment_label"] == "positive").mean()
        rows.append((int(cid), size, [morning, postw, yog, sweet, chalky, pos]))

    rows.sort(key=lambda r: -r[1])
    n = len(rows)
    cols = min(3, n)
    grows = math.ceil(n / cols)
    fig, axes = plt.subplots(grows, cols, figsize=(cols * 5, grows * 4.8),
                             subplot_kw=dict(polar=True))
    if n == 1:
        axes = np.array([axes])
    axes = np.array(axes).flatten()

    palette = plt.cm.Set1(np.linspace(0, 1, n))
    for ax, (cid, size, vals), color in zip(axes, rows, palette):
        angles = _radar_axes(ax, n_axes)
        vals_closed = vals + vals[:1]
        ax.plot(angles, vals_closed, color=color, linewidth=2)
        ax.fill(angles, vals_closed, color=color, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(axes_labels, fontsize=8)
        ax.set_yticks([0.25, 0.5, 0.75])
        ax.set_yticklabels(["0.25", "0.5", "0.75"], fontsize=7)
        ax.set_ylim(0, 1)
        title = f"C{cid} · {cluster_labels.get(cid, '')[:35]}"
        ax.set_title(f"{title}\n({size} tweets)", fontsize=10, weight="bold", y=1.12)

    for ax in axes[n:]:
        ax.set_visible(False)
    fig.suptitle("Consumer segment radar profiles", y=1.02, fontsize=18, weight="bold")
    fig.tight_layout()
    return save_fig(fig, filename)
