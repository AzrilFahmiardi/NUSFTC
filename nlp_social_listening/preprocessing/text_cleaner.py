"""
Text cleaner — English-only, social media noise removal.
Preserves sensory vocabulary needed for entity extraction.
"""

import re
import logging
from pathlib import Path

import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import SENSORY_PRESERVE, MIN_TEXT_LENGTH

logger = logging.getLogger(__name__)

EN_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "i", "me", "my", "you",
    "your", "yours", "he", "she", "it", "we", "they", "them", "their",
    "this", "that", "these", "those", "of", "in", "to", "for", "with",
    "on", "at", "by", "from", "as", "but", "or", "not", "so", "if",
    "then", "than", "very", "just", "really", "also", "and", "out",
    "about", "into", "over", "under", "again", "more", "most", "some",
    "any", "all", "no", "yes", "what", "when", "where", "who", "how",
    "rt", "im", "ive", "dont", "doesnt", "didnt", "cant", "wont", "us",
}

URL_RE = re.compile(r"https?://\S+|www\.\S+")
HTML_RE = re.compile(r"<[^>]+>")
MENTION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#(\w+)")
EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE,
)
SPECIAL_RE = re.compile(r"[^a-zA-Z0-9\s.,!?'-]")
WS_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""
    t = URL_RE.sub("", text)
    t = HTML_RE.sub("", t)
    t = MENTION_RE.sub("", t)
    t = HASHTAG_RE.sub(r"\1", t)
    t = EMOJI_RE.sub("", t)
    t = SPECIAL_RE.sub("", t)
    t = WS_RE.sub(" ", t).strip().lower()
    return t


def remove_stopwords(text: str) -> str:
    """Strip English stopwords but preserve sensory vocabulary."""
    words = text.split()
    return " ".join(
        w for w in words if w in SENSORY_PRESERVE or w not in EN_STOPWORDS
    )


def process_dataframe(df: pd.DataFrame, text_col: str = "text") -> pd.DataFrame:
    """Add clean_text, clean_text_no_stop, word_count columns; drop empties."""
    df = df.copy()
    df["clean_text"] = df[text_col].fillna("").apply(clean_text)
    df["clean_text_no_stop"] = df["clean_text"].apply(remove_stopwords)
    df["word_count"] = df["clean_text"].str.split().str.len().fillna(0).astype(int)
    df = df[df["clean_text"].str.len() >= MIN_TEXT_LENGTH].reset_index(drop=True)
    logger.info("Cleaned: %d rows kept (min %d chars)", len(df), MIN_TEXT_LENGTH)
    return df
