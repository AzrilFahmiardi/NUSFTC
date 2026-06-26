# Flavor Pairing: Molecular Compatibility Recommender

This module connects consumer flavour preferences to molecular flavour science. It
uses pre-trained 300-dimensional FlavorGraph embeddings (Park et al., 2021) to score
how molecularly compatible a candidate flavour is with the flavours consumers already
like, and to screen the full FlavorGraph ingredient vocabulary for new candidates.

This is a pairing-compatibility recommender and screening tool. It is not a liking
predictor. The output is a compatibility score (cosine similarity to a consumer-liked
anchor) and a qualitative affinity tier, not a predicted liking percentage.

## How it works

1. A consumer-preference anchor is built by averaging the embeddings of the flavours
   with the highest positive sentiment in the consumer intelligence pipeline (mango,
   vanilla, caramel, coconut, milk tea).
2. Each candidate flavour, or combined multi-ingredient variant, is scored by its
   cosine similarity to that anchor centroid.
3. Scores are mapped to affinity tiers (HIGH, MID-HIGH, MID, LOW) and used to rank
   thousands of candidate ingredients down to a small, human-testable shortlist.

## Data files

- `data/flavorgraph_embeddings.pickle`  Pre-trained 300-dim node embeddings (Park et al.)
- `data/nodes_191120.csv`               FlavorGraph node metadata (8,298 nodes)
- `data/mobai_target_nodes.csv`         MoBai flavour to FlavorGraph node mapping
- `data/nlp_flavor_sentiment.csv`       Flavour sentiment labels from the NLP pipeline
- `data/trained_models.pkl`             Consumer-liked anchor centroid and metadata

## Run order

```bash
conda activate ml
cd flavor_pairing

python notebooks/01_load_and_explore.py        # verify nodes and embeddings load
python notebooks/02_build_training_data.py      # build the 13-flavour labelled set
python notebooks/03_anchor_and_diagnostics.py   # build anchor; LOO-CV honesty diagnostic
python notebooks/04_predict_variants.py         # variant compatibility and Variant C screen
python notebooks/05_visualisations.py           # generate all figures
```

## Key results

| Result | Value |
|---|---|
| Variant A (Mango and Jasmine) compatibility | HIGH affinity tier, score 0.73 |
| Variant B (Coconut and Milk Tea) compatibility | HIGH affinity tier, score 0.79 |
| Discriminative baseline (Strawberry) | LOW affinity tier, score 0.26 |
| Variant C top screened candidate | Crushed Pineapple, MID-HIGH tier, score 0.61 |
| FlavorGraph dataset | 8,298 nodes, 8,297 with embeddings, 8,279 screened for Variant C |

## Honest limitations

1. We do not claim a predictive liking model. With 13 flavour samples against
   300-dimensional embeddings, every regressor has negative Leave-One-Out CV R2.
   This is statistically expected and recorded openly in `outputs/model_metrics.json`.
   FlavorGraph is therefore used as a molecular compatibility screen, which is the
   task it was peer-reviewed for in Park et al., 2021. Liking is validated downstream
   by a primary consumer panel.
2. The Pearson r = 0.60 figure between compatibility and sentiment is in-sample and
   descriptive only. The anchor is built from the same flavours it is correlated
   against, so it is inflated by construction. It supports the screening logic and is
   never reported as out-of-sample predictive performance.
3. The nodes for oolong and osmanthus do not exist in FlavorGraph. For Variant B we
   use black_tea and milk as a milk-tea proxy.
4. NLP sentiment is from global English-language Twitter. The labels are treated as
   flavour-universal signals; China-specific demand is corroborated by separate
   sources.
5. The screen does not account for flavour concentration, food-matrix protein
   binding, or thermal degradation. Those are addressed by formulation development
   and the off-note masking analysis in the `flavor_masking/` module.
