"""
Global settings for NLP Social Listening pipeline.
All scraping is free & unofficial — no paid APIs.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

# ============================================================
# PATHS
# ============================================================
BASE_DIR = Path(__file__).parent.parent
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"
DATA_RESULTS = BASE_DIR / "data" / "results"
OUTPUT_FIGURES = BASE_DIR / "outputs" / "figures"

# Ensure directories exist
for d in [DATA_RAW, DATA_PROCESSED, DATA_RESULTS, OUTPUT_FIGURES]:
    d.mkdir(parents=True, exist_ok=True)

# ============================================================
# TWITTER/X CREDENTIALS (via .env)
# ============================================================
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME", "")
TWITTER_EMAIL = os.getenv("TWITTER_EMAIL", "")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD", "")
TWITTER_COOKIES_PATH = BASE_DIR / "cookies.json"

# ============================================================
# SCRAPING PARAMETERS
# ============================================================
# Rate limiting (seconds between requests)
TWITTER_DELAY_MIN = 2.0
TWITTER_DELAY_MAX = 5.0
ECOMMERCE_DELAY_MIN = 2.0
ECOMMERCE_DELAY_MAX = 5.0

# Maximum items per scraping session
TWITTER_MAX_TWEETS = 5000
TOKOPEDIA_MAX_REVIEWS_PER_PRODUCT = 500
SHOPEE_MAX_REVIEWS_PER_PRODUCT = 500

# ============================================================
# KEYWORD QUERIES
# ============================================================

# Tier A: Product + Pain Point (Priority)
TIER_A_QUERIES = [
    # Bahasa Indonesia
    'susu protein pahit',
    'susu protein eneg',
    'whey protein rasa aneh',
    'minuman protein enek',
    'whey protein ga enak',
    'minuman protein tekstur',
    'susu protein menggumpal',
    'whey protein susah larut',
    'protein shake bikin mual',
    # English (banyak user fitness ID pakai EN)
    'protein shake chalky',
    'protein shake gritty',
    'protein drink bitter aftertaste',
    'whey protein taste artificial',
    'protein shake too sweet',
    'protein drink texture',
]

# Tier B: Sweetener-Specific
TIER_B_QUERIES = [
    'stevia protein pahit',
    'stevia whey aftertaste',
    'sucralose whey protein rasa',
    'monk fruit protein shake',
    'pemanis buatan protein',
    'stevia protein bitter',
    'sucralose protein taste',
]

# Tier C: Positive Signals
TIER_C_QUERIES = [
    'protein shake enak',
    'whey protein smooth',
    'protein shake recommended',
    'best tasting protein',
    'whey protein favorit',
    'susu protein enak banget',
    'protein shake creamy delicious',
]

# Tier D: Competitor Context
TIER_D_QUERIES = [
    'Evolene rasa review',
    'Musclefirst review rasa',
    'Vectorlabs master whey review',
    'Puro whey protein review',
    'Provus whey review',
    'Optimum Nutrition rasa',
    'Fitlife whey review',
]

ALL_QUERIES = TIER_A_QUERIES + TIER_B_QUERIES + TIER_C_QUERIES + TIER_D_QUERIES

# ============================================================
# NLP SETTINGS
# ============================================================
# Sensory vocabulary — DO NOT remove these from stopwords
SENSORY_PRESERVE = {
    "taste", "flavor", "flavour", "rasa", "sweet", "manis", "bitter", "pahit",
    "sour", "asam", "salty", "asin", "umami", "chalky", "gritty", "berpasir",
    "smooth", "creamy", "thick", "kental", "thin", "encer", "watery",
    "foamy", "frothy", "aftertaste", "metallic", "chemical", "artificial",
    "natural", "bland", "hambar", "rich", "strong", "mild", "refreshing",
    "disgusting", "horrible", "delicious", "enak", "eneg", "enek",
    "mual", "gross", "yucky", "zonk", "mantap", "gurih",
}

# Aspect definitions (bilingual ID/EN)
ASPECTS = {
    "taste": [
        "rasa", "taste", "flavor", "flavour", "enak", "eneg", "enek",
        "pahit", "bitter", "delicious", "yummy", "gross", "hambar", "bland",
    ],
    "texture": [
        "tekstur", "texture", "chalky", "berpasir", "gritty", "smooth",
        "creamy", "thick", "kental", "thin", "encer", "watery", "foamy",
        "menggumpal", "clumpy", "sandy",
    ],
    "sweetness": [
        "manis", "sweet", "sugar", "gula", "stevia", "sucralose",
        "monk fruit", "pemanis", "sweetener", "artificial sweetener",
        "terlalu manis", "kurang manis",
    ],
    "bitterness": [
        "pahit", "bitter", "aftertaste", "metallic", "chemical",
        "rasa obat", "aneh", "getir",
    ],
    "mixability": [
        "larut", "mix", "blend", "menggumpal", "clump", "dissolve",
        "lumpy", "shaker", "aduk", "susah larut", "cepat larut",
    ],
    "protein_content": [
        "protein", "whey", "casein", "isolate", "kandungan",
        "kadar protein", "plant-based", "pea protein", "soy",
    ],
    "value": [
        "harga", "price", "mahal", "murah", "worth", "value",
        "cost", "terjangkau", "ekonomis", "kemahalan",
    ],
    "health": [
        "sehat", "healthy", "organic", "natural", "BPOM", "halal",
        "clean label", "aman", "sustainable", "alami",
    ],
}

# ============================================================
# VISUALIZATION
# ============================================================
FIGURE_DPI = 300
FIGURE_FORMAT = "png"
COLOR_PALETTE = {
    "positive": "#2ecc71",
    "neutral": "#95a5a6",
    "negative": "#e74c3c",
    "primary": "#3498db",
    "secondary": "#9b59b6",
    "background": "#1a1a2e",
    "text": "#e0e0e0",
}
