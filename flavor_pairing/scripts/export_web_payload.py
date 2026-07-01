"""
Export a small, curated FlavorGraph payload for the mobai-web live compatibility tool.

The web tool computes molecular pairing-compatibility entirely in the browser:
cosine similarity between a (combined) candidate vector and the consumer-liked anchor
centroid. This script exports only what the browser needs:

- the 300-dim anchor centroid (already L2-normalised by notebook 03),
- a curated set of node vectors (variant ingredients, anchor/baseline flavours,
  and the Variant C beverage-friendly shortlist), each with its precomputed
  single-ingredient compatibility score and affinity tier,
- a few preset pairings (Variant A / B / baselines) for verification.

This mirrors notebooks/04_predict_variants.py exactly (same combine + cosine logic),
so browser scores reproduce pairing_compatibility.csv (mango x jasmine -> 0.73,
coconut x milk tea -> 0.79, strawberry -> 0.26). It is a compatibility-ranking screen,
not a liking prediction.

Run:
    conda activate ml
    python flavor_pairing/scripts/export_web_payload.py
"""
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT_DIR = ROOT.parent / "mobai-web" / "app" / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Fixed affinity-tier bands as published in the final report (Table 5).
TIER_HIGH = 0.70
TIER_MID_HIGH = 0.50
TIER_MID = 0.35


def tier_of(score: float) -> str:
    if score >= TIER_HIGH:
        return "HIGH"
    if score >= TIER_MID_HIGH:
        return "MID-HIGH"
    if score >= TIER_MID:
        return "MID"
    return "LOW"


def pretty(name: str) -> str:
    return name.replace("_", " ").strip().title()


# ---- Load assets -----------------------------------------------------------
with open(DATA / "flavorgraph_embeddings.pickle", "rb") as f:
    emb = pickle.load(f)
with open(DATA / "trained_models.pkl", "rb") as f:
    trained = pickle.load(f)

nodes = pd.read_csv(DATA / "nodes_191120.csv")
nodes["node_id_str"] = nodes["node_id"].astype(str)
name_to_id = dict(zip(nodes["name"], nodes["node_id_str"]))
id_to_type = dict(zip(nodes["node_id_str"], nodes["node_type"]))

cat_map = {}
cat_path = DATA / "dict_ingr2cate.csv"
if cat_path.exists():
    cat_df = pd.read_csv(cat_path)
    cat_map = dict(zip(cat_df["ingredient"], cat_df["category"]))

anchor = np.asarray(trained["top_anchor_centroid"], dtype=float)
anchor = anchor / np.linalg.norm(anchor)
anchor_flavors = [pretty(n) for n in trained.get("top_anchor_flavors", [])]


def vec(name):
    nid = name_to_id.get(name)
    if nid is None or nid not in emb:
        return None
    v = np.asarray(emb[nid], dtype=float)
    return v / np.linalg.norm(v)


def combine(names):
    vecs = [vec(n) for n in names]
    vecs = [v for v in vecs if v is not None]
    if not vecs:
        return None
    v = np.mean(vecs, axis=0)
    return v / np.linalg.norm(v)


def score_of(v):
    return float(np.dot(v, anchor))  # both unit-normalised -> cosine


# ---- Curated node selection ------------------------------------------------
variant_ingredients = ["fresh_mango", "jasmine_tea", "coconut", "black_tea", "milk", "yogurt"]
baseline_flavours = [
    "vanilla", "caramel", "strawberry", "chocolate", "oat",
    "coffee", "banana", "matcha_green_tea_powder", "canned_peach", "honey",
]
explore_extra = [
    "lychee", "passion_fruit", "white_peach", "pineapple", "kiwi",
    "almond", "walnut", "cinnamon", "mulberry", "date",
]

variant_c = []
cur_path = ROOT / "outputs" / "variant_c_curated_top20.csv"
if cur_path.exists():
    variant_c = pd.read_csv(cur_path)["name"].head(12).tolist()

# Group labels drive how the tool groups the picker list.
group_of = {}
for n in variant_ingredients:
    group_of[n] = "Variant ingredient"
for n in baseline_flavours:
    group_of[n] = "Reference flavour"
for n in variant_c:
    group_of.setdefault(n, "Variant C candidate")
for n in explore_extra:
    group_of.setdefault(n, "Explore")

ordered = []
for n in variant_ingredients + baseline_flavours + variant_c + explore_extra:
    if n not in ordered:
        ordered.append(n)

node_payload = []
seen = set()
for name in ordered:
    if name in seen:
        continue
    v = vec(name)
    if v is None:
        continue
    seen.add(name)
    s = score_of(v)
    node_payload.append({
        "name": name,
        "label": pretty(name),
        "group": group_of.get(name, "Explore"),
        "type": id_to_type.get(name_to_id.get(name, ""), "ingredient"),
        "category": cat_map.get(name, None),
        "score": round(s, 4),
        "tier": tier_of(s),
        "vec": [round(float(x), 5) for x in v.tolist()],
    })

# ---- Preset pairings (for verification + tool presets) ---------------------
preset_specs = [
    {"label": "Variant A - Mango x Jasmine", "names": ["fresh_mango", "jasmine_tea"]},
    {"label": "Variant B - Coconut x Milk Tea", "names": ["coconut", "black_tea", "milk"]},
    {"label": "Variant A full product", "names": ["yogurt", "fresh_mango", "jasmine_tea"]},
    {"label": "Variant B full product", "names": ["yogurt", "coconut", "black_tea", "milk"]},
    {"label": "Strawberry (low baseline)", "names": ["strawberry"]},
]
presets = []
for spec in preset_specs:
    v = combine(spec["names"])
    if v is None:
        continue
    s = score_of(v)
    presets.append({
        "label": spec["label"],
        "names": spec["names"],
        "score": round(s, 4),
        "tier": tier_of(s),
    })

payload = {
    "_note": "Molecular pairing-compatibility (cosine to consumer-liked anchor). Not a liking prediction.",
    "dim": int(anchor.shape[0]),
    "tiers": {"HIGH": TIER_HIGH, "MID_HIGH": TIER_MID_HIGH, "MID": TIER_MID},
    "anchorFlavors": anchor_flavors,
    "anchor": [round(float(x), 5) for x in anchor.tolist()],
    "nodes": node_payload,
    "presets": presets,
}

out_file = OUT_DIR / "compat_engine.json"
with open(out_file, "w") as f:
    json.dump(payload, f, separators=(",", ":"))

print(f"Wrote {out_file}  ({out_file.stat().st_size/1024:.0f} KB)")
print(f"  anchor dim: {payload['dim']}, nodes: {len(node_payload)}, presets: {len(presets)}")
print("  Verification (should match pairing_compatibility.csv):")
for p in presets:
    print(f"    {p['score']:.4f}  {p['tier']:9s}  {p['label']}")
