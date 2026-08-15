# ADR-0001: Local-First Hybrid Persistence Model (SQLite + File Tree)

## Status
Accepted

## Date
2026-08-16

## Context
The research engineering system requires a persistence layer capable of storing heterogeneous research entities (bibliographic sources, atomic claims, evidence passages, argument graphs, LaTeX equations, dataset manifests, and experiment run telemetry).
Key requirements include:
- Complete auditability and local inspectability without requiring cloud or server infrastructure.
- Strong relational integrity for graph queries (claim-evidence-source lineage).
- Human readability for canonical research specifications (Markdown and YAML).
- Windows compatibility with zero runtime friction.

## Decision
We adopt a hybrid local-first persistence architecture:
1. **Relational Canonical Database:** SQLite (`runtime/db/research.db`) is the primary transactional engine for indexed entity queries, graph traversal, monotonic ID sequences, and foreign key integrity.
2. **Filesystem Canonical Artifacts:** Raw PDFs, dataset manifests, experiment configurations, procedural checklists, and versioned research specifications are stored as immutable files with SHA-256 checksums in organized subtrees (`sources/`, `datasets/`, `experiments/`, `research_specs/`, `memory/procedural/`).

## Consequences
### Positive
- Zero external service dependencies; fully functional offline on Windows.
- SQLite provides ACID guarantees, foreign key cascades, and high-performance querying.
- Plain text and structured files allow direct human inspection, Git tracking, and diff audits.
### Negative / Tradeoffs
- Relational tables and file manifests must be kept synchronized via the Storage/Repository layer.
