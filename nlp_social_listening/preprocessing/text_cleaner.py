"""
Text Cleaning & Normalization Pipeline — Bilingual ID/EN

Handles Indonesian slang, English fitness jargon, and social media noise.
Preserves sensory vocabulary critical for aspect analysis.

Usage:
    from preprocessing.text_cleaner import TextCleaningPipeline
    cleaner = TextCleaningPipeline()
    df["clean_text"] = df["text"].apply(cleaner.clean)
"""

import re
import logging
from pathlib import Path

try:
    import spacy
except ImportError:
    spacy = None

try:
    from langdetect import detect as lang_detect
except ImportError:
    lang_detect = None

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import SENSORY_PRESERVE

logger = logging.getLogger(__name__)

# ============================================================
# Indonesian Slang / Abbreviation Dictionary
# ============================================================
INDO_SLANG = {
    "ga": "tidak", "gak": "tidak", "gk": "tidak", "g": "tidak",
    "ngga": "tidak", "nggak": "tidak", "tdk": "tidak",
    "tp": "tapi", "tpi": "tapi",
    "bgt": "banget", "bngt": "banget",
    "sm": "sama", "sma": "sama",
    "yg": "yang", "yng": "yang",
    "dg": "dengan", "dgn": "dengan",
    "dr": "dari",
    "utk": "untuk", "u/": "untuk",
    "krn": "karena", "krna": "karena",
    "lg": "lagi", "lgi": "lagi",
    "jg": "juga", "jga": "juga",
    "udh": "sudah", "udah": "sudah", "sdh": "sudah",
    "blm": "belum", "blum": "belum",
    "bs": "bisa", "bsa": "bisa",
    "org": "orang", "orng": "orang",
    "bnyk": "banyak", "byk": "banyak",
    "mantap": "mantap", "mantab": "mantap", "mantul": "mantap betul",
    "eneg": "mual", "enek": "mual",
    "zonk": "buruk",
    "kyk": "kayak", "kaya": "kayak",
    "bkn": "bukan",
    "sih": "", "nih": "", "deh": "", "dong": "", "lho": "",
    "wkwk": "", "wkwkwk": "", "haha": "", "hehe": "",
}

# Custom stopwords — common words that add no value but ARE NOT sensory
CUSTOM_STOPWORDS = {
    "yang", "dan", "di", "ini", "itu", "dengan", "untuk", "pada",
    "adalah", "dari", "ke", "dalam", "akan", "ada", "sudah", "juga",
    "saya", "aku", "kamu", "dia", "mereka", "kita", "kami",
    "the", "a", "an", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can",
    "i", "me", "my", "you", "your", "he", "she", "it", "we", "they",
    "this", "that", "these", "those", "of", "in", "to", "for",
    "with", "on", "at", "by", "from", "as", "but", "or", "not",
    "so", "if", "then", "than", "very", "just", "really", "also",
}


class TextCleaningPipeline:
    """
    Multi-step text cleaning pipeline for bilingual ID/EN social media text.
    Preserves sensory vocabulary for NLP analysis.
    """

    def __init__(self, expand_slang: bool = True, detect_language: bool = True):
        self.expand_slang = expand_slang
        self.detect_language = detect_language
        self._nlp = None

    def _get_nlp(self):
        """Lazy-load spaCy model."""
        if self._nlp is None and spacy is not None:
            try:
                self._nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
        return self._nlp

    def remove_urls(self, text: str) -> str:
        return re.sub(r"https?://\S+|www\.\S+", "", text)

    def remove_html(self, text: str) -> str:
        return re.sub(r"<[^>]+>", "", text)

    def remove_mentions_hashtags(self, text: str) -> str:
        text = re.sub(r"@\w+", "", text)
        # Keep hashtag text, remove # symbol
        text = re.sub(r"#(\w+)", r"\1", text)
        return text

    def remove_emojis(self, text: str) -> str:
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE,
        )
        return emoji_pattern.sub("", text)

    def expand_indonesian_slang(self, text: str) -> str:
        """Expand Indonesian abbreviations and slang."""
        words = text.split()
        expanded = []
        for w in words:
            lower = w.lower()
            if lower in INDO_SLANG:
                replacement = INDO_SLANG[lower]
                if replacement:  # skip empty replacements (filler words)
                    expanded.append(replacement)
            else:
                expanded.append(w)
        return " ".join(expanded)

    def normalize_whitespace(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def remove_special_chars(self, text: str) -> str:
        """Keep alphanumeric, spaces, and basic punctuation."""
        return re.sub(r"[^a-zA-Z0-9\s.,!?'-]", "", text)

    def detect_lang(self, text: str) -> str:
        """Detect language of text. Returns 'id', 'en', or 'unknown'."""
        if lang_detect is None:
            return "unknown"
        try:
            lang = lang_detect(text)
            return lang if lang in ("id", "en") else "other"
        except Exception:
            return "unknown"

    def remove_stopwords(self, text: str) -> str:
        """Remove stopwords but PRESERVE sensory vocabulary."""
        words = text.lower().split()
        filtered = [
            w for w in words
            if w in SENSORY_PRESERVE or w not in CUSTOM_STOPWORDS
        ]
        return " ".join(filtered)

    def clean(self, text: str) -> str:
        """
        Full cleaning pipeline. Returns cleaned text.

        Steps:
        1. Remove URLs
        2. Remove HTML tags
        3. Remove @mentions, clean #hashtags
        4. Remove emojis
        5. Expand Indonesian slang (optional)
        6. Remove special characters
        7. Normalize whitespace
        8. Lowercase
        """
        if not isinstance(text, str) or not text.strip():
            return ""

        text = self.remove_urls(text)
        text = self.remove_html(text)
        text = self.remove_mentions_hashtags(text)
        text = self.remove_emojis(text)

        if self.expand_slang:
            text = self.expand_indonesian_slang(text)

        text = self.remove_special_chars(text)
        text = self.normalize_whitespace(text)
        text = text.lower()

        # Skip very short texts
        if len(text.split()) < 3:
            return ""

        return text

    def clean_for_analysis(self, text: str) -> str:
        """Clean + remove stopwords. For TF-IDF/topic modeling."""
        cleaned = self.clean(text)
        if cleaned:
            cleaned = self.remove_stopwords(cleaned)
        return cleaned

    def process_dataframe(self, df, text_col: str = "text") -> "pd.DataFrame":
        """
        Process entire DataFrame: add clean_text, language, word_count columns.

        Args:
            df: DataFrame with text column
            text_col: Name of the text column

        Returns:
            DataFrame with new columns added
        """
        import pandas as pd

        df = df.copy()
        df["clean_text"] = df[text_col].apply(self.clean)
        df["clean_text_no_stop"] = df[text_col].apply(self.clean_for_analysis)
        df["word_count"] = df["clean_text"].apply(lambda x: len(x.split()) if x else 0)

        if self.detect_language:
            df["language"] = df[text_col].apply(self.detect_lang)

        # Remove empty rows
        df = df[df["clean_text"].str.len() > 0].reset_index(drop=True)

        logger.info(
            "Processed %d rows. Languages: %s",
            len(df),
            df["language"].value_counts().to_dict() if "language" in df.columns else "N/A",
        )
        return df
