"""
05 - Visualisasi untuk laporan. Versi Bahasa Indonesia, tanpa em-dash.
Output:
- outputs/tsne_mobai_subgraph.png
- outputs/variant_predictions_bar.png
- outputs/sim_vs_sentiment_scatter.png
- outputs/variant_c_top10.png
- outputs/ai_stack_diagram.png
"""
import pickle
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D
from pathlib import Path
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import linregress

try:
    from adjustText import adjust_text
    HAVE_ADJUST_TEXT = True
except ImportError:
    HAVE_ADJUST_TEXT = False

ROOT = Path("__file__" in globals() and __file__ or "notebooks/dummy.py").resolve().parents[1] if "__file__" in globals() else Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
DATA = ROOT / "data"
OUT = ROOT / "outputs"

with open(DATA / "flavorgraph_embeddings.pickle", "rb") as f:
    emb = pickle.load(f)
with open(DATA / "trained_models.pkl", "rb") as f:
    trained = pickle.load(f)
with open(DATA / "training_data.pkl", "rb") as f:
    td = pickle.load(f)

nodes = pd.read_csv(DATA / "nodes_191120.csv")
nodes["node_id_str"] = nodes["node_id"].astype(str)
name_to_id = dict(zip(nodes["name"], nodes["node_id_str"]))
id_to_name = dict(zip(nodes["node_id_str"], nodes["name"]))

X_train, y_train, names_train = td["X"], td["y"], td["names"]
anchor = trained["top_anchor_centroid"]

plt.rcParams.update({
    "figure.dpi": 110,
    "savefig.dpi": 180,
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titleweight": "bold",
})

# ===========================================
# (1) Scatter calibration: cosine similarity vs sentiment
# ===========================================
X_norm = X_train / np.linalg.norm(X_train, axis=1, keepdims=True)
sim_train = cosine_similarity(X_norm, anchor.reshape(1, -1)).flatten()
reg = linregress(sim_train, y_train)

def vec(name):
    nid = name_to_id.get(name)
    if nid is None or nid not in emb:
        return None
    v = np.asarray(emb[nid], dtype=float)
    return v / np.linalg.norm(v)

def combine(*names):
    vecs = [vec(n) for n in names if vec(n) is not None]
    v = np.mean(vecs, axis=0)
    return v / np.linalg.norm(v)

variant_pts = {
    "Varian A (Mangga x Melati)": combine("fresh_mango", "jasmine_tea"),
    "Varian B (Kelapa x Teh Susu)": combine("coconut", "black_tea", "milk"),
}

fig, ax = plt.subplots(figsize=(10, 6.5))
ax.scatter(sim_train, y_train, s=110, c=y_train, cmap="RdYlGn", edgecolor="black", zorder=3)

texts = []
for i, n in enumerate(names_train):
    texts.append(ax.text(sim_train[i] + 0.005, y_train[i] + 0.5, n, fontsize=9))

# Variant overlays
v_xs, v_ys, v_labels = [], [], []
for label, v in variant_pts.items():
    sim = float(cosine_similarity(v.reshape(1, -1), anchor.reshape(1, -1))[0, 0])
    pred = reg.slope * sim + reg.intercept
    ax.scatter([sim], [pred], marker="*", s=420, c="gold", edgecolor="black", zorder=4)
    texts.append(ax.text(sim + 0.005, pred + 0.5, label, fontsize=10, fontweight="bold", color="#7c1d1d"))
    v_xs.append(sim); v_ys.append(pred)

xs = np.linspace(sim_train.min() - 0.05, max(sim_train.max(), 0.85), 100)
ax.plot(xs, reg.slope * xs + reg.intercept, "--", c="steelblue", alpha=0.7,
        label=f"Garis kalibrasi linier (R kuadrat = {reg.rvalue**2:.2f}, Pearson r = {reg.rvalue:.2f})")

if HAVE_ADJUST_TEXT:
    adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle="-", color="gray", lw=0.5))

