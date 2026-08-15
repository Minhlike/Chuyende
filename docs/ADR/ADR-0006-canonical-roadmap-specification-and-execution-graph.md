# ADR-0006: Canonical Research Roadmap Specification and Execution Graph

## Status
Accepted

## Date
2026-08-16

## Context
The research project *"Nghiên cứu phương pháp trích xuất đặc trưng đối với dữ liệu log trong phát hiện tấn công"* requires a canonical research specification. The research roadmap is not merely a table of contents; it is the **execution graph** defining problem formulations, research gaps, research questions (RQ1–RQ5), hypotheses (H1–H5), proposed extraction mechanisms, negative controls, evaluation matrices, and claim boundaries.

Key architectural and methodological requirements:
1. **Preservation of Canonical Wording:** No silent alterations, renaming of chapters, or rewriting of technical phrasing (RC-15).
2. **Strict Object Boundary:** The central subject is exclusively the **feature representation** \( \mathbf{z} = f_\theta(\mathcal{L}_{1:t}) \), not an end-to-end intrusion detection system (IDS) or detector \( g \).
3. **Multi-Axis Alignment:** Explicit modeling of 5 core research axes (A1: Fidelity, A2: Multi-view, A3: Shift/Shortcuts, A4: Weak Evidence/Admin Noise, A5: Privacy/Streaming).
4. **Epistemic Invariants:** ATT&CK is modeled as a non-linear behavior/evidence taxonomy (not a linear state machine); provenance dependency is decoupled from causal inference; Tier A logs (HDFS/BGL) are recognized as insufficient alone for cyberattack semantics; negative results are preserved as valid outcomes.
5. **No Source Fabrication:** Literature references mentioned in the roadmap text (e.g. DeepLog, LogBERT, KAIROS) remain unresolved until the formal Reference/Ownership Map ingestion in Prompt 3.

## Decision
1. **Canonical Storage:**
   - Human-readable canonical wording is stored in `research_specs/roadmap/ROADMAP.md`.
   - Structured canonical specification is stored in `research_specs/roadmap/roadmap.yaml` with companion files (`traceability.yaml`, `rq-hypothesis.yaml`, `research-axes.yaml`, `controls.yaml`, `boundaries.yaml`, `VERSION`).
   - Transactional, relational execution state is persisted in SQLite (`roadmaps`, `roadmap_nodes`, `research_questions`, `hypotheses`, `research_axes`, `representation_contracts`, `negative_controls`, `research_boundaries`, `defensibility_questions`, `traceability_entries`).
2. **Idempotent Ingestion:** The `RoadmapIngestionService` validates hierarchy, unique IDs, RQ/H presence, and representation contracts before persisting with deterministic SHA-256 hashing.
3. **Query & Validation Interfaces:** Programmatic access via `RoadmapQueryService` and CLI validation via `python -m research_agent.cli roadmap validate` enforcing non-zero exit codes on integrity failure.

## Consequences
### Positive
- Fully auditable research lineage from gaps in Chapter 1 to mechanisms in Chapter 2 and falsification tests in Chapter 3.
- Complete traceability and negative control enforcement across all RQs.
- System is prepared for Reference/Ownership Map ingestion in Prompt 3.
### Negative / Tradeoffs
- Any future roadmap proposal requires a formal `DecisionRecord` and version increment rather than in-place text edits.
