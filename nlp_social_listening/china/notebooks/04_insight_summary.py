# %% [markdown]
# # 04 · Insight summary (1-page, for strategy integration)
# Assembles the brief's key findings from data/results/ into a markdown summary.
#
# Run: `conda activate ml && python notebooks/04_insight_summary.py`

# %%
import logging
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from config.settings import DATA_RESULTS, OUTPUTS_DIR


def _load(name):
    p = DATA_RESULTS / name
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


flavor = _load("flavor_frequency.csv")
pain = _load("pain_point_frequency.csv")
occ = _load("occasion_distribution.csv")
fmt = _load("format_mentions.csv")
comp = _load("competitor_sentiment.csv")
plat = _load("platform_summary.csv")
clusters = _load("cluster_profiles.csv")

# %%
lines = ["# KSF Consumer Intelligence — China (NLP Social Listening)\n"]

if not plat.empty:
    total = int(plat["posts"].sum())
    lines.append(f"**Total posts analyzed:** {total} across {len(plat)} platforms\n")
    lines.append("## Methodology — volume & sentiment per platform\n")
    lines.append(plat.to_markdown(index=False))

if not flavor.empty:
    lines.append("\n## Q1 — Top flavors by net sentiment\n")
    top = flavor[flavor["mentions"] >= 5].sort_values("net_score", ascending=False).head(8)
    lines.append(top[["flavor", "mentions", "pos_pct", "neg_pct", "net_score"]].to_markdown(index=False))

if not pain.empty:
    lines.append("\n## Q3 — Top sensory pain points\n")
    lines.append(pain.head(6)[["pain", "mentions", "severity", "pain_score"]].to_markdown(index=False))

if not fmt.empty:
    lines.append("\n## Q4 — Format appetite (net sentiment)\n")
    lines.append(fmt[["formats", "mentions", "net_score"]].to_markdown(index=False))

if not occ.empty:
    lines.append("\n## Q5 — Occasion distribution\n")
    lines.append(occ[["occasions", "mentions", "net_score"]].to_markdown(index=False))

if not comp.empty:
    lines.append("\n## Q6 — Competitor sentiment\n")
    lines.append(comp[["brands", "mentions", "pos_pct", "neg_pct", "net_score"]].to_markdown(index=False))

if not clusters.empty:
    lines.append("\n## Consumer segments (K-means)\n")
    cols = [c for c in ["cluster", "size_pct", "label", "top_flavor", "top_pain",
                        "top_occasion", "avg_sentiment"] if c in clusters.columns]
    lines.append(clusters[cols].to_markdown(index=False))

out = OUTPUTS_DIR / "insight_summary_cn.md"
out.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {out}")
print("\n".join(lines)[:1500])
