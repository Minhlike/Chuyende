# Research Agent Long-Term Memory (Prompt 4, Tiers M0..M5)

This directory stores persistent research memory, procedural rubrics, session journals, state snapshots, and human-readable memory exports.

## Directory Structure
- `sessions/`: Persistent markdown session journals (`YYYY-MM-DD_SES-xxxxxx.md`).
- `snapshots/`: JSON point-in-time state snapshots for research recovery.
- `procedural/`: Versioned research skills, protocols, checklists, and evaluation rubrics (M5).
- `exports/`: Human-readable research memory exports (`memory-export.md`).

## Memory Model Taxonomy
- **M0 (Working Memory):** Ephemeral, session-scoped context.
- **M1 (Source Memory):** Canonical bibliographic facts and verified artifacts.
- **M2 (Semantic Research Memory):** Atomic claims, contracts, definitions.
- **M3 (Episodic Research Memory):** Temporal events, experiment runs, and failure logs.
- **M4 (Argument Memory):** Claim-evidence dialectic graph, contradictions, assumptions.
- **M5 (Procedural Memory):** Versioned skills, rubrics, and checklists.

## Hard Rules & Safeguards
- **Memory is not truth:** Memory records reference canonical entities in SQLite database.
- **Anti-Hallucination:** LLM inferences cannot become `SOURCE_FACT` without verified external provenance (MR-01).
- **Contradiction Preservation:** Contradictory evidence is actively extracted and preserved concurrently.
- **Derived Index Disposability:** Derived vector and FTS indexes can be rebuilt at any time via `rebuild-index`.
