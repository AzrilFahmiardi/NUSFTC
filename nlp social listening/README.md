# NLP Social Listening 2 — KSF Global Innovation Competition 2026

Twitter-only consumer intelligence pipeline for the KSF high-protein beverage brief. Pulls ~2–3k clean English tweets across 6 query groups (flavor, morning routine, pain points, yogurt-drink format, occasion, competitor) and answers the six brief questions directly with mapped analyses + visualisations. Includes K-means consumer segmentation (silhouette-optimised) for the personalisation angle.

## Setup

```bash
cd "nlp social listening 2"
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

`cookies.json` is copied from the predecessor project and is valid. If a run returns no tweets, refresh cookies:

```bash
python -m scrapers.twitter_auth
```

## Run order

| Step | Notebook | Output |
|---|---|---|
| 1 | `notebooks/01_scrape.ipynb` | `data/raw/twitter_raw.csv` + `outputs/scraping_log.txt` |
| 2 | `notebooks/02_preprocess_and_enrich.ipynb` | `data/processed/twitter_enriched.csv` |
| 3a | `notebooks/03a_descriptive_analysis.ipynb` | 5 result CSVs + 7 PNGs (Q1–Q6) |
| 3b | `notebooks/03b_clustering.ipynb` | `cluster_profiles.csv` + PCA + radar PNGs |
| 4 | `notebooks/04_insight_summary.ipynb` | `insight_summary.md` |

## Brief question → module map

| # | Brief question | Module | Chart |
|---|---|---|---|
| Q1 | Top flavor preferences | `analysis/flavor_analysis.py` | diverging bar |
| Q2 | APAC morning routine | `analysis/occasion_analysis.py` | APAC split + monthly trend |
| Q3 | Sensory pain points | `analysis/pain_analysis.py` | ranked bar w/ severity + quotes |
| Q4 | Yogurt-drink appetite | `analysis/format_analysis.py` | donut + dual-axis comparison |
| Q5 | Dominant occasions | `analysis/occasion_analysis.py` | treemap + occasion×flavor heatmap |
| Q6 | Competitor sentiment | `analysis/competitor_analysis.py` | small-multiples scorecard |
| Bonus | Consumer segments | `analysis/clustering.py` | PCA scatter + radar profiles |

## Project layout

```
config/       settings, queries (6 groups), dictionaries (flavor/pain/occasion/format/brand/region)
scrapers/     twitter_auth (cookie login), twitter_scraper (Playwright interception)
preprocessing/ text_cleaner, language_filter, deduplicator
nlp/          sentiment (VADER + TextBlob), entity_extractor
analysis/     flavor, occasion, pain, format, competitor, clustering, _utils
visualization/ style, flavor_viz, occasion_viz, pain_viz, format_viz, competitor_viz, cluster_viz
notebooks/    01..04 ordered pipeline
data/         raw → processed → results
outputs/      figures (PNG 300dpi) + scraping_log.txt
```

## Notes

- Scope is **English-only**; Twitter is blocked in mainland China so Chinese-language signal is captured indirectly via SG / MY / PH / IN / TW / HK / expat APAC.
- Sentiment uses VADER as the primary engine, TextBlob as a cross-validator (consensus = average; confidence = 1 − |VADER − TextBlob|).
- Clustering uses TF-IDF (`max_features=500`, ngrams 1–2) + KMeans, with k selected by silhouette over k ∈ [2, 7].
- Wordclouds are intentionally **not** used — diverging bars, ranked bars, and small-multiples scorecards answer the brief's quantitative questions far more directly.