ax.set_xlabel("Kemiripan kosinus terhadap centroid sentimen tinggi (embedding FlavorGraph)")
ax.set_ylabel("Net sentimen konsumen (persen, dari NLP 5,021 tweet)")
ax.set_title("Kurva Kalibrasi Liking-Score\nKemiripan FlavorGraph berkorelasi dengan sentimen konsumen (Pearson r = 0.60)")
ax.grid(alpha=0.3)
ax.legend(loc="lower right")
plt.tight_layout()
plt.savefig(OUT / "sim_vs_sentiment_scatter.png", bbox_inches="tight")
plt.close()
print("Saved: sim_vs_sentiment_scatter.png")


# ===========================================
# (2) Variant predictions bar
# ===========================================
pred_df = pd.read_csv(OUT / "pairing_predictions.csv")
label_map = {
    "Variant B · Full product (yogurt + coconut + black_tea + milk)": "Varian B produk penuh (yogurt + kelapa + teh hitam + susu)",
    "Variant B · Coconut × Milk Tea": "Varian B (Kelapa x Teh Susu)",
    "Variant A · Mango × Jasmine (food node)": "Varian A (Mangga x Melati, food node)",
    "Variant A · Full product (yogurt + mango + jasmine_tea)": "Varian A produk penuh (yogurt + mangga + teh melati)",
    "Baseline · Mango alone": "Baseline: Mangga saja",
    "Baseline · Vanilla alone (top performer in NLP)": "Baseline: Vanila saja (peringkat 2 NLP)",
    "Baseline · Strawberry alone (lowest performer in NLP)": "Baseline: Stroberi saja (peringkat terendah NLP)",
}
pick = list(label_map.keys())
sub = pred_df[pred_df["label"].isin(pick)].copy()
sub["display"] = sub["label"].map(label_map)
sub = sub.sort_values("predicted_sentiment", ascending=True).reset_index(drop=True)

def color_for(val):
    if val >= 45: return "#2ca02c"
    if val >= 38: return "#1f77b4"
    if val >= 30: return "#ff7f0e"
    return "#d62728"
colors = sub["predicted_sentiment"].apply(color_for)

fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(sub["display"], sub["predicted_sentiment"], color=colors, edgecolor="black")
for bar, val, sim in zip(bars, sub["predicted_sentiment"], sub["sim_to_anchor"]):
    ax.text(val + 0.4, bar.get_y() + bar.get_height() / 2,
            f" {val:.1f}%  (sim={sim:.2f})", va="center", fontsize=9)
ax.axvline(x=y_train.mean(), color="gray", linestyle="--", alpha=0.6,
           label=f"Rerata sentimen training ({y_train.mean():.0f}%)")
ax.set_xlim(0, 65)
ax.set_xlabel("Prediksi net sentimen konsumen (persen)")
ax.set_title("Prediksi Liking Konsumen oleh Model AI\nVarian MoBai vs Baseline NLP")
ax.legend(loc="lower right")
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(OUT / "variant_predictions_bar.png", bbox_inches="tight")
plt.close()
print("Saved: variant_predictions_bar.png")


# ===========================================
# (3) Variant C top 10
# ===========================================
vc = pd.read_csv(OUT / "variant_c_curated_top20.csv").head(10).iloc[::-1].reset_index(drop=True)
display_name = {
    "crushed_pineapple": "Nanas cincang",
    "pecan": "Pecan",
    "macadamia_nut": "Kacang macadamia",
    "papaya": "Pepaya",
    "sweetened_condensed_milk": "Susu kental manis",
    "nut": "Kacang umum",
    "date": "Kurma",
    "ground_nutmeg": "Pala bubuk",
    "crushed_red_pepper_flake": "Cabai bubuk kasar",
    "fresh_lime_juice": "Perasan jeruk nipis segar",
}
vc["display"] = vc["name"].map(lambda n: display_name.get(n, n))
fig, ax = plt.subplots(figsize=(10, 5.5))
bars = ax.barh(vc["display"], vc["predicted_sentiment"], color="#6baed6", edgecolor="black")
cat_id = {"Fruit": "Buah", "Nut/Seed": "Kacang/Biji", "Beverage": "Minuman", "Spice": "Bumbu", "Flower": "Bunga"}
for bar, val, cat in zip(bars, vc["predicted_sentiment"], vc["category"]):
    cat_indo = cat_id.get(cat, cat)
    ax.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
            f" {val:.1f}%  ({cat_indo})", va="center", fontsize=9)
