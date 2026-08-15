# ADR-0004: Disposability of Derived Indices and Vector Stores

## Status
Accepted

## Date
2026-08-16

## Context
AI architectures often store canonical state inside vector databases (e.g., Chroma, Qdrant, Faiss) or graph caches. This makes system state opaque, non-deterministic, hard to inspect with Git, and susceptible to database corruption or embedding drift.

## Decision
All vector embeddings, BM25 indices, similarity graph caches, and runtime caches are declared strictly **non-canonical derived artifacts**:
1. The sole source of truth is the canonical SQLite database and immutable file tree.
2. The entire `runtime/indexes` and `runtime/cache` directories can be deleted at any time without data loss.
3. A deterministic rebuild script (`scripts/clean_derived_indexes.py` / `build_indexes.py`) regenerates all derived indices on demand.

## Consequences
### Positive
- Robust reproducibility and easy disaster recovery.
- Clean Git repository without binary embedding bloat.
### Negative / Tradeoffs
- Index rebuild incurs computation time upon index invalidation.
