"""
CJK-safe text cleaner + jieba tokenizer for Chinese social media text.

Why a separate cleaner: the sibling project's `text_cleaner.py` uses
SPECIAL_RE = [^a-zA-Z0-9\\s.,!?'-] which DELETES every CJK character. This module
keeps CJK + ASCII letters/digits, strips noise, and tokenizes Chinese with jieba.

Produces the SAME three columns as the sibling cleaner so downstream code matches:
    clean_text          — noise-stripped, original language preserved (fed to sentiment)
    clean_text_no_stop  — jieba-tokenized (zh) / word-split (en), stopwords removed
    word_count          — token count
"""

import re
import logging
from pathlib import Path

import pandas as pd
import jieba

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import MIN_TEXT_LENGTH
from config.stopwords_cn import CN_STOPWORDS, CN_SENSORY_PRESERVE
from config.dictionaries_cn import JIEBA_USERWORDS

logger = logging.getLogger(__name__)

# Inject brand/flavor neologisms so jieba keeps them as single tokens.
for _w in JIEBA_USERWORDS:
    jieba.add_word(_w)

URL_RE = re.compile(r"https?://\S+|www\.\S+")
HTML_RE = re.compile(r"<[^>]+>")
MENTION_RE = re.compile(r"@[\w一-鿿]+")        # @user (latin or CJK handle)
HASHTAG_RE = re.compile(r"#([\w一-鿿]+)#?")     # #topic# (Weibo) or #tag
# Emoji ranges — carefully chosen to EXCLUDE the CJK block (U+3000–U+9FFF).
# (The sibling English cleaner's catch-all U+24C2–U+1F251 would delete all Chinese.)
EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"   # symbols, pictographs, emoticons, transport, supplemental
    "\U0001F1E0-\U0001F1FF"   # regional indicators (flags)
    "\U00002600-\U000027BF"   # misc symbols + dingbats
    "\U00002B00-\U00002BFF"   # misc symbols & arrows
    "\U0000FE00-\U0000FE0F"   # variation selectors
    "\U00002190-\U000021FF"   # arrows
    "\U00002300-\U000023FF"   # misc technical (⌚ ⏰ etc.)
    "]+",
    flags=re.UNICODE,
)
# Keep: CJK, ASCII letters/digits, whitespace, basic punctuation (both scripts).
KEEP_RE = re.compile(r"[^一-鿿　-〿a-zA-Z0-9\s.,!?！？。，、'-]")
WS_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Strip social noise; preserve CJK + ASCII content. NOT lowercased for CJK,
    but ASCII is lowercased to match the English extractor's substring matching."""
    if not isinstance(text, str) or not text.strip():
        return ""
    t = URL_RE.sub("", text)
    t = HTML_RE.sub("", t)
    t = MENTION_RE.sub("", t)
    t = HASHTAG_RE.sub(r"\1", t)      # keep the topic word, drop the # markers
    t = EMOJI_RE.sub("", t)
    t = KEEP_RE.sub("", t)
    t = WS_RE.sub(" ", t).strip()
    # Lowercase only ASCII letters; CJK is unaffected by .lower().
    return t.lower()


def _keep_token(w: str) -> bool:
    if w in CN_SENSORY_PRESERVE:
        return True
    if w in CN_STOPWORDS:
        return False
    return len(w) > 1            # drop single stray chars / punctuation


def tokenize(text: str, lang: str = "zh") -> str:
    """Return space-joined tokens with stopwords removed, sensory vocab preserved."""
    if not text:
        return ""
    if lang.startswith("zh"):
        tokens = [tok.strip() for tok in jieba.cut(text) if tok.strip()]
    else:
        tokens = text.split()
    return " ".join(w for w in tokens if _keep_token(w))


def process_dataframe(
    df: pd.DataFrame, text_col: str = "text", lang_col: str = "detected_lang"
) -> pd.DataFrame:
    """Add clean_text, clean_text_no_stop, word_count; drop too-short rows.

    Requires `detected_lang` (run language_router first). Falls back to 'zh'
    tokenization when the language column is absent.
    """
    df = df.copy()
    df["clean_text"] = df[text_col].fillna("").apply(clean_text)

    langs = df[lang_col] if lang_col in df.columns else pd.Series(["zh"] * len(df))
    df["clean_text_no_stop"] = [
        tokenize(t, l if isinstance(l, str) else "zh")
        for t, l in zip(df["clean_text"], langs)
    ]
    df["word_count"] = df["clean_text_no_stop"].str.split().str.len().fillna(0).astype(int)

    before = len(df)
    df = df[df["clean_text"].str.len() >= MIN_TEXT_LENGTH].reset_index(drop=True)
    logger.info("Cleaned (CJK-safe): %d -> %d rows kept (min %d chars)", before, len(df), MIN_TEXT_LENGTH)
    return df
