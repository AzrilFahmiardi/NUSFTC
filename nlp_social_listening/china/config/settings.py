"""
Global settings & paths for nlp_social_china.
KSF Global Innovation Competition 2026 — Chinese multi-platform intelligence pipeline.

Mirrors `nlp social listening/config/settings.py` so that the China enriched CSV is
mergeable with the Twitter enriched CSV (same clustering params, same thresholds).
"""

from pathlib import Path

# ── Paths ───────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW = DATA_DIR / "raw"
DATA_INTERIM = DATA_DIR / "interim"          # raw MediaCrawler/Apify dumps pre-normalize
DATA_PROCESSED = DATA_DIR / "processed"
DATA_RESULTS = DATA_DIR / "results"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
LOG_PATH = OUTPUTS_DIR / "scraping_log.txt"

# Parent English/Twitter project (this China module lives at nlp_social_listening/china;
# its parent IS the English pipeline, whose analysis/ + visualization/ packages are reused).
SIBLING_PROJECT = PROJECT_ROOT.parent
TWITTER_ENRICHED_CSV = SIBLING_PROJECT / "data" / "processed" / "twitter_enriched.csv"

# MediaCrawler (self-hosted, runs in its own uv env)
MEDIACRAWLER_DIR = PROJECT_ROOT / "third_party" / "MediaCrawler"

for p in (DATA_RAW, DATA_INTERIM, DATA_PROCESSED, DATA_RESULTS, FIGURES_DIR):
    p.mkdir(parents=True, exist_ok=True)

# ── Scraper limits / engagement floors (brief §5) ───────────────────
# Per-keyword caps keep volume modest (MediaCrawler license = research, non-bulk).
XHS_MAX_PER_KEYWORD = 150
WEIBO_MAX_PER_KEYWORD = 150
DOUYIN_MAX_PER_KEYWORD = 100
BILI_MAX_PER_KEYWORD = 100
ZHIHU_MAX_PER_KEYWORD = 100

XHS_MIN_LIKES = 20                # OR comments >= 5
XHS_MIN_COMMENTS = 5
WEIBO_MIN_LIKES = 10              # OR reposts >= 3
WEIBO_MIN_REPOSTS = 3

SCRAPE_DELAY_MIN = 2.0
SCRAPE_DELAY_MAX = 5.0

# ── Cleaning / filtering thresholds ─────────────────────────────────
MIN_TEXT_LENGTH = 10                    # chars in cleaned text (Chinese is denser)
NEAR_DUP_THRESHOLD = 0.90               # cosine similarity for near-dup

# Languages we keep (multi-language corpus; we do NOT drop, we route).
KEEP_LANGUAGES = {"zh-cn", "zh-tw", "zh", "en", "id"}

# ── Sentiment ───────────────────────────────────────────────────────
# Same thresholds as sibling project so the 3-class label is comparable.
SENTIMENT_POS_THRESHOLD = 0.05
SENTIMENT_NEG_THRESHOLD = -0.05

# Primary Chinese sentiment model (brief §6 step 2). Binary (positive/negative);
# neutral is recovered via the consensus threshold above.
CN_SENTIMENT_MODEL = "uer/roberta-base-finetuned-jd-binary-chinese"
CN_SENTIMENT_BATCH_SIZE = 32
CN_SENTIMENT_MAX_LEN = 512

# ── Clustering (IDENTICAL to sibling project for comparability) ─────
TFIDF_MAX_FEATURES = 500
TFIDF_MIN_DF = 3
TFIDF_NGRAM_RANGE = (1, 2)
KMEANS_K_RANGE = (2, 7)
KMEANS_RANDOM_STATE = 42
KMEANS_N_INIT = 10

# ── Visualization ───────────────────────────────────────────────────
FIG_DPI = 300
FIG_FORMAT = "png"

# ── Apify actor slugs (verified live on Apify store) ────────────────
APIFY_XHS_SEARCH_ACTOR = "easyapi/rednote-xiaohongshu-search-scraper"
APIFY_XHS_COMMENTS_ACTOR = "easyapi/rednote-xiaohongshu-comments-scraper"
APIFY_XHS_SEARCH_ACTOR_FALLBACK = "zen-studio/rednote-search-scraper"
# Weibo: piotrv1001 is deprecated and has no keyword search. sian.agency supports
# the `searchWeibo` keyword mode with no login cookie (~$18.75/1k results).
APIFY_WEIBO_ACTOR = "sian.agency/weibo-scraper"
APIFY_WEIBO_ACTOR_FALLBACK = "zhorex/weibo-scraper"   # mode=search, ~$20/1k
APIFY_DOUYIN_ACTOR = "zen-studio/douyin-search-scraper"   # ~$4.99/1k results

# ── Apify free-credit budget caps (Weibo + Douyin) ──────────────────
# Douyin is the primary, cheap, high-relevance pain-point signal (~$4.99/1k). Cap 75 ×
# 13 keywords ≈ 975 results ≈ ~$4.9 → fits ONE free $5 account.
DOUYIN_MAX_PER_QUERY = 75
# Weibo is the costlier supporting/credibility platform (~$18.75/1k, ~10 posts/page).
# Each free account ≈ $5 ≈ ~266 Weibo rows. maxPages=4 spreads each account's budget
# across MORE keywords (breadth for clustering) instead of deep-paging a few. Cycle 3-4
# free accounts to finish the keyword set; the 01b skip-done guard resumes after each swap.
WEIBO_MAX_PAGES = 4
