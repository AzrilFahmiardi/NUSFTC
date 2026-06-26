"""
03 - Diagnostic: can any liking-score model generalise at n=13? (Answer: no.)

We deliberately test a panel of regressors with Leave-One-Out CV to establish,
transparently, that direct liking-score prediction does NOT generalise on 13
flavour samples (all LOO-CV R2 are negative — statistically expected for n=13).
This is WHY the downstream module (04) uses FlavorGraph only as a molecular
COMPATIBILITY SCREEN (ranking) rather than a liking predictor. We also persist
the consumer-liked anchor centroid used by that screen.

Outputs:
- outputs/model_metrics.json: LOO-CV scores per model (the honesty record)
- data/trained_models.pkl: consumer-liked anchor centroid + reference metadata
- outputs/loocv_predictions.csv: actual vs predicted per fold
"""
import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.kernel_ridge import KernelRidge
from sklearn.model_selection import LeaveOneOut
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.dummy import DummyRegressor

ROOT = Path("__file__" in globals() and __file__ or "notebooks/dummy.py").resolve().parents[1] if "__file__" in globals() else Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
DATA = ROOT / "data"
OUT = ROOT / "outputs"

with open(DATA / "training_data.pkl", "rb") as f:
    td = pickle.load(f)

X, y, names = td["X"], td["y"], td["names"]
print(f"Loaded training data: X={X.shape}, y={y.shape}")

# L2-normalise embeddings (best practice for cosine-based comparisons)
X_norm = X / np.linalg.norm(X, axis=1, keepdims=True)

# Consumer-liked anchor = centroid of the top-N highest-sentiment flavours.
# NOTE: the correlation printed below is IN-SAMPLE (the anchor is built from the
# same points it is correlated against), so it is descriptive only and inflated by
# construction. The out-of-sample truth is in the LOO-CV table further down (the
# sim_anchor fold recomputes the anchor from training data only). Do not quote the
# in-sample number as predictive performance.
N_ANCHOR = 5
top_idx = np.argsort(y)[-N_ANCHOR:]
top_centroid = X_norm[top_idx].mean(axis=0)
top_centroid = top_centroid / np.linalg.norm(top_centroid)
sim_to_top = cosine_similarity(X_norm, top_centroid.reshape(1, -1)).flatten()
print(f"Consumer-liked anchor flavours (top-{N_ANCHOR} sentiment): {[names[i] for i in top_idx]}")
print(f"Cosine sim to anchor: range=[{sim_to_top.min():.3f}, {sim_to_top.max():.3f}]")
print(f"In-sample (descriptive, inflated) Pearson corr(sim, y) = {np.corrcoef(sim_to_top, y)[0,1]:.3f}")
print("  -> see LOO-CV table below for the honest out-of-sample picture")

# Build feature variants
X_sim_feat = sim_to_top.reshape(-1, 1)  # single feature: similarity to liked anchors

# Define candidate models
def build_pca_ridge(n_components, alpha):
    return Pipeline([
        ("scale", StandardScaler()),
        ("pca", PCA(n_components=n_components, random_state=42)),
        ("model", Ridge(alpha=alpha)),
    ])

models = {
    "baseline_mean":     ("X",       DummyRegressor(strategy="mean")),
    "ridge_a1":          ("X",       Pipeline([("scale", StandardScaler()), ("model", Ridge(alpha=1.0))])),
    "ridge_a10":         ("X",       Pipeline([("scale", StandardScaler()), ("model", Ridge(alpha=10.0))])),
    "ridge_a100":        ("X",       Pipeline([("scale", StandardScaler()), ("model", Ridge(alpha=100.0))])),
    "pca5_ridge_a1":     ("X",       build_pca_ridge(5, 1.0)),
    "pca3_ridge_a1":     ("X",       build_pca_ridge(3, 1.0)),
    "pca2_ridge_a1":     ("X",       build_pca_ridge(2, 1.0)),
    "kernel_ridge_rbf":  ("X",       Pipeline([("scale", StandardScaler()), ("model", KernelRidge(alpha=1.0, kernel="rbf", gamma=0.01))])),
    "random_forest":     ("X",       RandomForestRegressor(n_estimators=200, max_depth=4, random_state=42)),
    "sim_anchor_linear": ("X_sim",   Pipeline([("scale", StandardScaler()), ("model", Ridge(alpha=0.1))])),
}

# LOO-CV
loo = LeaveOneOut()
results = {}
preds_records = []

