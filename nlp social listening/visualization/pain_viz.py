"""Q3 — Pain point ranked horizontal bar with severity color & sample quote."""

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import pandas as pd

from visualization.style import apply_theme, save_fig


def plot_pain_ranking(
    pain_df: pd.DataFrame,
    examples_by_pain: dict[str, list[dict]] | None = None,
    filename: str = "Q3_pain_ranking.png",
):
    """Horizontal bars (mention count) colored by severity (red = more negative).
    Inline sample quote per bar if examples_by_pain provided."""
    apply_theme()
    d = pain_df.sort_values("mentions", ascending=True)

    fig, ax = plt.subplots(figsize=(13, max(5, 0.55 * len(d))))
    norm = mcolors.Normalize(vmin=0, vmax=max(0.3, d["severity"].max()))
    colors = cm.Reds(norm(d["severity"]))

    bars = ax.barh(d["pain"].str.replace("_", " ").str.title(), d["mentions"], color=colors)
    for i, (bar, pain) in enumerate(zip(bars, d["pain"])):
        n = int(d.iloc[i]["mentions"])
        sev = d.iloc[i]["severity"]
        label = f"  n={n} · severity={sev:.2f}"
        if examples_by_pain and pain in examples_by_pain and examples_by_pain[pain]:
            q = examples_by_pain[pain][0]["text"]
            q = (q[:80] + "…") if isinstance(q, str) and len(q) > 80 else q
            label += f"  “{q}”"
        ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
                label, va="center", fontsize=9, color="#333")

    ax.set_xlabel("Mention count")
    ax.set_title("Q3 · Top sensory pain points (bar length = mentions, color = severity)")
    ax.set_xlim(0, d["mentions"].max() * 1.55)
    sm = cm.ScalarMappable(cmap=cm.Reds, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax, label="Severity (|avg negative sentiment|)", shrink=0.7)
    fig.tight_layout()
    return save_fig(fig, filename)
