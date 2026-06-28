# %% [markdown]
# # 06 · Visualisations — China NLP Social Listening (XHS)
# Generates charts for all Q1–Q6 + BONUS cluster radar + cross-market comparison.
#
# Run: `conda activate ml && python notebooks/06_visualisations.py`

# %%
import sys
import math
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import seaborn as sns

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import DATA_RESULTS, DATA_PROCESSED, FIGURES_DIR, FIG_DPI, SIBLING_PROJECT

PALETTE = {
    "pos":      "#2E8B57",
    "neg":      "#C0392B",
    "neu":      "#95A5A6",
    "accent":   "#E67E22",
    "primary":  "#2C3E50",
    "highlight": "#F1C40F",
}

def apply_theme():
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams.update({
        "figure.dpi": 100,
        "savefig.dpi": FIG_DPI,
        "font.family": "DejaVu Sans",
        "axes.titlesize": 15,
        "axes.titleweight": "bold",
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })

def save_fig(fig, name):
    out = FIGURES_DIR / name
    fig.savefig(out, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved → {out.name}")
    return out

# ──────────────────────────────────────────────────────────────
# Load result CSVs
# ──────────────────────────────────────────────────────────────
flavor_df     = pd.read_csv(DATA_RESULTS / "flavor_frequency.csv")
pain_df       = pd.read_csv(DATA_RESULTS / "pain_point_frequency.csv")
occasion_df   = pd.read_csv(DATA_RESULTS / "occasion_distribution.csv")
format_df     = pd.read_csv(DATA_RESULTS / "format_mentions.csv")
competitor_df = pd.read_csv(DATA_RESULTS / "competitor_sentiment.csv")
cluster_df    = pd.read_csv(DATA_RESULTS / "cluster_profiles.csv")
enriched      = pd.read_csv(DATA_PROCESSED / "china_enriched.csv")

print(f"Loaded data | flavors:{len(flavor_df)} pain:{len(pain_df)} "
      f"occ:{len(occasion_df)} fmt:{len(format_df)} "
      f"competitor:{len(competitor_df)} clusters:{len(cluster_df)}")

# ──────────────────────────────────────────────────────────────
# Q1 — Flavor diverging bar
# ──────────────────────────────────────────────────────────────
print("\n[Q1] Flavor diverging bar...")
apply_theme()
d = flavor_df.sort_values("net_score", ascending=True).tail(15).reset_index(drop=True)
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
ax.set_title("Q1 · Flavor preferences — diverging sentiment (XHS China)\nsorted by net score")
ax.legend(loc="lower right", frameon=True)
fig.tight_layout()
save_fig(fig, "Q1_cn_flavor_diverging.png")

# ──────────────────────────────────────────────────────────────
# Q3 — Pain point ranking (mentions + pos/neg split)
# ──────────────────────────────────────────────────────────────
print("[Q3] Pain point ranking...")
apply_theme()
d = pain_df.sort_values("mentions", ascending=True).reset_index(drop=True)
# Color by neg_pct since severity is 0 for this dataset
norm = mcolors.Normalize(vmin=0, vmax=max(1, d["neg_pct"].max()))
colors = cm.Reds(norm(d["neg_pct"]))

fig, ax = plt.subplots(figsize=(13, max(5, 0.55 * len(d))))
bars = ax.barh(d["pain"].str.replace("_", " ").str.title(), d["mentions"], color=colors)
for i, bar in enumerate(bars):
    n = int(d.iloc[i]["mentions"])
    neg = d.iloc[i]["neg_pct"]
    label = f"  n={n} · neg={neg:.0f}%"
    ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
            label, va="center", fontsize=9, color="#333")
ax.set_xlabel("Mention count")
ax.set_title("Q3 · Sensory pain points — XHS China\n(bar length = mentions, color = % negative sentiment)")
ax.set_xlim(0, d["mentions"].max() * 1.55)
sm = cm.ScalarMappable(cmap=cm.Reds, norm=norm)
sm.set_array([])
fig.colorbar(sm, ax=ax, label="% negative sentiment", shrink=0.7)
fig.tight_layout()
save_fig(fig, "Q3_cn_pain_ranking.png")

