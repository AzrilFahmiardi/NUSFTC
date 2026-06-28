# %% [markdown]
# # 00 · Import teammate's XHS scraped data
# Converts the friend's custom insight CSV schema → our canonical RAW schema
# and saves to data/raw/xiaohongshu_raw.csv so pipeline step 02 can pick it up.
#
# Source: https://github.com/Narscode/mobai-flavorgraph/blob/main/mediacrawler/insight/xhs_mobai_insights.csv
#
# Run: `conda activate ml && python notebooks/00_import_xhs_friend.py`

# %%
import hashlib
import io
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import DATA_RAW

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# %%
RAW_URL = (
    "https://raw.githubusercontent.com/Narscode/mobai-flavorgraph/main"
    "/mediacrawler/insight/xhs_mobai_insights.csv"
)
SCRAPED_DATE = "2026-06-24"  # from JSON metadata generation_time


# %%
def parse_likes(val) -> int:
    """Parse XHS like counts: handles raw ints, '1.6万', '10万+', etc."""
    s = str(val).strip().replace(",", "").replace("+", "").replace(" ", "")
    if not s or s in ("nan", "None", ""):
        return 0
    if "万" in s:
        try:
            return int(float(s.replace("万", "")) * 10_000)
        except ValueError:
            return 0
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return 0


def md5_hash(val) -> str:
    if not val or str(val).strip() in ("", "nan", "None"):
        return ""
    return hashlib.md5(str(val).strip().encode("utf-8")).hexdigest()


# %%
log.info("Downloading CSV from GitHub...")
resp = requests.get(RAW_URL, timeout=60)
resp.raise_for_status()
raw = pd.read_csv(io.StringIO(resp.text))
log.info("Downloaded: %d rows × %d cols", len(raw), len(raw.columns))
log.info("Columns: %s", raw.columns.tolist())

# %%
# Validate expected columns exist
EXPECTED = {"Type", "ID", "Title/Content", "Nickname", "Likes",
            "Sub-comments/Comments Count", "Source Keyword", "Group"}
missing = EXPECTED - set(raw.columns)
if missing:
    raise ValueError(f"Unexpected schema — missing columns: {missing}")

scraped_at = datetime.now(timezone.utc).isoformat()

rows = []
for _, r in raw.iterrows():
    row_type = str(r.get("Type", "Post")).strip()
    row_id = str(r.get("ID", "")).strip()

    if row_type.lower() == "comment":
        tweet_id = f"xhs_cmt_{row_id}"
    else:
        tweet_id = f"xhs_{row_id}"

    rows.append({
        "tweet_id":          tweet_id,
        "text":              str(r.get("Title/Content", "") or "").strip(),
        "created_at":        SCRAPED_DATE,
        "user_name":         "",
        "user_screen_name":  md5_hash(r.get("Nickname")),
        "user_followers":    None,
        "favorite_count":    parse_likes(r.get("Likes", 0)),
        "retweet_count":     0,
        "reply_count":       parse_likes(r.get("Sub-comments/Comments Count", 0)),
        "language":          "zh",
        "query":             str(r.get("Source Keyword", "") or "").strip(),
        "query_group":       str(r.get("Group", "flavor") or "flavor").strip(),
        "scraped_at":        scraped_at,
        "platform":          "xiaohongshu",
        "url":               "",
    })

df = pd.DataFrame(rows)

# Drop rows with empty text
before = len(df)
df = df[df["text"].str.len() > 0].reset_index(drop=True)
log.info("Dropped %d empty-text rows", before - len(df))

# %%
out_path = DATA_RAW / "xiaohongshu_raw.csv"
df.to_csv(out_path, index=False, encoding="utf-8-sig")
log.info("Saved %d rows → %s", len(df), out_path)

# Also save as china_all_raw.csv (expected by 02_preprocess_and_enrich.py)
all_path = DATA_RAW / "china_all_raw.csv"
df.to_csv(all_path, index=False, encoding="utf-8-sig")
log.info("Saved merged → %s", all_path)

# %%
print(f"\n{'='*60}")
print(f"Rows:    {len(df):,}")
print(f"Columns: {df.columns.tolist()}")
print(f"\nquery_group distribution:")
print(df["query_group"].value_counts().to_string())
print(f"\nType prefix distribution:")
print(df["tweet_id"].str[:7].value_counts().to_string())
print(f"\nSample rows:")
print(df[["tweet_id", "text", "query_group", "favorite_count"]].head(5).to_string())
print(f"{'='*60}")
print(f"\nDone. Proceed with: python notebooks/02_preprocess_and_enrich.py")
