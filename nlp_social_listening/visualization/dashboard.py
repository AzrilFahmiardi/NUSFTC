"""
Composite Dashboard — Single-page summary for presentation.

Combines key visuals into one figure: sentiment, aspect heatmap, pain points, word cloud.

Usage:
    from visualization.dashboard import DashboardGenerator
    gen = DashboardGenerator()
    gen.generate(df, aspect_matrix, pain_df)
"""

import logging
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from wordcloud import WordCloud

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import FIGURE_DPI, COLOR_PALETTE, OUTPUT_FIGURES

logger = logging.getLogger(__name__)

BG = COLOR_PALETTE["background"]
TXT = COLOR_PALETTE["text"]


class DashboardGenerator:
    """Generate a single composite dashboard image."""

    def generate(
        self,
        df: pd.DataFrame,
        aspect_matrix: pd.DataFrame | None = None,
        pain_df: pd.DataFrame | None = None,
        save_path: str | None = None,
    ):
        """Create the full dashboard."""
        fig = plt.figure(figsize=(20, 14), facecolor=BG)
        gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)

        # Title
        fig.suptitle(
            "NLP Social Listening — Consumer Insight Dashboard",
            fontsize=22, fontweight="bold", color=TXT, y=0.97,
        )

        # 1. Summary stats (top-left)
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_stats(ax1, df)

        # 2. Sentiment pie (top-center)
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_sentiment_pie(ax2, df)

        # 3. Word cloud (top-right)
        ax3 = fig.add_subplot(gs[0, 2])
        self._plot_mini_wordcloud(ax3, df)

        # 4. Aspect heatmap (bottom-left + center)
        ax4 = fig.add_subplot(gs[1, 0:2])
        self._plot_aspect_bars(ax4, aspect_matrix)

        # 5. Pain points (bottom-right)
        ax5 = fig.add_subplot(gs[1, 2])
        self._plot_pain_summary(ax5, pain_df)

        path = save_path or str(OUTPUT_FIGURES / "dashboard_composite.png")
        fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight", facecolor=BG)
        plt.close(fig)
        logger.info("Dashboard saved to %s", path)

    def _plot_stats(self, ax, df):
        ax.set_facecolor("#16213e")
        ax.axis("off")

        total = len(df)
        neg = (df.get("consensus_label") == "negative").sum() if "consensus_label" in df.columns else 0
        sources = df["source"].nunique() if "source" in df.columns else "?"
        avg_sent = df["vader_compound"].mean() if "vader_compound" in df.columns else 0

        stats = [
            f"📊 Total Data Points: {total:,}",
            f"📡 Sources: {sources}",
            f"😡 Negative Reviews: {neg:,} ({neg/total*100:.0f}%)" if total > 0 else "",
            f"📈 Avg Sentiment: {avg_sent:.3f}",
        ]

        for i, s in enumerate(stats):
            if s:
                ax.text(0.1, 0.85 - i * 0.2, s, fontsize=14, color=TXT,
                        transform=ax.transAxes, fontweight="bold")

        ax.set_title("Key Metrics", fontsize=15, color=TXT, fontweight="bold")

    def _plot_sentiment_pie(self, ax, df):
        ax.set_facecolor("#16213e")
        if "consensus_label" not in df.columns:
            ax.text(0.5, 0.5, "No data", ha="center", color=TXT, transform=ax.transAxes)
            return
        counts = df["consensus_label"].value_counts()
        colors = [COLOR_PALETTE.get(l, "#777") for l in counts.index]
        ax.pie(counts, labels=counts.index, colors=colors, autopct="%1.0f%%",
               textprops={"color": "white", "fontsize": 11})
        ax.set_title("Sentiment Split", fontsize=15, color=TXT, fontweight="bold")

    def _plot_mini_wordcloud(self, ax, df):
        ax.set_facecolor(BG)
        col = "clean_text_no_stop" if "clean_text_no_stop" in df.columns else "clean_text"
        if col not in df.columns:
            ax.axis("off")
            return
        text = " ".join(df[col].dropna().astype(str))
        if not text.strip():
            ax.axis("off")
            return
        wc = WordCloud(width=600, height=300, background_color=BG,
                       colormap="coolwarm", max_words=60).generate(text)
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        ax.set_title("Key Vocabulary", fontsize=15, color=TXT, fontweight="bold")

    def _plot_aspect_bars(self, ax, matrix):
        ax.set_facecolor("#16213e")
        if matrix is None or matrix.empty:
            ax.text(0.5, 0.5, "Run ABSA first", ha="center", color=TXT, transform=ax.transAxes)
            ax.set_title("Aspect Sentiment", fontsize=15, color=TXT, fontweight="bold")
            return

        aspects = matrix["aspect"].tolist()
        y = np.arange(len(aspects))
        h = 0.6

        ax.barh(y, matrix["positive_pct"], h, color=COLOR_PALETTE["positive"], label="Positive")
        ax.barh(y, matrix["neutral_pct"], h, left=matrix["positive_pct"],
                color=COLOR_PALETTE["neutral"], label="Neutral")
        ax.barh(y, matrix["negative_pct"], h,
                left=matrix["positive_pct"] + matrix["neutral_pct"],
                color=COLOR_PALETTE["negative"], label="Negative")

        ax.set_yticks(y)
        ax.set_yticklabels(aspects, fontsize=12)
        ax.set_xlabel("Percentage")
        ax.set_title("Aspect-Based Sentiment", fontsize=15, color=TXT, fontweight="bold")
        ax.legend(loc="lower right", fontsize=10)

    def _plot_pain_summary(self, ax, pain_df):
        ax.set_facecolor("#16213e")
        ax.axis("off")
        ax.set_title("Pain Point Ranking", fontsize=15, color=TXT, fontweight="bold")

        if pain_df is None or pain_df.empty:
            ax.text(0.5, 0.5, "No data", ha="center", color=TXT, transform=ax.transAxes)
            return

        for i, row in enumerate(pain_df.head(5).itertuples()):
            emoji = "🔴" if i < 2 else "🟡" if i < 4 else "🟢"
            text = f"{emoji} #{row.rank} {row.aspect}: {row.negative_pct:.0f}% negative"
            ax.text(0.05, 0.85 - i * 0.17, text, fontsize=13, color=TXT,
                    transform=ax.transAxes, fontweight="bold")
