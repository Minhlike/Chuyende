# ADR-0008: Long-Term Research Memory, Hybrid Retrieval & Knowledge Consolidation

## Status
**ACCEPTED**

## Date
2026-08-16

## Context
A long-running scientific research agent across multi-day or multi-month sessions faces severe failure modes if relying solely on ephemeral context windows or opaque vector databases:
1. **Amnesia:** Prior architectural decisions, negative results, and falsifications disappear upon session termination.
2. **Self-Reinforcing Hallucination Loops:** The agent recalls its own speculative past generation as grounded external facts, causing progressive distortion.
3. **Loss of Contradictions:** Naive vector search collapses nuanced contradictions, returning only the nearest average vector.
4. **Vector Database Lock-in:** Vector embeddings can become corrupt, misaligned, or unavailable without external cloud APIs.

## Decision
1. **6-Tier Canonical Memory Model (M0..M5):**
   - Explicitly separate Working (`M0`), Source (`M1`), Semantic (`M2`), Episodic (`M3`), Argument (`M4`), and Procedural (`M5`) memories.
2. **Hard Rule: Memory Record $\neq$ Truth:**
   - Canonical truth resides strictly in ACID SQLite relational tables (`sources`, `evidences`, `claims`, `decision_records`, `episodes`).
   - Vector indexes are strictly disposable derived caches.
3. **Anti-Hallucination Invariants (MR-01..MR-06):**
   - Enforce provenance verification at consolidation time. Unverified LLM outputs cannot be promoted to `SOURCE` or `SOURCE_FACT`.
4. **Multi-Signal Hybrid Retrieval:**
   - Exact Stable ID > Structured metadata filter > Lexical FTS5 > Cosine Vector similarity > Graph Traversal with active contradiction preservation.
5. **Deterministic Zero-External-Dependency Local Embeddings:**
   - Implement `LocalBM25TFIDFEmbeddingProvider` producing deterministic 128d dense vectors locally without external network calls.
6. **Session Handoff & Journal Generation:**
   - Persist Markdown session journals in `memory/sessions/` and point-in-time JSON snapshots in `memory/snapshots/`.

## Consequences
### Positive
- Research state is 100% recoverable across complete system restarts.
- Negative results, failures, and superseded decisions are preserved permanently.
- Contradictory evidence is retrieved alongside supporting evidence.
- Zero external dependency on third-party embedding APIs.

### Negative / Trade-offs
- Memory writes require explicit classification and validation through repository APIs.
- Derived vector index must be rebuilt if schema changes significantly (supported via `research-agent memory rebuild-index`).

## Compliance Verification
- Verified by automated tests `TEST-MEM-01` through `TEST-MEM-20` and realistic session restart continuity simulations in `tests/test_memory.py`.
- Benchmark validated in `tests/test_retrieval_benchmark.py`.
