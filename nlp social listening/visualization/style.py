"""Shared matplotlib/seaborn theme + savefig helper."""

from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import FIG_DPI, FIGURES_DIR

PALETTE = {
    "pos":      "#2E8B57",
    "neg":      "#C0392B",
    "neu":      "#95A5A6",
    "accent":   "#E67E22",
    "primary":  "#2C3E50",
    "highlight": "#F1C40F",
}
FLAVOR_PALETTE = "viridis"


def apply_theme():
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams.update({
        "figure.dpi": 100,
        "savefig.dpi": FIG_DPI,
        "font.family": "DejaVu Sans",
        "axes.titlesize": 16,
        "axes.titleweight": "bold",
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.titlesize": 18,
        "figure.titleweight": "bold",
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


def save_fig(fig, filename: str):
    apply_theme()
    out = FIGURES_DIR / filename
    fig.savefig(out, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    return out
