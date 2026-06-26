# NLP Social Listening (English)

Twitter-based consumer intelligence pipeline for the KSF high-protein beverage brief.
It collects 5,021 clean English-language tweets across six query groups (flavour
preferences, morning routine, sensory pain points, yogurt-drink format, consumption
occasions, and competitor sentiment) and answers the six brief questions directly with
mapped analyses and visualisations. It also includes K-Means consumer segmentation
(silhouette-optimised) for the personalisation angle.

## Setup

```bash
conda activate ml
pip install -r requirements.txt
playwright install chromium
```

If a scrape returns no tweets, refresh the session credentials:

```bash
python -m scrapers.twitter_auth
```

## Run order

| Step | Notebook | Output |
|---|---|---|
| 1 | `notebooks/01_scrape.ipynb` | `data/raw/twitter_raw.csv` and `outputs/scraping_log.txt` |
| 2 | `notebooks/02_preprocess_and_enrich.ipynb` | `data/processed/twitter_enriched.csv` |
| 3a | `notebooks/03a_descriptive_analysis.ipynb` | result CSVs and Q1 to Q6 figures |
| 3b | `notebooks/03b_clustering.ipynb` | cluster profiles, PCA, and radar figures |
| 4 | `notebooks/04_insight_summary.ipynb` | `insight_summary.md` |

## Brief question to module map

| Question | Topic | Module | Chart |
|---|---|---|---|
| Q1 | Top flavour preferences | `analysis/flavor_analysis.py` | diverging bar |
| Q2 | APAC morning routine | `analysis/occasion_analysis.py` | APAC split and monthly trend |
| Q3 | Sensory pain points | `analysis/pain_analysis.py` | ranked bar with severity |
| Q4 | Yogurt-drink appetite | `analysis/format_analysis.py` | donut and dual-axis comparison |
| Q5 | Dominant occasions | `analysis/occasion_analysis.py` | treemap and occasion-by-flavour heatmap |
| Q6 | Competitor sentiment | `analysis/competitor_analysis.py` | small-multiples scorecard |
| Bonus | Consumer segments | `analysis/clustering.py` | PCA scatter and radar profiles |

## Project layout

```
config/         settings, six query groups, dictionaries (flavour, pain, occasion, format, brand, region)
scrapers/       twitter_auth (session login), twitter_scraper (Playwright)
preprocessing/  text_cleaner, language_filter, deduplicator
nlp/            sentiment (VADER and TextBlob), entity_extractor
analysis/       flavor, occasion, pain, format, competitor, clustering, _utils
visualization/  style and per-dimension chart modules
notebooks/      ordered pipeline, steps 01 to 04
data/           raw, processed, results
outputs/        figures and scraping_log.txt
```

## Method notes

- Scope is English-only. The labels are treated as flavour-universal consumer signals,
  with APAC and China-specific demand corroborated by separate sources.
- Sentiment uses VADER as the primary engine and TextBlob as a cross-validator.
  Consensus is the average of the two, and confidence is 1 minus the absolute
  difference between them.
- Clustering uses TF-IDF (max_features 500, ngrams 1 to 2) with K-Means, where k is
  selected by silhouette score over k in the range 2 to 7.
- The Q1 flavour chart applies a minimum-mention threshold of 20 so that low-volume
  flavours do not distort the ranked signal.
- Wordclouds are intentionally not used. Diverging bars, ranked bars, and
  small-multiples scorecards answer the brief's quantitative questions more directly.