# ──────────────────────────────────────────────────────────────
# Q4 — Format share donut + mentions vs sentiment
# ──────────────────────────────────────────────────────────────
print("[Q4] Format appeal...")
apply_theme()
d = format_df.sort_values("mentions", ascending=False).reset_index(drop=True)
labels = [f.replace("_", " ").title() for f in d["formats"]]

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
colors = plt.cm.Set2(np.linspace(0, 1, len(d)))

# Donut
ax = axes[0]
wedges, texts, autotexts = ax.pie(
    d["mentions"], labels=labels, colors=colors, autopct="%1.0f%%",
    startangle=90, wedgeprops={"width": 0.42, "edgecolor": "white"},
    textprops={"fontsize": 11},
)
for w, fmt in zip(wedges, d["formats"]):
    if fmt == "yogurt_drink":
        w.set_edgecolor(PALETTE["accent"])
        w.set_linewidth(3)
ax.set_title("Format share-of-voice (XHS)")

# Bar + line
ax2 = axes[1]
x = np.arange(len(d))
ax2.bar(x, d["mentions"], color=PALETTE["primary"], alpha=0.75, label="Mentions")
ax2.set_xticks(x)
ax2.set_xticklabels(labels, rotation=30, ha="right")
ax2.set_ylabel("Mentions", color=PALETTE["primary"])
ax3 = ax2.twinx()
ax3.plot(x, d["net_score"], marker="o", color=PALETTE["accent"], linewidth=2.5, label="Net sentiment %")
ax3.set_ylabel("Net sentiment (%)", color=PALETTE["accent"])
ax3.axhline(0, color="gray", linestyle="--", linewidth=0.8)
ax2.set_title("Mentions vs Net Sentiment per Format")
if "yogurt_drink" in d["formats"].values:
    idx = list(d["formats"]).index("yogurt_drink")
    ax2.annotate("yogurt drink",
                 xy=(idx, d.iloc[idx]["mentions"]),
                 xytext=(idx + 0.3, d["mentions"].max() * 1.1),
                 fontsize=10, color=PALETTE["accent"],
                 arrowprops=dict(arrowstyle="->", color=PALETTE["accent"]))
fig.suptitle("Q4 · Appetite for protein yogurt drink format — XHS China", y=1.02)
fig.tight_layout()
save_fig(fig, "Q4_cn_format_appeal.png")

# ──────────────────────────────────────────────────────────────
# Q5 — Occasion treemap + flavor×occasion heatmap
# ──────────────────────────────────────────────────────────────
print("[Q5] Occasion charts...")

# Treemap (with squarify fallback)
apply_theme()
d = occasion_df.sort_values("mentions", ascending=False)
total = d["mentions"].sum()
d["pct_of_total"] = d["mentions"] / total * 100
try:
    import squarify
    fig, ax = plt.subplots(figsize=(11, 6))
    sq_labels = [
        f"{o.replace('_', ' ').title()}\n{m} ({p:.0f}%)"
        for o, m, p in zip(d["occasions"], d["mentions"], d["pct_of_total"])
    ]
    squarify.plot(
        sizes=d["mentions"], label=sq_labels, ax=ax,
        color=plt.cm.viridis(np.linspace(0.15, 0.85, len(d))),
        alpha=0.88, edgecolor="white", linewidth=2,
        text_kwargs={"fontsize": 11, "color": "white", "weight": "bold"},
    )
    ax.axis("off")
    ax.set_title("Q5 · Dominant consumption occasions — XHS China")
    fig.tight_layout()
    save_fig(fig, "Q5_cn_occasion_treemap.png")
except ImportError:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(d["occasions"].str.replace("_", " ").str.title(), d["mentions"], color=PALETTE["primary"])
    ax.set_title("Q5 · Occasion distribution — XHS China")
    fig.tight_layout()
    save_fig(fig, "Q5_cn_occasion_treemap.png")

# Occasion × Flavor heatmap
apply_theme()
import ast

def parse_list(val):
    if isinstance(val, list):
        return val
    if pd.isna(val) or val in ("", "[]"):
        return []
    try:
        return ast.literal_eval(str(val))
    except Exception:
        return []

enriched["flavors_list"]   = enriched["flavors"].apply(parse_list)
enriched["occasions_list"] = enriched["occasions"].apply(parse_list)

rows_hm = []
for _, r in enriched.iterrows():
    for occ in r["occasions_list"]:
        for flv in r["flavors_list"]:
            rows_hm.append({"occasion": occ, "flavor": flv})

