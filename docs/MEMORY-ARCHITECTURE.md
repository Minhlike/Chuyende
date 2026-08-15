# Research Agent Long-Term Memory Architecture & Hybrid Retrieval

> **Status:** RATIFIED  
> **Date:** 2026-08-16  
> **Constitutional Anchors:** `docs/RESEARCH-CONSTITUTION.md` (RC-01..RC-16), ADR-0008

---

## 1. Executive Summary & Core Paradigm

The **Research Agent Long-Term Memory System** provides durable, multi-session epistemic continuity across days, months, or years without relying on ephemeral LLM context windows or fragile vector-only databases.

### Fundamental Principle: Memory is Not Canonical Truth
```
  [ External Sources / Papers ] ---> [ Source Registry (SRC-...) ]
                                              |
  [ Physical Experiments / Code ] -> [ Evidence Store (EVD-...) ]
                                              |
  [ Formal Axioms & Invariants ] --> [ Canonical Claims (CLM-...) ]
                                              |
                                     (Provenanced Facts)
                                              v
                              +-------------------------------+
                              |    CANONICAL SQLITE DB        |
                              |    (Permanent Truth Store)    |
                              +---------------+---------------+
                                              |
                          +-------------------+-------------------+
                          |                                       |
                          v                                       v
             +------------------------+              +------------------------+
             |    FTS5 LEXICAL        |              |  DERIVED VECTOR INDEX  |
             |   Full-Text Index      |              |  (Disposable Cosine)   |
             +-----------+------------+              +------------+-----------+
                         |                                        |
                         +--------------------+-------------------+
                                              |
                                              v
                              +-------------------------------+
                              |    HYBRID RETRIEVAL ENGINE    |
                              |   Exact ID > FTS5 > Vectors   |
                              +---------------+---------------+
                                              |
                                              v
                                   [ ContextBundle to LLM ]
```

- **Memory Record $\neq$ Truth:** Memory records track *what was known, believed, attempted, decided, or falsified* by the agent at a specific point in time.
- **Canonical Truth:** Grounded exclusively in verified `Source`, `Evidence`, `Claim`, `DecisionRecord`, and reproducible `EpisodeRecord` entries in the ACID SQLite relational database.
- **Disposable Derived Indexes:** The semantic vector index (`runtime/indexes/derived_vectors.json`) and FTS5 table (`memory_fts`) can be purged and rebuilt idempotently from canonical relational rows with zero data loss.

---

## 2. Six-Tier Memory Model (M0..M5)

| Tier | Name | Persistence Scope | Canonical Reference | Epistemic Invariants |
|---|---|---|---|---|
| **M0** | Working Memory | Ephemeral (Session-only) | Runtime process memory | Discarded on session completion unless promoted. |
| **M1** | Source Memory | Permanent | `SRC-xxxxxx`, `EVD-xxxxxx` | External peer-reviewed literature, official benchmarks, verified locators. |
| **M2** | Semantic Memory | Permanent | `CLM-xxxxxx`, `EQN-xxxxxx` | Atomic assertions, contracts, definitions, axioms. Categorized by `Ownership`. |
| **M3** | Episodic Memory | Permanent | `EP-xxxxxx`, `EXP-xxxxxx` | Time-stamped actions, benchmark outcomes, **negative results**, and failure logs. |
| **M4** | Argument Memory | Permanent | `ARE-xxxxxx`, `DEC-xxxxxx`, `CTR-xxxxxx` | Dialectic relations (`SUPPORTS`, `CONTRADICTS`, `QUALIFIES`), ADRs, trade-offs. |
| **M5** | Procedural Memory | Permanent (Versioned) | `SKL-xxxxxx` (`memory/procedural/`) | Reusable protocols, execution checklists, evaluation rubrics, audit workflows. |

---

## 3. Anti-Self-Reinforcing Hallucination Safeguards (MR-01..MR-06)

To prevent LLM feedback loops where generated statements become accepted as facts over time, the consolidation pipeline strictly enforces:

1. **MR-01 (No Unprovenanced Source Facts):** An LLM-generated statement without external source verification can never be classified as `SOURCE` or `SOURCE_FACT`.
2. **MR-02 (Inference Preservation):** Any memory derived from agent reasoning must remain permanently tagged as `OUR_INFERENCE`.
3. **MR-03 (Summary Reference Invariant):** Generated summaries must set `is_generated_summary = True` and explicitly reference underlying canonical IDs.
4. **MR-04 (Provenance Transparency):** Every retrieved `ContextBundle` exposes source IDs, locators, ownership, and epistemic verification states.
5. **MR-05 (No Circular Self-Support):** A memory summary cannot cite itself or use its own generated text to validate underlying claims.
6. **MR-06 (Evidence Chain Termination):** Every evidence chain terminates at a verified external citation or reproducible experimental execution, never an old LLM transcript.

