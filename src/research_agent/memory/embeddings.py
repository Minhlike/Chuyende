"""
Embedding Provider Abstraction and Lightweight Local Vectorizer (Prompt 4, Section 23, Section 46, ADR-0008)
"""

import re
import math
import hashlib
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class EmbeddingVector(BaseModel):
    """Derived dense vector embedding with provenance metadata."""
    entity_id: str
    entity_type: str
    model_id: str
    model_version: str
    dimensions: int
    vector: List[float]
    normalized: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EmbeddingProvider(ABC):
    """Abstract interface for local or remote embedding backends (Section 46)."""

    @property
    @abstractmethod
    def model_id(self) -> str:
        pass

    @property
    @abstractmethod
    def model_version(self) -> str:
        pass

    @property
    @abstractmethod
    def dimensions(self) -> int:
        pass

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string into a normalized dense vector."""
        pass

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of text strings."""
        return [self.embed_text(t) for t in texts]


class LocalBM25TFIDFEmbeddingProvider(EmbeddingProvider):
    """
    Deterministic, high-performance, local feature-hash vectorizer.
    Produces L2-normalized 128-dimensional dense vectors from text tokens.
    Guarantees reproducible similarity ranking without external network or heavy dependencies.
    """

    def __init__(self, dim: int = 128, model_version: str = "1.0.0"):
        self._dim = dim
        self._version = model_version
        self._model_id = f"local-tfidf-hash-{dim}"

    @property
    def model_id(self) -> str:
        return self._model_id

    @property
    def model_version(self) -> str:
        return self._version

    @property
    def dimensions(self) -> int:
        return self._dim

    def _tokenize(self, text: str) -> List[str]:
        cleaned = text.lower()
        # Keep alphanumeric, hyphens, and dots for identifiers (e.g., CLM-001, 1.3.3)
        tokens = re.findall(r'[a-z0-9_\-\.]+', cleaned)
        return tokens

    def embed_text(self, text: str) -> List[float]:
        tokens = self._tokenize(text)
        if not tokens:
            return [0.0] * self._dim

        vec = [0.0] * self._dim
        tf_dict: Dict[str, int] = {}
        for token in tokens:
            tf_dict[token] = tf_dict.get(token, 0) + 1

        for token, count in tf_dict.items():
            # Sublinear term frequency: 1 + ln(count)
            weight = 1.0 + math.log(count)
            # Hash to index and sign for feature hashing
            h_val = int(hashlib.md5(token.encode('utf-8')).hexdigest(), 16)
            idx = h_val % self._dim
            sign = 1.0 if ((h_val >> 8) & 1) == 0 else -1.0
            vec[idx] += sign * weight

        # L2 Normalize
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 1e-9:
            vec = [v / norm for v in vec]
        return vec