if rows_hm:
    hm = pd.DataFrame(rows_hm)
    top_flavors = hm["flavor"].value_counts().head(12).index
    hm = hm[hm["flavor"].isin(top_flavors)]
    matrix = hm.pivot_table(index="occasion", columns="flavor", aggfunc="size", fill_value=0)
    fig, ax = plt.subplots(figsize=(max(8, 0.6 * len(matrix.columns)), max(4, 0.5 * len(matrix))))
    im = ax.imshow(matrix.values, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(matrix.columns)))
    ax.set_xticklabels([c.replace("_", " ").title() for c in matrix.columns], rotation=45, ha="right")
    ax.set_yticks(range(len(matrix)))
    ax.set_yticklabels([i.replace("_", " ").title() for i in matrix.index])
    for i in range(len(matrix)):
        for j in range(len(matrix.columns)):
            val = int(matrix.values[i, j])
            if val > 0:
                ax.text(j, i, val, ha="center", va="center",
                        color="white" if val > matrix.values.max() * 0.5 else "black", fontsize=9)
    fig.colorbar(im, ax=ax, label="Co-occurrences")
    ax.set_title("Q5 · Which flavors win which occasion? — XHS China")
    fig.tight_layout()
    save_fig(fig, "Q5_cn_occasion_x_flavor_heatmap.png")

# ──────────────────────────────────────────────────────────────
# Q6 — Competitor scorecard
# ──────────────────────────────────────────────────────────────
print("[Q6] Competitor scorecard...")
apply_theme()
scorecard = competitor_df.sort_values("mentions", ascending=False)
if not scorecard.empty:
    n = len(scorecard)
    cols_n = min(4, n)
    rows_n = math.ceil(n / cols_n)
    fig, axes = plt.subplots(rows_n, cols_n, figsize=(cols_n * 4.6, rows_n * 4.2))
    axes_flat = np.array(axes).flatten() if n > 1 else [axes]

    for ax, (_, row) in zip(axes_flat, scorecard.iterrows()):
        ax.set_axis_off()
        ax.text(0.5, 0.95, row["brands"], ha="center", va="top",
                fontsize=13, weight="bold", color=PALETTE["primary"])
        score = row["net_score"]
        gauge_color = PALETTE["pos"] if score >= 5 else (PALETTE["neg"] if score <= -5 else PALETTE["neu"])
        ax.text(0.5, 0.77, "Net sentiment", ha="center", fontsize=9, color="#666")
        ax.text(0.5, 0.66, f"{score:+.0f}%", ha="center", fontsize=22, weight="bold", color=gauge_color)
        ax.text(0.5, 0.56, f"{int(row['mentions'])} mentions", ha="center", fontsize=10, color="#666")
        ax.text(0.5, 0.42, f"Pos: {row['pos_pct']:.0f}%  |  Neg: {row['neg_pct']:.0f}%",
                ha="center", fontsize=10, color="#444")
        rect = plt.Rectangle((0.02, 0.02), 0.96, 0.96, fill=False, edgecolor="#ddd", linewidth=1.5)
        ax.add_patch(rect)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    for ax in axes_flat[n:]:
        ax.set_visible(False)
    fig.suptitle("Q6 · Competitor brand sentiment — XHS China", y=1.0, fontsize=16, weight="bold")
    fig.tight_layout()
    save_fig(fig, "Q6_cn_competitor_scorecard.png")

# ──────────────────────────────────────────────────────────────
# BONUS — Cluster radar
# ──────────────────────────────────────────────────────────────
print("[BONUS] Cluster radar...")
apply_theme()

enriched["pains_list"] = enriched["pains"].apply(parse_list)
enriched["formats_list"] = enriched["formats"].apply(parse_list)

assignments = pd.read_csv(DATA_RESULTS / "cluster_assignments.csv")
enriched = enriched.merge(assignments[["tweet_id", "cluster"]], on="tweet_id", how="left")

axes_labels = ["Morning", "Post-Workout", "Yogurt Drink", "Sweet-Tolerance",
               "Chalky-Tolerance", "Positivity"]
n_axes = len(axes_labels)