---

## 4. Multi-Signal Hybrid Retrieval Architecture

Retrieval operates through a cascaded multi-signal pipeline:

1. **Exact Stable ID Resolution (Rank 1):** Instant lookup for `CLM-...`, `SRC-...`, `DEC-...`, `EP-...`, `OQ-...`, `LES-...`, `NOD-...`, `RQ...`, `H...`.
2. **Structured Metadata Filter (Rank 2):** Filter by chapter, roadmap node, ownership (`OURS`, `SOURCE`), status (`SUPPORTED`, `CONTESTED`, `FALSIFIED`).
3. **Lexical Full-Text Search (Rank 3):** SQLite FTS5 index matching technical terminology, CVE IDs, method names, author keys.
4. **Semantic Vector Search (Rank 4):** Dense 128d cosine semantic ranking for conceptual similarity.
5. **Graph Traversal & Dialectic Expansion (Rank 5):**
   - Claims expand to linked Evidence and Sources.
   - Contradictory claims are extracted from `ClaimRelation` and `ContradictionRecord` and placed into the `contradictory_evidence` bucket.
   - Decisions expand along `supersedes_id` chains.
   - Research Questions expand to Hypotheses and Open Questions.
6. **Context Packaging & Token Budgeting:** Assemblies are formatted into typed `ContextBundle` objects with token estimation.

---

## 5. Controlled Memory Consolidation Pipeline

```
  [ Session Working Events (M0) ]
                 |
                 v
   +---------------------------+
   |   MR-01..06 Provenance    | ---> Invalid/Unbacked ---> [ REJECTED + Log Reason ]
   |      Verification         |
   +-------------+-------------+
                 | Valid
                 v
   +---------------------------+
   |  Canonical ID Validation  | ---> Non-existent ID  ---> [ REJECTED + Broken Ref ]
   +-------------+-------------+
                 | Valid
                 v
   +---------------------------+
   |   Duplicate Detection     | ---> Identical Topic  ---> [ REJECTED + Duplicate ]
   +-------------+-------------+
                 | Unique
                 v
   +---------------------------+
   |   Contradiction Check     | ---> Conflict Found   ---> [ Record Contradiction / Transition ]
   +-------------+-------------+
                 | Verified
                 v
   +---------------------------+
   |  Promote to CONSOLIDATED  | ---> Persist SQLite + FTS5 + Vectors
   +-------------+-------------+
                 |
                 v
   +---------------------------+
   |  Generate Session Journal | ---> Write `memory/sessions/YYYY-MM-DD_SES-xxxxxx.md`
   |  & Handoff Bundle (CLI)   |
   +---------------------------+
```

---

## 6. Failure Modes & Mitigations (FM-01..FM-15)

| Code | Failure Mode | Mitigation Mechanism |
|---|---|---|
| **FM-01** | Hallucination drift | MR-01..MR-06 invariants block unprovenanced source facts. |
| **FM-02** | Context window overflow | Deterministic token budgeting and structured `ContextBundle` packaging. |
| **FM-03** | Siloing negative results | Mandatory `is_failure = True` logging on `EpisodeRecord` (RC-14). |
| **FM-04** | Overwriting contradicted claims | Contradictions recorded concurrently; status evolves via `StatusTransitionRecord`. |
| **FM-05** | Broken references | Database foreign keys + `MemoryConsolidationService` validation. |
| **FM-06** | Stale / retracted citations | Source retraction status propagation and `MemoryHealthAuditor` MQ-09 check. |
| **FM-07** | Vector index corruption | Zero-dependency local `LocalBM25TFIDFEmbeddingProvider` + disposable vector rebuild. |
| **FM-08** | Circular reasoning | Anti-circular self-support check (MR-05 / MQ-12). |
| **FM-09** | Loss of decision context | Mandatory `rationale` and `consequences` fields on `DecisionRecord`. |
| **FM-10** | Untracked parameter shifts | Immutable dataset and configuration hashes on experiment runs. |
| **FM-11** | Premature question resolution | MQ-15 mandates resolution notes and resolver entity for resolved questions. |
| **FM-12** | Inconsistent skill execution | Versioned procedural markdown protocols stored in `memory/procedural/`. |
| **FM-13** | Database locking / deadlocks | Shared transaction connection indexing (`_index_fts_on_conn`). |
| **FM-14** | Prompt injection via literature | PDF payloads sandboxed as untrusted strings; cannot become executable skills. |
| **FM-15** | Agent amnesia across restarts | Continuation bootstrap ContextBundle generated via `research-agent resume`. |
