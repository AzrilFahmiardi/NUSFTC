# NLP Social Listening — Protein Beverage Consumer Intelligence

Pipeline NLP untuk mengekstrak insight konsumen dari data social media & e-commerce Indonesia.

## Pilar 3: AI Framework untuk NUS Food Technology Challenge (KSF Master Kong)

### Sumber Data (Gratis, Unofficial)
- **Twitter/X** — via `twikit` (cookies-based, no API key)
- **Tokopedia** — via `Playwright` headless browser
- **Shopee** — via `Playwright` headless browser

### Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers
playwright install chromium

# 3. Download spaCy model
python -m spacy download en_core_web_sm

# 4. Setup credentials
cp .env.example .env
# Edit .env with your Twitter/X burner account credentials
```

### Menjalankan Pipeline

```bash
# Scraping Twitter
python -m scrapers.twitter_scraper

# Scraping Tokopedia
python -m scrapers.tokopedia_scraper

# Scraping Shopee
python -m scrapers.shopee_scraper
```

### Struktur Output
```
data/raw/         → Raw scraped data (CSV)
data/processed/   → Cleaned & annotated data
data/results/     → Analysis outputs
outputs/figures/  → Charts & word clouds (300 DPI)
```

### Modul
| Modul | Deskripsi |
|-------|-----------|
| `config/` | Settings, keyword tiers, competitor database |
| `scrapers/` | Twitter, Tokopedia, Shopee scrapers |
| `preprocessing/` | Bilingual text cleaning (ID/EN) |
| `analysis/` | Sentiment, keyword, ABSA, topic modeling |
| `visualization/` | Word clouds, charts, composite dashboard |