ax.set_xlabel("Prediksi net sentimen jika dipasangkan dengan basis yogurt + teh hitam (persen)")
ax.set_title("Variant C Discovery: 10 Kandidat Terbaik untuk Minuman\nHasil screening 8.279 node FlavorGraph dengan filter kategori")
ax.set_xlim(30, 50)
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(OUT / "variant_c_top10.png", bbox_inches="tight")
plt.close()
print("Saved: variant_c_top10.png")


# ===========================================
# (4) t-SNE projection with adjustText (or fallback label pruning)
# ===========================================
focus_names = list(names_train) + [
    "jasmine_tea", "Benzyl_Acetate", "Linalool",
    "yogurt", "white_peach", "lychee", "passion_fruit",
]
focus_names += list(pd.read_csv(OUT / "variant_c_curated_top20.csv").head(10)["name"])
focus_ids = []
seen = set()
for n in focus_names:
    nid = name_to_id.get(n)
    if nid and nid in emb and nid not in seen:
        focus_ids.append(nid)
        seen.add(nid)

rng = np.random.default_rng(42)
all_ids = [i for i in emb.keys() if i not in seen]
sample_ids = rng.choice(all_ids, size=350, replace=False).tolist()

plot_ids = focus_ids + sample_ids
vectors = np.stack([emb[i] for i in plot_ids])
labels = [id_to_name.get(i, i) for i in plot_ids]

print(f"Running t-SNE on {len(plot_ids)} nodes...")
ts = TSNE(n_components=2, random_state=42, perplexity=30, init="pca")
coords = ts.fit_transform(vectors)

fig, ax = plt.subplots(figsize=(13, 9))
ax.scatter(coords[len(focus_ids):, 0], coords[len(focus_ids):, 1],
           c="lightgray", s=12, alpha=0.5)

training_set = set(names_train)
variant_c_set = set(pd.read_csv(OUT / "variant_c_curated_top20.csv").head(10)["name"])
mobai_set = {"jasmine_tea", "Benzyl_Acetate", "Linalool", "white_peach", "lychee", "passion_fruit", "yogurt"}

# Plot focus points
texts = []
for i in range(len(focus_ids)):
    x, yc = coords[i]
    name = labels[i]
    if name in training_set:
        ax.scatter(x, yc, c="orange", s=130, edgecolor="black", zorder=3)
        texts.append(ax.text(x, yc, name, fontsize=9, fontweight="bold"))
    elif name in mobai_set:
        ax.scatter(x, yc, c="red", s=160, marker="*", edgecolor="black", zorder=4)
        texts.append(ax.text(x, yc, name, fontsize=9, color="#7c1d1d"))
    elif name in variant_c_set:
        ax.scatter(x, yc, c="green", s=110, marker="D", edgecolor="black", zorder=3)
        texts.append(ax.text(x, yc, name, fontsize=9, color="#1b5e20"))

if HAVE_ADJUST_TEXT:
    adjust_text(texts, ax=ax,
                arrowprops=dict(arrowstyle="-", color="gray", lw=0.6, alpha=0.7),
                expand_text=(1.4, 1.4), expand_points=(1.3, 1.3),
                force_text=(0.7, 0.9), force_points=(0.5, 0.7))

