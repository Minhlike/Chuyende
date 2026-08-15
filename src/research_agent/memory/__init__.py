"""
Research Agent Long-Term Memory & Hybrid Retrieval Package
"""

from research_agent.memory.embeddings import (
    EmbeddingProvider,
    EmbeddingVector,
    LocalBM25TFIDFEmbeddingProvider,
)
from research_agent.memory.vector_index import DerivedVectorIndex
from research_agent.memory.retrieval import HybridRetrievalEngine
from research_agent.memory.consolidation import (
    MemoryConsolidationService,
    ConsolidationResult,
)
from research_agent.memory.health import MemoryHealthAuditor
from research_agent.memory.manager import MemoryManager

__all__ = [
    "EmbeddingProvider",
    "EmbeddingVector",
    "LocalBM25TFIDFEmbeddingProvider",
    "DerivedVectorIndex",
    "HybridRetrievalEngine",
    "MemoryConsolidationService",
    "ConsolidationResult",
    "MemoryHealthAuditor",
    "MemoryManager",
]
