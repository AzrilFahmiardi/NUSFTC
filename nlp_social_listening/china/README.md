# NLP Social Listening — China (KSF / MoBai)

Chinese-language, multi-platform consumer-intelligence pipeline for the KSF Global
Innovation Competition 2026 (high-protein beverage brief, target market: urban China).
This is the Chinese module of the parent `nlp_social_listening/` pipeline (one level up).
It reuses the parent's `analysis/` and `visualization/` packages and produces an
**enriched CSV with a schema mergeable** with the parent's `twitter_enriched.csv`, so a
joint EN+ZH k-means segmentation is possible (`notebooks/05`).

## Strategy (hybrid)

| Platform | Method | Why |
|---|---|---|
| **Xiaohongshu (RED)** #1 | **Apify** `easyapi~rednote-…` (search + comments) | Login-gated; needs +86 to self-host → use managed actor |
| **Weibo** #2 | MediaCrawler `--platform wb` (throwaway account) | Accepts intl numbers; QR login works |
| **Bilibili** | MediaCrawler `--platform bili` | Public search largely works |
| **Zhihu** | MediaCrawler `--platform zhihu` | Long-form honest reviews |
| **Douyin** | MediaCrawler `--platform dy` → Apify fallback | Harder device-binding |

Chinese NLP: **jieba** tokenization + **RoBERTa-JD** sentiment (primary) + **SnowNLP**
(cross-validator), mirroring the English VADER+TextBlob consensus. Sentiment runs on
**original-language** text (no pre-translation, per brief §10.2).

## Setup

### ✅ Already done (verified)
- Python deps installed in conda env `ml` (jieba, snownlp, apify-client, tabulate; torch/
  transformers/vaderSentiment/textblob/langdetect/sklearn already present).
- All modules import cleanly; full enrich pipeline verified on synthetic data; the Chinese
  RoBERTa-JD sentiment model downloads & runs.
- MediaCrawler cloned to `third_party/MediaCrawler` and `uv sync`-ed (its own venv); CLI works.
- `google-chrome` present (for MediaCrawler CDP login mode).

To re-create deps elsewhere: `conda activate ml && pip install -r requirements.txt`.

### ⛔ YOU still need to do (before scraping)
1. **Register ONE throwaway China account** (e.g. Weibo with your Indonesian number —
   NOT a personal account; treat it as disposable). Login is via QR scan when the runner
   launches Chrome in 01a.
2. **Apify token** — register free at apify.com (~$5 free credits, no card), then create
   `nlp_social_china/.env` (gitignored):
   ```
   APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxx
   ```

## Run order

| Step | File | Output | Spend |
|---|---|---|---|
| 0 | — | setup above; register account + token | $0 |
| 1 | `notebooks/01_smoke_test.py` | 1 keyword/platform; verify schema + merge | ~$0.10 |
| 2 | `notebooks/01a_scrape_mediacrawler.py` | Weibo/Bilibili/Zhihu/Douyin → `data/interim/` | ~$0 |
| 3 | `notebooks/01b_scrape_apify.py` | XHS search + comments → `data/interim/` | ~$10–25 |
| 4 | `notebooks/01c_normalize_to_raw.py` | `data/raw/*_raw.csv` + `china_all_raw.csv` | $0 |
| 5 | `notebooks/02_preprocess_and_enrich.py` | `data/processed/china_enriched.csv` | $0 |
| 6 | `notebooks/03a_descriptive_analysis.py` | result CSVs + figures (Q1–Q6, per platform) | $0 |
| 7 | `notebooks/03b_clustering.py` | China cluster profiles + PCA/radar | $0 |
| 8 | `notebooks/04_insight_summary.py` | `outputs/insight_summary_cn.md` | $0 |
| 9 | `notebooks/05_joint_clustering_en_zh.py` | merged EN+ZH segmentation | $0 |

> The `.py` scripts double as notebook sources (run with `python notebooks/<file>.py`).
> Convert to `.ipynb` with `jupytext --to notebook notebooks/*.py` if desired.

## Project layout
```
config/         settings, queries_cn (A1–A6/B/E), dictionaries_cn (bilingual), stopwords_cn
scrapers/       mediacrawler_runner, apify_client_xhs, apify_client_generic, normalize (adapter)
preprocessing/  text_cleaner_cn (CJK-safe + jieba), language_router
nlp/            sentiment_cn (RoBERTa-JD + SnowNLP consensus, language-routed)
data/           interim (raw dumps) → raw (normalized) → processed (enriched) → results
outputs/        figures + scraping_log.txt
third_party/    MediaCrawler (gitignored)
notebooks/      01_smoke_test, 01a/01b/01c, 02, 03a, 03b, 04, 05
```

## Reuse from sibling project (`../nlp social listening/`)
Imported via `sys.path` (kept in sync, not copied): `deduplicator`, `language_filter.detect_lang`,
`entity_extractor.extract` (fed `dictionaries_cn`), all `analysis/*` & `visualization/*`,
and the English `SentimentAnalyzer` (for en-language rows).

## Honest limitations (for judges)
- Throwaway-account ban risk (rate-limited, `MAX_CONCURRENCY_NUM=1`, partial dumps saved).
- XHS unreachable on a +62 number → Apify-first by design (plan does not depend on self-hosting XHS).
- RoBERTa-JD is **binary**; the `neutral` class is recovered via the consensus threshold (±0.05),
  weaker than English VADER neutral — documented.
- MediaCrawler is **research/learning-licensed** — volumes kept modest; bulk shifted to Apify.
- Joint EN+ZH clustering uses **language-agnostic entity/sentiment features** (not bilingual
  TF-IDF, which would trivially split by language) — an intentional, judge-explained choice.
