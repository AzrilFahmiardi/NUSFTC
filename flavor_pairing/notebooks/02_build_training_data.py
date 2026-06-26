"""
02 - Build training dataset: match NLP flavor sentiment to FlavorGraph embeddings.

Outputs:
- data/training_data.pkl: dict with 'X' (n_samples, 300), 'y' (n_samples,), 'names'
- data/training_data_summary.csv: human-readable summary
"""
import pickle
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path("__file__" in globals() and __file__ or "notebooks/dummy.py").resolve().parents[1] if "__file__" in globals() else Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
DATA = ROOT / "data"

# Load assets
with open(DATA / "flavorgraph_embeddings.pickle", "rb") as f:
    emb = pickle.load(f)
target_map = pd.read_csv(DATA / "mobai_target_nodes.csv")
nlp = pd.read_csv(DATA / "nlp_flavor_sentiment.csv")
print(f"NLP flavors: {len(nlp)}")
print(f"Target map entries: {len(target_map)}")


def get_vector(node_or_compound: str) -> np.ndarray | None:
    """Resolve a target spec (possibly compound like 'black_tea+milk') to vector."""
    if not isinstance(node_or_compound, str) or not node_or_compound:
        return None
    if "+" in node_or_compound:
        # Compound proxy - average vectors
        parts = node_or_compound.split("+")
        vecs = []
        for p in parts:
            # Look up the part name -> node_id from target_map flavorgraph_node column
            match = target_map[target_map["flavorgraph_node"] == p]
            if not match.empty:
                nid = str(match.iloc[0]["node_id"])
                if nid in emb:
                    vecs.append(emb[nid])
        if vecs:
            return np.mean(vecs, axis=0)
        return None
    else:
        match = target_map[target_map["flavorgraph_node"] == node_or_compound]
        if not match.empty:
            nid = str(match.iloc[0]["node_id"])
            if nid in emb:
                return emb[nid]
        return None


# Build training samples
samples = []
for _, nlp_row in nlp.iterrows():
    flavor = nlp_row["flavor_name"]
    target = target_map[target_map["mobai_term"] == flavor]
    if target.empty:
        print(f"  SKIP {flavor}: no target mapping")
        continue
    fg_node = target.iloc[0]["flavorgraph_node"]
    vec = get_vector(fg_node)
    if vec is None:
        print(f"  SKIP {flavor}: no vector for '{fg_node}'")
        continue
    samples.append({
        "flavor_name": flavor,
        "flavorgraph_node": fg_node,
        "vector": vec,
        "net_sentiment": nlp_row["net_sentiment_pct"],
        "mention_count": nlp_row["mention_count"],
    })
    print(f"  OK   {flavor:12s} -> {fg_node:25s} sentiment={nlp_row['net_sentiment_pct']:+d}")

if not samples:
    raise SystemExit("No training samples!")

# Stack into arrays
X = np.stack([s["vector"] for s in samples])
y = np.array([s["net_sentiment"] for s in samples])
names = [s["flavor_name"] for s in samples]

print(f"\n=== Training data ===")
print(f"X shape: {X.shape}")
print(f"y shape: {y.shape}")
print(f"y range: [{y.min()}, {y.max()}], mean={y.mean():.1f}, std={y.std():.1f}")

# Save
out = {"X": X, "y": y, "names": names, "feature_dim": X.shape[1]}
with open(DATA / "training_data.pkl", "wb") as f:
    pickle.dump(out, f)

summary = pd.DataFrame([{
    "flavor_name": s["flavor_name"],
    "flavorgraph_node": s["flavorgraph_node"],
    "net_sentiment": s["net_sentiment"],
    "mention_count": s["mention_count"],
    "vector_norm": float(np.linalg.norm(s["vector"])),
} for s in samples])
summary.to_csv(DATA / "training_data_summary.csv", index=False)
print(f"\nSaved: training_data.pkl ({len(samples)} samples), training_data_summary.csv")
print(summary.to_string(index=False))
