"""
04 - Predict liking for MoBai Variant A (Mango × Jasmine) & Variant B (Coconut × Milk Tea),
     then screen Variant C candidates via the embedding-based ranker.

Outputs:
- outputs/pairing_predictions.csv
- outputs/variant_c_top20.csv
- outputs/variant_c_curated_top10.csv
"""
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path("__file__" in globals() and __file__ or "notebooks/dummy.py").resolve().parents[1] if "__file__" in globals() else Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
DATA = ROOT / "data"
OUT = ROOT / "outputs"

# Load assets
with open(DATA / "flavorgraph_embeddings.pickle", "rb") as f:
    emb = pickle.load(f)
with open(DATA / "trained_models.pkl", "rb") as f:
    trained = pickle.load(f)
nodes = pd.read_csv(DATA / "nodes_191120.csv")
target = pd.read_csv(DATA / "mobai_target_nodes.csv")

# Build lookups
nodes["node_id_str"] = nodes["node_id"].astype(str)
name_to_id = dict(zip(nodes["name"], nodes["node_id_str"]))
id_to_name = dict(zip(nodes["node_id_str"], nodes["name"]))
id_to_type = dict(zip(nodes["node_id_str"], nodes["node_type"]))
id_to_hub = dict(zip(nodes["node_id_str"], nodes["is_hub"]))


def vec(name):
    nid = name_to_id.get(name)
    if nid is None or nid not in emb:
        return None
    v = np.asarray(emb[nid], dtype=float)
    return v / np.linalg.norm(v)


def combine(names, weights=None):
    """Weighted average of normalized vectors."""
    vecs = [vec(n) for n in names if vec(n) is not None]
    if not vecs:
        return None
    weights = weights or [1.0] * len(vecs)
    v = np.average(vecs, axis=0, weights=weights[:len(vecs)])
    return v / np.linalg.norm(v)


# Recover anchor + training data
anchor = trained["top_anchor_centroid"]
anchor_flavors = trained["top_anchor_flavors"]
y_mean = trained["training_y_mean"]
y_min, y_max = trained["training_y_min"], trained["training_y_max"]
print(f"Anchor flavors (high-sentiment centroid): {anchor_flavors}")
print(f"Training y range: [{y_min}, {y_max}], mean={y_mean:.1f}")

# Load training data to score it as a baseline reference
with open(DATA / "training_data.pkl", "rb") as f:
    td = pickle.load(f)
X_train, y_train, names_train = td["X"], td["y"], td["names"]
X_train_norm = X_train / np.linalg.norm(X_train, axis=1, keepdims=True)
sim_train = cosine_similarity(X_train_norm, anchor.reshape(1, -1)).flatten()

# Calibrate: linear map sim -> sentiment using training data
# So we can produce point estimates with empirical anchoring
from scipy.stats import linregress
reg = linregress(sim_train, y_train)
print(f"\nCalibration: sentiment = {reg.slope:.2f} * sim + {reg.intercept:.2f}  (R²={reg.rvalue**2:.3f})")


def predict(name_or_vec, label=""):
    if isinstance(name_or_vec, str):
        v = vec(name_or_vec)
    else:
        v = name_or_vec
    if v is None:
        return None
    sim = float(cosine_similarity(v.reshape(1, -1), anchor.reshape(1, -1))[0, 0])
    sent_est = reg.slope * sim + reg.intercept
    # Bucket
    if sent_est >= y_train.mean() + y_train.std():
        bucket = "HIGH"
    elif sent_est >= y_train.mean():
        bucket = "MID-HIGH"
    elif sent_est >= y_train.mean() - y_train.std():
        bucket = "MID-LOW"
    else:
        bucket = "LOW"
    return {"label": label, "sim_to_anchor": sim, "predicted_sentiment": sent_est, "bucket": bucket}


# ===== Variant A & B =====
print("\n=== Variant A & B predictions ===")