legend_elems = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor="lightgray", markersize=8, label="Node lain (sampel acak)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="orange", markeredgecolor="black", markersize=10, label="Flavor training NLP (13)"),
    Line2D([0], [0], marker="*", color="w", markerfacecolor="red", markeredgecolor="black", markersize=14, label="Bahan MoBai (Varian A/B)"),
    Line2D([0], [0], marker="D", color="w", markerfacecolor="green", markeredgecolor="black", markersize=9, label="Kandidat Varian C top 10"),
]
ax.legend(handles=legend_elems, loc="upper right")
ax.set_title("Proyeksi 2D t-SNE dari ruang embedding FlavorGraph\nNode terkait MoBai disorot dari 8.297 node total")
ax.set_xlabel("Dimensi t-SNE 1")
ax.set_ylabel("Dimensi t-SNE 2")
ax.grid(alpha=0.2)
plt.tight_layout()
plt.savefig(OUT / "tsne_mobai_subgraph.png", bbox_inches="tight")
plt.close()
print("Saved: tsne_mobai_subgraph.png")


# ===========================================
# (5) AI Stack Diagram (Bahasa Indonesia, no em-dash)
# ===========================================
fig, ax = plt.subplots(figsize=(13, 8.5))
ax.set_xlim(0, 13)
ax.set_ylim(0, 9)
ax.axis("off")

layers = [
    {"y": 7.2, "color": "#fde68a",
     "title": "LAYER 1: Consumer Voice",
     "subtitle": "VADER, TextBlob, TF-IDF, K-Means (NLP Social Listening)",
     "input": "Input: 5.021 tweet konsumen",
     "output": "Output: skor sentimen per flavor (13 flavor), 5 segmen konsumen, 9 pain point"},
    {"y": 5.4, "color": "#bae6fd",
     "title": "LAYER 2: Molecular AI (FlavorGraph)",
     "subtitle": "metapath2vec + Chemical Structure Prediction (Park et al., 2021)",
     "input": "Input: 8.297 node bahan dan senyawa kimia, 147.179 edge",
     "output": "Output: embedding 300 dimensi per bahan"},
    {"y": 3.6, "color": "#bbf7d0",
     "title": "LAYER 3: Liking-Score Predictor (kontribusi kami)",
     "subtitle": "Cosine similarity ke centroid sentimen tinggi, kalibrasi linier",
     "input": "Input: keluaran Layer 1 (skor) + keluaran Layer 2 (vektor)",
     "output": "Output: prediksi liking untuk kombinasi flavor apapun"},
    {"y": 1.8, "color": "#fecaca",
     "title": "LAYER 4: Product Science",
     "subtitle": "Stack masking off-note 5 mekanisme (Best 2025, Tian 2020, JAFC 2024)",
     "input": "Input: Variant A dan B dari Layer 3",
     "output": "Output: formulasi produk MoBai"},
]

for L in layers:
    box = FancyBboxPatch((0.5, L["y"] - 0.65), 12.0, 1.3,
                         boxstyle="round,pad=0.05", linewidth=1.5,
                         facecolor=L["color"], edgecolor="black")
    ax.add_patch(box)
    ax.text(0.85, L["y"] + 0.4, L["title"], fontsize=13, fontweight="bold")
    ax.text(0.85, L["y"] + 0.1, L["subtitle"], fontsize=10, style="italic", color="#374151")
    ax.text(0.85, L["y"] - 0.18, L["input"], fontsize=9, color="#111827")
    ax.text(0.85, L["y"] - 0.42, L["output"], fontsize=9, color="#111827")

for i in range(len(layers) - 1):
    y_from = layers[i]["y"] - 0.7
    y_to = layers[i + 1]["y"] + 0.7
    ax.annotate("", xy=(6.5, y_to), xytext=(6.5, y_from),
                arrowprops=dict(arrowstyle="->", lw=2, color="#374151"))

ax.text(6.5, 8.6, "Arsitektur Pipeline AI MoBai (4 Lapis)", fontsize=16,
        fontweight="bold", ha="center")
ax.text(6.5, 8.2, "Dari bahasa konsumen menuju embedding molekuler, prediksi liking, dan formulasi produk",
        fontsize=10.5, ha="center", style="italic", color="#4b5563")

plt.savefig(OUT / "ai_stack_diagram.png", bbox_inches="tight")
plt.close()
print("Saved: ai_stack_diagram.png")

print("\nSemua visualisasi selesai.")
