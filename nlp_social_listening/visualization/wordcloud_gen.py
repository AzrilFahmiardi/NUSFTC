"""
Word Cloud Generator — Presentation-ready word clouds.

Usage:
    from visualization.wordcloud_gen import WordCloudGenerator
    gen = WordCloudGenerator()
    gen.generate_complaint_cloud(df, save_path="outputs/figures/complaint_cloud.png")
"""

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

try:
    from wordcloud import WordCloud
except ImportError:
    raise ImportError("pip install wordcloud")

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import FIGURE_DPI, COLOR_PALETTE, OUTPUT_FIGURES

logger = logging.getLogger(__name__)


class WordCloudGenerator:
    """Generate presentation-ready word clouds."""

    def __init__(self):
        self.default_params = {
            "width": 1200,
            "height": 600,
            "max_words": 100,
            "background_color": COLOR_PALETTE["background"],
            "colormap": "RdYlGn_r",
            "relative_scaling": 0.5,
            "min_font_size": 10,
            "max_font_size": 80,
            "contour_width": 2,
            "contour_color": COLOR_PALETTE["primary"],
        }

    def _generate(self, text: str, title: str, save_path: str | None = None, **kwargs):
        """Generate and optionally save a word cloud."""
        params = {**self.default_params, **kwargs}
        wc = WordCloud(**params).generate(text)

        fig, ax = plt.subplots(1, 1, figsize=(14, 7), facecolor=COLOR_PALETTE["background"])
        ax.imshow(wc, interpolation="bilinear")
        ax.set_title(title, fontsize=18, color=COLOR_PALETTE["text"], pad=15, fontweight="bold")
        ax.axis("off")
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches="tight",
                        facecolor=COLOR_PALETTE["background"])
            logger.info("Saved word cloud to %s", save_path)
        plt.close(fig)
        return wc

    def generate_overall(self, df, text_col="clean_text_no_stop", save_path=None):
        """Generate word cloud from all reviews."""
        text = " ".join(df[text_col].dropna().astype(str))
        return self._generate(text, "Overall Consumer Vocabulary",
                              save_path or str(OUTPUT_FIGURES / "wc_overall.png"))

    def generate_complaint_cloud(self, df, text_col="clean_text_no_stop",
                                  label_col="consensus_label", save_path=None):
        """Word cloud from NEGATIVE reviews only — key deliverable."""
        neg = df[df[label_col] == "negative"][text_col]
        text = " ".join(neg.dropna().astype(str))
        return self._generate(text, "Consumer Complaints — Word Cloud",
                              save_path or str(OUTPUT_FIGURES / "wc_complaints.png"),
                              colormap="Reds")

    def generate_praise_cloud(self, df, text_col="clean_text_no_stop",
                               label_col="consensus_label", save_path=None):
        """Word cloud from POSITIVE reviews."""
        pos = df[df[label_col] == "positive"][text_col]
        text = " ".join(pos.dropna().astype(str))
        return self._generate(text, "What Consumers Love — Word Cloud",
                              save_path or str(OUTPUT_FIGURES / "wc_praise.png"),
                              colormap="Greens")

    def generate_all(self, df, text_col="clean_text_no_stop", label_col="consensus_label"):
        """Generate all word clouds at once."""
        self.generate_overall(df, text_col)
        self.generate_complaint_cloud(df, text_col, label_col)
        self.generate_praise_cloud(df, text_col, label_col)
        logger.info("All word clouds generated in %s", OUTPUT_FIGURES)