variant_specs = [
    {"label": "Variant A · Mango × Jasmine (food node)",
     "vector": combine(["fresh_mango", "jasmine_tea"])},
    {"label": "Variant A · Mango × Jasmine (compound proxy Benzyl_Acetate)",
     "vector": combine(["fresh_mango", "Benzyl_Acetate"])},
    {"label": "Variant A · Mango × Jasmine (compound proxy Linalool)",
     "vector": combine(["fresh_mango", "Linalool"])},
    {"label": "Variant A · Mango × Jasmine (compound proxy Jasmine_lactone)",
     "vector": combine(["fresh_mango", "Jasmine_lactone"])},
    {"label": "Variant B · Coconut × Milk Tea",
     "vector": combine(["coconut", "black_tea", "milk"])},
    {"label": "Variant B · Coconut × Black Tea (no milk)",
     "vector": combine(["coconut", "black_tea"])},
    # Baseline references
    {"label": "Baseline · Mango alone",
     "vector": vec("fresh_mango")},
    {"label": "Baseline · Vanilla alone (top performer in NLP)",
     "vector": vec("vanilla")},
    {"label": "Baseline · Strawberry alone (lowest performer in NLP)",
     "vector": vec("strawberry")},
    # MoBai full product context (incl. yogurt base)
    {"label": "Variant A · Full product (yogurt + mango + jasmine_tea)",
     "vector": combine(["yogurt", "fresh_mango", "jasmine_tea"])},
    {"label": "Variant B · Full product (yogurt + coconut + black_tea + milk)",
     "vector": combine(["yogurt", "coconut", "black_tea", "milk"])},
]

records = []
for spec in variant_specs:
    if spec["vector"] is None:
        print(f"  SKIP {spec['label']} (missing node)")
        continue
    r = predict(spec["vector"], label=spec["label"])
    print(f"  {r['bucket']:8s} sim={r['sim_to_anchor']:.3f}  pred={r['predicted_sentiment']:+.1f}%  {r['label']}")
    records.append(r)

pred_df = pd.DataFrame(records)
pred_df.to_csv(OUT / "pairing_predictions.csv", index=False)
print(f"\nSaved: {OUT / 'pairing_predictions.csv'}")


# ===== Variant C screening =====
print("\n=== Variant C: screening 6,000+ candidates ===")

# Build candidate pool: all FlavorGraph nodes EXCEPT those in MoBai already
mobai_used = set([
    "fresh_mango", "mango", "dried_mango",
    "jasmine_tea", "jasmine_rice", "cooked_jasmine_rice",
    "coconut", "coconut_milk", "coconut_water", "coconut_cream",
    "black_tea", "brewed_black_tea", "tea", "milk", "whole_milk", "skim_milk",
    "yogurt", "plain_yogurt", "greek_yogurt",
])

# MoBai base context: yogurt + black_tea (the "tea-yogurt base")
base = combine(["yogurt", "black_tea"])

# Predict for each candidate as: avg(base, candidate)
results = []
ids_all = list(emb.keys())
for nid in ids_all:
    name = id_to_name.get(nid)
    if name is None or name in mobai_used:
        continue
    v_cand = np.asarray(emb[nid], dtype=float)
    v_cand = v_cand / np.linalg.norm(v_cand)
    v_combined = (base + v_cand) / 2
    v_combined = v_combined / np.linalg.norm(v_combined)
    sim = float(cosine_similarity(v_combined.reshape(1, -1), anchor.reshape(1, -1))[0, 0])
    sent_est = reg.slope * sim + reg.intercept
    results.append({
        "name": name,
        "node_id": nid,
        "node_type": id_to_type.get(nid),
        "is_hub": id_to_hub.get(nid),
        "sim_to_anchor": sim,
        "predicted_sentiment": sent_est,
    })

c_df = pd.DataFrame(results).sort_values("predicted_sentiment", ascending=False).reset_index(drop=True)
c_df["rank"] = c_df.index + 1
print(f"Screened {len(c_df)} candidates")
print("\nTop 20 (unfiltered):")
print(c_df.head(20).to_string(index=False))
c_df.head(50).to_csv(OUT / "variant_c_top50.csv", index=False)

# Curated filter: use FlavorGraph official categories for beverage-friendly flavors
cat_df = pd.read_csv(DATA / "dict_ingr2cate.csv")
cat_map = dict(zip(cat_df["ingredient"], cat_df["category"]))

BEVERAGE_FRIENDLY_CATS = {"Fruit", "Flower", "Spice", "Beverage", "Nut/Seed"}
c_df["category"] = c_df["name"].map(cat_map)

c_curated = c_df[c_df["category"].isin(BEVERAGE_FRIENDLY_CATS)].head(20).reset_index(drop=True)
c_curated["culinary_rank"] = c_curated.index + 1
print("\nTop 10 (curated by FlavorGraph category - beverage-friendly only):")
print(c_curated.head(10)[["culinary_rank", "name", "category", "sim_to_anchor", "predicted_sentiment"]].to_string(index=False))
c_curated.to_csv(OUT / "variant_c_curated_top20.csv", index=False)
print(f"\nSaved: {OUT / 'variant_c_curated_top20.csv'}")
