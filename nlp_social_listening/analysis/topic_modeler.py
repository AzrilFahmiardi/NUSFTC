"""
Topic Modeler — LDA (primary) + BERTopic (optional)

Discovers latent complaint themes beyond predefined aspects.

Usage:
    from analysis.topic_modeler import TopicModeler
    modeler = TopicModeler()
    topics_df = modeler.fit_lda(texts, n_topics=10)
"""

import logging
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

logger = logging.getLogger(__name__)


class TopicModeler:
    """Topic modeling for discovering latent complaint themes."""

    def __init__(self):
        self.lda_model = None
        self.vectorizer = None
        self.feature_names = None

    def fit_lda(
        self,
        texts: pd.Series,
        n_topics: int = 10,
        max_features: int = 3000,
        top_words: int = 10,
    ) -> pd.DataFrame:
        """
        Fit LDA topic model and return topic descriptions.

        Returns DataFrame: topic_id, top_words, coherence_hint
        """
        texts = texts.dropna().astype(str)
        texts = texts[texts.str.len() > 10]

        self.vectorizer = CountVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),
            min_df=3,
            max_df=0.9,
        )
        doc_term = self.vectorizer.fit_transform(texts)
        self.feature_names = self.vectorizer.get_feature_names_out()

        self.lda_model = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=20,
            learning_method="online",
        )
        self.lda_model.fit(doc_term)

        topics = []
        for idx, topic in enumerate(self.lda_model.components_):
            top_idx = topic.argsort()[-top_words:][::-1]
            words = [self.feature_names[i] for i in top_idx]
            topics.append({
                "topic_id": idx,
                "top_words": ", ".join(words),
                "weight_sum": round(topic[top_idx].sum(), 2),
                })

        logger.info("Fitted LDA with %d topics", n_topics)
        return pd.DataFrame(topics)

    def get_document_topics(self, texts: pd.Series) -> pd.DataFrame:
        """Get dominant topic for each document."""
        if self.lda_model is None:
            raise ValueError("Run fit_lda first")

        doc_term = self.vectorizer.transform(texts.fillna("").astype(str))
        topic_dist = self.lda_model.transform(doc_term)

        return pd.DataFrame({
            "dominant_topic": topic_dist.argmax(axis=1),
            "topic_confidence": topic_dist.max(axis=1),
        })

    def fit_bertopic(self, texts: pd.Series, n_topics: int = 10) -> pd.DataFrame:
        """
        Fit BERTopic (requires bertopic + torch installed).
        Falls back to LDA if unavailable.
        """
        try:
            from bertopic import BERTopic
            model = BERTopic(
                language="multilingual",
                nr_topics=n_topics,
                verbose=True,
            )
            docs = texts.dropna().astype(str).tolist()
            topics, probs = model.fit_transform(docs)
            topic_info = model.get_topic_info()
            logger.info("BERTopic fitted: %d topics", len(topic_info))
            return topic_info

        except ImportError:
            logger.warning("BERTopic not installed. Falling back to LDA.")
            return self.fit_lda(texts, n_topics=n_topics)
