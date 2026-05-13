"""
Competitor product database for Indonesian protein market.
Used for targeted scraping on Tokopedia, Shopee, and Twitter.
"""

# ============================================================
# PRODUK KOMPETITOR INDONESIA
# ============================================================

COMPETITORS = {
    # --- Merek Lokal ---
    "evolene": {
        "name": "Evolene Whey Protein",
        "brand": "Evolene",
        "origin": "lokal",
        "tokopedia_slug": "evolene-whey-protein",
        "shopee_keywords": "Evolene Whey Protein",
        "twitter_keywords": ["evolene", "evolene whey"],
        "notes": "Merek lokal populer, sering diuji lab independen",
    },
    "musclefirst": {
        "name": "Musclefirst Pro Whey",
        "brand": "Musclefirst",
        "origin": "lokal",
        "tokopedia_slug": "musclefirst-pro-whey-protein",
        "shopee_keywords": "Musclefirst Pro Whey",
        "twitter_keywords": ["musclefirst", "muscle first whey"],
        "notes": "Protein lokal dengan varian rasa Indonesia",
    },
    "puro": {
        "name": "Puro Whey Protein",
        "brand": "Puro",
        "origin": "lokal",
        "tokopedia_slug": "puro-whey-protein",
        "shopee_keywords": "Puro Whey Protein",
        "twitter_keywords": ["puro whey", "puro protein"],
        "notes": "Brand lokal, fokus clean label",
    },
    "provus": {
        "name": "Provus Whey Protein",
        "brand": "Provus",
        "origin": "lokal",
        "tokopedia_slug": "provus-whey-protein",
        "shopee_keywords": "Provus Whey Protein",
        "twitter_keywords": ["provus", "provus whey"],
        "notes": "Populer di komunitas gym Indonesia",
    },
    "vectorlabs": {
        "name": "Vectorlabs Master Whey",
        "brand": "Vectorlabs",
        "origin": "lokal",
        "tokopedia_slug": "vectorlabs-master-whey",
        "shopee_keywords": "Vectorlabs Master Whey",
        "twitter_keywords": ["vectorlabs", "master whey"],
        "notes": "Harga ekonomis, rasa dianggap enak oleh banyak user",
    },
    "fitlife": {
        "name": "Fitlife Whey Protein",
        "brand": "Fitlife",
        "origin": "lokal",
        "tokopedia_slug": "fitlife-whey-protein",
        "shopee_keywords": "Fitlife Whey Protein",
        "twitter_keywords": ["fitlife whey", "fitlife protein"],
        "notes": "Brand lokal mid-range",
    },
    # --- Merek Impor (populer di Indonesia) ---
    "on_gold": {
        "name": "Optimum Nutrition Gold Standard Whey",
        "brand": "Optimum Nutrition",
        "origin": "impor",
        "tokopedia_slug": "optimum-nutrition-gold-standard-whey",
        "shopee_keywords": "Optimum Nutrition Gold Standard Whey",
        "twitter_keywords": ["optimum nutrition", "ON gold standard", "ON whey"],
        "notes": "Standard emas global, benchmark rasa & kualitas",
    },
    "muscletech": {
        "name": "MuscleTech NitroTech",
        "brand": "MuscleTech",
        "origin": "impor",
        "tokopedia_slug": "muscletech-nitrotech-whey-protein",
        "shopee_keywords": "MuscleTech NitroTech",
        "twitter_keywords": ["muscletech", "nitrotech"],
        "notes": "Populer di gym-goers Indonesia",
    },
    "dymatize": {
        "name": "Dymatize ISO 100",
        "brand": "Dymatize",
        "origin": "impor",
        "tokopedia_slug": "dymatize-iso-100",
        "shopee_keywords": "Dymatize ISO 100",
        "twitter_keywords": ["dymatize", "iso 100"],
        "notes": "Hydrolyzed whey, premium segment",
    },
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_all_twitter_keywords() -> list[str]:
    """Get flat list of all Twitter keywords for competitor scraping."""
    keywords = []
    for product in COMPETITORS.values():
        keywords.extend(product["twitter_keywords"])
    return keywords


def get_all_tokopedia_slugs() -> dict[str, str]:
    """Get mapping of competitor_id -> tokopedia_slug."""
    return {k: v["tokopedia_slug"] for k, v in COMPETITORS.items()}


def get_all_shopee_keywords() -> dict[str, str]:
    """Get mapping of competitor_id -> shopee search keywords."""
    return {k: v["shopee_keywords"] for k, v in COMPETITORS.items()}


def get_local_brands() -> dict:
    """Get only local Indonesian brands."""
    return {k: v for k, v in COMPETITORS.items() if v["origin"] == "lokal"}


def get_import_brands() -> dict:
    """Get only imported brands."""
    return {k: v for k, v in COMPETITORS.items() if v["origin"] == "impor"}
