# ADR-0011: Academic Composer, Anti-Hallucination Compiler, and Multi-Dimensional Thesis Auditor

## Status
ACCEPTED

## Date
2026-08-16

## Context
A primary risk in LLM-assisted scientific research and thesis writing is hallucination, citation invention, ownership conflation (attributing prior art to oneself or vice versa), and exaggerated causal claims. To eliminate these risks, writing cannot be performed from raw parametric model weights. It must be strictly formulated as a compiler over verified research entities.

## Decision
1. **Document IR Architecture:** Hierarchical representation `ThesisDocument` $\to$ `Chapter` $\to$ `Section` $\to$ `Subsection` $\to$ `Paragraph` $\to$ `Sentence` with typed anchors (`CitationAnchor`, `EquationAnchor`, `TableAnchor`, `FigureAnchor`).
2. **Writing Gates:** Nodes must satisfy prerequisite checks (`NOT_READY`, `PROVISIONAL`, `READY`, `BLOCKED`, `DRAFTED`, `AUDITED`, `APPROVED`).
3. **Anti-Hallucination Compiler:** 10-point sentence-level compilation checking propositional entailment, citation authorization, ownership theft, unbacked novelty buzzwords, causal inflation, and domain invariants (e.g. Anomaly $\ne$ Attack, ATT&CK non-linearity).
4. **Multi-Dimensional Thesis Auditor:** 18 audit categories and 10 Defensibility Questions (DQ-01..DQ-10) evaluated prior to build.
5. **Human Edit Preservation & Invalidation Cascading:** Manual human changes (`is_human_edited=True`) are preserved; upstream invalidations mark referencing paragraphs `STALE`.

## Consequences
- Guarantees 100% scientific provenance and empirical grounding.
- Fails closed in `FINAL` compilation mode if any critical audit issue exists.
- Enables reproducible thesis builds with cryptographic SHA-256 build manifests.
