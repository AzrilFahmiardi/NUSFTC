"""
Charts Module — Bar charts, heatmaps, radar charts for presentation.

Usage:
    from visualization.charts import ChartGenerator
    gen = ChartGenerator()
    gen.plot_sentiment_distribution(df)
    gen.plot_aspect_heatmap(aspect_matrix)
    gen.plot_pain_point_ranking(pain_df)
"""

import logging
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import seaborn as sns

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import FIGURE_DPI, COLOR_PALETTE, OUTPUT_FIGURES

logger = logging.getLogger(__name__)

# Global style
plt.rcParams.update({
    "figure.facecolor": COLOR_PALETTE["background"],
    "axes.facecolor": "#16213e",
    "axes.edgecolor": "#444",
    "text.color": COLOR_PALETTE["text"],
    "axes.labelcolor": COLOR_PALETTE["text"],
    "xtick.color": COLOR_PALETTE["text"],
    "ytick.color": COLOR_PALETTE["text"],
    "font.family": "sans-serif",
    "font.size": 12,
})


class ChartGenerator:
    """Generate presentation-ready charts."""

    def _save(self, fig, name: str):
        path = OUTPUT_FIGURES / f"{name}.png"
        fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight",
                    facecolor=COLOR_PALETTE["background"])
        plt.close(fig)
        logger.info("Saved chart: %s", path)

    def plot_sentiment_distribution(self, df: pd.DataFrame, label_col="consensus_label"):
        """Pie + bar chart of sentiment distribution."""
        counts = df[label_col].value_counts()
        colors = [COLOR_PALETTE.get(l, "#777") for l in counts.index]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6),
                                        facecolor=COLOR_PALETTE["background"])
        # Pie
        ax1.pie(counts, labels=counts.index, colors=colors, autopct="%1.1f%%",
                textprops={"color": "white", "fontsize": 13}, startangle=90)
        ax1.set_title("Sentiment Distribution", fontsize=16, fontweight="bold")

        # Bar
        ax2.barh(counts.index, counts.values, color=colors, edgecolor="#333")
        ax2.set_xlabel("Count")
        ax2.set_title("Sentiment Counts", fontsize=16, fontweight="bold")
        for i, v in enumerate(counts.values):
            ax2.text(v + 5, i, str(v), va="center", fontsize=12)

        plt.tight_layout()
        self._save(fig, "sentiment_distribution")

    def plot_aspect_heatmap(self, matrix: pd.DataFrame):
        """Heatmap of aspect sentiment — key presentation visual."""
        if matrix.empty:
            return

        data = matrix.set_index("aspect")[["positive_pct", "neutral_pct", "negative_pct"]]
        data.columns = ["Positive %", "Neutral %", "Negative %"]

        fig, ax = plt.subplots(figsize=(10, max(6, len(data) * 0.8)),
                                facecolor=COLOR_PALETTE["background"])
        sns.heatmap(
            data, annot=True, fmt=".1f", cmap="RdYlGn",
            linewidths=1, linecolor="#333", ax=ax,
            cbar_kws={"label": "Percentage"},
            annot_kws={"fontsize": 13, "fontweight": "bold"},
        )
        ax.set_title("Aspect-Based Sentiment Analysis", fontsize=16, fontweight="bold", pad=15)
        ax.set_ylabel("")

        plt.tight_layout()
        self._save(fig, "aspect_heatmap")

    def plot_pain_point_ranking(self, pain_df: pd.DataFrame):
        """Horizontal bar chart of pain points by rank."""
        if pain_df.empty:
            return

        fig, ax = plt.subplots(figsize=(12, max(6, len(pain_df) * 0.7)),
                                facecolor=COLOR_PALETTE["background"])

        colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(pain_df)))
        bars = ax.barh(
            pain_df["aspect"], pain_df["negative_pct"],
            color=colors, edgecolor="#333",
        )

        for bar, row in zip(bars, pain_df.itertuples()):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                    f"{row.negative_pct:.0f}% neg (n={row.mention_count})",
                    va="center", fontsize=11, color=COLOR_PALETTE["text"])

        ax.set_xlabel("Negative Review %")
        ax.set_title("Consumer Pain Point Hierarchy", fontsize=16, fontweight="bold", pad=15)
        ax.invert_yaxis()

        plt.tight_layout()
        self._save(fig, "pain_point_ranking")

    def plot_top_complaints(self, keywords_df: pd.DataFrame, top_n: int = 15):
        """Bar chart of top complaint keywords."""
        data = keywords_df.head(top_n)
        if data.empty:
            return

        fig, ax = plt.subplots(figsize=(12, 8), facecolor=COLOR_PALETTE["background"])

        if "count" in data.columns:
            col = "count"
        elif "tfidf_score_neg" in data.columns:
            col = "tfidf_score_neg"
        else:
            col = "tfidf_score"
            
        colors = plt.cm.OrRd(np.linspace(0.3, 0.9, len(data)))
        label_col = "ngram" if "ngram" in data.columns else "keyword"

        ax.barh(data[label_col], data[col], color=colors, edgecolor="#333")
        ax.set_xlabel(col.replace("_", " ").title())
        ax.set_title(f"Top {top_n} Consumer Complaint Keywords", fontsize=16, fontweight="bold")
        ax.invert_yaxis()

        plt.tight_layout()
        self._save(fig, "top_complaints")

    def plot_source_comparison(self, df: pd.DataFrame, source_col="source"):
        """Compare sentiment across data sources (Twitter vs Tokopedia vs Shopee)."""
        if source_col not in df.columns:
            return

        fig, ax = plt.subplots(figsize=(12, 6), facecolor=COLOR_PALETTE["background"])

        pivot = df.groupby([source_col, "consensus_label"]).size().unstack(fill_value=0)
        pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

        colors_map = {
            "positive": COLOR_PALETTE["positive"],
            "neutral": COLOR_PALETTE["neutral"],
            "negative": COLOR_PALETTE["negative"],
        }
        cols = [c for c in ["positive", "neutral", "negative"] if c in pivot_pct.columns]
        pivot_pct[cols].plot(
            kind="bar", stacked=True, ax=ax,
            color=[colors_map.get(c, "#777") for c in cols],
            edgecolor="#333",
        )

        ax.set_ylabel("Percentage")
        ax.set_title("Sentiment by Data Source", fontsize=16, fontweight="bold")
        ax.legend(title="Sentiment")
        plt.xticks(rotation=0)

        plt.tight_layout()
        self._save(fig, "source_comparison")

    def generate_all(self, df, aspect_matrix=None, pain_df=None, complaint_kw=None):
        """Generate all charts at once."""
        self.plot_sentiment_distribution(df)
        self.plot_source_comparison(df)
        if aspect_matrix is not None:
            self.plot_aspect_heatmap(aspect_matrix)
        if pain_df is not None:
            self.plot_pain_point_ranking(pain_df)
        if complaint_kw is not None:
            self.plot_top_complaints(complaint_kw)
        logger.info("All charts generated in %s", OUTPUT_FIGURES)
