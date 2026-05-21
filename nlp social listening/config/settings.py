"""
Global settings & paths for nlp social listening 2.
KSF Global Innovation Competition 2026 — Twitter-only intelligence pipeline.
"""

from pathlib import Path

# ── Paths ───────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW = DATA_DIR / "raw"
DATA_PROCESSED = DATA_DIR / "processed"
DATA_RESULTS = DATA_DIR / "results"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
LOG_PATH = OUTPUTS_DIR / "scraping_log.txt"

TWITTER_COOKIES_PATH = PROJECT_ROOT / "cookies.json"

for p in (DATA_RAW, DATA_PROCESSED, DATA_RESULTS, FIGURES_DIR):
    p.mkdir(parents=True, exist_ok=True)

# ── Scraper rate limits ─────────────────────────────────────────────
TWITTER_DELAY_MIN = 2.0
TWITTER_DELAY_MAX = 5.0
TWITTER_MAX_TWEETS = 8000               # global cap per session
TWITTER_MAX_PER_QUERY = 200             # per-query cap
TWITTER_TIME_RANGE_DAYS = 180           # Nov 2025 – May 2026

# ── Cleaning / filtering thresholds ────────────────────────────────
MIN_TEXT_LENGTH = 15                    # chars in cleaned text
MIN_ENGAGEMENT_FAVORITES = 0            # no engagement floor by default
NEAR_DUP_THRESHOLD = 0.90               # cosine similarity for near-dup
TARGET_LANGUAGE = "en"

# ── Sentiment thresholds ────────────────────────────────────────────
SENTIMENT_POS_THRESHOLD = 0.05
SENTIMENT_NEG_THRESHOLD = -0.05

# ── Clustering ─────────────────────────────────────────────────────
TFIDF_MAX_FEATURES = 500
TFIDF_MIN_DF = 3
TFIDF_NGRAM_RANGE = (1, 2)
KMEANS_K_RANGE = (2, 7)
KMEANS_RANDOM_STATE = 42
KMEANS_N_INIT = 10

# ── Visualization ──────────────────────────────────────────────────
FIG_DPI = 300
FIG_FORMAT = "png"

# ── Sensory vocabulary preserved through stopword removal ─────────
SENSORY_PRESERVE = {
    "sweet", "bitter", "sour", "salty", "umami",
    "chalky", "creamy", "smooth", "thick", "thin",
    "gritty", "grainy", "watery", "frothy", "foamy",
    "flavor", "taste", "aftertaste", "texture", "mouthfeel",
    "artificial", "natural", "fresh", "stale", "off",
    "fruity", "tropical", "earthy", "nutty", "floral",
    "rich", "light", "heavy", "refreshing", "satisfying",
    "matcha", "coconut", "mango", "strawberry", "lychee",
    "peach", "taro", "chocolate", "vanilla", "coffee",
    "yogurt", "shake", "powder", "rtd", "drinkable",
    "morning", "breakfast", "workout", "commute", "snack",
    "protein", "whey", "casein", "plant",
}