radar_rows = []
for cid, sub in enriched.dropna(subset=["cluster"]).groupby("cluster"):
    size = len(sub)
    morning = sub["occasions_list"].apply(lambda l: "morning" in l).mean()
    postw   = sub["occasions_list"].apply(lambda l: "post_workout" in l).mean()
    yog     = sub["formats_list"].apply(lambda l: "yogurt_drink" in l).mean()
    sweet   = 1 - sub["pains_list"].apply(lambda l: "too_sweet" in l).mean()
    chalky  = 1 - sub["pains_list"].apply(lambda l: "chalky" in l).mean()
    pos     = (sub["sentiment_label"] == "positive").mean()
    label   = cluster_df[cluster_df["cluster"] == int(cid)]["label"].values
    label   = label[0] if len(label) else f"C{cid}"
    radar_rows.append((int(cid), size, [morning, postw, yog, sweet, chalky, pos], label))

radar_rows.sort(key=lambda r: -r[1])
n = len(radar_rows)
cols_r = min(3, n)
rows_r = math.ceil(n / cols_r)
fig, axes = plt.subplots(rows_r, cols_r, figsize=(cols_r * 5, rows_r * 4.8),
                         subplot_kw=dict(polar=True))
axes_flat = np.array(axes).flatten() if n > 1 else [axes]
palette = plt.cm.Set1(np.linspace(0, 1, n))

angles = np.linspace(0, 2 * np.pi, n_axes, endpoint=False).tolist()
angles += angles[:1]

for ax, (cid, size, vals, label), color in zip(axes_flat, radar_rows, palette):
    vals_closed = vals + vals[:1]
    ax.plot(angles, vals_closed, color=color, linewidth=2)
    ax.fill(angles, vals_closed, color=color, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(axes_labels, fontsize=8)
    ax.set_yticks([0.25, 0.5, 0.75])
    ax.set_yticklabels(["0.25", "0.5", "0.75"], fontsize=7)
    ax.set_ylim(0, 1)
    ax.set_title(f"C{cid} · {label[:35]}\n({size} posts)", fontsize=9, weight="bold", y=1.12)

for ax in axes_flat[n:]:
    ax.set_visible(False)
fig.suptitle("Consumer segment radar profiles — XHS China (k=7)", y=1.02, fontsize=16, weight="bold")
fig.tight_layout()
save_fig(fig, "BONUS_cn_cluster_radar.png")

# ──────────────────────────────────────────────────────────────
# BONUS — Cross-market flavor comparison (China XHS vs Twitter EN)
# ──────────────────────────────────────────────────────────────
print("[BONUS] Cross-market flavor comparison...")
twitter_results = SIBLING_PROJECT / "data" / "results"
twitter_flavor_path = twitter_results / "flavor_ranking.csv"

if twitter_flavor_path.exists():
    apply_theme()
    tw = pd.read_csv(twitter_flavor_path)
    cn = flavor_df.copy()

    # Normalize to same flavor keys, take top 10 overlap
    overlap = set(tw["flavor"].str.lower()) & set(cn["flavor"].str.lower())
    tw_f = tw[tw["flavor"].str.lower().isin(overlap)].set_index("flavor")["net_score"]
    cn_f = cn[cn["flavor"].str.lower().isin(overlap)].set_index("flavor")["net_score"]
    compare = pd.DataFrame({"Twitter (EN)": tw_f, "XHS China (ZH)": cn_f}).dropna()
    compare = compare.sort_values("XHS China (ZH)", ascending=True).tail(12)

    fig, ax = plt.subplots(figsize=(11, max(6, 0.45 * len(compare))))
    x = np.arange(len(compare))
    w = 0.38
    ax.barh(x - w/2, compare["Twitter (EN)"],  w, color=PALETTE["accent"],  alpha=0.85, label="Twitter (EN)")
    ax.barh(x + w/2, compare["XHS China (ZH)"], w, color=PALETTE["primary"], alpha=0.85, label="XHS China (ZH)")
    ax.set_yticks(x)
    ax.set_yticklabels([f.replace("_", " ").title() for f in compare.index])
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Net sentiment (%)")
    ax.set_title("BONUS · Cross-market flavor sentiment: Twitter EN vs XHS China")
    ax.legend(frameon=True)
    fig.tight_layout()
    save_fig(fig, "BONUS_cross_market_flavor.png")
else:
    print("  Skipped cross-market chart (Twitter flavor_ranking.csv not found)")

# ──────────────────────────────────────────────────────────────
print(f"\nAll charts saved to: {FIGURES_DIR}")
print(f"Files: {sorted(p.name for p in FIGURES_DIR.glob('*.png'))}")