def fresh_model(model_name):
    """Build a fresh unfit estimator (avoid LOO leakage from refitting)."""
    if model_name == "baseline_mean":
        return DummyRegressor(strategy="mean")
    if model_name.startswith("ridge_a"):
        a = float(model_name.split("_a")[1])
        return Pipeline([("scale", StandardScaler()), ("model", Ridge(alpha=a))])
    if model_name.startswith("pca"):
        # e.g. pca5_ridge_a1
        parts = model_name.split("_")
        n = int(parts[0].replace("pca", ""))
        a = float(parts[2].replace("a", ""))
        return build_pca_ridge(n, a)
    if model_name == "kernel_ridge_rbf":
        return Pipeline([("scale", StandardScaler()), ("model", KernelRidge(alpha=1.0, kernel="rbf", gamma=0.01))])
    if model_name == "random_forest":
        return RandomForestRegressor(n_estimators=200, max_depth=4, random_state=42)
    if model_name == "sim_anchor_linear":
        return Pipeline([("scale", StandardScaler()), ("model", Ridge(alpha=0.1))])
    raise ValueError(model_name)


for model_name, (feat_key, _) in models.items():
    preds = np.zeros(len(y))
    # For sim_anchor, anchor centroid must be recomputed per fold (to avoid leakage)
    for train_idx, test_idx in loo.split(X):
        if feat_key == "X_sim":
            # Recompute anchor from training data only
            train_top = train_idx[np.argsort(y[train_idx])[-N_ANCHOR:]]
            anchor = X_norm[train_top].mean(axis=0)
            anchor = anchor / np.linalg.norm(anchor)
            X_fold = cosine_similarity(X_norm, anchor.reshape(1, -1))
        else:
            X_fold = X

        m_ = fresh_model(model_name)
        m_.fit(X_fold[train_idx], y[train_idx])
        preds[test_idx[0]] = m_.predict(X_fold[test_idx])[0]

    mae = mean_absolute_error(y, preds)
    r2 = r2_score(y, preds)
    rmse = float(np.sqrt(np.mean((y - preds) ** 2)))
    spearman = float(pd.Series(y).corr(pd.Series(preds), method="spearman"))
    results[model_name] = {
        "loocv_mae": float(mae),
        "loocv_r2": float(r2),
        "loocv_rmse": rmse,
        "spearman_corr": spearman,
    }
    for i, (a, p) in enumerate(zip(y, preds)):
        preds_records.append({"model": model_name, "flavor": names[i], "actual": int(a), "predicted": float(p)})

print("\n=== LOO-CV Results ===")
df_metrics = pd.DataFrame(results).T
print(df_metrics.round(3).to_string())

# Save metrics
OUT.mkdir(exist_ok=True)
with open(OUT / "model_metrics.json", "w") as f:
    json.dump(results, f, indent=2)

pred_df = pd.DataFrame(preds_records)
pred_df.to_csv(OUT / "loocv_predictions.csv", index=False)

# Pick best non-baseline model by Spearman (more robust for small-N ranking-style use case)
ranked = sorted(
    (n for n in results if n != "baseline_mean"),
    key=lambda n: results[n]["spearman_corr"],
    reverse=True,
)
best_name = ranked[0]
print(f"\nBest non-baseline model (by Spearman): {best_name}")
print(f"  Spearman={results[best_name]['spearman_corr']:.3f}, R²={results[best_name]['loocv_r2']:.3f}, MAE={results[best_name]['loocv_mae']:.2f}")

# Fit final models on FULL data
final_models = {}
feat_key, _ = models[best_name]
final_models["best"] = fresh_model(best_name)
if feat_key == "X_sim":
    final_models["best"].fit(sim_to_top.reshape(-1, 1), y)
else:
    final_models["best"].fit(X, y)

# Also keep sim_anchor_linear as the conservative default (interpretable, low-variance)
final_models["sim_anchor_linear"] = fresh_model("sim_anchor_linear")
final_models["sim_anchor_linear"].fit(sim_to_top.reshape(-1, 1), y)

with open(DATA / "trained_models.pkl", "wb") as f:
    pickle.dump({
        "models": final_models,
        "best_name": best_name,
        "best_feature_key": feat_key,
        "top_anchor_centroid": top_centroid,
        "top_anchor_flavors": [names[i] for i in top_idx],
        "training_y_mean": float(y.mean()),
        "training_y_std": float(y.std()),
        "training_y_min": float(y.min()),
        "training_y_max": float(y.max()),
    }, f)
print(f"Saved trained models: {list(final_models.keys())}")
print(f"Outputs: outputs/model_metrics.json, outputs/loocv_predictions.csv, data/trained_models.pkl")
