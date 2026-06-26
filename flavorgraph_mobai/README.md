# FlavorGraph × MoBai — AI-Driven Flavor Pipeline

**Project context:** Submission asset for **KSF Global Innovation Competition 2026** (problem statement: "AI + consumer data → personalised flavours for sustainable high protein beverages").

This module implements the **AI bridge layer** between consumer NLP and product science — a **molecular pairing-compatibility recommender** that uses FlavorGraph 300-dim embeddings to screen and rank flavour combinations against the flavours consumers already like. It is a screening/ranking tool, not a liking-score predictor: with n=13 no liking model generalises (all LOO-CV R² negative, reported openly below), so we use the embeddings for the task they were peer-reviewed for in Park et al. 2021 — food-pairing recommendation — and validate liking downstream with a primary sensory panel.

## Pipeline Architecture

```
LAYER 1 · Consumer Voice               →   5,021 tweets, NLP (VADER + K-Means)
LAYER 2 · Molecular AI                 →   FlavorGraph (metapath2vec + CSP, Park et al. 2021)
LAYER 3 · Flavor-Pairing Recommender   →   THIS MODULE (molecular-compatibility screening)
LAYER 4 · Product Science              →   MoBai 5-mechanism off-note masking
```

## Key Results

The compatibility score is the cosine similarity of a candidate (or candidate pairing)
to the centroid of the highest-sentiment NLP flavours (the "consumer-liked anchor").
It ranks candidates; it is **not** a liking percentage. Affinity tiers are defined
relative to the 13 NLP flavours' own compatibility scores.

| Result | Value |
|---|---|
| Variant A (Mango × Jasmine) molecular compatibility | **HIGH affinity tier** |
| Variant B (Coconut × Milk Tea) molecular compatibility | **HIGH affinity tier** |
| Discriminative baseline (Strawberry) | LOW affinity tier |
| In-sample directional consistency (compatibility vs NLP sentiment) | Pearson r = 0.60 (descriptive, not predictive) |
| Out-of-sample liking prediction (LOO-CV) | All models R² < 0 → not claimed; see `model_metrics.json` |
| Variant C top screened candidate | Crushed Pineapple (HIGH affinity tier) |
| FlavorGraph dataset | 8,298 nodes (6,653 ingredients + 1,645 compounds), 8,297 with embeddings |

## Folder Layout

```
flavorgraph_mobai/
├── README.md                            (this file)
├── data/
│   ├── flavorgraph_embeddings.pickle    Pre-trained 300-dim node embeddings (Park et al.)
│   ├── nodes_191120.csv                 8,298 node metadata (6,653 ingredients + 1,645 compounds; FlavorGraph repo)
│   ├── dict_ingr2cate.csv               616 ingredient → category mapping
│   ├── nlp_flavor_sentiment.csv         Auto-generated from NLP report Q1 chart
│   ├── mobai_target_nodes.csv           Curated MoBai-flavor → FlavorGraph-node mapping
│   ├── training_data.pkl                X (13 × 300), y (13), names
│   ├── training_data_summary.csv        Human-readable training table
│   └── trained_models.pkl               Best model + anchor centroid + metadata
├── notebooks/                           Executable Python scripts (call via `python <file>`)
│   ├── 01_load_and_explore.py
│   ├── 02_build_training_data.py
│   ├── 03_train_liking_model.py
│   ├── 04_predict_variants.py
│   └── 05_visualisations.py
├── outputs/
│   ├── pairing_compatibility.csv        Variant A/B + baseline compatibility scores
│   ├── variant_c_curated_top20.csv      Top 20 beverage-friendly Variant C candidates
│   ├── variant_c_top50.csv              Unfiltered top 50 (for transparency)
│   ├── model_metrics.json               LOO-CV scores across 10 candidate models (all R²<0)
│   ├── loocv_predictions.csv            Actual vs predicted per LOO fold
│   ├── sim_vs_sentiment_scatter.png     In-sample consistency check (descriptive, r=0.60)
│   ├── variant_compatibility_bar.png    Variant A/B vs baseline compatibility chart
│   ├── variant_c_top10.png              Variant C top 10 chart
│   ├── tsne_mobai_subgraph.png          2D t-SNE w/ MoBai nodes highlighted
│   └── ai_stack_diagram.png             4-layer architecture visualisation
└── docs/
    ├── concept_one_pager.md             Final submission per Guideline slide 18
    ├── audit_trail_nlp_to_mobai.md      Justification for NLP→MoBai flavor pivot
    ├── ksf_brand_integration.md         Master Kong brand DNA leverage
    └── revenue_model.md                 TAM/SAM/SOM + unit economics
```

## Reproducing the Pipeline

```bash
conda activate ml
cd flavorgraph_mobai

python notebooks/01_load_and_explore.py    # verify nodes available
python notebooks/02_build_training_data.py # build 13-flavor labeled set
python notebooks/03_train_liking_model.py  # LOO-CV diagnostic across 10 model variants
python notebooks/04_predict_variants.py    # Variant A/B compatibility + screen Variant C
python notebooks/05_visualisations.py      # all 5 figures
```

## Honest Limitations (eksplisit untuk juri)

1. **We do not claim a predictive liking model.** With n=13 (× 300-dim embeddings) every regressor has negative LOO-CV R² — statistically expected, and recorded openly in `model_metrics.json`. FlavorGraph is therefore used as a molecular **compatibility screen** (ranking thousands of candidates to a human-testable shortlist), the task it was peer-reviewed for in Park et al. 2021. Liking itself is validated downstream by a primary sensory panel.
2. **The Pearson r = 0.60 figure is in-sample and descriptive only.** It is the directional consistency between the compatibility score and NLP sentiment on the same 13 flavours that build the anchor (inflated by construction). It supports the screening logic; it is not out-of-sample predictive performance and is never reported as such.
3. **`oolong` and `osmanthus` nodes do not exist** in FlavorGraph. For Variant B we use `black_tea + milk` as a milk-tea proxy.
4. **NLP sentiment is from global Twitter (5,021 tweets)** — 99% English-speaking audience, only 65 APAC-explicit tweets. The labels are flavour-universal signals; China-specific demand is corroborated by the China NLP pipeline (Xiaohongshu/Weibo) and Innova/Mintel/Kerry (cited).
5. **The screen does not account for** flavour concentration/ratio, food-matrix protein binding, HTST thermal degradation, or psychophysical masking — those are handled by MoBai Section 5's 5-mechanism stack with peer-reviewed lit.

## References

- Park, D., Kim, K., Kim, S., Spranger, M., & Kang, J. (2021). FlavorGraph: a large-scale food-chemical graph for generating food representations and recommending food pairings. *Scientific Reports* 11, 931. https://github.com/lamypark/FlavorGraph
- MoBai product concept (sibling document under `reference/`).
- NLP Consumer Intelligence Report (sibling document under `nlp social listening/outputs/`).
