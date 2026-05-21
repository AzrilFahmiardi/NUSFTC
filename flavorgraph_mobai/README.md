# FlavorGraph × MoBai — AI-Driven Flavor Pipeline

**Project context:** Submission asset for **KSF Global Innovation Competition 2026** (problem statement: "AI + consumer data → personalised flavours for sustainable high protein beverages").

This module implements the **AI bridge layer** between consumer NLP and product science — a liking-score predictor that connects FlavorGraph 300-dim embeddings to consumer sentiment, enabling both validation of MoBai's chosen variants and systematic Variant C ideation.

## Pipeline Architecture

```
LAYER 1 · Consumer Voice          →   5,021 tweets, NLP (VADER + K-Means)
LAYER 2 · Molecular AI            →   FlavorGraph (metapath2vec + CSP, Park et al. 2021)
LAYER 3 · Liking-Score Predictor  →   THIS MODULE (cosine-anchor calibration)
LAYER 4 · Product Science         →   MoBai 5-mechanism off-note masking
```

## Key Results

| Result | Value |
|---|---|
| Variant A (Mango × Jasmine) predicted sentiment | **+46.9%** (HIGH bucket) |
| Variant B (Coconut × Milk Tea) predicted sentiment | **+49.4%** (HIGH bucket) |
| Discriminative baseline (Strawberry) | +26.7% (LOW-MID) |
| Pearson r between FlavorGraph similarity & NLP sentiment | **0.60** |
| Variant C top candidate | Crushed Pineapple, +41.5% |
| Total FlavorGraph nodes screened | 8,279 |

## Folder Layout

```
flavorgraph_mobai/
├── README.md                            (this file)
├── data/
│   ├── flavorgraph_embeddings.pickle    Pre-trained 300-dim node embeddings (Park et al.)
│   ├── nodes_191120.csv                 8,298 nodes metadata (FlavorGraph repo)
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
│   ├── pairing_predictions.csv          Variant A/B predictions vs baselines
│   ├── variant_c_curated_top20.csv      Top 20 beverage-friendly Variant C candidates
│   ├── variant_c_top50.csv              Unfiltered top 50 (for transparency)
│   ├── model_metrics.json               LOO-CV scores across 10 candidate models
│   ├── loocv_predictions.csv            Actual vs predicted per LOO fold
│   ├── sim_vs_sentiment_scatter.png     Calibration curve (Pearson r=0.60)
│   ├── variant_predictions_bar.png      Variant A/B vs baseline bar chart
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
python notebooks/03_train_liking_model.py  # LOO-CV across 10 model variants
python notebooks/04_predict_variants.py    # Variant A/B + screen Variant C
python notebooks/05_visualisations.py      # all 5 figures
```

## Honest Limitations (eksplisit untuk juri)

1. **Training set is small (n=13).** LOO-CV R² is negative for direct embedding regression — this is statistically expected with 13 samples × 300 features. We pivoted to **cosine-similarity-to-anchor as a single calibrated feature** (Pearson r=0.60 on training data, interpretable).
2. **`oolong` and `osmanthus` nodes do not exist** in FlavorGraph. For Variant B we use `black_tea + milk` as a milk-tea proxy.
3. **NLP sentiment is from global Twitter (5,021 tweets)** — 99% English-speaking audience, only 65 APAC-explicit tweets. The training labels are flavor-universal signals; China-specific preferences came from Innova/Mintel/Kerry (cited).
4. **Liking-score predictor calibration R² is 0.36 on training data** — useful for ranking (Spearman-driven decisions) but not for precise point estimates. Variant predictions are reported with sim-to-anchor numbers so judges can audit.
5. **The model does not account for** flavor concentration/rasio, food matrix protein-binding, HTST thermal degradation, or psychophysical masking — those are handled by MoBai Section 5's 5-mechanism stack with peer-reviewed lit.

## References

- Park, D., Kim, K., Kim, S., Spranger, M., & Kang, J. (2021). FlavorGraph: a large-scale food-chemical graph for generating food representations and recommending food pairings. *Scientific Reports* 11, 931. https://github.com/lamypark/FlavorGraph
- MoBai product concept (sibling document under `reference/`).
- NLP Consumer Intelligence Report (sibling document under `nlp social listening/outputs/`).
