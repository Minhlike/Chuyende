---
name: claim_extraction_and_normalization
id: SKILL-01
category: REASONING_FOUNDATION
version: 1.0.0
inputs:
  - text: string (raw scientific paragraph or assertion)
  - source_id: string (optional canonical source key)
  - locator: string (optional section / page / paragraph locator)
outputs:
  - atomic_claims: list[AtomicClaimCandidate]
---

# SKILL-01: Claim Extraction & Proposition Normalization

## 1. Objective
Extract discrete, atomic propositional claims from unstructured or semi-structured scientific text while preserving original scope bounds, qualifiers ("may", "under setup X"), and conditions without rhetorical inflation.

## 2. Invariants
- `CLM-NORM-01`: Multi-clause conjunctions must be split into atomic claims.
- `CLM-NORM-02`: Scope bounds (dataset, domain, metric) must be extracted into `ClaimScope`.
- `CLM-NORM-03`: No causal inflation (do not convert "correlates" to "causes").

## 3. Procedure
1. Segment input text into candidate sentences.
2. Identify and split compound propositional clauses.
3. Extract operational scope parameters (`dataset`, `domain`, `metric`).
4. Identify hedging qualifiers and preconditions.
5. Standardize grammatical capitalization and punctuation.
6. Output list of `AtomicClaimCandidate` objects.
